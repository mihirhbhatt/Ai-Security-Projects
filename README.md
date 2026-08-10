# AI Security Projects

A portfolio of hands-on AI security labs designed to show real-world capability in attacking, defending, monitoring, and governing AI systems.

This repository is built for a recruiter and hiring-manager audience: it demonstrates practical skills, not just coursework. Each project follows a realistic security workflow: identify the risk, test the system, implement a control, retest, and explain the business impact.

> Safety note: Every project runs in an isolated environment using fictional data and planted fake secrets. Never test these techniques against systems, models, or accounts you do not control.

---

## Why this repository stands out

Most AI security learning material stops at theory or toy demos. This work is different because it is designed to look like evidence-backed security engineering.

Each project is built to show that you can:

- reason about AI attack paths and trust boundaries
- test models and pipelines with adversarial inputs
- map findings to OWASP LLM Top 10 and MITRE ATLAS
- implement practical mitigations
- verify controls through retesting
- communicate technical findings in business language

This is exactly the kind of evidence employers look for when hiring AI security, application security, or platform security talent.

---

## Portfolio summary

| # | Project | What it demonstrates | OWASP LLM Top 10 | Status |
|---|---|---|---|---|
| 1 | [Automated AI Red-Teaming Lab](./01-ai-red-teaming-lab/README.md) | Red-team a chatbot, automate tests, and validate mitigations in CI | LLM01, LLM02, LLM07 | Planned |
| 2 | [Secure AI Agent](./02-secure-ai-agent/README.md) | Break and re-architect a tool-using autonomous agent | LLM01, LLM06, LLM07 | Planned |
| 3 | [Secure RAG Application](./03-secure-rag-application/README.md) | Evaluate retrieval pipelines for prompt injection and data leakage | LLM01, LLM02, LLM08 | Planned |
| 4 | [AI Security Monitoring & Detection Lab](./04-ai-security-monitoring/README.md) | Detect misuse, abuse, and suspicious activity across AI systems | LLM01, LLM02, LLM06 | Planned |
| 5 | [AI Security & Governance Assurance System](./05-ai-governance-assurance/README.md) | Connect technical findings to governance, risk, and evidence | All (via mapping) | Planned |

Each project includes a dedicated README covering:

- business scenario and fictional use case
- architecture and trust boundaries
- threat model and attack catalogue
- methodology and tooling
- findings mapped to security standards
- mitigations and retest evidence
- references to tools and frameworks

The goal is not breadth for its own sake. The goal is to produce a few complete, well-documented security projects that show real capability.

---

## Learning approach

These projects follow a practical, repeatable security lifecycle:

1. Understand the system and the business context
2. Map the data flows and trust boundaries
3. Identify realistic attack paths
4. Run attacks using adversarial prompts and tooling
5. Score and classify the findings
6. Implement a mitigation or control
7. Retest and document the result
8. Present the work in technical and executive-ready language

This is a strong model for real-world AI security assessment and demonstrates clear engineering discipline.

---

## Standards and frameworks referenced

| Framework | Use | Link |
|---|---|---|
| OWASP Top 10 for LLM Applications | Classify prompt, RAG, and output risks | https://owasp.org/www-project-top-10-for-large-language-model-applications/ |
| OWASP GenAI Security Project — Agentic AI Threats | Evaluate agent-specific risks like goal hijacking and tool misuse | https://genai.owasp.org/ |
| MITRE ATLAS | Map adversary tactics and techniques against AI systems | https://atlas.mitre.org/ |
| NIST AI Risk Management Framework (AI RMF 1.0) | Govern, map, measure, and manage AI risk | https://www.nist.gov/itl/ai-risk-management-framework |
| NIST Generative AI Profile (NIST AI 600-1) | Extend AI RMF guidance for GenAI-specific risk | https://www.nist.gov/itl/ai-risk-management-framework |

---

## Tools referenced across projects

| Tool | Purpose | Link |
|---|---|---|
| Ollama | Run open-weight models locally in an isolated lab | https://ollama.com/ |
| Garak | LLM security scanning and vulnerability probing | https://github.com/NVIDIA/garak |
| PyRIT | Adversarial prompt orchestration and attack generation | https://github.com/Azure/PyRIT |
| Promptfoo | Fast red-team and evaluation workflows for LLM applications | https://www.promptfoo.dev/ |
| LangChain | Retrieval and orchestration for RAG pipelines | https://python.langchain.com/ |
| LlamaIndex | Alternative retrieval and indexing framework | https://www.llamaindex.ai/ |
| Chroma | Local vector store for experimentation and search | https://www.trychroma.com/ |
| Elastic / OpenSearch | Telemetry and data visibility for monitoring labs | https://www.elastic.co/ · https://opensearch.org/ |
| GitHub Actions | CI automation for rerunning security checks | https://docs.github.com/actions |

---

## How each project is documented

Each project is intentionally written like a real security assessment, not a tutorial for beginners only. The documentation includes:

- business scenario — the fictional organization and AI use case
- architecture — system design and trust boundaries
- threat model — what is being tested and why
- methodology — tools, tests, and scoring approach
- findings format — how findings map to OWASP and MITRE frameworks
- mitigations and retest — the control and proof it worked
- portfolio checklist — production-quality artifacts to ship

---

## Recommended project flow

### 1. Start with the strongest match to your goals

- Prompt injection and model abuse → [01-ai-red-teaming-lab](./01-ai-red-teaming-lab/README.md)
- Agent security and tool misuse → [02-secure-ai-agent](./02-secure-ai-agent/README.md)
- Retrieval pipeline risk → [03-secure-rag-application](./03-secure-rag-application/README.md)
- Monitoring and detection → [04-ai-security-monitoring](./04-ai-security-monitoring/README.md)
- Governance and assurance → [05-ai-governance-assurance](./05-ai-governance-assurance/README.md)

### 2. Treat each project as a portfolio asset

Document results clearly, including:

- what was built
- what failed or was exploited
- what control was added
- how it was validated
- what still needs human review

### 3. Present your work professionally

For each completed project, aim to deliver:

- a concise README
- a short demo video or walkthrough
- a one-page summary written for business stakeholders

---

## Final message

AI security is one of the fastest-growing areas in modern engineering, and employers want candidates who can show real evidence, not just certificates. This repository is designed to help you build that evidence.

The goal is simple: demonstrate that you can attack, defend, verify, and explain AI systems in a professional, security-first way.
