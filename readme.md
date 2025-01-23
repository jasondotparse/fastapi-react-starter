# FastAPI React Starter Project

**FastAPI React Starter Project** is a boilerplate repository for building full-stack web applications using **FastAPI** as the backend framework and **React** as the frontend framework. This project is designed to provide developers with a starting point for modern web application development, supporting separate or unified backend and frontend deployments.

## Why This Project Is Important

- **Quick Start**: Offers a ready-to-use structure for full-stack projects, reducing setup time.
- **Flexibility**: Allows running the backend and frontend separately during development or as a single app in production.
- **Scalability**: Built with modularity and best practices to make it easy to extend and scale.
- **Developer-Friendly**: Includes features like CORS support, environment-based configuration, and clear instructions for deployment.

---

## Features

- **Backend**: FastAPI-powered REST API.
- **Frontend**: React app with Bootstrap for styling.
- **CORS Support**: Preconfigured for seamless backend-frontend communication.
- **Environment Variables**: `.env` support for flexible configuration.
- **Unified Deployment**: Option to serve the React app directly from FastAPI.

---

## How to Run the Project

### Prerequisites

1. **Backend Requirements**:
   - Python (3.9 or higher)
   - Virtual environment setup (optional but recommended)

2. **Frontend Requirements**:
   - Node.js (16.x or higher)
   - npm or Yarn package manager

### Running the Backend (FastAPI) Separately

1. **Clone the Repository**

    ```bash
    git clone https://github.com/naderzare/fastapi-react-starter.git
    cd fastapi-react-starter
    ```

2. **Create and Activate a Python Virtual Environment**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python Dependencies**
   
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the FastAPI Backend**

    ```bash
    python -m uvicorn app.main:app --reload
    ```

5. **Access the Backend**

   - Open `http://127.0.0.1:8000` in your browser.
   - API documentation is available at `http://127.0.0.1:8000/docs`.

---

### Running the Frontend (React) Separately

1. **Navigate to the `frontend` Directory**

    ```bash
    cd app/frontend
    ```

2. **Install Node.js Dependencies**

    ```bash
    npm install
    ```

3. **Run the React Development Server**

    ```bash
    npm start
    ```

4. **Access the Frontend**

   - Open `http://localhost:3000` in your browser.

---

### Running the Backend and Frontend Together

To serve the React app through FastAPI in production:

1. **Build the React App**

    ```bash
    cd app/frontend
    npm run build
    ```

   This will generate a `build` folder in the `frontend` directory.

2. **Update the `.env` File**
   - Open the `.env` file and set:
     ```env
     SERVE_UI=true
     ```

3. **Run the FastAPI App**

   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. **Access the Unified App**
   - Open `http://127.0.0.1:8000` in your browser to see the React frontend served by FastAPI.

---

## Project Structure

```
fastapi-react-starter/
├── app/
│   ├── main.py         # FastAPI app definition
│   ├── database.py     # Database configuration
│   ├── models.py       # SQLAlchemy models
│   ├── schemas.py      # Pydantic schemas
│   ├── logger.py       # Custom logger setup
│   ├── frontend/       # React app
│   │   ├── build/      # React build files
│   │   ├── src/        # React source code
│   └── __init__.py
├── requirements.txt    # Python dependencies
├── .env                # Environment variables
└── README.md           # Project documentation
```

---

## API Endpoints

### Backend API

1. **Add a User**
   - **POST** `/user/add`
   - Request Body:
     ```json
     {
       "username": "john_doe",
       "age": 30
     }
     ```
   - Response:
     ```json
     {
       "id": 1,
       "message": "User created successfully"
     }
     ```

2. **Get All Users**
   - **GET** `/user/all`
   - Response:
     ```json
     [
       {
         "id": 1,
         "username": "john_doe",
         "age": 30
       }
     ]
     ```

---

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push the branch.
4. Open a pull request for review.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contact

If you have any questions or feedback, feel free to reach out or open an issue in the repository.

---

## Keywords

- FastAPI React Starter
- Full-stack web development
- FastAPI boilerplate
- React frontend with FastAPI
- Modern web app example

