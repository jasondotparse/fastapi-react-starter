import os
import signal
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.schemas import ContinueConversationRequest, InitalizeCharactersRequest, Participant, Conversation
from app.services.character_sandbox_service import CharacterSandboxService
from dotenv import load_dotenv
import logging
from typing import List

# Load environment variables and setup logger
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create and configure the FastAPI app."""

    app = FastAPI(title="CHAI Agent Playground")
    
    # Initialize the character sandbox service
    character_sandbox_service = CharacterSandboxService()

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3001", "http://localhost:3000"],  # Allow React app origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Static file serving
    static_dir = "app/frontend/build/static"
    if not os.path.exists(static_dir):
        raise FileNotFoundError(f"Static directory '{static_dir}' does not exist.")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Routes
    @app.post("/initializeCharacters")
    async def initialize_characters(request: InitalizeCharactersRequest) -> List[Participant]:
        """
          This API is invoked at the start of a conversation, to generate a cast of AI agents. 
        """
        try:
            characters = await character_sandbox_service.initialize_characters(request)
            return characters
        except Exception as e:
            logger.error(f"Error initializing characters: {str(e)}")
            raise HTTPException(status_code=500, detail="Error initializing characters")

    @app.post("/continueConversation")
    async def continue_conversation(request: ContinueConversationRequest) -> Conversation:
        """
          At a high level, this simply takes in a <Conversation> (see section "data model" below) and returns an 
          updated <Conversation> containing additional <DialogTurns> that encode the AI's response to the most recent <DialogTurn>. 
          In this way, application state is held in the requests themselves, allowing the back end to be fully stateless. 
          When a Conversation is sent from the back end to the front end, the front end can reply with an updated <Conversation> 
          containing additional dialog turns, if the user chose to add a comment to the ongoing conversation. 
          See readme.md section "Conversation flow" for more.
        """
        try:
            updated_conversation = await character_sandbox_service.continue_conversation(request)
            return updated_conversation
        except Exception as e:
            logger.error(f"Error continuing conversation: {str(e)}")
            raise HTTPException(status_code=500, detail="Error continuing conversation")

    @app.get("/")
    def serve_root():
        return FileResponse("app/frontend/build/index.html")

    return app


def signal_handler(sig, frame):
    """Handle termination signals for graceful shutdown."""
    logger.info("Signal received. Shutting down...")
    os._exit(0)  # Exit the application gracefully


# Create the app instance
app = create_app()
