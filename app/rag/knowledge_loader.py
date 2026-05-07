from pathlib import Path
from langchain_core.documents import Document


KNOWLEDGE_BASE_DIR = Path("data/knowledge_base")


def load_markdown_knowledge_base() -> list[Document]:
    documents: list[Document] = []

    for path in KNOWLEDGE_BASE_DIR.rglob("*.md"):
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