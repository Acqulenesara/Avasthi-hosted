const API_URL = "http://127.0.0.1:8000"; // Your FastAPI backend URL

/**
 * A helper function for making API requests.
 * @param {string} endpoint The endpoint to call (e.g., "/login").
 * @param {string} method The HTTP method (e.g., "POST").
 * @param {object} body The request body for POST requests.
 * @param {boolean} isFormData Whether the body should be sent as FormData.
 * @returns {Promise<any>} The JSON response from the server.
 */
async function request(endpoint, method = "GET", body = null, isFormData = false) {
    const url = `${API_URL}${endpoint}`;
    const options = {
        method,
        headers: {},
    };

    if (body) {
        if (isFormData) {
            options.body = new URLSearchParams();
            for (const key in body) {
                options.body.append(key, body[key]);
            }
        } else {
            options.headers["Content-Type"] = "application/json";
            options.body = JSON.stringify(body);
        }
    }

    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "An error occurred");
        }
        return await response.json();
    } catch (error) {
        console.error("API request failed:", error);
        throw error;
    }
}

// Authentication API calls
export const registerUser = (username, password) =>
    request("/register", "POST", { username, password });

export const loginUser = (username, password) =>
    request("/login", "POST", { username, password }, true);

// Main Application API calls
export const getRecommendations = (username) =>
    request("/recommendations", "POST", { username, top_k: 5 });

export const sendFeedback = (username, activity_title, liked) =>
    request("/feedback", "POST", { username, activity_title, liked });

export const getHistory = (username) =>
    request(`/recommendation-history?username=${username}`);

export const sendChatMessage = (query) =>
    request("/query", "POST", { query });