// Get API URL from environment variable or use default
const API_BASE_URL = process.env.VUE_APP_API_URL || window.location.origin;  // Will use the same origin in production

export default API_BASE_URL;