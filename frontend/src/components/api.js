const API_URL = 'http://localhost:5000/api';

class API {
    constructor() {
        this.token = localStorage.getItem('token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('token');
    }

    getToken() {
        return this.token;
    }

    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    async request(endpoint, options = {}) {
        const url = `${API_URL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.getHeaders(),
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, config);

            // Check content type before parsing
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                // Server returned HTML or something else
                const text = await response.text();
                console.error('Server returned non-JSON response:', text.substring(0, 200));
                const error = new Error('Server error - check if backend is running correctly');
                error.status = response.status;
                throw error;
            }

            const data = await response.json();

            if (!response.ok) {
                const error = new Error(data.error || 'Request failed');
                error.status = response.status;
                throw error;
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            // If error doesn't have status, add it (for network errors)
            if (!error.status && error.name === 'TypeError') {
                error.status = 0; // Network error
            }
            throw error;
        }
    }

    // Auth
    async register(username, email, password) {
        const data = await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, password })
        });
        this.setToken(data.access_token);
        return data;
    }

    async login(username, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        this.setToken(data.access_token);
        return data;
    }

    async logout() {
        await this.request('/auth/logout', { method: 'POST' });
        this.clearToken();
    }

    async getCurrentUser() {
        return await this.request('/auth/me');
    }

    // Games
    async getGames(search = '') {
        let url = '/games';
        if (search) {
            url += `?search=${encodeURIComponent(search)}`;
        }
        return await this.request(url);
    }

    async getGame(gameId) {
        return await this.request(`/games/${gameId}`);
    }

    async createGame(formData) {
        const url = `${API_URL}/games`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`
            },
            body: formData
        });
        return await response.json();
    }

    async downloadGame(gameId) {
        const url = `${API_URL}/games/${gameId}/download`;
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${this.token}`
            }
        });
        return response;
    }

    async deleteGame(gameId) {
        return await this.request(`/games/${gameId}`, { method: 'DELETE' });
    }

    // User Library
    async getLibrary() {
        return await this.request('/users/library');
    }

    async addToLibrary(gameId) {
        return await this.request(`/users/library/${gameId}`, { method: 'POST' });
    }

    async removeFromLibrary(gameId) {
        return await this.request(`/users/library/${gameId}`, { method: 'DELETE' });
    }

    async updateLibraryGame(gameId, updates) {
        return await this.request(`/users/library/${gameId}`, {
            method: 'PATCH',
            body: JSON.stringify(updates)
        });
    }

    async getProfile() {
        return await this.request('/users/profile');
    }

    async updateProfile(updates) {
        return await this.request('/users/profile', {
            method: 'PATCH',
            body: JSON.stringify(updates)
        });
    }

    async searchUsers(query) {
        return await this.request(`/users/search?q=${encodeURIComponent(query)}`);
    }

    // Friends
    async getFriends() {
        return await this.request('/friends');
    }

    async getFriendRequests() {
        return await this.request('/friends/requests');
    }

    async getSentRequests() {
        return await this.request('/friends/requests/sent');
    }

    async sendFriendRequest(friendId) {
        return await this.request(`/friends/add/${friendId}`, { method: 'POST' });
    }

    async acceptFriendRequest(requestId) {
        return await this.request(`/friends/requests/${requestId}/accept`, { method: 'POST' });
    }

    async rejectFriendRequest(requestId) {
        return await this.request(`/friends/requests/${requestId}/reject`, { method: 'POST' });
    }

    async removeFriend(friendId) {
        return await this.request(`/friends/${friendId}`, { method: 'DELETE' });
    }

    // Game Requests
    async getGameRequests() {
        return await this.request('/game-requests');
    }

    async getAllGameRequests(status) {
        const query = status ? `?status=${status}` : '';
        return await this.request(`/game-requests/all${query}`);
    }

    async createGameRequest(gameTitle, description) {
        return await this.request('/game-requests', {
            method: 'POST',
            body: JSON.stringify({ game_title: gameTitle, description })
        });
    }

    async updateGameRequest(requestId, updates) {
        return await this.request(`/game-requests/${requestId}`, {
            method: 'PATCH',
            body: JSON.stringify(updates)
        });
    }

    async deleteGameRequest(requestId) {
        return await this.request(`/game-requests/${requestId}`, { method: 'DELETE' });
    }
}

const api = new API();
