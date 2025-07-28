from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI
from core.config import OPENAI_API_KEY

vector_stores: dict = {}

def _get_embedding_model():
    """Dynamically imports and returns the sentence transformer embedding model."""
    from langchain_community.embeddings import SentenceTransformerEmbeddings
    return SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

def create_vector_store(document_text: str, ticker: str):
    """Creates and caches a vector store for a given document."""
    if not document_text:
        return
        
    print(f"Creating vector store for {ticker}...")
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_text(document_text)
    
    embedding_model = _get_embedding_model()
    
    vector_store = Chroma.from_texts(texts, embedding_model)
    vector_stores[ticker] = vector_store
    print(f"Vector store for {ticker} created successfully.")

def get_qa_answer(query: str, ticker: str):
    """Answers a question using the cached vector store for a ticker."""
    if ticker not in vector_stores:
        raise ValueError(f"No document has been processed for {ticker} yet. Please generate a report first.")
    
    vector_store = vector_stores[ticker]
    llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever()
    )
    
    response = qa_chain.invoke(query)
    return response.get('result', "Could not find an answer.")
