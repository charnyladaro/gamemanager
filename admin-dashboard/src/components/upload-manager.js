/**
 * Upload Manager - Handles background file uploads with progress tracking
 */

class UploadManager {
    constructor() {
        this.uploads = new Map();
        this.loadUploadsFromStorage();
        this.createUploadWidget();
    }

    createUploadWidget() {
        // Create floating upload widget
        const widget = document.createElement('div');
        widget.id = 'upload-widget';
        widget.className = 'upload-widget';
        widget.innerHTML = `
            <div class="upload-widget-header">
                <span class="upload-widget-title">Uploads (<span id="upload-count">0</span>)</span>
                <button class="upload-widget-toggle" onclick="uploadManager.toggleWidget()">−</button>
            </div>
            <div class="upload-widget-body" id="upload-widget-body">
                <div class="upload-empty">No active uploads</div>
            </div>
        `;

        if (!document.body) {
            window.addEventListener('DOMContentLoaded', () => {
                document.body.appendChild(widget);
            });
        } else {
            document.body.appendChild(widget);
        }
    }

    toggleWidget() {
        const body = document.getElementById('upload-widget-body');
        const toggle = document.querySelector('.upload-widget-toggle');

        if (body.style.display === 'none') {
            body.style.display = 'block';
            toggle.textContent = '−';
        } else {
            body.style.display = 'none';
            toggle.textContent = '+';
        }
    }

    loadUploadsFromStorage() {
        try {
            const stored = localStorage.getItem('active_uploads');
            if (stored) {
                const uploads = JSON.parse(stored);
                // Filter out completed uploads older than 1 hour
                const now = Date.now();
                const filtered = uploads.filter(u => {
                    if (u.status === 'completed' && (now - u.completedAt) > 3600000) {
                        return false;
                    }
                    return true;
                });
                filtered.forEach(upload => {
                    this.uploads.set(upload.id, upload);
                });
                this.updateWidget();
            }
        } catch (error) {
            console.error('Failed to load uploads from storage:', error);
        }
    }

    saveUploadsToStorage() {
        try {
            const uploads = Array.from(this.uploads.values());
            localStorage.setItem('active_uploads', JSON.stringify(uploads));
        } catch (error) {
            console.error('Failed to save uploads to storage:', error);
        }
    }

