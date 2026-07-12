from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.utils.logger import logger

class RAGException(Exception):
    """Base exception for RAG system errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class DocumentNotFoundError(RAGException):
    def __init__(self, message: str = "Requested document not found"):
        super().__init__(message, status_code=404)

class LLMServiceError(RAGException):
    def __init__(self, message: str = "Failed to communicate with LLM service"):
        super().__init__(message, status_code=500)

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(RAGException)
    async def rag_exception_handler(request: Request, exc: RAGException):
        logger.warning(f"RAG Application Exception on {request.url.path}: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Format errors into a simple list of messages
        errors = []
        for error in exc.errors():
            loc = " -> ".join(str(x) for x in error.get("loc", []))
            msg = error.get("msg", "Validation error")
            errors.append(f"{loc}: {msg}")
        
        err_msg = "; ".join(errors)
        logger.warning(f"Validation Error on {request.url.path}: {err_msg}")
        
        return JSONResponse(
            status_code=400,
            content={"detail": f"Validation failed: {err_msg}"}
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )
