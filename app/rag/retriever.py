from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

VECTORSTORE_DIR = "vectorstore/jppm_knowledge"


def get_retriever(k: int = 4):
    vectorstore = Chroma(
        persist_directory=VECTORSTORE_DIR,
        embedding_function=OpenAIEmbeddings(),
    )

    return vectorstore.as_retriever(search_kwargs={"k": k})


def retrieve_context(query: str, k: int = 4) -> str:
    retriever = get_retriever(k=k)
    docs = retriever.invoke(query)

    if not docs:
        return ""

    return "\n\n---\n\n".join(
        f"Source: {doc.metadata.get('source', 'unknown')}\n\n{doc.page_content}"
        for doc in docs
    )