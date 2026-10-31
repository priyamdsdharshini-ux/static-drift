from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from dotenv import load_dotenv

load_dotenv()

DATA_DIR = "./data"  # drug leaflets / symptom guideline PDFs (public, no patient data)

def process_pdfs(data_dir: str = DATA_DIR):
    documents = []
    for pdf in Path(data_dir).glob("*.pdf"):
        documents += PyPDFLoader(str(pdf)).load()

    # ~900 chars keeps one drug's dosage section inside a single chunk
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=120,
        separators=["\n\n", "\n", ". ", " "]
    )

    return splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)

vector_store = Chroma(
    embedding_function=embeddings,
    collection_name="medical_data_collection",
    persist_directory="./vector_db"
)

def ingest_data():
    chunks = process_pdfs()
    if not chunks:
        return "No PDFs found in ./data. Add leaflets or guidelines first."

    vector_store.reset_collection()  # avoids duplicate chunks if you ingest twice
    vector_store.add_documents(chunks)

    return f"Data ingestion completed. {len(chunks)} chunks stored."

def get_retriever():
    return vector_store.as_retriever(search_kwargs={"k": 3})

if __name__ == "__main__":
    # Step 1: run once after adding PDFs to ./data
    print(ingest_data())

    # Step 2: test retrieval precision before building the agent
    for q in ["paracetamol maximum daily dose", "ibuprofen side effects", "when is a fever dangerous"]:
        print("\nQUERY:", q)
        for d in get_retriever().invoke(q):
            print("-", d.metadata.get("source"), "p.", d.metadata.get("page"), "|", d.page_content[:120])
    pass
