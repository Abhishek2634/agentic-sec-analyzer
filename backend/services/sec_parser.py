from bs4 import BeautifulSoup
from sec_api import QueryApi, RenderApi
from core.config import SEC_API_KEY
import re

# ... get_latest_filing_html and extract_text_from_html functions remain the same ...

def get_latest_filing_html(ticker: str, filing_type: str = "10-K"):
    """
    Fetches the latest filing HTML by using sec-api.io's Query and Render APIs.
    """
    if not SEC_API_KEY:
        raise ValueError("SEC_API_KEY not found. Please set it in your .env file.")
    try:
        queryApi = QueryApi(api_key=SEC_API_KEY)
        query = {
            "query": { "query_string": { "query": f"ticker:{ticker} AND formType:\"{filing_type}\"" }},
            "from": "0", "size": "1", "sort": [{ "filedAt": { "order": "desc" } }]
        }
        response = queryApi.get_filings(query)
        filings = response.get('filings')
        if not filings:
            raise ValueError(f"No filings of type {filing_type} found for ticker {ticker}.")
        filing_url = filings[0].get('linkToFilingDetails')
        if not filing_url:
            raise ValueError("Filing found, but it's missing a URL to its details.")
        print(f"Found filing URL: {filing_url}")
        renderApi = RenderApi(api_key=SEC_API_KEY)
        filing_html = renderApi.get_filing(url=filing_url)
        return filing_html
    except Exception as e:
        print(f"An error occurred in get_latest_filing_html: {e}")
        raise e

def extract_text_from_html(html_content: str):
    """Extracts plain text from filing HTML."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, 'lxml')
    return soup.get_text(separator='\n', strip=True)

def extract_specific_section(text: str, section_title: str) -> str | None:
    """
    Extracts a specific section from the document text, e.g., 'Risk Factors'.
    This implementation is now more robust to handle variations in formatting.
    """
    start_pattern = re.compile(
        r"(?:ITEM|Item)\s+(?:1A|lA)\s*\.?\s*Risk\s*Factors", re.IGNORECASE
    )
    start_match = start_pattern.search(text)
    if not start_match:
        return None
    end_pattern = re.compile(
        r"(?:ITEM|Item)\s+(?:1B|lB|2|3)\s*\.?", re.IGNORECASE
    )
    end_match = end_pattern.search(text, pos=start_match.end())
    start_index = start_match.start()
    end_index = end_match.start() if end_match else start_index + 80000
    return text[start_index:end_index]

# --- NEW FUNCTION ADDED HERE ---
def extract_financial_statements(text: str) -> str | None:
    """
    Extracts the main financial statements section, typically starting with
    'CONSOLIDATED STATEMENTS OF OPERATIONS'.
    """
    # Pattern to find the start of the main income statement.
    start_pattern = re.compile(
        r"CONSOLIDATED STATEMENTS OF OPERATIONS", re.IGNORECASE
    )
    start_match = start_pattern.search(text)
    
    # Fallback for different naming conventions
    if not start_match:
        start_pattern = re.compile(r"STATEMENTS OF INCOME", re.IGNORECASE)
        start_match = start_pattern.search(text)

    if not start_match:
        return None

    # Pattern to find the end. This is usually the start of the next statement.
    end_pattern = re.compile(
        r"(CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME|CONSOLIDATED BALANCE SHEETS|CONSOLIDATED STATEMENTS OF CASH FLOWS)", 
        re.IGNORECASE
    )
    end_match = end_pattern.search(text, pos=start_match.end())

    start_index = start_match.start()
    # Take a large chunk if end is not found, as these tables can be long.
    end_index = end_match.start() if end_match else start_index + 30000 

    return text[start_index:end_index]
