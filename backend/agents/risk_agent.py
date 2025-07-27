from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from core.config import OPENAI_API_KEY
import ast # Import the Abstract Syntax Tree module for safe parsing

def extract_risks(document_text: str):
    """Extracts the top 5-7 risk factors using an OpenAI model."""
    if not document_text:
        return ["Risk section was empty or not found."]
        
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")

    chat = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, model_name="gpt-4o")

    system_prompt = (
        "You are an expert financial analyst specializing in risk assessment. "
        "Your task is to identify and list the most critical risk factors from the provided text, which is the 'Risk Factors' section of an SEC filing. "
        "Focus on the top 5 to 7 most significant risks. "
        "Your response MUST be a valid Python list of strings. For example: ['Risk 1 description...', 'Risk 2 description...']. "
        "Do NOT include any other text, explanations, or markdown formatting like ```."
    )
    human_prompt = (
        "Analyze the following 'Risk Factors' section and extract the key risks:\n\n{text}\n\n---"
    )
    
    prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", human_prompt)])
    chain = prompt | chat
    
    response = chain.invoke({"text": document_text})
    
    # A more robust way to clean up potential markdown formatting
    content = response.content.strip()
    if content.startswith("```"):
        content = content.replace("```python", "", 1)
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    
    try:
        # Use ast.literal_eval for safely parsing the string as a Python list
        risks = ast.literal_eval(content)
        if isinstance(risks, list):
            return risks
    except (ValueError, SyntaxError):
        # Fallback for parsing bullet points if literal_eval fails
        return [line.strip('-* ').strip() for line in content.split('\n') if line.strip() and len(line) > 10]

    return ["Could not parse risk factors from the provided section."]
