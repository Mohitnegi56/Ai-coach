import { FaceLandmarker, FilesetResolver, type NormalizedLandmark } from '@mediapipe/tasks-vision'

const MODEL_URL =
  'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task'

const WASM_URL = 'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm'

const LEFT_IRIS = 468
const RIGHT_IRIS = 473
const LEFT_INNER = 133
const LEFT_OUTER = 33
const RIGHT_INNER = 362
const RIGHT_OUTER = 263

let landmarkerPromise: Promise<FaceLandmarker> | null = null
let frameTimestamp = 0

export async function getFaceLandmarker(): Promise<FaceLandmarker> {
  if (!landmarkerPromise) {
    landmarkerPromise = createLandmarker('GPU').catch(() => createLandmarker('CPU'))
  }
  return landmarkerPromise
}

async function createLandmarker(delegate: 'GPU' | 'CPU'): Promise<FaceLandmarker> {
  const vision = await FilesetResolver.forVisionTasks(WASM_URL)
  return FaceLandmarker.createFromOptions(vision, {
    baseOptions: { modelAssetPath: MODEL_URL, delegate },
    runningMode: 'VIDEO',
    numFaces: 1,
    outputFaceBlendshapes: false,
  })
}

export function resetFaceLandmarkerClock(): void {
  frameTimestamp = 0
}

function irisRatio(landmarks: NormalizedLandmark[], iris: number, outer: number, inner: number): number {
  const outerX = landmarks[outer].x
  const innerX = landmarks[inner].x
  const irisX = landmarks[iris].x
  const span = innerX - outerX
  if (Math.abs(span) < 0.001) return 0.5
  return (irisX - outerX) / span
}

function headPoseLookingAtCamera(landmarks: NormalizedLandmark[]): boolean {
  const nose = landmarks[1]
  const leftCheek = landmarks[234]
  const rightCheek = landmarks[454]
  const faceCenterX = (leftCheek.x + rightCheek.x) / 2
  const horizontalOffset = Math.abs(nose.x - faceCenterX)
  const faceWidth = Math.abs(rightCheek.x - leftCheek.x)
  if (faceWidth < 0.001) return false
  return horizontalOffset / faceWidth < 0.12
}

export function isLookingAtCamera(landmarks: NormalizedLandmark[]): boolean {
  if (landmarks.length > RIGHT_IRIS) {
    const leftRatio = irisRatio(landmarks, LEFT_IRIS, LEFT_OUTER, LEFT_INNER)
    const rightRatio = irisRatio(landmarks, RIGHT_IRIS, RIGHT_OUTER, RIGHT_INNER)
    return leftRatio >= 0.35 && leftRatio <= 0.65 && rightRatio >= 0.35 && rightRatio <= 0.65
  }
  return headPoseLookingAtCamera(landmarks)
}

export function detectEyeContact(video: HTMLVideoElement, landmarker: FaceLandmarker): boolean {
  if (video.readyState < 2 || video.videoWidth === 0) return false
  frameTimestamp += 33
  const result = landmarker.detectForVideo(video, frameTimestamp)
  const landmarks = result.faceLandmarks?.[0]
  if (!landmarks) return false
  return isLookingAtCamera(landmarks)
}
