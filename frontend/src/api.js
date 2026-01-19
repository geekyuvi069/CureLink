import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/api';

// Create axios instance
const api = axios.create({
    baseURL: 'http://localhost:8000/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add a request interceptor to include the JWT token
// No interceptor needed as auth is removed for ultra-plain version

export const sendMessage = async (message, sessionId) => {
    try {
        const response = await api.post('/chat', {
            message,
            session_id: sessionId,
            user_role: 'patient'
        });
        return response.data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
};

export default api;
