const config = {
  apiBaseUrl: process.env.NODE_ENV === 'development' 
    ? 'http://localhost:8000/api'  // Development API URL
    : '/api'  // Production API URL (when served by FastAPI)
};

export default config;