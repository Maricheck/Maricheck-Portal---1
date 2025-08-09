// Maricheck JavaScript - Maritime Crew Management System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap is loaded
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert && alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
    
    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            // Add loading state to submit buttons
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML || submitBtn.value;
                if (submitBtn.tagName === 'BUTTON') {
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                } else {
                    submitBtn.value = 'Processing...';
                }
                submitBtn.disabled = true;
                
                // Re-enable after 10 seconds as fallback
                setTimeout(function() {
                    if (submitBtn.tagName === 'BUTTON') {
                        submitBtn.innerHTML = originalText;
                    } else {
                        submitBtn.value = originalText;
                    }
                    submitBtn.disabled = false;
                }, 10000);
            }
        });
    });
    
    // File upload preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(event) {
            const file = event.target.files[0];
            const label = input.closest('.form-group, .col-md-6')?.querySelector('.form-label');
            
            if (file && label) {
                // Create or update file info
                let fileInfo = label.parentNode.querySelector('.file-info');
                if (!fileInfo) {
                    fileInfo = document.createElement('small');
                    fileInfo.className = 'file-info text-success d-block mt-1';
                    label.parentNode.appendChild(fileInfo);
                }
                
                const fileSize = (file.size / 1024 / 1024).toFixed(2);
                fileInfo.innerHTML = `<i class="fas fa-check-circle me-1"></i>Selected: ${file.name} (${fileSize} MB)`;
            }
        });
    });
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(event) {
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                event.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Enhanced table functionality
    const tables = document.querySelectorAll('.table-responsive table');
    tables.forEach(function(table) {
        // Add click handler for rows with data-href
        const rows = table.querySelectorAll('tbody tr[data-href]');
        rows.forEach(function(row) {
            row.style.cursor = 'pointer';
            row.addEventListener('click', function(event) {
                // Don't navigate if clicking on buttons or inputs
                if (!event.target.closest('button, a, input')) {
                    window.location.href = row.dataset.href;
                }
            });
        });
    });
    
    // Search form auto-submit with debounce
    const searchInputs = document.querySelectorAll('input[name="search"]');
    searchInputs.forEach(function(input) {
        let timeout;
        input.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(function() {
                if (input.value.length >= 3 || input.value.length === 0) {
                    const form = input.closest('form');
                    if (form) {
                        // Submit form programmatically
                        form.submit();
                    }
                }
            }, 500);
        });
    });
    
    // Progress bar animations
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(function(bar) {
        const width = bar.style.width || bar.getAttribute('aria-valuenow') + '%';
        bar.style.width = '0%';
        setTimeout(function() {
            bar.style.transition = 'width 1s ease-in-out';
            bar.style.width = width;
        }, 100);
    });
    
    // Status badge click handler (for filtering)
    const statusBadges = document.querySelectorAll('.badge[data-status]');
    statusBadges.forEach(function(badge) {
        badge.style.cursor = 'pointer';
        badge.addEventListener('click', function() {
            const status = badge.dataset.status;
            const currentUrl = new URL(window.location);
            currentUrl.searchParams.set('status', status);
            window.location.href = currentUrl.toString();
        });
    });
});

