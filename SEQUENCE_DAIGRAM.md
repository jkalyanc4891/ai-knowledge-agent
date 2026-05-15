# System Sequence Diagram

The following sequence diagram illustrates the flow of a query through the Sense-Plan-Act architecture, from the initial UI request to the final validated response.

```mermaid
sequenceDiagram
    autonumber

    participant UI as Streamlit UI
    participant Client as api_client.py
    participant API as FastAPI /query
    participant Models as QueryModel
    participant Orchestrator as AgentOrchestrator
    participant Planner as PlannerAgent
    participant Retriever as RetrievalAgent
    participant VS as ChromaVectorStore
    participant RAG as RAGPipeline
    participant Reasoner as ReasoningAgent
    participant Validator as ValidatorAgent
    participant Guard as guardrails.py

    %% SENSE
    UI->>Client: Build query request
    Client->>API: POST /query
    API->>Models: Validate QueryModel
    Models-->>API: Validated query

    %% PLAN
    API->>Orchestrator: run(query, document_ids)
    Orchestrator->>Planner: plan(query, document_ids)
    Planner-->>Orchestrator: {retrieve, top_k, documents}

    %% ACT — RETRIEVE
    Orchestrator->>Retriever: retrieve(query, docs, top_k)
    Retriever->>VS: query_embeddings()
    VS-->>Retriever: chunks
    Retriever-->>Orchestrator: retrieved_chunks

    %% ACT — REASON
    Orchestrator->>Reasoner: reason(query, context_text)
    Reasoner-->>Orchestrator: reasoning_trace

    %% ACT — RAG PIPELINE
    Orchestrator->>RAG: run(query, document_ids)
    RAG->>VS: retrieve_for_rag()
    VS-->>RAG: rag_chunks
    RAG-->>Orchestrator: {answer, sources}

    %% ACT — VALIDATION / SAFETY
    Orchestrator->>Validator: validate(answer, context_text)
    Validator->>Guard: run_guardrails(answer, context_text)
    Guard-->>Validator: safety_report
    Validator-->>Orchestrator: {grounded, confidence, explanation, full_report}

    %% RESPONSE
    Orchestrator-->>API: Final response payload
    API-->>Client: JSON response
    Client-->>UI: Render answer