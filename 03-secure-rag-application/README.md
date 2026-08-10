flowchart TB
    subgraph Untrusted["Untrusted Zone (Attack Surface)"]
        Emp([Employee User])
        HR([HR/Admin User])
        PoisonedDocs[/Poisoned Docs\nincl. Indirect Injection/]
    end

    subgraph App["Hardened RAG Agent"]
        Auth[AuthN/AuthZ Role Check]
        Retriever[Retriever w/ Metadata Filter]
        Gatekeeper[Security Gatekeeper\nAction & Output Validation]
        PromptBuilder[Prompt Builder\nXML Trust Labels]
    end

    subgraph Data["Data Stores"]
        VDB[(Chroma Vector DB)]
        Inventory[(Asset Inventory DB)]
    end

    Model[(Ollama / Mistral)]

    Emp -->|query| Auth
    HR -->|query| Auth
    Auth -->|authorized query| Retriever
    Retriever -->|role-filtered search| VDB
    VDB -->|context| Retriever
    Retriever --> PromptBuilder
    PromptBuilder -->|labeled context| Model
    Model -->|action request| Gatekeeper
    Gatekeeper -->|validation| Inventory
    Gatekeeper -->|final response| Emp
    
    PoisonedDocs -->|ingest| VDB