from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import asyncio
import os

from services.sec_parser import get_latest_filing_html, extract_text_from_html, extract_specific_section, extract_financial_statements
from agents.summary_agent import generate_summary
from agents.risk_agent import extract_risks
from agents.kpi_agent import extract_kpis
from agents.qa_agent import create_vector_store, get_qa_answer

app = FastAPI(
    title="Agentic AI Platform for SEC Filings",
    description="API for analyzing SEC filings using AI agents."
)

# --- FINAL DEBUGGING STEP ---
# Let's print the environment variables to the logs to see what the app is getting.
frontend_url_from_env = os.getenv("FRONTEND_URL")
print("--- CORS DEBUGGING INFO ---")
print(f"Value of FRONTEND_URL from environment: '{frontend_url_from_env}'")

# Create the list of allowed origins
origins = [
    "http://localhost:3000", # Always allow for local development
]
if frontend_url_from_env:
    origins.append(frontend_url_from_env)

print(f"Final list of allowed origins for CORS: {origins}")
print("---------------------------")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

reports_cache: Dict[str, Any] = {}

@app.api_route("/", tags=["Status"], methods=["GET", "HEAD"])
async def read_root():
    return {"status": "ok", "message": "Welcome to the Agentic AI Platform for SEC Filings"}

# ... The rest of your main.py file remains exactly the same ...
class ReportRequest(BaseModel):
    ticker: str
    filing_type: str

class QARequest(BaseModel):
    ticker: str
    question: str

@app.post("/api/generate-report", tags=["Reports"])
async def create_report(request: ReportRequest):
    cache_key = f"{request.ticker.upper()}-{request.filing_type}"
    if cache_key in reports_cache:
        print(f"Returning cached report for {cache_key}")
        return reports_cache[cache_key]
    
    if request.filing_type == "8-K":
        print("Running INSTANT test for 8-K...")
        report = {
            "ticker": request.ticker.upper(),
            "filingType": "8-K",
            "executiveSummary": "This is an instant test report for an 8-K filing. If you see this, the connection is working.",
            "riskFactors": ["N/A for this test."],
            "financialKPIs": {"total_revenue": "N/A", "net_income": "N/A", "eps": "N/A"},
        }
        reports_cache[cache_key] = report
        return report
    
    try:
        print(f"Step 1: Fetching filing for {cache_key}...")
        filing_html = await asyncio.to_thread(get_latest_filing_html, request.ticker, request.filing_type)
        document_text = await asyncio.to_thread(extract_text_from_html, filing_html)
        
        summary, risk_factors, kpis = "", [], {}
        
        if request.filing_type in ["10-K", "10-Q"]:
            print(f"Running full analysis for {request.filing_type}...")
            risk_section_text = await asyncio.to_thread(extract_specific_section, document_text, "risk factors")
            financials_text = await asyncio.to_thread(extract_financial_statements, document_text)
            
            summary_task = asyncio.to_thread(generate_summary, document_text)
            risks_task = asyncio.to_thread(extract_risks, risk_section_text) if risk_section_text else asyncio.sleep(0, result=["'Risk Factors' section not found."])
            kpis_task = asyncio.to_thread(extract_kpis, financials_text) if financials_text else asyncio.sleep(0, result={"total_revenue": "N/A", "net_income": "N/A", "eps": "N/A"})
            
            summary, risk_factors, kpis = await asyncio.gather(summary_task, risks_task, kpis_task)
            print("Full analysis complete.")
        else:
            raise HTTPException(status_code=400, detail=f"Filing type '{request.filing_type}' is not supported.")
            
        await asyncio.to_thread(create_vector_store, document_text, request.ticker.upper())
        
        report = {
            "ticker": request.ticker.upper(),
            "filingType": request.filing_type,
            "executiveSummary": summary,
            "riskFactors": risk_factors,
            "financialKPIs": kpis,
        }
        reports_cache[cache_key] = report
        return report
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/qna", tags=["Q&A"])
async def answer_question(request: QARequest):
    ticker = request.ticker.upper()
    try:
        answer = await asyncio.to_thread(get_qa_answer, query=request.question, ticker=ticker)
        return {"answer": answer}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
