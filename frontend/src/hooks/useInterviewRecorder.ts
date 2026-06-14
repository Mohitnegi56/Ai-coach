import { useCallback, useRef, useState } from 'react'
import { detectEyeContact, getFaceLandmarker, resetFaceLandmarkerClock } from './useFaceMesh'

export interface EyeContactStats {
  percentage: number
  samples: number
  lookingAtCamera: number
}

const FRAME_INTERVAL_MS = 2000

function pickAudioMimeType(): string | undefined {
  const candidates = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg']
  return candidates.find((type) => MediaRecorder.isTypeSupported(type))
}

export function useInterviewRecorder() {
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<BlobPart[]>([])
  const frameBlobsRef = useRef<Blob[]>([])
  const eyeStatsRef = useRef({ samples: 0, looking: 0 })
  const rafRef = useRef<number | null>(null)
  const frameTimerRef = useRef<number | null>(null)
  const startTimeRef = useRef<number>(0)
  const landmarkerRef = useRef<Awaited<ReturnType<typeof getFaceLandmarker>> | null>(null)

  const [isRecording, setIsRecording] = useState(false)
  const [isInitializing, setIsInitializing] = useState(false)
  const [faceTrackingReady, setFaceTrackingReady] = useState(false)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const [frameBlobs, setFrameBlobs] = useState<Blob[]>([])
  const [eyeContact, setEyeContact] = useState<EyeContactStats>({
    percentage: 0,
    samples: 0,
    lookingAtCamera: 0,
  })
  const [liveEyeContact, setLiveEyeContact] = useState(0)
  const [recordingDuration, setRecordingDuration] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [warning, setWarning] = useState<string | null>(null)

  const stopTracks = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop())
    streamRef.current = null
  }, [])

  const stopProcessing = useCallback(() => {
    if (rafRef.current !== null) {
      cancelAnimationFrame(rafRef.current)
      rafRef.current = null
    }
    if (frameTimerRef.current !== null) {
      window.clearInterval(frameTimerRef.current)
      frameTimerRef.current = null
    }
  }, [])

  const captureFrame = useCallback(async () => {
    const video = videoRef.current
    if (!video || video.videoWidth === 0) return

    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    const blob = await new Promise<Blob | null>((resolve) => {
      canvas.toBlob((result) => resolve(result), 'image/jpeg', 0.85)
    })
    if (blob) {
      frameBlobsRef.current.push(blob)
      setFrameBlobs([...frameBlobsRef.current])
    }
  }, [])

  const startRecording = useCallback(async () => {
    setError(null)
    setWarning(null)
    setAudioBlob(null)
    setFrameBlobs([])
    setEyeContact({ percentage: 0, samples: 0, lookingAtCamera: 0 })
    setLiveEyeContact(0)
    setRecordingDuration(0)
    setFaceTrackingReady(false)
    chunksRef.current = []
    frameBlobsRef.current = []
    eyeStatsRef.current = { samples: 0, looking: 0 }
    stopProcessing()
    stopTracks()
    setIsInitializing(true)

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' },
      })
      streamRef.current = stream

      const video = videoRef.current
      if (video) {
        video.srcObject = stream
        await video.play()
      }

      const mimeType = pickAudioMimeType()
      const audioStream = new MediaStream(stream.getAudioTracks())
      const mediaRecorder = mimeType
        ? new MediaRecorder(audioStream, { mimeType })
        : new MediaRecorder(audioStream)
      mediaRecorderRef.current = mediaRecorder

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data)
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, {
          type: mediaRecorder.mimeType || mimeType || 'audio/webm',
        })
        setAudioBlob(blob.size > 0 ? blob : null)
        if (blob.size === 0) {
          setError('No audio captured. Try recording for at least 2–3 seconds.')
        }
        setRecordingDuration((performance.now() - startTimeRef.current) / 1000)
        stopProcessing()
        stopTracks()
      }

      resetFaceLandmarkerClock()
      startTimeRef.current = performance.now()
      mediaRecorder.start(250)
      setIsRecording(true)
      setIsInitializing(false)

      void getFaceLandmarker()
        .then((landmarker) => {
          landmarkerRef.current = landmarker
          setFaceTrackingReady(true)
        })
        .catch(() => {
          landmarkerRef.current = null
          setFaceTrackingReady(false)
          setWarning('Eye contact tracking unavailable. Audio recording still works.')
        })

      const trackEyeContact = () => {
        const currentVideo = videoRef.current
        const landmarker = landmarkerRef.current
        if (currentVideo && landmarker) {
          const looking = detectEyeContact(currentVideo, landmarker)
          eyeStatsRef.current.samples += 1
          if (looking) eyeStatsRef.current.looking += 1
          const pct = (eyeStatsRef.current.looking / eyeStatsRef.current.samples) * 100
          setLiveEyeContact(Math.round(pct))
          setEyeContact({
            percentage: Math.round(pct),
            samples: eyeStatsRef.current.samples,
            lookingAtCamera: eyeStatsRef.current.looking,
          })
        }
        rafRef.current = requestAnimationFrame(trackEyeContact)
      }
      rafRef.current = requestAnimationFrame(trackEyeContact)

      frameTimerRef.current = window.setInterval(() => {
        void captureFrame()
      }, FRAME_INTERVAL_MS)
    } catch (err) {
      stopProcessing()
      stopTracks()
      setIsInitializing(false)
      setIsRecording(false)
      setError(err instanceof Error ? err.message : 'Camera/microphone access denied')
    }
  }, [captureFrame, stopProcessing, stopTracks])

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop()
    }
    setIsRecording(false)
    setIsInitializing(false)
  }, [])

  const resetRecording = useCallback(() => {
    stopProcessing()
    stopTracks()
    setAudioBlob(null)
    setFrameBlobs([])
    setEyeContact({ percentage: 0, samples: 0, lookingAtCamera: 0 })
    setLiveEyeContact(0)
    setRecordingDuration(0)
    setFaceTrackingReady(false)
    setError(null)
    setWarning(null)
    chunksRef.current = []
    frameBlobsRef.current = []
    eyeStatsRef.current = { samples: 0, looking: 0 }
    landmarkerRef.current = null
    if (videoRef.current) videoRef.current.srcObject = null
  }, [stopProcessing, stopTracks])

  return {
    videoRef,
    isRecording,
    isInitializing,
    faceTrackingReady,
    audioBlob,
    frameBlobs,
    eyeContact,
    liveEyeContact,
    recordingDuration,
    error,
    warning,
    startRecording,
    stopRecording,
    resetRecording,
  }
}
