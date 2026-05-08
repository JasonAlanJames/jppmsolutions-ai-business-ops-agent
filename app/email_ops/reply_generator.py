import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.rag.retriever import retrieve_context

load_dotenv()


REPLY_SYSTEM_PROMPT = """
You are the business communications assistant for JPPM Solutions.

Your job is to draft professional customer email replies using ONLY the provided JPPM knowledge base context and the incoming email.

Rules:
- Never claim pricing, timelines, guarantees, availability, or policies unless present in the knowledge base context.
- Never say an email has been sent.
- Never approve work, accept a contract, or make commitments.
- Never ask for passwords, API keys, payment card details, or private credentials.
- Keep the tone professional, helpful, and concise.
- Ask practical clarifying questions when needed.
- Route the customer to the correct JPPM brand or contact when available.
- Mention that the team can review the details, not that work is guaranteed.
- Do not include markdown.
- Do not include a subject line in the body.
"""


def generate_rag_reply(
    subject: str,
    sender: str,
    body: str,
    brand_route: str,
) -> str:
    """
    Generate a brand-grounded draft reply using retrieved knowledge base context.

    If OPENAI_API_KEY is missing, return a safe deterministic fallback.
    """

    if not os.getenv("OPENAI_API_KEY"):
        return (
            f"Thank you for reaching out to {brand_route}. "
            "We received your inquiry and can review the details. "
            "Please provide any relevant project goals, timelines, website links, specifications, and contact information so the appropriate team can follow up."
        )

    query = f"{brand_route}\n{subject}\n{body[:2000]}"
    knowledge_context = retrieve_context(query=query, k=5)

    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.2,
    )

    prompt = f"""
JPPM knowledge base context:
{knowledge_context}

Brand route:
{brand_route}

Incoming email:
Subject: {subject}
From: {sender}

Body:
{body[:5000]}

Draft a professional customer reply email body only.
"""

    response = llm.invoke(
        [
            ("system", REPLY_SYSTEM_PROMPT),
            ("human", prompt),
        ]
    )

    return str(response.content).strip()