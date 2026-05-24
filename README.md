# 🧠 AI‑Powered Document Intelligence with Agentic RAG

[![Python Version](https://img.shields.io/badge/Python-3.14%2B-blue?logo=python&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)](#)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](#)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Enabled-orange)](#)
[![Pydantic](https://img.shields.io/badge/Pydantic-E92063?logo=pydantic&logoColor=white)](#)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?logo=openai&logoColor=white)](#)
[![License](https://img.shields.io/badge/License-MIT-green)](#)
[![Architecture](https://img.shields.io/badge/Architecture-View-purple)](./ARCHITECTURE.md)
[![Sequence Diagram](https://img.shields.io/badge/Sequence-View-purple)](./SEQUENCE_DAIGRAM.md)

> **An enterprise-grade document intelligence system that leverages agentic retrieval-augmented generation (RAG) to transform static files into an interactive, conversational knowledge engine.**

## 📖 Overview

A modern Generative AI application that transforms enterprise documents into an interactive knowledge system. Upload PDFs, spreadsheets, or text files and ask natural‑language questions. Behind the scenes, autonomous AI agents orchestrate document parsing, semantic retrieval, and LLM‑based reasoning to deliver accurate, grounded answers. Built with FastAPI, Streamlit, and a pluggable vector database layer for local or cloud deployment.

---

## ✨ Key Features

* 🤖 **Autonomous AI Agents:** Built-in agents for intelligent retrieval, step-by-step reasoning, and response validation.
* 🧩 **Modular RAG Pipeline:** Customizable ingestion pipeline handling document parsing, chunking, embedding, and semantic search.
* ⚡ **High-Performance Vector Store:** Pluggable local vector database powered by **ChromaDB** for ultra-fast, offline retrieval.
* 🔌 **Robust API Backend:** Fully documented, async-ready REST API served by **FastAPI**.
* 🖥️ **Interactive UI:** Clean, user-friendly frontend built with **Streamlit**.
* 🛡️ **Enterprise Guardrails:** Built-in safety mechanisms and governance rules for policy enforcement and audit logging.

---

## 🚀 Installation & Setup

You can run this project locally using a standard Python virtual environment or deploy it instantly using Docker.

### Option A: Run Locally (Without Docker)

**1. Clone the repository**
```bash
git clone https://github.com/jkalyanc4891/ai-knowledge-agent.git
cd ai-knowledge-agent
```
**2. Create and activate a virtual environment**
```bash
python3 -m venv venv

# macOS/Linux
source venv/bin/activate  

# Windows
venv\Scripts\activate

# Windows PowerShell
.\venv\Scripts\Activate.ps1
```
**3. Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
**4. Set Environment Variables**

Create a `.env` file in the root directory of the project to securely manage your API keys and configuration settings:

```env
# Application Settings
APP_NAME="AI Knowledge & Decision Support System"
APP_ENV=local

# AI Service Provider
OPENAI_API_KEY=<your_openai_api_key_here>
OPENAI_MODEL=gpt-5.4-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-large

# Vector Store Backend
VECTOR_DB_BACKEND=chroma

# Application Settings
LOG_LEVEL=INFO

# Optional: Chroma Persistence (only used if chroma_store.py uses it)
# ----------------------------------------------------
CHROMA_PERSIST_DIR=.chroma
```
**5. Launch the Application**

To run the full stack locally, you will need to start the FastAPI backend and the Streamlit UI in two separate terminal sessions:

* **Terminal 1: Start FastAPI Backend**
    ```bash
    # Ensure your virtual environment is active
    uvicorn app.main:app --host 0.0.0.0 --port 10000 --reload
    ```
    *The API will be accessible at `http://localhost:10000` with interactive Swagger docs at `/docs`.*

* **Terminal 2: Start Streamlit UI**
    ```bash
    # Ensure your virtual environment is active
    streamlit run ui/main_app.py --server.port 8501
    ```
    *The user interface will automatically open in your default browser at `http://localhost:8501`.*

> [!NOTE]  
> The `--reload` flag in the backend is recommended for development as it automatically restarts the server when code changes are detected.

### Option B: Run Locally With Docker 🐳

This method is recommended for a consistent environment across different operating systems, as it packages all dependencies into a single container.

**1. Prerequisites**

Ensure you have a .env file in the root directory containing your API key:

```bash
OPENAI_API_KEY=your_sk_key_here
```
**2. Start the services**

Once the image is built, execute the following command to spin up both the backend and the frontend services within the container:

```bash
# Build and start all services defined in docker-compose.yml
docker-compose up --build
```
**3. Access the Services**

Once the container is running, you can access the application components via your web browser at the following local addresses:

| Service | URL                                                       | Description |
| :--- |:----------------------------------------------------------| :--- |
| **Backend API** | [http://localhost:10000/docs](http://localhost:8000/docs) | Interactive Swagger UI for testing endpoints. |
| **Frontend UI** | [http://localhost:8501](http://localhost:8501)            | Streamlit interface for document uploads and chat. |

> [NOTE]  
> The vector database is automatically persisted using a named volume (rag_vector_storage) defined in your docker-compose.yml. Your data will remain safe even when you stop or restart the containers.

## 📐 System Design [SENSE -> PLAN -> ACT]

[View Full Architecture Document](./ARCHITECTURE.md)

[View Full Sequence Diagram](./SEQUENCE_DAIGRAM.md)

### 📁 Project Structure
```
ai-knowledge-agent/
│
├── app/                 # FastAPI backend
│   ├── api/             # Endpoints
│   ├── rag/             # RAG pipeline
│   ├── agents/          # Agentic AI components
│   ├── ingestion/       # Document parsing + chunking
│   ├── vectorstore/     # ChromaDB implementation
│   ├── validation/      # Guardrails + governance
│   └── models/          # Pydantic models
│
├── ui/                  # Streamlit frontend
│
├── .env
├── requirements.txt
├── Dockerfile.backend
├── Dockerfile.backend
├── docker-compose.yml
├── render.yaml          # Blueprint file for Render deployment
├── ARCHITECTURE.md
├── SEQUENCE_DIAGRAM.md
└── README.md

```
## 📄 License

This project is licensed under the **MIT License**.

> See the [LICENSE](LICENSE) file in the root directory for more information.

