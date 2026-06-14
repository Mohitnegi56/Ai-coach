import { useEffect, useState } from 'react'
import {
  analyzePresence,
  analyzeSpeech,
  computeInterviewScore,
  evaluateAnswer,
  generateFeedback,
  getMetadata,
  getRandomQuestion,
  transcribeAudio,
} from './api/client'
import { useInterviewRecorder } from './hooks/useInterviewRecorder'
import type {
  Difficulty,
  EvaluationResponse,
  InterviewAnalysis,
  Question,
  QuestionBankMetadata,
} from './types'
import './App.css'

const TOPIC_LABELS: Record<string, string> = {
  machine_learning: 'Machine Learning',
  deep_learning: 'Deep Learning',
  statistics: 'Statistics',
  python_data: 'Python & Data',
  feature_engineering: 'Feature Engineering',
  model_evaluation: 'Model Evaluation',
  nlp: 'NLP',
  computer_vision: 'Computer Vision',
  mlops: 'MLOps',
  sql_databases: 'SQL & Databases',
}

function formatTopic(topic: string) {
  return TOPIC_LABELS[topic] ?? topic.replaceAll('_', ' ')
}

function scoreClass(score: number) {
  if (score >= 75) return 'good'
  if (score >= 50) return 'mid'
  return 'low'
}

