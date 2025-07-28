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

# --- CORS Configuration ---
# Reads the frontend URL from the environment variable for secure CORS setup.
frontend_url_from_env = os.getenv("FRONTEND_URL")
origins = ["http://localhost:3000"] # Default for local development
if frontend_url_from_env:
    origins.append(frontend_url_from_env)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache to store generated reports
reports_cache: Dict[str, Any] = {}

@app.api_route("/", tags=["Status"], methods=["GET", "HEAD"])
async def read_root():
    """Provides a simple status check and welcome message."""
    return {"status": "ok", "message": "Welcome to the Agentic AI Platform for SEC Filings"}

class ReportRequest(BaseModel):
    ticker: str
    filing_type: str

class QARequest(BaseModel):
    ticker: str
    question: str

@app.post("/api/generate-report", tags=["Reports"])
async def create_report(request: ReportRequest):
    """
    Generates a full analysis report for a given company ticker and filing type.
    """
    cache_key = f"{request.ticker.upper()}-{request.filing_type}"
    if cache_key in reports_cache:
        print(f"Returning cached report for {cache_key}")
        return reports_cache[cache_key]

    try:
        print(f"Step 1: Fetching filing for {cache_key}...")
        filing_html = await asyncio.to_thread(get_latest_filing_html, request.ticker, request.filing_type)
        document_text = await asyncio.to_thread(extract_text_from_html, filing_html)

        summary = ""
        risk_factors = []
        kpis = {}

        if request.filing_type in ["10-K", "10-Q"]:
            print(f"Running full analysis for {request.filing_type}...")
            risk_section_text = await asyncio.to_thread(extract_specific_section, document_text, "risk factors")
            financials_text = await asyncio.to_thread(extract_financial_statements, document_text)
            
            # Run AI agents concurrently to save time
            summary_task = asyncio.to_thread(generate_summary, document_text)
            risks_task = asyncio.to_thread(extract_risks, risk_section_text) if risk_section_text else asyncio.sleep(0, result=["'Risk Factors' section not found."])
            kpis_task = asyncio.to_thread(extract_kpis, financials_text) if financials_text else asyncio.sleep(0, result={"total_revenue": "N/A", "net_income": "N/A", "eps": "N/A"})

            summary, risk_factors, kpis = await asyncio.gather(summary_task, risks_task, kpis_task)
            print("Full analysis complete.")

        elif request.filing_type == "8-K":
            print("Running summary-only analysis for 8-K...")
            summary = await asyncio.to_thread(generate_summary, document_text)
            risk_factors = ["Not applicable for 8-K filings."]
            kpis = {"total_revenue": "N/A", "net_income": "N/A", "eps": "N/A"}
            print("8-K summary complete.")
        
        else:
            raise HTTPException(status_code=400, detail=f"Filing type '{request.filing_type}' is not supported.")

        # Create Vector Store for Q&A after generating the main report
        print("Creating Vector Store for Q&A...")
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
        print(f"An error occurred during report generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/qna", tags=["Q&A"])
async def answer_question(request: QARequest):
    """
    Answers a question about a previously processed filing.
    """
    ticker = request.ticker.upper()
    try:
        answer = await asyncio.to_thread(get_qa_answer, query=request.question, ticker=ticker)
        return {"answer": answer}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"An error occurred in Q&A: {e}")
        raise HTTPException(status_code=500, detail=str(e))
