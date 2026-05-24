# System Architecture

The following diagram illustrates the core architecture of our system, organized into the UI Layer and the **Sense-Plan-Act** cognitive flow. 

```mermaid
flowchart LR

%% ============================
%% UI LAYER
%% ============================
subgraph UI["Streamlit UI (Sense Input)"]
    UQ["User Query"]
    UF["File Uploads(≤30MB per file, Max 10 files)"]
    API_Client["api_client.py"]
end

%% ============================
%% SENSE LAYER (Observe & Validate)
%% ============================
subgraph Sense["SENSE — Observe, Validate, Ingest"]
    API_Query["api/query.py"]
    API_Documents["api/documents.py"]
    Ingest_Pipeline["ingestion/pipeline.py"]
    
    %% The Unified Safety Workflow
    subgraph Safety["Safety Engine (guardrails.py)"]
        Guardrails["run_guardrails()"]
        ValidatorAgent["agents/validator_agent.py"]
        Classifiers["classifiers.py"]
        Filters["filters.py"]
        Audit["audit.py"]
    end
end

%% Internal Workflow Links
Guardrails --> Classifiers
Guardrails --> Filters
Guardrails --> Audit
Guardrails --> ValidatorAgent

%% ============================
%% PLAN LAYER (Cognitive Processing)
%% ============================
subgraph Plan["PLAN — Decide, Strategize"]
    Orchestrator["agents/orchestrator.py"]
    Planner["agents/planner_agent.py"]
    RAG_Pipeline["rag/pipeline.py"]
end

%% ============================
%% ACT LAYER (Execution)
%% ============================
subgraph Act["ACT — Retrieve, Reason"]
    RetrievalAgent["agents/retrieval_agent.py"]
    ReasoningAgent["agents/reasoning_agent.py"]
    Vector_Chroma["vectorstore/chroma_store.py"]
end

%% ============================
%% FLOWS
%% ============================

%% UI inputs
UQ --> API_Client
UF --> API_Client

%% API Routing
API_Client -- "/query" --> API_Query
API_Client -- "/upload" --> API_Documents

%% Sense to Plan
API_Query --> Orchestrator
API_Documents --> Ingest_Pipeline
Ingest_Pipeline --> Vector_Chroma

%% Plan to Act & Safety
Orchestrator --> Planner
Orchestrator --> RAG_Pipeline
Orchestrator --> Guardrails

%% Planner Logic
Planner --> RetrievalAgent
Planner --> ReasoningAgent

%% Act Flow
RetrievalAgent --> Vector_Chroma
ReasoningAgent --> RAG_Pipeline

%% Response
Orchestrator --> API_Client

%% ============================
%% COLOR CODING
%% ============================
classDef sense fill:#cce5ff,stroke:#004085,stroke-width:2px,color:#000;
classDef plan fill:#fff3cd,stroke:#856404,stroke-width:2px,color:#000;
classDef act fill:#d4edda,stroke:#155724,stroke-width:2px,color:#000;
classDef ui fill:#e2e3e5,stroke:#6c757d,stroke-width:2px,color:#000;

class API_Query,API_Documents,Ingest_Pipeline,Safety sense;
class Orchestrator,Planner,RAG_Pipeline plan;
class RetrievalAgent,ReasoningAgent,Vector_Chroma act;
class UQ,UF,API_Client ui;