// Global utility functions
window.MaricheckUtils = {
    // Copy text to clipboard
    copyToClipboard: function(text, successCallback, errorCallback) {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(function() {
                if (successCallback) successCallback();
            }).catch(function(err) {
                if (errorCallback) errorCallback(err);
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {
                document.execCommand('copy');
                if (successCallback) successCallback();
            } catch (err) {
                if (errorCallback) errorCallback(err);
            } finally {
                document.body.removeChild(textArea);
            }
        }
    },
    
    // Show toast notification
    showToast: function(message, type = 'info') {
        const toastContainer = document.querySelector('.toast-container') || this.createToastContainer();
        const toast = this.createToast(message, type);
        toastContainer.appendChild(toast);
        
        if (typeof bootstrap !== 'undefined') {
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
        }
        
        // Auto remove after 5 seconds
        setTimeout(function() {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    },
    
    createToastContainer: function() {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    },
    
    createToast: function(message, type) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.setAttribute('role', 'alert');
        
        const iconMap = {
            success: 'fa-check-circle text-success',
            error: 'fa-exclamation-circle text-danger',
            warning: 'fa-exclamation-triangle text-warning',
            info: 'fa-info-circle text-info'
        };
        
        const icon = iconMap[type] || iconMap.info;
        
        toast.innerHTML = `
            <div class="toast-header">
                <i class="fas ${icon} me-2"></i>
                <strong class="me-auto">Maricheck</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        return toast;
    },
    
    // Format file size
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    // Validate file type
    validateFileType: function(file, allowedTypes) {
        const fileExtension = file.name.split('.').pop().toLowerCase();
        return allowedTypes.includes(fileExtension);
    },
    
    // Confirm dialog
    confirmAction: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    }
};

// Copy profile URL function (used in templates)
function copyProfileUrl(crewId) {
    const urlInput = document.getElementById('profileUrl' + (crewId || ''));
    if (!urlInput) return;
    
    MaricheckUtils.copyToClipboard(urlInput.value, 
        function() {
            // Success callback
            const btn = event.target.closest('button');
            if (btn) {
                const originalHTML = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-check"></i>';
                btn.classList.remove('btn-outline-secondary');
                btn.classList.add('btn-success');
                
                setTimeout(function() {
                    btn.innerHTML = originalHTML;
                    btn.classList.remove('btn-success');
                    btn.classList.add('btn-outline-secondary');
                }, 2000);
            }
            
            MaricheckUtils.showToast('Profile link copied to clipboard!', 'success');
        },
        function(err) {
            // Error callback
            console.error('Failed to copy: ', err);
            MaricheckUtils.showToast('Failed to copy link. Please try again.', 'error');
        }
    );
}

// Copy private URL function (used in admin templates)
function copyPrivateUrl() {
    const urlInput = document.getElementById('privateProfileUrl');
    if (!urlInput) return;
    
    MaricheckUtils.copyToClipboard(urlInput.value,
        function() {
            // Success callback
            const btn = event.target.closest('button');
            if (btn) {
                const originalHTML = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
                btn.classList.remove('btn-outline-sea-green');
                btn.classList.add('btn-success');
                
                setTimeout(function() {
                    btn.innerHTML = originalHTML;
                    btn.classList.remove('btn-success');
                    btn.classList.add('btn-outline-sea-green');
                }, 2000);
            }
            
            MaricheckUtils.showToast('Private profile link copied to clipboard!', 'success');
        },
        function(err) {
            // Error callback
            console.error('Failed to copy: ', err);
            MaricheckUtils.showToast('Failed to copy link. Please try again.', 'error');
        }
    );
}

// International phone input initialization (if library is loaded)
function initializePhoneInput(selector = '#phone') {
    if (typeof intlTelInput !== 'undefined') {
        const phoneInputField = document.querySelector(selector);
        if (phoneInputField) {
            const phoneInput = window.intlTelInput(phoneInputField, {
                initialCountry: "auto",
                geoIpLookup: function(callback) {
                    fetch('https://ipapi.co/json')
                        .then(function(res) { return res.json(); })
                        .then(function(data) { callback(data.country_code); })
                        .catch(function() { callback("in"); });
                },
                utilsScript: "https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/js/utils.js"
            });
            
            // Update the hidden input with the full number including country code
            phoneInputField.addEventListener('blur', function() {
                phoneInputField.value = phoneInput.getNumber();
            });
            
            return phoneInput;
        }
    }
    return null;
}

// File upload validation
function validateFileUpload(input, maxSize = 16) {
    const file = input.files[0];
    if (!file) return true;
    
    const maxSizeBytes = maxSize * 1024 * 1024; // Convert MB to bytes
    
    if (file.size > maxSizeBytes) {
        MaricheckUtils.showToast(`File size must be less than ${maxSize}MB`, 'error');
        input.value = '';
        return false;
    }
    
    return true;
}

// Admin table row selection
function toggleRowSelection(checkbox) {
    const row = checkbox.closest('tr');
    if (checkbox.checked) {
        row.classList.add('table-active');
    } else {
        row.classList.remove('table-active');
    }
    
    // Update bulk action buttons
    updateBulkActionButtons();
}

function updateBulkActionButtons() {
    const selectedCheckboxes = document.querySelectorAll('tbody input[type="checkbox"]:checked');
    const bulkActionButtons = document.querySelectorAll('.bulk-action-btn');
    
    bulkActionButtons.forEach(function(btn) {
        btn.disabled = selectedCheckboxes.length === 0;
    });
}

// Select all functionality
function toggleSelectAll(masterCheckbox) {
    const checkboxes = document.querySelectorAll('tbody input[type="checkbox"]');
    checkboxes.forEach(function(checkbox) {
        checkbox.checked = masterCheckbox.checked;
        toggleRowSelection(checkbox);
    });
}

// Export functionality
function exportData(format, type) {
    const selectedRows = document.querySelectorAll('tbody input[type="checkbox"]:checked');
    const ids = Array.from(selectedRows).map(cb => cb.value);
    
    let url = `/admin/${type}/export`;
    if (format === 'csv') {
        url += '?format=csv';
    }
    
    if (ids.length > 0) {
        url += (url.includes('?') ? '&' : '?') + 'ids=' + ids.join(',');
    }
    
    window.location.href = url;
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + K for search
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.querySelector('input[name="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to clear search
    if (event.key === 'Escape') {
        const searchInput = document.querySelector('input[name="search"]');
        if (searchInput && searchInput === document.activeElement) {
            searchInput.value = '';
            searchInput.blur();
        }
    }
});
