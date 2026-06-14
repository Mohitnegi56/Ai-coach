export type Difficulty = 'easy' | 'medium' | 'hard'

export interface Question {
  id: string
  question: string
  topic: string
  difficulty: Difficulty
  tags: string[]
}

export interface QuestionBankMetadata {
  version: string
  total_questions: number
  topics: string[]
  difficulties: string[]
}

export interface TranscriptionResponse {
  text: string
  language: string | null
  duration_seconds: number | null
}

export interface GrammarIssue {
  message: string
  context: string
  offset: number
  length: number
}

export interface IntentResult {
  extracted_intent: string
  key_concepts: string[]
  addresses_question: boolean
  score: number
  feedback: string
}

export interface TechnicalResult {
  score: number
  cosine_similarity: number
}

export interface GrammarResult {
  score: number
  error_count: number
  issues: GrammarIssue[]
}

export interface EvaluationResponse {
  question_id: string
  question: string
  answer: string
  ideal_answer: string
  intent: IntentResult
  technical: TechnicalResult
  grammar: GrammarResult
  overall_score: number
  intent_source: 'groq' | 'fallback'
}

export interface FillerWordResult {
  total_count: number
  per_minute: number
  breakdown: Record<string, number>
}

export interface CommunicationResult {
  score: number
  speaking_rate_score: number
  filler_score: number
  structure_score: number
  voice_confidence: number | null
  speaking_rate_wpm: number
  pitch_variance: number | null
  pause_ratio: number | null
  filler_words: FillerWordResult
}

export interface SpeechAnalyticsResponse {
  communication: CommunicationResult
  voice_source: 'librosa' | 'unavailable'
}

export interface EyeContactStats {
  percentage: number
  samples: number
  looking_at_camera: number
}

export interface EmotionSnapshot {
  timestamp_seconds: number
  dominant_emotion: string
  confidence: number
  scores: Record<string, number>
}

export interface PresenceAnalyticsResponse {
  score: number
  eye_contact: EyeContactStats
  eye_contact_score: number
  emotion_score: number
  dominant_emotion: string
  emotions: EmotionSnapshot[]
  frames_analyzed: number
}

export interface InterviewAnalysis {
  evaluation: EvaluationResponse
  speech: SpeechAnalyticsResponse | null
  presence: PresenceAnalyticsResponse | null
  interview_score: number
  feedbackPackage: FeedbackPackageResponse | null
}

export interface ScoreRadar {
  technical: number
  communication: number
  presence: number
  grammar: number
}

export interface FeedbackResponse {
  summary: string
  strengths: string[]
  improvements: string[]
  action_items: string[]
  voice_script: string
  radar: ScoreRadar
  interview_score: number
  source: 'groq' | 'fallback'
}

export interface FeedbackPackageResponse {
  feedback: FeedbackResponse
  radar_chart_base64: string
  audio_base64: string | null
  audio_mime: string | null
  session_id: number | null
}
