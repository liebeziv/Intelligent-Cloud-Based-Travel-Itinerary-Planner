// frontend/src/api/config.js
// Prefer environment-provided API base, fallback to a placeholder (please override via VITE_API_URL)
const API_BASE_URL = 'https://travelplan.us-east-1.elasticbeanstalk.com';

export const apiConfig = {
  baseURL: API_BASE_URL,
  endpoints: {
    auth: {
      register: '/api/auth/register',
      login: '/api/auth/login'
    },
    recommendations: '/api/recommendations',
    health: '/health'
  }
};


export async function apiCall(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  };

  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
}