function App() {
  const [metadata, setMetadata] = useState<QuestionBankMetadata | null>(null)
  const [question, setQuestion] = useState<Question | null>(null)
  const [topic, setTopic] = useState('')
  const [difficulty, setDifficulty] = useState<Difficulty | ''>('')
  const [transcript, setTranscript] = useState('')
  const [analysis, setAnalysis] = useState<InterviewAnalysis | null>(null)
  const [loadingQuestion, setLoadingQuestion] = useState(false)
  const [loadingTranscript, setLoadingTranscript] = useState(false)
  const [loadingEvaluation, setLoadingEvaluation] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [warnings, setWarnings] = useState<string[]>([])

  const {
    videoRef,
    isRecording,
    isInitializing,
    faceTrackingReady,
    audioBlob,
    frameBlobs,
    eyeContact,
    liveEyeContact,
    recordingDuration,
    error: recorderError,
    warning: recorderWarning,
    startRecording,
    stopRecording,
    resetRecording,
  } = useInterviewRecorder()

  useEffect(() => {
    getMetadata()
      .then(setMetadata)
      .catch((err: Error) => setError(err.message))
  }, [])

  const loadQuestion = async () => {
    setLoadingQuestion(true)
    setError(null)
    setTranscript('')
    setAnalysis(null)
    setWarnings([])
    resetRecording()

    try {
      const next = await getRandomQuestion(topic || undefined, difficulty || undefined)
      setQuestion(next)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load question')
    } finally {
      setLoadingQuestion(false)
    }
  }

  const handleTranscribe = async () => {
    if (!audioBlob) return

    setLoadingTranscript(true)
    setError(null)
    setAnalysis(null)

    try {
      const result = await transcribeAudio(audioBlob)
      setTranscript(result.text)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Transcription failed')
    } finally {
      setLoadingTranscript(false)
    }
  }

  const handleEvaluate = async () => {
    if (!question || !transcript.trim()) return

    setLoadingEvaluation(true)
    setError(null)
    setWarnings([])

    try {
      const results = await Promise.allSettled([
        evaluateAnswer(question.id, transcript),
        audioBlob
          ? analyzeSpeech(audioBlob, transcript, recordingDuration || undefined)
          : Promise.resolve(null),
        frameBlobs.length > 0 || eyeContact.samples > 0
          ? analyzePresence(frameBlobs, eyeContact)
          : Promise.resolve(null),
      ])

      const nextWarnings: string[] = []

      if (results[0].status === 'rejected') {
        throw results[0].reason
      }

      const evaluation = results[0].value
      const speech = results[1].status === 'fulfilled' ? results[1].value : null
      const presence = results[2].status === 'fulfilled' ? results[2].value : null

      if (results[1].status === 'rejected') {
        const reason = results[1].reason
        nextWarnings.push(
          `Speech analytics failed: ${reason instanceof Error ? reason.message : String(reason)}`,
        )
      }
      if (results[2].status === 'rejected') {
        const reason = results[2].reason
        nextWarnings.push(
          `Presence analytics failed: ${reason instanceof Error ? reason.message : String(reason)}`,
        )
      }

      const interviewScore = computeInterviewScore(evaluation, speech, presence)
      const communicationScore = speech?.communication.score ?? evaluation.overall_score * 0.7
      const presenceScore = presence?.score ?? 65

      let feedbackPackage = null
      try {
        feedbackPackage = await generateFeedback({
          question_id: question.id,
          question: question.question,
          answer: transcript,
          topic: question.topic,
          difficulty: question.difficulty,
          technical: evaluation.technical.score,
          communication: communicationScore,
          presence: presenceScore,
          grammar: evaluation.grammar.score,
          interview_score: interviewScore,
        })
      } catch (err) {
        nextWarnings.push(
          `Feedback generation failed: ${err instanceof Error ? err.message : String(err)}`,
        )
      }

      setWarnings(nextWarnings)
      setAnalysis({
        evaluation,
        speech,
        presence,
        interview_score: interviewScore,
        feedbackPackage,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Evaluation failed')
    } finally {
      setLoadingEvaluation(false)
    }
  }

  const evaluation: EvaluationResponse | null = analysis?.evaluation ?? null

  return (
    <div className="app">
      <header className="header">
        <div>
          <p className="eyebrow">Phases 2–6 · Full Interview Coach</p>
          <h1>AI Interview Coach</h1>
          <p className="subtitle">
            Practice ML interviews with scoring, speech & presence analytics, Groq feedback, and voice coaching.
          </p>
        </div>
        {metadata && (
          <div className="stats">
            <span>{metadata.total_questions} questions</span>
            <span>{metadata.topics.length} topics</span>
          </div>
        )}
      </header>

      <section className="panel filters">
        <label>
          Topic
          <select value={topic} onChange={(event) => setTopic(event.target.value)}>
            <option value="">All topics</option>
            {metadata?.topics.map((item) => (
              <option key={item} value={item}>
                {formatTopic(item)}
              </option>
            ))}
          </select>
        </label>

        <label>
          Difficulty
          <select
            value={difficulty}
            onChange={(event) => setDifficulty(event.target.value as Difficulty | '')}
          >
            <option value="">All levels</option>
            {metadata?.difficulties.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>

        <button type="button" className="primary" onClick={loadQuestion} disabled={loadingQuestion}>
          {loadingQuestion ? 'Loading…' : question ? 'Next Question' : 'Start Interview'}
        </button>
      </section>

      {error && <div className="alert error">{error}</div>}
      {recorderError && <div className="alert error">{recorderError}</div>}
      {recorderWarning && <div className="alert warn">{recorderWarning}</div>}
      {warnings.length > 0 && (
        <div className="alert warn">
          {warnings.map((item) => (
            <p key={item}>{item}</p>
          ))}
        </div>
      )}

      {question && (
        <section className="panel question-card">
          <div className="badges">
            <span className="badge topic">{formatTopic(question.topic)}</span>
            <span className={`badge difficulty ${question.difficulty}`}>{question.difficulty}</span>
          </div>
          <h2>{question.question}</h2>
          <p className="question-id">ID: {question.id}</p>
        </section>
      )}

      {question && (
        <section className="panel answer-card">
          <h3>Your Answer</h3>
          <p className="hint">
            Record with webcam enabled. Eye contact is tracked live; frames are analyzed for emotion after you evaluate.
          </p>

          <div className="media-layout">
            <div className="webcam-panel">
              <video ref={videoRef} className="webcam-preview" muted playsInline />
              {isRecording && (
                <div className="live-metrics">
                  <span className="live-pill recording">REC</span>
                  <span className="live-pill">Eye contact {liveEyeContact}%</span>
                  <span className="live-pill">{frameBlobs.length} frames captured</span>
                </div>
              )}
              {!isRecording && !audioBlob && (
                <div className="webcam-placeholder">Webcam preview appears when recording starts</div>
              )}
            </div>

            <div className="controls-column">
              <div className="controls">
                {!isRecording ? (
                  <button type="button" className="primary" onClick={startRecording} disabled={isInitializing}>
                    {isInitializing ? 'Starting camera…' : 'Start Recording'}
                  </button>
                ) : (
                  <button type="button" className="danger" onClick={stopRecording}>
                    Stop Recording
                  </button>
                )}

                <button
                  type="button"
                  onClick={handleTranscribe}
                  disabled={!audioBlob || loadingTranscript}
                >
                  {loadingTranscript ? 'Transcribing…' : 'Transcribe Answer'}
                </button>

                <button
                  type="button"
                  className="primary"
                  onClick={handleEvaluate}
                  disabled={!transcript.trim() || loadingEvaluation}
                >
                  {loadingEvaluation ? 'Analyzing…' : 'Evaluate Answer'}
                </button>

                {audioBlob && (
                  <button type="button" className="ghost" onClick={resetRecording}>
                    Clear Recording
                  </button>
                )}
              </div>

              {isRecording && (
                <p className="recording-indicator">
                  Recording… speak your answer now.
                  {faceTrackingReady ? ` Eye contact ${liveEyeContact}%.` : ' Loading face tracking…'}
                </p>
              )}

              {audioBlob && !isRecording && (
                <p className="hint">
                  Recorded {recordingDuration.toFixed(1)}s · eye contact {eyeContact.percentage}% ·{' '}
                  {frameBlobs.length} frame(s) for emotion analysis
                </p>
              )}
            </div>
          </div>

          {transcript && (
            <div className="transcript">
              <h4>Transcript</h4>
              <p className="hint">Edit the transcript if speech-to-text made mistakes before evaluating.</p>
              <textarea
                className="transcript-editor"
                value={transcript}
                onChange={(event) => {
                  setTranscript(event.target.value)
                  setAnalysis(null)
                }}
                rows={5}
              />
            </div>
          )}
        </section>
      )}

      {analysis && evaluation && (
        <>
          <section className="panel evaluation-card">
            <div className="overall-score">
              <span className="overall-label">Interview Score</span>
              <span className={`overall-value ${scoreClass(analysis.interview_score)}`}>
                {analysis.interview_score.toFixed(1)}
              </span>
            </div>

            <div className="score-grid score-grid-5">
              <div className="score-item">
                <span className="score-label">Content</span>
                <span className={`score-value ${scoreClass(evaluation.overall_score)}`}>
                  {evaluation.overall_score.toFixed(1)}
                </span>
                <span className="score-meta">answer quality</span>
              </div>
              {analysis.speech && (
                <div className="score-item">
                  <span className="score-label">Communication</span>
                  <span className={`score-value ${scoreClass(analysis.speech.communication.score)}`}>
                    {analysis.speech.communication.score.toFixed(1)}
                  </span>
                  <span className="score-meta">{analysis.speech.voice_source} voice</span>
                </div>
              )}
              {analysis.presence && (
                <div className="score-item">
                  <span className="score-label">Presence</span>
                  <span className={`score-value ${scoreClass(analysis.presence.score)}`}>
                    {analysis.presence.score.toFixed(1)}
                  </span>
                  <span className="score-meta">{analysis.presence.dominant_emotion}</span>
                </div>
              )}
              <div className="score-item">
                <span className="score-label">Technical</span>
                <span className={`score-value ${scoreClass(evaluation.technical.score)}`}>
                  {evaluation.technical.score.toFixed(1)}
                </span>
                <span className="score-meta">cosine {evaluation.technical.cosine_similarity.toFixed(3)}</span>
              </div>
              <div className="score-item">
                <span className="score-label">Intent</span>
                <span className={`score-value ${scoreClass(evaluation.intent.score)}`}>
                  {evaluation.intent.score.toFixed(1)}
                </span>
                <span className="score-meta">
                  {evaluation.intent.addresses_question ? 'on-topic' : 'off-topic'}
                </span>
              </div>
            </div>
          </section>

          {analysis.speech && (
            <section className="panel analytics-card">
              <h3>Speech Analytics</h3>
              <div className="score-grid">
                <div className="score-item">
                  <span className="score-label">Voice Confidence</span>
                  <span className={`score-value ${scoreClass(analysis.speech.communication.voice_confidence ?? 0)}`}>
                    {(analysis.speech.communication.voice_confidence ?? 0).toFixed(1)}
                  </span>
                  <span className="score-meta">{analysis.speech.communication.speaking_rate_wpm} wpm</span>
                </div>
                <div className="score-item">
                  <span className="score-label">Filler Words</span>
                  <span className={`score-value ${scoreClass(analysis.speech.communication.filler_score)}`}>
                    {analysis.speech.communication.filler_score.toFixed(1)}
                  </span>
                  <span className="score-meta">
                    {analysis.speech.communication.filler_words.total_count} total ·{' '}
                    {analysis.speech.communication.filler_words.per_minute}/min
                  </span>
                </div>
                <div className="score-item">
                  <span className="score-label">Structure</span>
                  <span className={`score-value ${scoreClass(analysis.speech.communication.structure_score)}`}>
                    {analysis.speech.communication.structure_score.toFixed(1)}
                  </span>
                  <span className="score-meta">sentence clarity</span>
                </div>
              </div>

              {Object.keys(analysis.speech.communication.filler_words.breakdown).length > 0 && (
                <div className="feedback-block">
                  <h4>Filler Breakdown</h4>
                  <div className="chips">
                    {Object.entries(analysis.speech.communication.filler_words.breakdown).map(([word, count]) => (
                      <span key={word} className="chip">
                        {word}: {count}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {analysis.speech.communication.pitch_variance !== null && (
                <p className="feedback-text">
                  Pitch variance {analysis.speech.communication.pitch_variance.toFixed(3)} · pause ratio{' '}
                  {(analysis.speech.communication.pause_ratio ?? 0).toFixed(2)}
                </p>
              )}
            </section>
          )}

          {analysis.presence && (
            <section className="panel analytics-card">
              <h3>Presence Analytics</h3>
              <div className="score-grid">
                <div className="score-item">
                  <span className="score-label">Eye Contact</span>
                  <span className={`score-value ${scoreClass(analysis.presence.eye_contact_score)}`}>
                    {analysis.presence.eye_contact_score.toFixed(1)}
                  </span>
                  <span className="score-meta">
                    {analysis.presence.eye_contact.looking_at_camera}/{analysis.presence.eye_contact.samples} samples
                  </span>
                </div>
                <div className="score-item">
                  <span className="score-label">Emotion</span>
                  <span className={`score-value ${scoreClass(analysis.presence.emotion_score)}`}>
                    {analysis.presence.emotion_score.toFixed(1)}
                  </span>
                  <span className="score-meta">{analysis.presence.dominant_emotion}</span>
                </div>
                <div className="score-item">
                  <span className="score-label">Frames</span>
                  <span className="score-value mid">{analysis.presence.frames_analyzed}</span>
                  <span className="score-meta">MediaPipe + DeepFace</span>
                </div>
              </div>

              {analysis.presence.emotions.length > 0 && (
                <div className="feedback-block">
                  <h4>Emotion Timeline</h4>
                  <ul className="issue-list">
                    {analysis.presence.emotions.map((snapshot) => (
                      <li key={snapshot.timestamp_seconds}>
                        <strong>
                          {snapshot.timestamp_seconds}s · {snapshot.dominant_emotion}
                        </strong>
                        <span>{snapshot.confidence.toFixed(1)}% confidence</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </section>
          )}

          {analysis.feedbackPackage && (
            <section className="panel feedback-card">
              <h3>Coaching Feedback</h3>
              <div className="feedback-layout">
                <div>
                  <p>{analysis.feedbackPackage.feedback.summary}</p>
                  <div className="feedback-block">
                    <h4>Strengths</h4>
                    <ul className="issue-list">
                      {analysis.feedbackPackage.feedback.strengths.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="feedback-block">
                    <h4>Improvements</h4>
                    <ul className="issue-list">
                      {analysis.feedbackPackage.feedback.improvements.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="feedback-block">
                    <h4>Action Items</h4>
                    <ul className="issue-list">
                      {analysis.feedbackPackage.feedback.action_items.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  {analysis.feedbackPackage.audio_base64 && (
                    <div className="feedback-block">
                      <h4>Voice Feedback</h4>
                      <audio
                        controls
                        src={`data:${analysis.feedbackPackage.audio_mime ?? 'audio/wav'};base64,${analysis.feedbackPackage.audio_base64}`}
                      />
                    </div>
                  )}
                  {analysis.feedbackPackage.session_id && (
                    <p className="hint">Session saved #{analysis.feedbackPackage.session_id}</p>
                  )}
                </div>
                <div className="radar-panel">
                  <h4>Score Radar</h4>
                  <img
                    className="radar-chart"
                    src={`data:image/svg+xml;base64,${analysis.feedbackPackage.radar_chart_base64}`}
                    alt="Interview score radar chart"
                  />
                </div>
              </div>
            </section>
          )}

          <section className="panel evaluation-card">
            <h3>Answer Evaluation</h3>
            <div className="score-grid">
              <div className="score-item">
                <span className="score-label">Technical</span>
                <span className={`score-value ${scoreClass(evaluation.technical.score)}`}>
                  {evaluation.technical.score.toFixed(1)}
                </span>
              </div>
              <div className="score-item">
                <span className="score-label">Intent</span>
                <span className={`score-value ${scoreClass(evaluation.intent.score)}`}>
                  {evaluation.intent.score.toFixed(1)}
                </span>
              </div>
              <div className="score-item">
                <span className="score-label">Grammar</span>
                <span className={`score-value ${scoreClass(evaluation.grammar.score)}`}>
                  {evaluation.grammar.score.toFixed(1)}
                </span>
                <span className="score-meta">{evaluation.grammar.error_count} issues</span>
              </div>
            </div>

            <div className="feedback-block">
              <h4>Intent Analysis</h4>
              <p>{evaluation.intent.extracted_intent}</p>
              {evaluation.intent.key_concepts.length > 0 && (
                <div className="chips">
                  {evaluation.intent.key_concepts.map((concept) => (
                    <span key={concept} className="chip">{concept}</span>
                  ))}
                </div>
              )}
              <p className="feedback-text">{evaluation.intent.feedback}</p>
            </div>

            {evaluation.grammar.issues.length > 0 && (
              <div className="feedback-block">
                <h4>Grammar Issues</h4>
                <ul className="issue-list">
                  {evaluation.grammar.issues.map((issue, index) => (
                    <li key={`${issue.offset}-${index}`}>
                      <strong>{issue.message}</strong>
                      <span>{issue.context}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="feedback-block ideal-answer-block">
              <h4>Reference Answer</h4>
              {evaluation.intent_source === 'fallback' && (
                <p className="hint">Intent scoring used a local fallback — set GROQ_API_KEY for richer analysis.</p>
              )}
              <p className="ideal-answer">{evaluation.ideal_answer}</p>
            </div>
          </section>
        </>
      )}

      {!question && !loadingQuestion && (
        <section className="panel empty-state">
          <h3>Ready when you are</h3>
          <p>Choose filters if you want, then click Start Interview to get your first question.</p>
        </section>
      )}
    </div>
  )
}

export default App
