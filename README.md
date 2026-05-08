# JPPM Solutions AI Business Operations Agent

An enterprise-grade AI business communications and workflow orchestration platform built for the JPPM Solutions ecosystem.

This project demonstrates a production-oriented AI systems architecture using:

- LangChain
- LangGraph
- Chroma Vector RAG
- Gmail API integration
- FastAPI
- Human-in-the-loop approval workflows
- Knowledge-grounded AI response generation
- Multi-brand enterprise routing

The system intelligently classifies emails, routes customer inquiries to the correct business unit, retrieves relevant business knowledge, generates professional AI-assisted draft responses, and enforces strict human approval before any outbound communication occurs.

---

# 🚀 Overview

The JPPM Solutions AI Business Operations Agent functions as an AI-powered business communications assistant capable of:

- Classifying inbound business emails
- Routing customer inquiries to the correct subsidiary brand
- Retrieving context from a vectorized knowledge base
- Generating grounded AI draft responses
- Creating Gmail drafts safely
- Enforcing human approval before any action
- Maintaining audit logs of workflow decisions
- Running stateful LangGraph workflows

This repository demonstrates real-world enterprise AI orchestration patterns suitable for production business automation systems.

---

# 🧠 Core Capabilities

## 1. Multi-Brand AI Routing

The system intelligently routes inquiries across the JPPM Solutions ecosystem.

Supported brands include:

- AI Agent Innovation Academy
- App & Web Developers
- MyPrintingDeals
- 3D Figs
- USA Marketing NOW
- Realty Media Expert
- SoCal Television
- World Television TV
- Tripping AI
- VLOGit Social Media
- TapCard Digital Business Card
- Useful AI Hacks

Routing decisions are based on:

- Semantic classification
- Knowledge base retrieval
- Business-specific intent detection
- Email content analysis

---

## 2. LangGraph Stateful Workflow Orchestration

The system uses LangGraph to orchestrate AI business workflows.

Workflow example:

```text
START
→ Initialize State
→ Email Classification
→ Brand Routing
→ Action Selection
→ RAG Reply Generation
→ Human Approval
→ Gmail Draft Creation
→ END
```

Each workflow maintains state, audit logs, routing decisions, and safety controls throughout execution.

---

## 3. Retrieval-Augmented Generation (RAG)

The platform uses a Chroma vector database built from structured Markdown knowledge files.

Knowledge sources include:

```text
data/
  knowledge_base/
    company.md
    brands/
      *.md
```

The RAG pipeline provides:

- Brand-aware response generation
- Reduced hallucinations
- Context-grounded customer replies
- Knowledge-constrained AI behavior
- Semantic retrieval across company data

---

## 4. AI-Powered Email Classification

Incoming emails are classified into categories such as:

- `needs_reply`
- `archive`
- `human_review`
- `spam`
- `trash`

The classification layer combines:

- Rule-based safety logic
- LangChain/OpenAI LLM analysis
- RAG context retrieval
- Brand validation rules

---

## 5. AI-Generated Customer Reply Drafts

For legitimate customer inquiries, the system generates professional AI-assisted draft responses.

Features include:

- Brand-specific reply tone
- Context-aware messaging
- RAG-grounded response generation
- Safe fallback behavior
- Human review before use

The system never auto-sends emails.

---

## 6. Human-in-the-Loop (HITL) Safety Layer

All outbound actions require explicit approval.

Safety protections include:

- No automatic email sending
- Human approval required
- Audit logging
- Controlled Gmail draft creation
- Brand-constrained routing
- Knowledge-grounded responses
- Sensitive-topic escalation

This architecture reflects enterprise AI governance and operational safety practices.

---

## 7. Gmail API Integration

The platform integrates directly with Gmail using OAuth authentication.

Capabilities include:

- Reading unread emails
- Extracting message content
- Creating Gmail drafts
- Approval-driven workflows
- Safe email processing

No automatic sending exists in the system.

---

# 🏗️ High-Level Architecture

```text
Gmail Inbox
        ↓
LangGraph Workflow Engine
        ↓
LLM Classification Layer
        ↓
Brand Routing Engine
        ↓
Chroma Vector RAG Retrieval
        ↓
AI Draft Generation
        ↓
Human Approval API
        ↓
Gmail Draft Creation
        ↓
Manual Human Send
```

