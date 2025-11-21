/**
 * UI Utility Functions for Admin Dashboard
 */

const { ipcRenderer } = require('electron');

// Window Controls
function minimizeWindow() {
    ipcRenderer.send('minimize-window');
}

function maximizeWindow() {
    ipcRenderer.send('maximize-window');
}

function closeWindow() {
    ipcRenderer.send('close-window');
}

function navigateTo(page) {
    ipcRenderer.send('navigate', page);
}

// Modal Controls
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Toast Notifications
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    const container = document.getElementById('toast-container') || createToastContainer();
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// Loading Overlay
function showLoading(message = 'Loading...') {
    let overlay = document.getElementById('loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-message">${message}</div>
        `;
        document.body.appendChild(overlay);
    } else {
        overlay.querySelector('.loading-message').textContent = message;
    }
    overlay.style.display = 'flex';
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// Format Functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

function formatPlaytime(minutes) {
    if (minutes < 60) {
        return `${minutes} min`;
    }

    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;

    if (hours < 24) {
        return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
    }

    const days = Math.floor(hours / 24);
    const remainingHours = hours % 24;

    return remainingHours > 0 ? `${days}d ${remainingHours}h` : `${days}d`;
}

function formatDate(dateString) {
    if (!dateString) return 'Never';

    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (seconds < 60) return 'Just now';
    if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    if (days < 7) return `${days} day${days > 1 ? 's' : ''} ago`;

    return date.toLocaleDateString();
}

function formatDateTime(dateString) {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Authentication Helpers
function checkAuth() {
    const token = localStorage.getItem('admin_token');
    if (!token) {
        navigateTo('login.html');
        return false;
    }
    return true;
}

async function logout() {
    try {
        await API.logout();
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        localStorage.removeItem('admin_token');
        navigateTo('login.html');
    }
}

// Pagination Helper
function createPagination(pagination, onPageChange) {
    const { page, pages, total } = pagination;

    const container = document.createElement('div');
    container.className = 'pagination';

    if (pages <= 1) return container;

    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.textContent = 'Previous';
    prevBtn.disabled = page === 1;
    prevBtn.onclick = () => onPageChange(page - 1);
    container.appendChild(prevBtn);

    // Page info
    const pageInfo = document.createElement('span');
    pageInfo.className = 'page-info';
    pageInfo.textContent = `Page ${page} of ${pages} (${total} total)`;
    container.appendChild(pageInfo);

    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.textContent = 'Next';
    nextBtn.disabled = page === pages;
    nextBtn.onclick = () => onPageChange(page + 1);
    container.appendChild(nextBtn);

    return container;
}

// Confirmation Dialog
function confirmAction(message) {
    return new Promise((resolve) => {
        const overlay = document.createElement('div');
        overlay.className = 'confirm-overlay';

        const dialog = document.createElement('div');
        dialog.className = 'confirm-dialog';

        const messageEl = document.createElement('p');
        messageEl.textContent = message;

        const actions = document.createElement('div');
        actions.className = 'confirm-actions';

        const confirmBtn = document.createElement('button');
        confirmBtn.className = 'btn-danger';
        confirmBtn.textContent = 'Confirm';
        confirmBtn.onclick = () => {
            overlay.remove();
            resolve(true);
        };

        const cancelBtn = document.createElement('button');
        cancelBtn.className = 'btn-secondary';
        cancelBtn.textContent = 'Cancel';
        cancelBtn.onclick = () => {
            overlay.remove();
            resolve(false);
        };

        actions.appendChild(cancelBtn);
        actions.appendChild(confirmBtn);

        dialog.appendChild(messageEl);
        dialog.appendChild(actions);
        overlay.appendChild(dialog);

        document.body.appendChild(overlay);
    });
}

// Table Helpers
function createTable(columns, data, actions = null) {
    const table = document.createElement('table');
    table.className = 'data-table';

    // Header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');

    columns.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col.label;
        if (col.width) th.style.width = col.width;
        headerRow.appendChild(th);
    });

    if (actions) {
        const th = document.createElement('th');
        th.textContent = 'Actions';
        th.style.width = actions.width || '120px';
        headerRow.appendChild(th);
    }

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Body
    const tbody = document.createElement('tbody');

    data.forEach(row => {
        const tr = document.createElement('tr');

        columns.forEach(col => {
            const td = document.createElement('td');
            const value = col.key.split('.').reduce((obj, key) => obj?.[key], row);

            if (col.format) {
                td.innerHTML = col.format(value, row);
            } else {
                td.textContent = value ?? '-';
            }

            tr.appendChild(td);
        });

        if (actions) {
            const td = document.createElement('td');
            td.className = 'actions-cell';
            td.appendChild(actions.render(row));
            tr.appendChild(td);
        }

        tbody.appendChild(tr);
    });

    table.appendChild(tbody);

    return table;
}

// Search Debounce
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Status Badge
function getStatusBadge(status) {
    const badges = {
        'pending': '<span class="badge badge-warning">Pending</span>',
        'approved': '<span class="badge badge-success">Approved</span>',
        'rejected': '<span class="badge badge-danger">Rejected</span>',
        'completed': '<span class="badge badge-info">Completed</span>',
        'accepted': '<span class="badge badge-success">Accepted</span>',
        'online': '<span class="badge badge-success">Online</span>',
        'offline': '<span class="badge badge-secondary">Offline</span>'
    };

    return badges[status] || `<span class="badge">${status}</span>`;
}

// Export functions
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        minimizeWindow,
        maximizeWindow,
        closeWindow,
        navigateTo,
        showModal,
        hideModal,
        showToast,
        showLoading,
        hideLoading,
        formatFileSize,
        formatPlaytime,
        formatDate,
        formatDateTime,
        checkAuth,
        logout,
        createPagination,
        confirmAction,
        createTable,
        debounce,
        getStatusBadge
    };
}
