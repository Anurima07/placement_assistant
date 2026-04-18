from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
import os

# Load embedding model
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Load documents
docs = []
data_path = "data"

for file in os.listdir(data_path):
    if file.endswith(".txt"):
        loader = TextLoader(os.path.join(data_path, file))
        docs.extend(loader.load())

# Split documents
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_docs = text_splitter.split_documents(docs)

# Create Chroma DB (auto persists now)
db = Chroma.from_documents(
    split_docs,
    embedding,
    persist_directory="vectordb"
)

print("ChromaDB created successfully")