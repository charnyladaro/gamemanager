/**
 * Admin API Client for GameManager Admin Dashboard
 */

class AdminAPI {
    constructor() {
        this.baseURL = 'http://localhost:5000/api';
        this.token = localStorage.getItem('admin_token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('admin_token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('admin_token');
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            const contentType = response.headers.get('content-type');
            let data;

            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                data = await response.text();
            }

            if (!response.ok) {
                throw new Error(data.error || data.message || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Authentication
    async login(username, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        if (data.access_token) {
            this.setToken(data.access_token);
        }
        return data;
    }

    async logout() {
        try {
            await this.request('/auth/logout', { method: 'POST' });
        } finally {
            this.clearToken();
        }
    }

    async getCurrentUser() {
        return this.request('/auth/me');
    }

    // Admin Statistics
    async getStatistics() {
        return this.request('/admin/stats');
    }

    async getActivity(limit = 50) {
        return this.request(`/admin/activity?limit=${limit}`);
    }

    // User Management
    async getAllUsers(page = 1, perPage = 50, search = '') {
        let url = `/admin/users?page=${page}&per_page=${perPage}`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        return this.request(url);
    }

    async getUserDetail(userId) {
        return this.request(`/admin/users/${userId}`);
    }

    async createUser(userData) {
        return this.request('/admin/users', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    async updateUser(userId, userData) {
        return this.request(`/admin/users/${userId}`, {
            method: 'PATCH',
            body: JSON.stringify(userData)
        });
    }

    async deleteUser(userId) {
        return this.request(`/admin/users/${userId}`, {
            method: 'DELETE'
        });
    }

    // Game Management
    async getAllGames(page = 1, perPage = 50, search = '') {
        let url = `/admin/games?page=${page}&per_page=${perPage}`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        return this.request(url);
    }

    async getGameDetail(gameId) {
        return this.request(`/games/${gameId}`);
    }

    async createGame(formData) {
        // Special handling for file uploads
        const url = `${this.baseURL}/games`;
        const headers = {};

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const response = await fetch(url, {
            method: 'POST',
            headers,
            body: formData // FormData, not JSON
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Failed to create game');
        }

        return data;
    }

    async updateGame(gameId, gameData) {
        return this.request(`/admin/games/${gameId}`, {
            method: 'PATCH',
            body: JSON.stringify(gameData)
        });
    }

    async deleteGame(gameId) {
        return this.request(`/games/${gameId}`, {
            method: 'DELETE'
        });
    }

    async toggleGameAvailability(gameId) {
        return this.request(`/admin/games/${gameId}/toggle-availability`, {
            method: 'POST'
        });
    }

    // Game Request Management
    async getAllGameRequests(status = null, page = 1, perPage = 50) {
        let url = `/admin/game-requests?page=${page}&per_page=${perPage}`;
        if (status) url += `&status=${status}`;
        return this.request(url);
    }

    async updateGameRequest(requestId, updates) {
        return this.request(`/admin/game-requests/${requestId}`, {
            method: 'PATCH',
            body: JSON.stringify(updates)
        });
    }

    // File Management
    async cleanupOrphanedFiles() {
        return this.request('/admin/files/cleanup', {
            method: 'POST'
        });
    }

    // Scanned Games Management
    async getScannedGames(page = 1, perPage = 50, search = '', status = null) {
        let url = `/admin/scanned-games?page=${page}&per_page=${perPage}`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        if (status) url += `&status=${status}`;
        return this.request(url);
    }

    async scanGamesFolder() {
        return this.request('/admin/scanned-games/scan', {
            method: 'POST'
        });
    }

    async addScannedGameToLibrary(scannedGameId, metadata = {}) {
        return this.request(`/admin/scanned-games/${scannedGameId}/add-to-library`, {
            method: 'POST',
            body: JSON.stringify(metadata)
        });
    }

    async updateScannedGameTitle(scannedGameId, title) {
        return this.request(`/admin/scanned-games/${scannedGameId}/title`, {
            method: 'PUT',
            body: JSON.stringify({ title })
        });
    }

    async deleteScannedGame(scannedGameId, removeFile = false) {
        return this.request(`/admin/scanned-games/${scannedGameId}`, {
            method: 'DELETE',
            body: JSON.stringify({ remove_file: removeFile })
        });
    }

    async fetchScannedGameCover(scannedGameId) {
        return this.request(`/admin/scanned-games/${scannedGameId}/fetch-cover`, {
            method: 'POST'
        });
    }

    async fetchAllScannedCovers() {
        return this.request('/admin/scanned-games/fetch-all-covers', {
            method: 'POST'
        });
    }

    // Payment Management
    async getAllPayments(page = 1, perPage = 50, status = '') {
        let url = `/payments/all?page=${page}&per_page=${perPage}`;
        if (status) url += `&status=${encodeURIComponent(status)}`;
        return this.request(url);
    }

    async getPaymentStats() {
        return this.request('/payments/stats');
    }

    async verifyPayment(paymentId) {
        return this.request(`/payments/${paymentId}/verify`, {
            method: 'POST'
        });
    }

    async rejectPayment(paymentId) {
        return this.request(`/payments/${paymentId}/reject`, {
            method: 'POST'
        });
    }

    // Helper methods
    getImageUrl(path) {
        if (!path) return null;
        return `${this.baseURL}${path}`;
    }

    getCoverUrl(gameId) {
        return `${this.baseURL}/games/${gameId}/cover`;
    }
}

// Export singleton instance
const API = new AdminAPI();

