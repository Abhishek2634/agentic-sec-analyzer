from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from core.config import OPENAI_API_KEY
import json

def extract_kpis(document_text: str):
    """Extracts key financial KPIs using an OpenAI model."""
    chat = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, model_name="gpt-4o")

    system_prompt = (
        "You are an expert financial data analyst. Your task is to extract key financial KPIs "
        "from the provided SEC filing's financial statements. "
        "Find values for Total Revenues (or Total Net Sales), Net Income, and Earnings Per Share (EPS). "
        "Search for the most recent full fiscal year's data. If a value is not found, use 'N/A'. "
        "Return the result as a JSON object with keys: 'total_revenue', 'net_income', 'eps'."
    )
    human_prompt = "Here is the financial statements content:\n\n{text}\n\n--- \nPlease extract the financial KPIs as a JSON object."
    
    prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", human_prompt)])
    chain = prompt | chat
    
    response = chain.invoke({"text": document_text})
    
    try:
        return json.loads(response.content)
    except:
        return {"total_revenue": "N/A", "net_income": "N/A", "eps": "N/A"}
