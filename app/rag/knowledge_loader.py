from pathlib import Path

from langchain_core.documents import Document


KNOWLEDGE_BASE_DIR = Path("data/knowledge_base")

EXCLUDED_RAG_FOLDERS = {
    "internal",
    "private",
    "secrets",
}


def should_exclude_path(path: Path) -> bool:
    """
    Prevent private/internal knowledge files from being embedded into
    the customer-facing RAG vector store.
    """
    path_parts = {part.lower() for part in path.parts}

    return any(folder in path_parts for folder in EXCLUDED_RAG_FOLDERS)


def load_markdown_knowledge_base() -> list[Document]:
    documents: list[Document] = []

    for path in KNOWLEDGE_BASE_DIR.rglob("*.md"):
        if should_exclude_path(path):
            continue

        content = path.read_text(encoding="utf-8")

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": str(path),
                    "file_name": path.name,
                    "category": path.parent.name,
                },
            )
        )

    return documents