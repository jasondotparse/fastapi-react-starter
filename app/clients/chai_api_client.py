import httpx
import logging
from typing import List, Optional, Dict, Any
from app.clients.schemas.chai_schemas import ChatMessage, CHAIAPIRequest
from app.utils.env_validator import validate_chai_api_key

logger = logging.getLogger(__name__)

class CHAIAPIClient:
    
    def __init__(self):
        self.api_key = validate_chai_api_key()
        self.base_url = "http://guanaco-submitter.guanaco-backend.k2.chaiverse.com/endpoints/onsite/chat"
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        logger.info("CHAIAPIClient initialized with valid API key")
    
    async def invoke_llm(
        self,
        prompt: str,
        character_1_name: str,
        character_2_name: str,
        chat_history: List[Dict[str, str]]
    ) -> Optional[str]:
        try:
            formatted_chat_history = [
                ChatMessage(sender=msg["sender"], message=msg["message"])
                for msg in chat_history
            ]
            
            request_data = CHAIAPIRequest(
                memory="",  # Deprecated
                prompt=prompt,
                bot_name=character_1_name,
                user_name=character_2_name,
                chat_history=formatted_chat_history
            )

            logger.info(f"\n\nRequest data for CHAI API: {request_data.model_dump()}\n")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=request_data.model_dump(),
                    timeout=60.0  # Increased timeout for LLM API calls
                )
                response.raise_for_status()
                data = response.json()
                logger.info(f"\nResponse from CHAI API: {data['model_output'].strip()}\n\n")
                return data["model_output"].strip()
            
        except Exception as e:
            logger.error(f"Error invoking CHAI API: {str(e)}")
            raise
