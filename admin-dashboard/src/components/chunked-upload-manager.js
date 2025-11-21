/**
 * Chunked Upload Manager - Handles large file uploads with resume capability
 */

class ChunkedUploadManager {
    constructor() {
        this.uploads = new Map();
        this.CHUNK_SIZE = 5 * 1024 * 1024; // 5MB chunks
        this.MAX_RETRIES = 3;
        this.RETRY_DELAY = 2000; // 2 seconds
        this.loadUploadsFromStorage();
        this.syncWithServer(); // Recover lost sessions
        this.createUploadWidget();
    }

    createUploadWidget() {
        const widget = document.createElement('div');
        widget.id = 'upload-widget';
        widget.className = 'upload-widget';
        widget.innerHTML = `
            <div class="upload-widget-header">
                <span class="upload-widget-title">Uploads (<span id="upload-count">0</span>)</span>
                <button class="upload-widget-toggle" onclick="chunkedUploadManager.toggleWidget()">−</button>
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
            const stored = localStorage.getItem('chunked_uploads');
            if (stored) {
                const uploads = JSON.parse(stored);
                const now = Date.now();

                uploads.forEach(upload => {
                    // Filter out completed uploads older than 1 hour
                    if (upload.status === 'completed' && (now - upload.completedAt) > 3600000) {
                        return;
                    }
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
            const uploads = Array.from(this.uploads.values()).map(u => ({
                ...u,
                file: null, // Don't store file object
                currentChunkBlob: null // Don't store blob
            }));
            localStorage.setItem('chunked_uploads', JSON.stringify(uploads));
        } catch (error) {
            console.error('Failed to save uploads to storage:', error);
        }
    }

    async startUpload(file, gameData, coverImage, onComplete, onError) {
        const uploadId = Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        const totalChunks = Math.ceil(file.size / this.CHUNK_SIZE);

        const upload = {
            id: uploadId,
            fileName: gameData.title || file.name,
            file: file,
            fileSize: file.size,
            totalChunks: totalChunks,
            uploadedChunks: [],
            currentChunk: 0,
            progress: 0,
            status: 'initializing', // initializing, uploading, paused, completed, error
            startedAt: Date.now(),
            gameData: gameData,
            coverImage: coverImage,
            retryCount: 0,
            sessionId: null,
            onComplete: onComplete,
            onError: onError
        };

        this.uploads.set(uploadId, upload);
        this.updateWidget();
        this.saveUploadsToStorage();

        // Initialize upload session
        await this.initializeUploadSession(upload);

        return uploadId;
    }

    async initializeUploadSession(upload) {
        try {
            const token = localStorage.getItem('admin_token');
            const response = await fetch('http://localhost:5000/api/chunked-upload/init', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    fileName: upload.file.name,
                    fileSize: upload.fileSize,
                    totalChunks: upload.totalChunks,
                    gameData: upload.gameData
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to initialize upload');
            }

            upload.sessionId = data.uploadId;
            upload.status = 'uploading';
            this.updateWidget();
            this.saveUploadsToStorage();

            // Start uploading chunks
            await this.uploadNextChunk(upload.id);

        } catch (error) {
            console.error('Failed to initialize upload:', error);
            upload.status = 'error';
            upload.error = error.message;
            this.updateWidget();

            if (upload.onError) {
                upload.onError(error);
            }
        }
    }

    async uploadNextChunk(uploadId) {
        const upload = this.uploads.get(uploadId);
        if (!upload || upload.status !== 'uploading') return;

        // Check if all chunks uploaded
        if (upload.currentChunk >= upload.totalChunks) {
            await this.completeUpload(uploadId);
            return;
        }

        try {
            // Get chunk data
            const start = upload.currentChunk * this.CHUNK_SIZE;
            const end = Math.min(start + this.CHUNK_SIZE, upload.fileSize);
            const chunkBlob = upload.file.slice(start, end);

            // Upload chunk
            const formData = new FormData();
            formData.append('uploadId', upload.sessionId);
            formData.append('chunkIndex', upload.currentChunk);
            formData.append('chunk', chunkBlob);

            const token = localStorage.getItem('admin_token');
            const response = await fetch('http://localhost:5000/api/chunked-upload/chunk', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to upload chunk');
            }

            // Update progress
            upload.uploadedChunks = data.uploadedChunks;
            upload.currentChunk++;
            upload.progress = Math.floor((upload.currentChunk / upload.totalChunks) * 100);
            upload.retryCount = 0; // Reset retry count on success

            this.updateUploadProgress(uploadId);
            this.saveUploadsToStorage();

            // Upload next chunk
            setTimeout(() => this.uploadNextChunk(uploadId), 10);

        } catch (error) {
            console.error(`Failed to upload chunk ${upload.currentChunk}:`, error);

            // Retry logic
            if (upload.retryCount < this.MAX_RETRIES) {
                upload.retryCount++;
                upload.status = 'retrying';
                upload.error = `Retrying... (${upload.retryCount}/${this.MAX_RETRIES})`;
                this.updateWidget();

                console.log(`Retrying chunk ${upload.currentChunk}, attempt ${upload.retryCount}`);
                setTimeout(() => {
                    upload.status = 'uploading';
                    this.uploadNextChunk(uploadId);
                }, this.RETRY_DELAY * upload.retryCount);
            } else {
                // Max retries exceeded, pause upload
                upload.status = 'paused';
                upload.error = 'Network error. Click Resume to continue.';
                this.updateWidget();
                this.saveUploadsToStorage();
            }
        }
    }

    async completeUpload(uploadId) {
        const upload = this.uploads.get(uploadId);
        if (!upload) return;

        try {
            upload.status = 'completing';
            upload.error = 'Finalizing upload...';
            this.updateWidget();

            // Convert cover image to base64 if provided
            let coverImageBase64 = null;
            if (upload.coverImage) {
                coverImageBase64 = await this.fileToBase64(upload.coverImage);
            }

            const token = localStorage.getItem('admin_token');
            const response = await fetch('http://localhost:5000/api/chunked-upload/complete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    uploadId: upload.sessionId,
                    coverImage: coverImageBase64
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to complete upload');
            }

            upload.status = 'completed';
            upload.progress = 100;
            upload.completedAt = Date.now();
            upload.error = null;
            this.updateWidget();
            this.saveUploadsToStorage();

            if (upload.onComplete) {
                upload.onComplete(data);
            }

            // Remove from widget after 5 seconds
            setTimeout(() => {
                this.removeUpload(uploadId);
            }, 5000);

        } catch (error) {
            console.error('Failed to complete upload:', error);
            upload.status = 'error';
            upload.error = error.message;
            this.updateWidget();

            if (upload.onError) {
                upload.onError(error);
            }
        }
    }

    async resumeUpload(uploadId) {
        const upload = this.uploads.get(uploadId);
        if (!upload || upload.status !== 'paused') return;

        try {
            // Check upload status on server
            const token = localStorage.getItem('admin_token');
            const response = await fetch(`http://localhost:5000/api/chunked-upload/status/${upload.sessionId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            const data = await response.json();

            if (response.ok) {
                // Update with server state
                upload.uploadedChunks = data.uploadedChunks;
                upload.currentChunk = data.uploadedChunks.length;
                upload.progress = data.progress;
                upload.status = 'uploading';
                upload.retryCount = 0;
                upload.error = null;

                this.updateWidget();
                this.saveUploadsToStorage();

                // Resume uploading
                await this.uploadNextChunk(uploadId);
            } else {
                throw new Error('Upload session not found on server');
            }

        } catch (error) {
            console.error('Failed to resume upload:', error);
            upload.error = 'Failed to resume. Try restarting upload.';
            this.updateWidget();
        }
    }

    async cancelUpload(uploadId) {
        const upload = this.uploads.get(uploadId);
        if (!upload) return;

        try {
            if (upload.sessionId) {
                const token = localStorage.getItem('admin_token');
                await fetch(`http://localhost:5000/api/chunked-upload/cancel/${upload.sessionId}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
            }
        } catch (error) {
            console.error('Failed to cancel upload on server:', error);
        }

        this.removeUpload(uploadId);
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
                statusEl.innerHTML = this.getStatusBadge(upload);
            }
        }

        this.saveUploadsToStorage();
    }

    getStatusBadge(upload) {
        switch (upload.status) {
            case 'initializing':
                return '<span class="badge badge-info">Initializing...</span>';
            case 'uploading':
                return '<span class="badge badge-info">Uploading...</span>';
            case 'retrying':
                return '<span class="badge badge-warning">Retrying...</span>';
            case 'paused':
                return '<span class="badge badge-warning">⏸ Paused</span>';
            case 'completing':
                return '<span class="badge badge-info">Finalizing...</span>';
            case 'completed':
                return '<span class="badge badge-success">✓ Completed</span>';
            case 'error':
                return `<span class="badge badge-danger">✗ Error</span>`;
            default:
                return '<span class="badge">Unknown</span>';
        }
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

            const actionButtons = upload.status === 'paused'
                ? `<button class="btn-success btn-small" onclick="chunkedUploadManager.resumeUpload('${upload.id}')">Resume</button>
                   <button class="btn-danger btn-small" onclick="chunkedUploadManager.cancelUpload('${upload.id}')">Cancel</button>`
                : upload.status === 'uploading' || upload.status === 'retrying'
                    ? `<button class="btn-danger btn-small" onclick="chunkedUploadManager.cancelUpload('${upload.id}')">Cancel</button>`
                    : upload.status === 'completed'
                        ? `<button class="btn-secondary btn-small" onclick="chunkedUploadManager.removeUpload('${upload.id}')">Remove</button>`
                        : `<button class="btn-secondary btn-small" onclick="chunkedUploadManager.removeUpload('${upload.id}')">Remove</button>`;

            uploadEl.innerHTML = `
                <div class="upload-item-header">
                    <div class="upload-file-name">${upload.fileName}</div>
                    <div class="upload-status">${this.getStatusBadge(upload)}</div>
                </div>
                <div class="upload-progress">
                    <div class="upload-progress-bar" style="width: ${upload.progress}%"></div>
                </div>
                <div class="upload-item-footer">
                    <div class="upload-progress-text">${Math.round(upload.progress)}%</div>
                    <div class="upload-file-size">${this.formatFileSize(upload.fileSize)}</div>
                    <div class="upload-actions">${actionButtons}</div>
                </div>
                ${upload.error ? `<div class="upload-error">${upload.error}</div>` : ''}
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

    async fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    hasActiveUploads() {
        return Array.from(this.uploads.values()).some(
            u => u.status === 'uploading' || u.status === 'initializing' || u.status === 'retrying'
        );
    }

    async syncWithServer() {
        try {
            const token = localStorage.getItem('admin_token');
            if (!token) return;

            const response = await fetch('http://localhost:5000/api/chunked-upload/active', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const activeUploads = await response.json();
                let updated = false;

                activeUploads.forEach(serverUpload => {
                    // If we don't have this upload locally, add it
                    if (!this.uploads.has(serverUpload.id)) {
                        const upload = {
                            id: serverUpload.id,
                            sessionId: serverUpload.id, // Same as ID for recovered uploads
                            fileName: serverUpload.fileName,
                            fileSize: serverUpload.fileSize,
                            totalChunks: serverUpload.totalChunks,
                            uploadedChunks: [], // Will be filled on resume
                            currentChunk: serverUpload.uploadedChunks,
                            progress: Math.floor(serverUpload.progress),
                            status: 'paused', // Recovered uploads start as paused
                            gameData: serverUpload.gameData,
                            retryCount: 0,
                            error: 'Session recovered. Click Resume to continue.'
                        };

                        this.uploads.set(upload.id, upload);
                        updated = true;
                    }
                });

                if (updated) {
                    this.updateWidget();
                    this.saveUploadsToStorage();
                }
            }
        } catch (error) {
            console.error('Failed to sync with server:', error);
        }
    }
}

// Create global instance
const chunkedUploadManager = new ChunkedUploadManager();
