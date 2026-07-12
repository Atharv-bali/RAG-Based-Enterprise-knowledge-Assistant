import os
import requests
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.rag_service import RagService
from app.models.request_models import QuestionRequest
from app.models.response_models import AnswerResponse
from app.utils.metrics import metrics_collector
from app.utils.logger import logger
import tempfile
import PyPDF2

router = APIRouter()

@router.post("/query", response_model=AnswerResponse)
def query_rag(request: QuestionRequest):
    result = RagService.ask(request.question)
    return AnswerResponse(
        status=result.get("status", "UNKNOWN"),
        answer=result.get("answer", "")
    )

@router.get("/health")
def health_check():
    # Check if Ollama is accessible
    ollama_status = "down"
    try:
        response = requests.get("http://localhost:11434/", timeout=2)
        if response.status_code == 200 or "Ollama is running" in response.text:
            ollama_status = "up"
    except Exception as e:
        logger.warning(f"Health check failed to contact Ollama: {str(e)}")

    # Check if local storage files exist
    vectorstore_status = "up" if os.path.exists("output/child_chunks.json") else "down"

    system_status = "healthy" if ollama_status == "up" and vectorstore_status == "up" else "unhealthy"

    return {
        "status": system_status,
        "components": {
            "ollama": ollama_status,
            "vector_store_files": vectorstore_status
        }
    }

@router.post("/upload-pdf")
def upload_pdf(pdf: UploadFile = File(...)):
    """
    PDF upload and processing endpoint
    Accepts PDF file, extracts text, chunks it, and updates the knowledge base
    """
    if not pdf.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = pdf.file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
            
        # Extract text from PDF
        text_content = ""
        try:
            with open(tmp_file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page in pdf_reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text_content += extracted + "\n"
        finally:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
            
        # Save extracted text as markdown for processing
        filename_base = os.path.splitext(pdf.filename)[0]
        pdf_md_path = os.path.join("data", "parsed_docs", f"{filename_base}.md")
        os.makedirs(os.path.dirname(pdf_md_path), exist_ok=True)
        
        with open(pdf_md_path, 'w', encoding='utf-8') as md_file:
            md_file.write(f"# {pdf.filename}\n\n{text_content}")
            
        # Process the document using existing chunker
        try:
            from ingestion.chunker import main as process_chunks
            process_chunks()
        except Exception as chunk_error:
            logger.warning(f"Warning: Chunking process failed: {chunk_error}")
            
        return {
            "message": f'PDF "{pdf.filename}" uploaded and processed successfully',
            "filename": pdf.filename,
            "text_length": len(text_content)
        }
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

@router.get("/metrics")
def get_metrics():
    return metrics_collector.get_metrics()