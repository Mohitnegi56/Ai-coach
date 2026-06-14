# AI Interview Coach

ML and Data Science interview practice app with local speech-to-text and automated answer evaluation.

## What's included

### Phase 1 — Core Pipeline
- **FastAPI backend** with health, question bank, and transcription endpoints
- **React frontend** for question practice and audio recording
- **faster-whisper** STT using the local `base` model (free, runs on CPU)
- **110 curated questions** in `data/questions.json`, tagged by topic and difficulty

### Phase 2 — Answer Evaluation Engine
- **Groq Llama 3** intent extraction (free API) — understands what the candidate is trying to explain
- **sentence-transformers** technical score — cosine similarity vs ideal reference answers
- **language_tool_python** grammar score — local LanguageTool checks
- **Weighted overall score** — 50% technical, 30% intent, 20% grammar

### Phase 3 — Speech Analytics
- **Filler word detection** — regex matching on transcript (`um`, `uh`, `like`, `actually`, etc.) with per-minute frequency
- **Voice confidence** — librosa pitch variance, speaking rate, and pause ratio from recorded audio
- **Communication score** — weighted blend of speaking rate, filler ratio, and sentence structure

### Phase 4 — Computer Vision Add-ons
- **Eye contact** — MediaPipe FaceLandmarker in the browser tracks iris position during recording
- **Emotion detection** — DeepFace analyzes sampled webcam frames for confidence/nervousness signals
- **Presence score** — 55% eye contact + 45% emotion positivity

### Phase 5 — Feedback & Voice Response
- **Groq Llama 3** structured feedback — summary, strengths, improvements, action items
- **TTS voice coaching** — pyttsx3 (offline) with gTTS fallback
- **Radar chart** — SVG radar for Technical, Communication, Presence, Grammar (Plotly optional in Streamlit)

### Phase 6 — Integration & Polish
- **Streamlit UI** — full interview flow with feedback, radar chart, and voice playback
- **SQLite session history** — local DB at `data/sessions.db`
- **Mock interview script** — 12-round validation via `scripts/run_mock_interviews.py`

## Project structure

```text
backend/          FastAPI app, routers, services
frontend/         React + Vite UI
data/             Question bank JSON (with ideal answers)
scripts/          Question bank + ideal answer generator
tests/            API and evaluation tests
```

## Setup

### 1. Python environment

```powershell
cd "AI interview coach"
python -m venv myenv
.\myenv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and add your Groq API key (free at [console.groq.com](https://console.groq.com)):

```env
GROQ_API_KEY=your_key_here
WHISPER_MODEL_SIZE=base
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8
GROQ_MODEL=llama-3.1-8b-instant
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### 3. Generate or refresh the question bank

```powershell
python scripts/generate_questions.py
```

### 4. Start the backend

```powershell
$env:PYTHONPATH="."
uvicorn backend.main:app --reload --reload-dir backend --port 8000
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. Start the frontend

```powershell
cd frontend
npm install
npm run dev
```

App: [http://localhost:5173](http://localhost:5173)

### 6. Streamlit UI (Phase 6)

```powershell
streamlit run streamlit_app.py
```

Streamlit app: [http://localhost:8501](http://localhost:8501)

### 7. Run mock interview validation

```powershell
$env:PYTHONPATH="."
python scripts/run_mock_interviews.py
```

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Service health check |
| GET | `/api/questions/metadata` | Topics, difficulties, counts |
| GET | `/api/questions` | List questions with optional filters |
| GET | `/api/questions/random` | Random question |
| GET | `/api/questions/{id}` | Question by ID |
| POST | `/api/transcribe` | Upload audio and get transcript |
| POST | `/api/evaluate` | Score a transcribed answer |
| POST | `/api/analyze-speech` | Filler words + librosa voice metrics + communication score |
| POST | `/api/analyze-presence` | Eye contact stats + DeepFace emotion on webcam frames |
| POST | `/api/feedback` | Groq structured feedback + radar chart + TTS audio |
| GET | `/api/sessions` | List saved interview sessions |
| GET | `/api/sessions/{id}` | Get a saved session |

### Evaluate request

```json
{
  "question_id": "ml-001",
  "answer": "Supervised learning uses labeled data..."
}
```

### Evaluate response (abbreviated)

```json
{
  "overall_score": 82.5,
  "ideal_answer": "Supervised learning trains on labeled pairs...",
  "intent_source": "groq",
  "technical": { "score": 85.2, "cosine_similarity": 0.852 },
  "intent": { "score": 80.0, "extracted_intent": "...", "key_concepts": ["..."] },
  "grammar": { "score": 78.0, "error_count": 2, "issues": [] }
}
```

Ideal answers are **hidden** from question endpoints and only returned after evaluation.

## Scoring breakdown

| Component | Method | Weight |
|-----------|--------|--------|
| Technical | `all-MiniLM-L6-v2` embedding cosine similarity vs ideal answer | 45% |
| Intent | Groq Llama 3.1 JSON extraction + on-topic scoring | 30% |
| Grammar | LanguageTool error density penalty | 25% |

### Interview score (UI)

When speech and presence analytics are available:

| Component | Weight |
|-----------|--------|
| Content (Phase 2) | 50% |
| Communication (Phase 3) | 25% |
| Presence (Phase 4) | 25% |

### Communication score (Phase 3)

| Sub-score | Weight | Method |
|-----------|--------|--------|
| Speaking rate | 35% | Optimal ~120–160 wpm |
| Filler words | 35% | Lower fillers/min = higher score |
| Sentence structure | 30% | Complete sentences, reasonable length |

## Run tests

```powershell
pip install pytest httpx
$env:PYTHONPATH="."
pytest tests/ -v
```

## Notes

- First transcription downloads the Whisper `base` model (~150 MB).
- First evaluation downloads the `all-MiniLM-L6-v2` embedding model (~90 MB).
- LanguageTool requires **Java 8+** installed for local grammar checks.
- Groq API key is required for intent scoring; technical and grammar work without it in isolation.
- Use Chrome or Edge for microphone + webcam recording in the browser.
- **ffmpeg** is recommended for librosa to decode WebM audio (speech analytics falls back to transcript-only metrics without it).
- DeepFace emotion analysis requires `pip install deepface tf-keras` (first run downloads models).
- MediaPipe FaceLandmarker loads from CDN on first recording (~5 MB).
