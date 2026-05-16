from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_classic.retrievers import ContextualCompressionRetriever
from dotenv import load_dotenv

from src.model.chat_model import llm_model
from src.embedding.embedding_model import get_model
from src.rag.retriever import get_retriever

load_dotenv()

model = llm_model()

FILE_PATH = ""
pdf_file_loader = PyPDFLoader(file_path=FILE_PATH)

pdf_pages = []

for doc in pdf_file_loader.lazy_load():
    pdf_pages.append(doc)

splitter = RecursiveCharacterTextSplitter(chunk_size=800,
                                          chunk_overlap=150,
                                          separators=["\n\n", "\n", "."])
documents = splitter.split_documents(pdf_pages)
print("Total No. of Documents: ", documents)

# create metadata, for citation and references
for i, chunk in enumerate(documents):
    chunk.metadata["source"] = FILE_PATH
    chunk.metadata["chunk_id"] = i
    chunk.metadata["page"] += 1     # PyPDF automatically provides metadata['page']

temp_db = Chroma.from_documents(
    documents=documents,
    embeddings=get_model(),
    collection_name=f"testing_001"
)

arxiv_retriever = get_retriever()
uploaded_doc_retriever = temp_db.as_retriever(
    search_kwargs={"k": 5}
)

query = "Most efficient model for blood group classification"

arxiv_context = arxiv_retriever.invoke(query)
uploaded_context = uploaded_doc_retriever.invoke(query)

compressor = CrossEncoderReranker(
    model="BAAI/bge-reranker-base"
)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    # base_retriever=
)