---

# ⚙️ Technology Stack

| Layer | Technology |
|---|---|
| AI Orchestration | LangChain |
| Stateful Workflows | LangGraph |
| Vector Database | ChromaDB |
| Embeddings | OpenAI Embeddings |
| LLM Provider | OpenAI |
| API Framework | FastAPI |
| Email Integration | Gmail API |
| Testing | Pytest |
| Environment Management | python-dotenv |
| Language | Python 3.13 |

---

# 📁 Project Structure

```text
app/
│
├── email_ops/
│   ├── approval_schemas.py
│   ├── approval_service.py
│   ├── classifier.py
│   ├── gmail_client.py
│   ├── gmail_triage.py
│   ├── llm_classifier.py
│   ├── reply_generator.py
│   └── workflow_graph.py
│
├── rag/
│   ├── ingest.py
│   ├── knowledge_loader.py
│   └── retriever.py
│
├── main.py
│
data/
│
├── knowledge_base/
│   ├── company.md
│   └── brands/
│       ├── ai_agent_innovation_academy.md
│       ├── app_and_web_developers.md
│       ├── myprintingdeals.md
│       ├── useful_ai_hacks.md
│       └── ...
│
tests/
│
├── test_email_classifier.py
├── test_email_workflow_graph.py
├── test_llm_classifier_safety.py
└── test_reply_generation.py
│
vectorstore/
│
README.md
requirements.txt
docker-compose.yml
Dockerfile
.env.example
```

---

# ⚙️ Setup

## 1. Clone Repository

```bash
git clone https://github.com/JasonAlanJames/jppmsolutions-ai-business-ops-agent.git

cd jppmsolutions-ai-business-ops-agent
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create:

```text
.env
```

Example:

```env
OPENAI_API_KEY=your_openai_api_key

OPENAI_MODEL=gpt-4o-mini

LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_TRACING_V2=true

GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret
GMAIL_REFRESH_TOKEN=your_gmail_refresh_token
```

---

## 5. Build the Vector Knowledge Base

```bash
python -m app.rag.ingest
```

Expected:

```text
Ingested X knowledge base chunks into Chroma.
```

---

## 6. Run FastAPI Server

```bash
uvicorn app.main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

# 📬 FastAPI Endpoints

## GET `/emails/triage`

Runs Gmail inbox triage workflow.

---

## POST `/emails/approve`

Approves or rejects workflow actions.

---

## GET `/emails/approvals`

Returns approval audit log.

---

# 🧪 Testing

Run the full test suite:

```bash
pytest
```

Current test coverage includes:

- LangGraph workflow tests
- LLM fallback safety tests
- Approval workflow tests
- RAG reply generation tests
- Email classification tests

---

# 🔐 Safety Architecture

The platform is intentionally designed with strict AI safety constraints.

## Safety Guarantees

- No automatic email sending
- Human approval required
- Brand-constrained routing
- RAG-grounded response generation
- Audit logging
- Sensitive-topic escalation
- Safe deterministic fallbacks

---

# 📈 Future Enhancements

Planned roadmap items include:

- Slack / Discord notifications
- CRM integration
- Multi-user approval dashboard
- PostgreSQL persistence layer
- Agent memory systems
- Scheduled workflows
- Analytics dashboard
- Docker production deployment
- Kubernetes deployment architecture
- Role-based access controls
- Advanced observability

---

# 👤 Author

## Jason James

Founder, AI Agent Innovation Academy

Websites:

- https://jppmsolutions.com
- https://aiagentinnovation.com
- https://usefulaihacks.com

GitHub:

- https://github.com/JasonAlanJames

LinkedIn:

- https://linkedin.com/in/jasonalanjames

---

# 🧾 License

This repository is intended for:

- Portfolio demonstration
- Educational purposes
- AI workflow experimentation
- Enterprise AI architecture demonstrations

---

# 💡 Final Note

This project demonstrates how modern AI systems can safely augment real-world business operations using:

- AI orchestration
- Stateful workflows
- Human oversight
- Retrieval-Augmented Generation
- Enterprise-safe automation patterns

It represents a scalable foundation for production-grade AI business communications systems.