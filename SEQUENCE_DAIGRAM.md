# System Sequence Diagram

The following sequence diagram illustrates the flow of a query through the Sense-Plan-Act architecture, from the initial UI request to the final validated response.

```mermaid
sequenceDiagram
    autonumber

    participant UI as Streamlit UI
    participant Client as api_client.py
    participant API as FastAPI /query
    participant Orchestrator as AgentOrchestrator
    participant Planner as PlannerAgent
    participant Retriever as RetrievalAgent
    participant RAG as RAGPipeline
    participant Reasoner as ReasoningAgent
    
    %% Safety Facade Participants
    participant Guard as guardrails.py
    participant Classifiers as Classifiers
    participant Filters as RedactionFilter
    participant Validator as ValidatorAgent
    participant Audit as SafetyAuditLogger

    %% 1. PLAN
    UI->>Client: Query/Upload
    Client->>API: POST /query
    API->>Orchestrator: run(query, doc_ids)
    Orchestrator->>Planner: plan(query)
    
    %% 2. ACT (Retrieve & Reason)
    Orchestrator->>Retriever: retrieve(docs)
    Orchestrator->>Reasoner: reason(query, context)
    Orchestrator->>RAG: run(query)
    RAG-->>Orchestrator: rag_result (answer)

    %% 3. SAFETY FACADE (The new workflow)
    Orchestrator->>Guard: run_guardrails(answer, context)
    
    %% Internal Guardrail Workflow
    Guard->>Classifiers: classify(answer)
    Classifiers-->>Guard: pii/toxicity status
    
    Guard->>Filters: apply(answer)
    Filters-->>Guard: scrubbed_answer
    
    Guard->>Validator: validate(answer, context)
    Validator-->>Guard: grounding/confidence
    
    Guard->>Audit: log_decision()
    
    Guard-->>Orchestrator: {safe, scrubbed_answer, report}

    %% 4. RESPOND
    Orchestrator-->>API: {answer: scrubbed_answer, ...}
    API-->>UI: Display Results