import os
from dotenv import load_dotenv
load_dotenv()

os.environ["UPSTAGE_API_KEY"] = os.getenv("UPSTAGE_API_KEY")

from langchain_upstage import UpstageEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma

# Load the document, split it into chunks, embed each chunk and load it into the vector store.
raw_documents = TextLoader('test.txt').load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = text_splitter.split_documents(raw_documents)
db = Chroma.from_documents(documents, UpstageEmbeddings(model="solar-embedding-1-large"))

query = "Solar LLM 기능"
docs = db.similarity_search(query)
print(docs[0].page_content)