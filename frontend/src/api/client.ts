import type {
  EvaluationResponse,
  FeedbackPackageResponse,
  PresenceAnalyticsResponse,
  Question,
  QuestionBankMetadata,
  SpeechAnalyticsResponse,
  TranscriptionResponse,
} from '../types'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'

function parseErrorDetail(raw: string, status: number): string {
  if (!raw) return `Request failed (${status})`
  try {
    const payload = JSON.parse(raw) as { detail?: string | Array<{ msg: string }> }
    if (typeof payload.detail === 'string') return payload.detail
    if (Array.isArray(payload.detail)) {
      return payload.detail.map((item) => item.msg).join('; ')
    }
  } catch {
    // plain text response
  }
  return raw
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init)
  if (!response.ok) {
    const detail = await response.text()
    throw new Error(parseErrorDetail(detail, response.status))
  }
  return response.json() as Promise<T>
}

export function getMetadata(): Promise<QuestionBankMetadata> {
  return request<QuestionBankMetadata>('/questions/metadata')
}

export function getRandomQuestion(
  topic?: string,
  difficulty?: string,
): Promise<Question> {
  const params = new URLSearchParams()
  if (topic) params.set('topic', topic)
  if (difficulty) params.set('difficulty', difficulty)
  const query = params.toString()
  return request<Question>(`/questions/random${query ? `?${query}` : ''}`)
}

export async function transcribeAudio(blob: Blob, filename = 'recording.webm'): Promise<TranscriptionResponse> {
  const formData = new FormData()
  formData.append('file', blob, filename)
  return request<TranscriptionResponse>('/transcribe', {
    method: 'POST',
    body: formData,
  })
}

export function evaluateAnswer(questionId: string, answer: string): Promise<EvaluationResponse> {
  return request<EvaluationResponse>('/evaluate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question_id: questionId, answer }),
  })
}

export async function analyzeSpeech(
  blob: Blob,
  transcript: string,
  durationSeconds?: number,
  filename = 'recording.webm',
): Promise<SpeechAnalyticsResponse> {
  const formData = new FormData()
  formData.append('file', blob, filename)
  formData.append('transcript', transcript)
  if (durationSeconds !== undefined) {
    formData.append('duration_seconds', String(durationSeconds))
  }
  return request<SpeechAnalyticsResponse>('/analyze-speech', {
    method: 'POST',
    body: formData,
  })
}

export async function analyzePresence(
  frames: Blob[],
  eyeContact: { percentage: number; samples: number; lookingAtCamera: number },
): Promise<PresenceAnalyticsResponse> {
  const formData = new FormData()
  formData.append('eye_contact_percentage', String(eyeContact.percentage))
  formData.append('eye_contact_samples', String(eyeContact.samples))
  formData.append('eye_contact_looking', String(eyeContact.lookingAtCamera))
  frames.forEach((frame, index) => {
    formData.append('frames', frame, `frame-${index}.jpg`)
  })
  return request<PresenceAnalyticsResponse>('/analyze-presence', {
    method: 'POST',
    body: formData,
  })
}

export function computeInterviewScore(
  evaluation: EvaluationResponse,
  speech: SpeechAnalyticsResponse | null,
  presence: PresenceAnalyticsResponse | null,
): number {
  const contentScore = evaluation.overall_score
  const speechScore = speech?.communication.score ?? null
  const presenceScore = presence?.score ?? null

  if (speechScore !== null && presenceScore !== null) {
    return contentScore * 0.5 + speechScore * 0.25 + presenceScore * 0.25
  }
  if (speechScore !== null) {
    return contentScore * 0.65 + speechScore * 0.35
  }
  if (presenceScore !== null) {
    return contentScore * 0.65 + presenceScore * 0.35
  }
  return contentScore
}

export function generateFeedback(payload: {
  question_id: string
  question: string
  answer: string
  topic: string
  difficulty: string
  technical: number
  communication: number
  presence: number
  grammar: number
  interview_score: number
  save_session?: boolean
}): Promise<FeedbackPackageResponse> {
  return request<FeedbackPackageResponse>('/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...payload,
      include_tts: true,
      save_session: payload.save_session ?? true,
    }),
  })
}
