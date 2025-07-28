from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from core.config import OPENAI_API_KEY

def generate_summary(document_text: str):
    """Generates an executive summary using an OpenAI model."""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")

    chat = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, model_name="gpt-4o")

    system_prompt = "You are an expert financial analyst. Your task is to provide a concise executive summary of the following SEC filing text."
    human_prompt = "Here is the filing content:\n\n{text}\n\n--- \nPlease generate the executive summary."
    
    prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", human_prompt)])
    chain = prompt | chat
    
    # truncate chars to avoid exceeding token limits
    response = chain.invoke({"text": document_text[:80000]})
    
    return response.content
