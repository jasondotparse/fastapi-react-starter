import os
import signal
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.models import UserModel
from app.schemas import UserSchema, UserRespSchema
from dotenv import load_dotenv
from app.logger import setup_logger

# Load environment variables and setup logger
load_dotenv()


def create_app() -> FastAPI:
    """Create and configure the FastAPI app."""
    # Read the SERVE_UI value from the .env file
    serve_ui = os.getenv("SERVE_UI", "false").lower() == "true"

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
    @app.post("/user/add")
    def add_user(user: UserSchema, db: Session = Depends(get_db)):
        """
        Add a new user to the database.
        """
        try:
            new_user = UserModel(username=user.username, age=user.age)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            logger.info(f"Created new user ID: {new_user.id}")
            return {"id": new_user.id, "message": "User created successfully"}
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(status_code=500, detail="Error creating user")

    @app.get("/user/all")
    def get_all_users(db: Session = Depends(get_db)):
        """
        Get all users from the database.
        """
        try:
            users = db.query(UserModel).all()
            user_list = [UserRespSchema(id=user.id, username=user.username, age=user.age) for user in users]
            user_list = [user.dict() for user in user_list]
            logger.info("Retrieved all users")
            return user_list
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
