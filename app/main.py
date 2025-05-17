import os
import signal
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.schemas import InitalizeCharactersRequest, Participant, Conversation
from dotenv import load_dotenv
import logging
from typing import List

# Load environment variables and setup logger
load_dotenv()

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create and configure the FastAPI app."""

    app = FastAPI(title="FastAPI User Manager")

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
    def initialize_characters(initalizeCharactersRequest: InitalizeCharactersRequest) -> List[Participant]:
        """
          This API is invoked at the start of a conversation, to generate a cast of AI agents which will 
          List<Participant> (see section "data model" below) in the conversation.
        """
        try:
            ## todo: implement this
            participantList = []
            return participantList
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(status_code=500, detail="Error creating user")

    @app.post("/continueConversation")
    def continue_conversation(conversation: Conversation) -> Conversation:
        """
          At a high level, this simply takes in a <Conversation> (see section "data model" below) and returns an 
          updated <Conversation> containing additional <DialogTurns> that encode the AI's response to the most recent <DialogTurn>. 
          In this way, application state is held in the requests themselves, allowing the back end to be fully stateless. 
          When a Conversation is sent from the back end to the front end, the front end can reply with an updated <Conversation> 
          containing additional dialog turns, if the user chose to add a comment to the ongoing conversation. 
          See readme.md section "Conversation flow" for more.
        """
        try:
            ## todo: implement this
            updated_conversation = {}
            return updated_conversation
        except Exception as e:
            logger.error(f"Error retrieving users: {str(e)}")
            raise HTTPException(status_code=500, detail="Error retrieving users")

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
