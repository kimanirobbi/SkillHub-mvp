// Global variables
let map, marker;

// Initialize when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(function(el) {
        new bootstrap.Tooltip(el);
    });

    // Initialize based on user type
    if (document.body.classList.contains('professional-dashboard')) {
        initProfessionalDashboard();
    } else if (document.body.classList.contains('client-dashboard')) {
        initClientDashboard();
    }
});

// Professional Dashboard Functions
function initProfessionalDashboard() {
    const jobsMap = initMap('jobs-map', [-1.286389, 36.817223], 13);
    const refreshBtn = document.getElementById('refresh-jobs');
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => loadJobs(jobsMap));
        loadJobs(jobsMap); // Initial load
    }
}

// Client Dashboard Functions
function initClientDashboard() {
    const map = initMap('map', [-1.286389, 36.817223], 13);
    const locationSearch = document.getElementById('location-search');
    const latInput = document.getElementById('latitude');
    const lngInput = document.getElementById('longitude');
    let marker = null;

    // Use current location if available
    if (navigator.geolocation) {
        const currentLocationBtn = document.getElementById('use-current-location');
        if (currentLocationBtn) {
            currentLocationBtn.addEventListener('click', () => {
                navigator.geolocation.getCurrentPosition(pos => {
                    const { latitude, longitude } = pos.coords;
                    updateMarker(map, [latitude, longitude]);
                    updateAddress(latitude, longitude, locationSearch);
                    map.setView([latitude, longitude], 15);
                });
            });
        }
    }

    // Map click handler
    map.on('click', e => {
        updateMarker(map, [e.latlng.lat, e.latlng.lng]);
        updateAddress(e.latlng.lat, e.latlng.lng, locationSearch);
    });

    // Initialize form handling
    initJobForm();
}

// Map Utility Functions
function initMap(elementId, center, zoom = 13) {
    const map = L.map(elementId).setView(center, zoom);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    return map;
}

function updateMarker(map, latlng) {
    if (window.marker) {
        window.marker.setLatLng(latlng);
    } else {
        window.marker = L.marker(latlng).addTo(map);
    }
    
    const latInput = document.getElementById('latitude');
    const lngInput = document.getElementById('longitude');
    
    if (latInput && lngInput) {
        latInput.value = latlng[0];
        lngInput.value = latlng[1];
    }
    
    map.setView(latlng, 15);
}

