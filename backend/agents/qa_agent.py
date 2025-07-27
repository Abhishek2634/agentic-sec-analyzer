from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_openai import ChatOpenAI # Changed from langchain_groq

from core.config import OPENAI_API_KEY # Changed from GROQ_API_KEY

# Global cache for vector stores to avoid re-creating them
vector_store_cache = {}

def create_vector_store(doc_text: str, ticker: str):
    """Creates a ChromaDB vector store from document text."""
    if ticker in vector_store_cache:
        return vector_store_cache[ticker]

    print(f"Creating vector store for {ticker}...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_text(doc_text)

    # Use a local, open-source embedding model
    embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vector_store = Chroma.from_texts(texts=splits, embedding=embedding_model)
    
    vector_store_cache[ticker] = vector_store
    print(f"Vector store for {ticker} created and cached.")
    return vector_store

def get_qa_answer(query: str, ticker: str):
    """Answers a question based on the cached vector store for a ticker."""
    if ticker not in vector_store_cache:
        raise ValueError(f"Report for {ticker} has not been generated yet. Please generate the report first.")

    vector_store = vector_store_cache[ticker]
    retriever = vector_store.as_retriever()
    
    # Changed to ChatOpenAI and a suitable model like gpt-4o
    llm = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, model_name="gpt-4o")

    template = """
    You are a helpful assistant for answering questions about SEC filings.
    Use only the following context to answer the question. If you don't know the answer, just say that you don't know.
    Context: {context}
    Question: {question}
    Answer:
    """
    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    answer = chain.invoke(query)
    return answer
