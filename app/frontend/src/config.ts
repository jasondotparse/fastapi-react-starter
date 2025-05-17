const config = {
  apiBaseUrl: process.env.NODE_ENV === 'development' 
    ? 'http://localhost:8000'  // Development API URL
    : ''  // Production API URL (when served by FastAPI)
};

export default config;
