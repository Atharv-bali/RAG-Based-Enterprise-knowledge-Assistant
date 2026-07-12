import requests
from agents.self_correcting_rag import query
from app.utils.exceptions import LLMServiceError
from app.utils.logger import logger

class RagService:
    
    @staticmethod
    def ask(question: str) -> dict:
        logger.info(f"RAG Service processing question: '{question}'")
        try:
            result = query(question)
            logger.info(f"RAG Service completed processing with status: {result.get('status')}")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in LLM/Ollama communication: {str(e)}")
            raise LLMServiceError("Failed to communicate with Ollama/LLM service")
        except Exception as e:
            logger.error(f"Unexpected error in RAG service: {str(e)}", exc_info=True)
            raise e