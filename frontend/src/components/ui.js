const { ipcRenderer } = require('electron');

// Window controls
function setupTitleBar() {
    document.getElementById('btn-minimize')?.addEventListener('click', () => {
        ipcRenderer.send('window-minimize');
    });

    document.getElementById('btn-maximize')?.addEventListener('click', () => {
        ipcRenderer.send('window-maximize');
    });

    document.getElementById('btn-close')?.addEventListener('click', () => {
        ipcRenderer.send('window-close');
    });
}

// Navigation
function navigate(page) {
    ipcRenderer.send('navigate', page);
}

// Modal
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// Toast notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 50px;
        right: 20px;
        background: ${type === 'error' ? '#d94141' : type === 'success' ? '#5c9e3c' : '#66c0f4'};
        color: white;
        padding: 15px 20px;
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Loading spinner
function showLoading() {
    const loading = document.createElement('div');
    loading.id = 'loading-overlay';
    loading.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    `;
    loading.innerHTML = '<div class="spinner"></div>';
    document.body.appendChild(loading);
}

function hideLoading() {
    const loading = document.getElementById('loading-overlay');
    if (loading) {
        loading.remove();
    }
}

// Format playtime
function formatPlaytime(minutes) {
    if (minutes < 60) {
        return `${minutes}m`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    if (diffMins < 10080) return `${Math.floor(diffMins / 1440)}d ago`;

    return date.toLocaleDateString();
}

// Check if user is authenticated
function isAuthenticated() {
    return !!localStorage.getItem('token');
}

// Redirect if not authenticated
function requireAuth() {
    if (!isAuthenticated()) {
        navigate('login');
        return false;
    }
    return true;
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }

    .spinner {
        width: 50px;
        height: 50px;
        border: 4px solid rgba(255, 255, 255, 0.3);
        border-top-color: #66c0f4;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

// Setup on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setupTitleBar();
    });
} else {
    // DOM is already loaded, call setupTitleBar immediately
    setupTitleBar();
}
