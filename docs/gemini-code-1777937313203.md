# System Architecture

The following diagram illustrates the core architecture of our system, organized into the UI Layer and the **Sense-Plan-Act** cognitive flow. 

```mermaid
flowchart LR

%% ============================
%% UI LAYER
%% ============================
subgraph UI["Streamlit UI (ui/)"]
    UI_Main["main_app.py"]
    UI_Client["api_client.py"]
    UI_Components["components.py"]
end

%% ============================
%% SENSE + PLAN (Top Row)
%% ============================
subgraph Top[" "]

    %% ---------- SENSE ----------
    subgraph Sense["SENSE — Observe, Validate, Ingest"]
        API_Query["api/query.py"]
        API_Documents["api/documents.py"]
        API_Health["api/health.py"]

        Ingest_Pipeline["ingestion/pipeline.py"]
        Ingest_Chunker["ingestion/chunker.py"]
        Ingest_Parsers["ingestion/parsers/*.py"]

        Models_Query["models/query_models.py"]
        Models_Doc["models/document_models.py"]
        Models_Response["models/response_models.py"]

        Validation_Filters["validation/filters.py"]
        Validation_Classifiers["validation/classifiers.py"]
        Validation_Policies["validation/policies.py"]
        Validation_Audit["validation/audit.py"]
    end

    %% ---------- PLAN ----------
    subgraph Plan["PLAN — Decide, Strategize"]
        Orchestrator["agents/orchestrator.py"]
        Planner["agents/planner_agent.py"]

        RAG_Pipeline["rag/pipeline.py"]
        RAG_Prompt["rag/prompt_builder.py"]

        Core_Config["core/config.py"]
        Core_Logging["core/logging.py"]
    end

end

%% ============================
%% ACT (Bottom Row)
%% ============================
subgraph Act["ACT — Retrieve, Reason, Validate"]
    RetrievalAgent["agents/retrieval_agent.py"]
    ReasoningAgent["agents/reasoning_agent.py"]
    ValidatorAgent["agents/validator_agent.py"]

    RAG_Retriever["rag/retriever.py"]
    RAG_Generator["rag/generator.py"]

    Vector_Chroma["vectorstore/chroma_store.py"]
    Vector_Base["vectorstore/base.py"]
    Vector_Memory["vectorstore/in_memory.py"]

    Guardrails["validation/guardrails.py"]
end

%% ============================
%% FLOWS
%% ============================

%% UI → SENSE
UI_Main --> UI_Client
UI_Client --> API_Query
UI_Client --> API_Documents
UI_Client --> API_Health

%% SENSE flows
API_Documents --> Ingest_Pipeline
Ingest_Pipeline --> Ingest_Parsers
Ingest_Pipeline --> Ingest_Chunker
Ingest_Pipeline --> Vector_Chroma

API_Query --> Models_Query
API_Query --> Validation_Filters
API_Query --> Validation_Classifiers
API_Query --> Validation_Policies

%% PLAN flows
API_Query --> Orchestrator
Orchestrator --> Planner
Orchestrator --> RAG_Pipeline
RAG_Pipeline --> RAG_Prompt
Orchestrator --> Core_Config

%% SENSE → PLAN → ACT
Planner --> RetrievalAgent
Planner --> ReasoningAgent
Planner --> ValidatorAgent

%% ACT flows
RetrievalAgent --> RAG_Retriever
RAG_Retriever --> Vector_Chroma

ReasoningAgent --> RAG_Generator

ValidatorAgent --> Guardrails
Guardrails --> Validation_Audit

%% Response back to UI
Orchestrator --> Models_Response
API_Query --> UI_Client
UI_Client --> UI_Main

%% ============================
%% COLOR CODING
%% ============================
classDef sense fill:#cce5ff,stroke:#004085,stroke-width:2px,color:#000;
classDef plan fill:#fff3cd,stroke:#856404,stroke-width:2px,color:#000;
classDef act fill:#d4edda,stroke:#155724,stroke-width:2px,color:#000;
classDef ui fill:#e2e3e5,stroke:#6c757d,stroke-width:2px,color:#000;

class API_Query,API_Documents,API_Health,Ingest_Pipeline,Ingest_Chunker,Ingest_Parsers,Models_Query,Models_Doc,Models_Response,Validation_Filters,Validation_Classifiers,Validation_Policies,Validation_Audit sense;
class Orchestrator,Planner,RAG_Pipeline,RAG_Prompt,Core_Config,Core_Logging plan;
class RetrievalAgent,ReasoningAgent,ValidatorAgent,RAG_Retriever,RAG_Generator,Vector_Chroma,Vector_Base,Vector_Memory,Guardrails act;
class UI_Main,UI_Components,UI_Client ui;