async function updateAddress(lat, lng, locationSearch) {
    if (!locationSearch) return;
    
    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`);
        const data = await response.json();
        
        if (data.display_name) {
            locationSearch.value = data.display_name;
        }
    } catch (error) {
        console.error('Error updating address:', error);
    }
}

// Job Management Functions
async function loadJobs(map) {
    const jobList = document.getElementById('job-list');
    const refreshBtn = document.getElementById('refresh-jobs');
    
    if (!jobList) return;
    
    // Show loading state
    jobList.innerHTML = `
        <div class="text-center p-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 mb-0">Loading available jobs...</p>
        </div>
    `;
    
    if (refreshBtn) {
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Loading...';
    }
    
    try {
        const response = await fetch(window.jobsApiUrl || '/api/jobs');
        const jobs = await response.json();
        
        updateJobList(jobs);
        updateJobMarkers(map, jobs);
        
    } catch (error) {
        console.error('Error loading jobs:', error);
        jobList.innerHTML = `
            <div class="alert alert-danger m-3">
                Failed to load jobs. Please try again later.
            </div>
        `;
    } finally {
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refresh';
        }
    }
}

function updateJobList(jobs) {
    const jobList = document.getElementById('job-list');
    if (!jobList) return;
    
    if (!jobs || jobs.length === 0) {
        jobList.innerHTML = `
            <div class="text-center p-4">
                <i class="bi bi-inbox text-muted" style="font-size: 2.5rem;"></i>
                <p class="mt-2 mb-0 text-muted">No jobs available at the moment</p>
            </div>
        `;
        return;
    }
    
    jobList.innerHTML = jobs.map(job => `
        <div class="list-group-item list-group-item-action job-item" 
             data-lat="${job.latitude}" 
             data-lng="${job.longitude}"
             onclick="focusOnJob(${job.latitude}, ${job.longitude})">
            <div class="d-flex w-100 justify-content-between">
                <h6 class="mb-1 job-title">${escapeHtml(job.title)}</h6>
                <small class="text-muted">${formatDate(job.created_at)}</small>
            </div>
            <p class="mb-1 job-description">${escapeHtml(job.description || 'No description provided')}</p>
            <div class="d-flex justify-content-between align-items-center">
                <span class="badge badge-profession">${escapeHtml(job.profession)}</span>
                <strong>Ksh ${job.budget ? job.budget.toLocaleString() : '0'}</strong>
            </div>
            <small class="text-muted job-location">
                <i class="bi bi-geo-alt"></i> ${escapeHtml(job.location || 'Location not specified')}
            </small>
        </div>
    `).join('');
}

function updateJobMarkers(map, jobs) {
    if (!map) return;
    
    // Clear existing markers
    map.eachLayer(layer => {
        if (layer instanceof L.Marker) {
            map.removeLayer(layer);
        }
    });
    
    // Add new markers
    jobs.forEach(job => {
        if (job.latitude && job.longitude) {
            const marker = L.marker([job.latitude, job.longitude]).addTo(map);
            marker.bindPopup(`
                <b>${escapeHtml(job.title)}</b><br>
                ${escapeHtml(job.profession)}<br>
                <small>${escapeHtml(job.location)}</small><br>
                <strong>Ksh ${job.budget ? job.budget.toLocaleString() : '0'}</strong>
            `);
        }
    });
    
    // Fit bounds to show all markers
    if (jobs.length > 0 && jobs.some(job => job.latitude && job.longitude)) {
        const bounds = L.latLngBounds(jobs.filter(job => job.latitude && job.longitude)
            .map(job => [job.latitude, job.longitude]));
        map.fitBounds(bounds, { padding: [20, 20] });
    }
}

// Form Handling
function initJobForm() {
    const form = document.getElementById('job-form');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const submitBtn = this.querySelector('#submit-btn');
        const spinner = submitBtn.querySelector('.spinner-border');
        const submitIcon = submitBtn.querySelector('.bi-send-check');
        
        // Validate location
        const latInput = document.getElementById('latitude');
        const lngInput = document.getElementById('longitude');
        
        if (!latInput.value || !lngInput.value) {
            showAlert('Please select a location on the map.', 'warning');
            return;
        }
        
        // Show loading state
        submitBtn.disabled = true;
        spinner.classList.remove('d-none');
        submitIcon.classList.add('d-none');
        
        try {
            const formData = new FormData(this);
            
            const response = await fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                showAlert(data.message || 'Job posted successfully!', 'success');
                this.reset();
                
                // Reset map if needed
                if (window.marker) {
                    window.marker.remove();
                    window.marker = null;
                }
                
            } else {
                throw new Error(data.message || 'Failed to post job');
            }
            
        } catch (error) {
            console.error('Error submitting form:', error);
            showAlert(error.message || 'An error occurred. Please try again.', 'danger');
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            spinner.classList.add('d-none');
            submitIcon.classList.remove('d-none');
        }
    });
}

// Utility Functions
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (isNaN(diffDays)) return '';
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
    return date.toLocaleDateString();
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentElement) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Global function for job focus
window.focusOnJob = function(lat, lng) {
    const mapElement = document.getElementById('jobs-map');
    if (mapElement && mapElement._leaflet_map) {
        const map = mapElement._leaflet_map;
        map.setView([lat, lng], 15);
        
        // Open popup if marker exists
        map.eachLayer(layer => {
            if (layer instanceof L.Marker) {
                const markerLatLng = layer.getLatLng();
                if (markerLatLng.lat === lat && markerLatLng.lng === lng) {
                    layer.openPopup();
                }
            }
        });
    }
};
