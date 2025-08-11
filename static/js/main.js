// Inspora - Main JavaScript File

class InsporaApp {
    constructor() {
        this.initialize();
    }

    initialize() {
        this.setupEventListeners();
        this.initializeWebSockets();
        this.setupTooltips();
        this.setupModals();
        this.setupNotifications();
    }

    setupEventListeners() {
        // Sidebar toggle for mobile
        const sidebarToggle = document.querySelector('.sidebar-toggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                document.body.classList.toggle('sidebar-open');
            });
        }

        // Form validation
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });

        // Auto-save forms
        this.setupAutoSave();
    }

    initializeWebSockets() {
        // Initialize WebSocket connections for real-time updates
        if (typeof WebSocket !== 'undefined') {
            this.setupNotificationWebSocket();
            this.setupProjectWebSocket();
        }
    }

    setupNotificationWebSocket() {
        const notificationSocket = new WebSocket(
            `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/notifications/`
        );

        notificationSocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'notification') {
                this.showNotification(data.message, data.notification_id);
            }
        };

        notificationSocket.onclose = () => {
            console.log('Notification WebSocket connection closed');
            // Attempt to reconnect after 5 seconds
            setTimeout(() => this.setupNotificationWebSocket(), 5000);
        };
    }

    setupProjectWebSocket() {
        // Project-specific WebSocket connections
        const projectElements = document.querySelectorAll('[data-project-id]');
        projectElements.forEach(element => {
            const projectId = element.dataset.projectId;
            this.connectToProject(projectId);
        });
    }

    connectToProject(projectId) {
        const projectSocket = new WebSocket(
            `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/projects/${projectId}/`
        );

        projectSocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'project_message') {
                this.handleProjectUpdate(data);
            }
        };
    }

    setupTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    setupModals() {
        // Initialize Bootstrap modals
        const modalTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="modal"]'));
        modalTriggerList.map(function (modalTriggerEl) {
            return new bootstrap.Modal(modalTriggerEl);
        });
    }

    setupNotifications() {
        // Check if browser supports notifications
        if ('Notification' in window) {
            if (Notification.permission === 'default') {
                Notification.requestPermission();
            }
        }
    }

    setupAutoSave() {
        // Auto-save form data
        const autoSaveForms = document.querySelectorAll('.auto-save');
        autoSaveForms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('change', () => {
                    this.autoSaveForm(form);
                });
            });
        });
    }

    autoSaveForm(form) {
        const formData = new FormData(form);
        const url = form.action || window.location.pathname;
        
        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showToast('Form auto-saved successfully', 'success');
            }
        })
        .catch(error => {
            console.error('Auto-save failed:', error);
        });
    }

    showNotification(message, notificationId) {
        // Show in-app notification
        const notification = document.createElement('div');
        notification.className = 'alert alert-info alert-dismissible fade show';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.messages') || document.querySelector('main');
        container.insertBefore(notification, container.firstChild);

        // Show browser notification if permitted
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Inspora', { body: message });
        }

        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    showToast(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        const toastContainer = document.querySelector('.toast-container') || this.createToastContainer();
        toastContainer.appendChild(toast);

        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
        return container;
    }

    handleProjectUpdate(data) {
        // Handle real-time project updates
        console.log('Project update received:', data);
        
        // Update UI elements based on the update
        this.updateProjectUI(data);
    }

    updateProjectUI(data) {
        // Update project progress, task counts, etc.
        const projectElement = document.querySelector(`[data-project-id="${data.project_id}"]`);
        if (projectElement) {
            // Update specific project elements
            this.updateProjectProgress(projectElement, data);
        }
    }

    updateProjectProgress(projectElement, data) {
        const progressBar = projectElement.querySelector('.progress-bar');
        if (progressBar && data.progress !== undefined) {
            progressBar.style.width = `${data.progress}%`;
            progressBar.textContent = `${data.progress}%`;
        }
    }

    getCSRFToken() {
        // Get CSRF token from cookie or meta tag
        const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
                     document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
        return token;
    }

    // Utility methods
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString();
    }

    formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString();
    }

    formatDuration(minutes) {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        if (hours > 0) {
            return `${hours}h ${mins}m`;
        }
        return `${mins}m`;
    }

    debounce(func, wait) {
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

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.insporaApp = new InsporaApp();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = InsporaApp;
}
