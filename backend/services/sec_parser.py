from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from sec_api import QueryApi, RenderApi
from core.config import SEC_API_KEY
import re
import warnings
import traceback # Import the traceback module

# Suppress the specific warning from BeautifulSoup
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

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
            "from": "0",
            "size": "1",
            "sort": [{ "filedAt": { "order": "desc" } }]
        }
        response = queryApi.get_filings(query)
        filings = response.get('filings')
        if not filings:
            raise ValueError(f"No filings of type {filing_type} found for ticker {ticker}.")
        
        filing_url = filings[0].get('linkToFilingDetails')
        if not filing_url:
            raise ValueError("Filing found, but it's missing a URL to its details.")
        
        print(f"Found filing URL: {filing_url}")
        print("Now calling RenderApi to get filing HTML. This can be a slow operation...")
        renderApi = RenderApi(api_key=SEC_API_KEY)
        filing_html = renderApi.get_filing(url=filing_url)
        print("Successfully fetched filing HTML.")
        return filing_html
    except Exception as e:
        # We added this detailed logging to find the real error
        error_trace = traceback.format_exc()
        print("--- [CRITICAL ERROR] An exception occurred in get_latest_filing_html ---")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Details: {e}")
        print("--- FULL TRACEBACK ---")
        print(error_trace)
        print("--------------------------------------------------------------------")
        raise e # Re-raise the original exception

def extract_text_from_html(html_content: str):
    """Extracts plain text from filing HTML."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, 'lxml')
    return soup.get_text(separator='\n', strip=True)

def extract_specific_section(text: str, section_title: str) -> str | None:
    """
    Extracts a specific section from the document text, e.g., 'Risk Factors'.
    """
    start_pattern = re.compile(r"(?:ITEM|Item)\s+(?:1A|lA)\s*\.?\s*Risk\s*Factors", re.IGNORECASE)
    start_match = start_pattern.search(text)
    if not start_match:
        return None
    end_pattern = re.compile(r"(?:ITEM|Item)\s+(?:1B|lB|2|3)\s*\.?", re.IGNORECASE)
    end_match = end_pattern.search(text, pos=start_match.end())
    start_index = start_match.start()
    end_index = end_match.start() if end_match else start_index + 80000
    return text[start_index:end_index]

def extract_financial_statements(text: str) -> str | None:
    """
    Extracts the consolidated financial statements from the document by locating Item 8.
    """
    item_8_start_pattern = re.compile(r"(?:ITEM|Item)\s+8\s*\.\s*Financial\s+Statements\s+and\s+Supplementary\s+Data", re.IGNORECASE)
    notes_start_pattern = re.compile(r"Notes\s+to\s+Consolidated\s+Financial\s+Statements", re.IGNORECASE)
    item_8_match = item_8_start_pattern.search(text)
    if not item_8_match:
        print("Warning: 'Item 8' not found. Falling back to direct statement search.")
        statement_start_pattern = re.compile(r"CONSOLIDATED\s+STATEMENTS\s+OF\s+OPERATIONS", re.IGNORECASE)
        start_match = statement_start_pattern.search(text)
        if not start_match:
            print("Error: Could not find financial statements.")
            return None
        start_index = start_match.start()
        notes_match = notes_start_pattern.search(text, pos=start_index)
        end_index = notes_match.start() if notes_match else start_index + 40000
        return text[start_index:end_index]
    start_index = item_8_match.start()
    notes_match = notes_start_pattern.search(text, pos=start_index)
    end_index = notes_match.start() if notes_match else start_index + 60000
    return text[start_index:end_index]
