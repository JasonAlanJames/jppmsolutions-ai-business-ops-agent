from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

from app.rag.knowledge_loader import load_markdown_knowledge_base

load_dotenv()

VECTORSTORE_DIR = "vectorstore/jppm_knowledge"


def ingest_knowledge_base() -> int:
    documents = load_markdown_knowledge_base()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
    )

    chunks = splitter.split_documents(documents)

    Chroma.from_documents(
        documents=chunks,
        embedding=OpenAIEmbeddings(),
        persist_directory=VECTORSTORE_DIR,
    )

    return len(chunks)


if __name__ == "__main__":
    count = ingest_knowledge_base()
    print(f"Ingested {count} knowledge base chunks into Chroma.")