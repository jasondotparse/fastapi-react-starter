import httpx
import logging
import asyncio
from typing import List, Optional, Dict, Any
from app.clients.schemas.chai_schemas import ChatMessage, CHAIAPIRequest
from app.utils.env_validator import validate_chai_api_key

logger = logging.getLogger(__name__)

class CHAIAPIClient:
    
    def __init__(self, max_retries=3, initial_backoff=1, backoff_factor=2):
        self.api_key = validate_chai_api_key()
        self.base_url = "http://guanaco-submitter.guanaco-backend.k2.chaiverse.com/endpoints/onsite/chat"
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        # Retry configuration
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.backoff_factor = backoff_factor
        logger.info("CHAIAPIClient initialized with valid API key and retry mechanism")
    
    async def invoke_llm(
        self,
        prompt: str,
        character_1_name: str,
        character_2_name: str,
        chat_history: List[Dict[str, str]]
    ) -> Optional[str]:
        # Format the request data outside the retry loop
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
        
        # Initialize retry variables
        retries = 0
        backoff_time = self.initial_backoff
        
        # Retry loop
        while True:
            try:
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
                
            except httpx.HTTPStatusError as e:
                # Check if it's a 429 error and we haven't exceeded max retries
                if e.response.status_code == 429 and retries < self.max_retries:
                    retries += 1
                    logger.warning(f"Received 429 Too Many Requests. Retry attempt {retries}/{self.max_retries} after {backoff_time}s backoff")
                    await asyncio.sleep(backoff_time)
                    backoff_time *= self.backoff_factor  # Exponential backoff
                    continue  # Try again
                
                # If it's not a 429 error or we've exceeded max retries, log and re-raise
                logger.error(f"Error invoking CHAI API: {str(e)}")
                raise
                
            except Exception as e:
                # For any other exception, log and re-raise
                logger.error(f"Error invoking CHAI API: {str(e)}")
                raise