    startUpload(file, formData, onComplete, onError) {
        const uploadId = Date.now() + '_' + Math.random().toString(36).substr(2, 9);

        const upload = {
            id: uploadId,
            fileName: formData.get('title') || file.name,
            fileSize: file.size,
            progress: 0,
            status: 'uploading', // uploading, completed, error
            startedAt: Date.now(),
            xhr: null
        };

        this.uploads.set(uploadId, upload);
        this.updateWidget();
        this.saveUploadsToStorage();

        // Create XMLHttpRequest for progress tracking
        const xhr = new XMLHttpRequest();
        upload.xhr = xhr;

        // Progress tracking
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                upload.progress = percentComplete;
                this.updateUploadProgress(uploadId);
            }
        });

        // Upload complete
        xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    upload.status = 'completed';
                    upload.progress = 100;
                    upload.completedAt = Date.now();
                    this.updateUploadProgress(uploadId);
                    this.saveUploadsToStorage();

                    if (onComplete) {
                        onComplete(response);
                    }

                    // Remove from widget after 5 seconds
                    setTimeout(() => {
                        this.removeUpload(uploadId);
                    }, 5000);
                } catch (error) {
                    upload.status = 'error';
                    upload.error = 'Invalid server response';
                    this.updateUploadProgress(uploadId);

                    if (onError) {
                        onError(new Error('Invalid server response'));
                    }
                }
            } else {
                try {
                    const errorData = JSON.parse(xhr.responseText);
                    upload.status = 'error';
                    upload.error = errorData.error || 'Upload failed';
                } catch {
                    upload.status = 'error';
                    upload.error = `Upload failed with status ${xhr.status}`;
                }
                this.updateUploadProgress(uploadId);

                if (onError) {
                    onError(new Error(upload.error));
                }
            }
        });

        // Upload error
        xhr.addEventListener('error', () => {
            upload.status = 'error';
            upload.error = 'Network error';
            this.updateUploadProgress(uploadId);

            if (onError) {
                onError(new Error('Network error'));
            }
        });

        // Upload aborted
        xhr.addEventListener('abort', () => {
            upload.status = 'error';
            upload.error = 'Upload cancelled';
            this.updateUploadProgress(uploadId);
        });

        // Start upload
        const token = localStorage.getItem('admin_token');
        xhr.open('POST', 'http://localhost:5000/api/games');

        if (token) {
            xhr.setRequestHeader('Authorization', `Bearer ${token}`);
        }

        xhr.send(formData);

        return uploadId;
    }

    cancelUpload(uploadId) {
        const upload = this.uploads.get(uploadId);
        if (upload && upload.xhr) {
            upload.xhr.abort();
            this.removeUpload(uploadId);
        }
    }

    removeUpload(uploadId) {
        this.uploads.delete(uploadId);
        this.updateWidget();
        this.saveUploadsToStorage();
    }

    updateUploadProgress(uploadId) {
        const upload = this.uploads.get(uploadId);
        if (!upload) return;

        const uploadEl = document.getElementById(`upload-${uploadId}`);
        if (uploadEl) {
            const progressBar = uploadEl.querySelector('.upload-progress-bar');
            const progressText = uploadEl.querySelector('.upload-progress-text');
            const statusEl = uploadEl.querySelector('.upload-status');

            if (progressBar) {
                progressBar.style.width = `${upload.progress}%`;
            }

            if (progressText) {
                progressText.textContent = `${Math.round(upload.progress)}%`;
            }

            if (statusEl) {
                if (upload.status === 'completed') {
                    statusEl.innerHTML = '<span class="badge badge-success">✓ Completed</span>';
                } else if (upload.status === 'error') {
                    statusEl.innerHTML = `<span class="badge badge-danger">✗ ${upload.error}</span>`;
                } else {
                    statusEl.innerHTML = '<span class="badge badge-info">Uploading...</span>';
                }
            }
        }

        this.saveUploadsToStorage();
    }

    updateWidget() {
        const body = document.getElementById('upload-widget-body');
        const count = document.getElementById('upload-count');

        if (!body || !count) return;

        count.textContent = this.uploads.size;

        if (this.uploads.size === 0) {
            body.innerHTML = '<div class="upload-empty">No active uploads</div>';
            return;
        }

        body.innerHTML = '';

        this.uploads.forEach((upload) => {
            const uploadEl = document.createElement('div');
            uploadEl.id = `upload-${upload.id}`;
            uploadEl.className = 'upload-item';

            const statusBadge = upload.status === 'completed'
                ? '<span class="badge badge-success">✓ Completed</span>'
                : upload.status === 'error'
                ? `<span class="badge badge-danger">✗ ${upload.error}</span>`
                : '<span class="badge badge-info">Uploading...</span>';

            uploadEl.innerHTML = `
                <div class="upload-item-header">
                    <div class="upload-file-name">${upload.fileName}</div>
                    <div class="upload-status">${statusBadge}</div>
                </div>
                <div class="upload-progress">
                    <div class="upload-progress-bar" style="width: ${upload.progress}%"></div>
                </div>
                <div class="upload-item-footer">
                    <div class="upload-progress-text">${Math.round(upload.progress)}%</div>
                    <div class="upload-file-size">${this.formatFileSize(upload.fileSize)}</div>
                    ${upload.status === 'uploading' ?
                        `<button class="btn-danger btn-small" onclick="uploadManager.cancelUpload('${upload.id}')">Cancel</button>` :
                        `<button class="btn-secondary btn-small" onclick="uploadManager.removeUpload('${upload.id}')">Remove</button>`
                    }
                </div>
            `;

            body.appendChild(uploadEl);
        });
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
    }

    getActiveUploads() {
        return Array.from(this.uploads.values()).filter(u => u.status === 'uploading');
    }

    hasActiveUploads() {
        return this.getActiveUploads().length > 0;
    }
}

// Create global instance
const uploadManager = new UploadManager();
