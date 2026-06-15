# AI Interview Coach

🚀 **Live Demo:** [AI Interview Coach](https://ai-coach-gqwwv59m9-mohit-negis-projects-11ef8bac.vercel.app/)

A full-stack, AI-powered simulator designed to help machine learning and data science candidates practice technical interviews with real-time feedback, speech analytics, and behavioral insights.

---

## Key Features

- **💡 Technical Evaluation**: Uses local SentenceTransformers (`all-MiniLM-L6-v2`) to compute semantic cosine similarity against golden answers, combined with local LanguageTool grammar checks and Groq-powered intent extraction.
- **🎤 Speech & Communication Analytics**: Matches spoken answers against filler words and uses `librosa` to analyze speech cadence, speaking rate (WPM), and pauses. Includes offline TTS voice coaching.
- **👁️ Computer Vision Insights**: Browser-side MediaPipe iris tracking evaluates eye contact. Sampled frames are checked via `DeepFace` for emotion/confidence timeline insights.
- **📊 Interactive Radar Charts**: Visualizes score breakdowns (Technical, Communication, Presence, Grammar) in a comprehensive radar graph.
- **💾 Session Persistence**: Locally archives all mock interviews, transcripts, and evaluation history using SQLite.

---

## Project Structure

```text
backend/          FastAPI application, routers, scoring/TTS services
frontend/         React + TypeScript + Vite dashboard
tests/            Pytest unit and integration test suite
scripts/          Question bank generator & mock run scripts
```

---

## Setup & Execution

### 1. Backend Server Setup

```powershell
# Create & activate a virtual environment
python -m venv myenv
.\myenv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Create .env config
# Add your GROQ_API_KEY from console.groq.com
```

Start the FastAPI application:
```powershell
$env:PYTHONPATH="backend"
uvicorn main:app --reload --port 8000
```
*API Swagger Documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).*

### 2. Frontend Application Setup

In a new terminal:
```powershell
cd frontend
npm install
npm run dev
```
*Access the interactive interface at [http://localhost:5173](http://localhost:5173).*

---

## Verification & Testing

Verify that all systems and scorers are working properly:

- **Run Pytest Suite**:
  ```powershell
  .\myenv\Scripts\pytest
  ```
- **Run Mock Interview Simulator**:
  ```powershell
  .\myenv\Scripts\python scripts/run_mock_interviews.py
  ```
