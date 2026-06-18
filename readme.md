# Plum AI Claims Multi-Agent Adjudicator 🚀

An autonomous, multi-agent AI pipeline designed to instantly adjudicate health insurance claims. Built with **LangGraph**, **FastAPI**, **Next.js**, and **Google Vertex AI (Gemini Flash)**, this system automates triage, medical data extraction, and strict policy evaluation while providing full human-readable reasoning traces for compliance.

---

## ✨ Core Features

1. **Multi-Agent State Machine (LangGraph)**
   * **Agent 1: Triage:** Validates uploaded documents (Prescriptions, Hospital Bills, etc.) against specific claim category requirements.
   * **Agent 2: Extraction:** Maps unstructured medical documents into a strict JSON schema, flagging missing data and calculating extraction confidence.
   * **Agent 3: Adjudicator:** Applies strict insurance policy rules (co-pays, network discounts, sub-limits, waiting periods, fraud flags) to calculate final payouts.
2. **Automated Compliance Evaluation Suite**
   * A built-in testing engine that runs 12 complex edge-case scenarios (e.g., fraud velocity, out-of-network math, missing prescriptions) against ground-truth expected outcomes.
3. **Live Admin Dashboard & Processing**
   * A responsive Next.js interface for live claim submission and an admin queue to review AI decisions, reasoning traces, and trigger manual overrides.

---

## 🛠️ Tech Stack

* **Frontend:** Next.js (React), Tailwind CSS, Lucide React
* **Backend:** Python, FastAPI, Uvicorn
* **AI & Orchestration:** LangGraph, LangChain, Google Vertex AI (`gemini-2.5-flash` / `gemini-1.5-flash`), Pydantic

---

## 🚀 Local Setup Instructions

### Prerequisites
* **Python 3.10+** installed
* **Node.js 18+** installed
* A **Google Cloud Platform (GCP)** account with the **Vertex AI API** enabled and a Service Account JSON key.

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/insurance-claim-agent.git](https://github.com/your-username/insurance-claim-agent.git)
cd insurance-claim-agent
```

### 2. Backend Setup (FastAPI + LangGraph)
Open a terminal and navigate to the `backend` directory:
```bash
cd backend
```

Create and activate a virtual environment:
```bash
# On Windows:
python -m venv venv
.\venv\Scripts\activate

# On Mac/Linux:
python3 -m venv venv
source venv/bin/activate
```

Install the required Python dependencies:
```bash
pip install -r requirements.txt
```

Set up your Environment Variables:
1. Create a `.env` file inside the `backend` folder.
2. Add the following variables:
```env
GCP_PROJECT_ID="your-gcp-project-id"
GCP_LOCATION="us-central1"
GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-file.json"
```

Start the FastAPI Server:
```bash
# Ensure you are in the backend directory
python main.py

# Alternatively, run with uvicorn directly:
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
*The backend is now running at http://localhost:8000*

### 3. Frontend Setup (Next.js)
Open a **new** terminal window and navigate to the `frontend` directory:
```bash
cd frontend
```

Install the Node dependencies:
```bash
npm install
```

Set up your Environment Variables:
1. Create a `.env.local` file inside the `frontend` folder.
2. Add the API URL to connect to your local backend:
```env
NEXT_PUBLIC_API_URL="http://localhost:8000"
```

Start the Next.js Development Server:
```bash
npm run dev
```
*The frontend is now running at http://localhost:3000*

---

## 🧪 How to Use the Application

1. **Process a Live Claim:** * Navigate to `http://localhost:3000`.
   * Fill out the claim details and submit.
   * Watch the AI process the claim in 2-3 seconds and generate a detailed reasoning trace.
2. **Run the Automated Evaluation Suite:**
   * Navigate to the **Eval Report** tab (`http://localhost:3000/eval-report`).
   * Click **Run All 12 Test Cases**.
   * The backend will asynchronously process the test cases (respecting a 5-second rate limit buffer between calls to prevent Google API throttling).
   * After ~60-90 seconds, the dashboard will populate with the pass/fail matrix and the AI's internal reasoning logs.

---

## ☁️ Deployment Architecture
This project is architected for split deployment to properly handle long-running background tasks without serverless timeouts:
* **Frontend:** Hosted on [Vercel](https://vercel.com/) for optimal Next.js performance.
* **Backend:** Hosted on [Render](https://render.com/) (Web Service) to support persistent, long-running asynchronous background tasks like the evaluation loop.


---
*Built for the Plum Health Insurance AI Engineering challenge.*