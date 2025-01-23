import axios from 'axios';

// Set the base URL for your FastAPI backend
axios.defaults.baseURL = 'http://localhost:8000';

// Optionally set other defaults, like headers or timeout
axios.defaults.headers.common['Content-Type'] = 'application/json';
axios.defaults.timeout = 5000; // 5 seconds timeout

export default axios;
