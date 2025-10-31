/**
 * SkillHub Dashboard JavaScript
 * Handles interactive elements and data visualization for the dashboard
 */

// Global variables
let map, marker;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard JS loaded');
    
    if (!window.dashboardConfig) {
        console.error('Dashboard configuration not found!');
        return;
    }
    
    // Initialize based on user type
    if (window.dashboardConfig.userType === 'professional') {
        initProfessionalDashboard();
    } else {
        initClientDashboard();
    }
});

function initProfessionalDashboard() {
    console.log('Initializing professional dashboard');
    
    const jobsMap = initMap('jobs-map', [-1.286389, 36.817223], 10);
    const refreshBtn = document.getElementById('refresh-jobs');
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => loadJobs(jobsMap));
    }
    
    // Load initial jobs
    if (window.dashboardConfig.initialJobs && window.dashboardConfig.initialJobs.length > 0) {
        updateJobList(window.dashboardConfig.initialJobs);
        updateJobMarkers(jobsMap, window.dashboardConfig.initialJobs);
    } else {
        loadJobs(jobsMap);
    }
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => loadJobs(jobsMap));
    }
}

// Client Dashboard Functions  
function initClientDashboard() {
    const mapElement = document.getElementById('map');
    if (!mapElement) {
        console.error('Map element not found');
        return;
    }
    
    const map = initMap('map', [-1.286389, 36.817223], 10);
    const locationSearch = document.getElementById('location-search');
    const latInput = document.getElementById('latitude');
    const lngInput = document.getElementById('longitude');

    // Use current location if available
    const useCurrentBtn = document.getElementById('use-current-location');
    if (useCurrentBtn && navigator.geolocation) {
        useCurrentBtn.addEventListener('click', () => {
            useCurrentBtn.disabled = true;
            useCurrentBtn.innerHTML = '<i class="bi bi-geo"></i> Getting Location...';
            
            navigator.geolocation.getCurrentPosition(
                pos => {
                    const { latitude, longitude } = pos.coords;
                    updateMarker(map, [latitude, longitude]);
                    updateAddress(latitude, longitude, locationSearch);
                    map.setView([latitude, longitude], 15);
                    
                    useCurrentBtn.disabled = false;
                    useCurrentBtn.innerHTML = '<i class="bi bi-geo"></i> Use My Location';
                },
                error => {
                    console.error('Error getting location:', error);
                    let errorMsg = 'Unable to get your location. ';
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMsg += 'Please enable location permissions in your browser.';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMsg += 'Location information is unavailable.';
                            break;
                        case error.TIMEOUT:
                            errorMsg += 'Location request timed out.';
                            break;
                    }
                    showAlert(errorMsg, 'warning');
                    
                    useCurrentBtn.disabled = false;
                    useCurrentBtn.innerHTML = '<i class="bi bi-geo"></i> Use My Location';
                },
                { timeout: 10000 }
            );
        });
    }

    // Map click handler
    map.on('click', e => {
        updateMarker(map, [e.latlng.lat, e.latlng.lng]);
        updateAddress(e.latlng.lat, e.latlng.lng, locationSearch);
    });

    // Search functionality
    if (locationSearch) {
        locationSearch.addEventListener('keypress', e => {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchLocation(locationSearch.value, map);
            }
        });
    }

    // Initialize form
    initJobForm();
}

// Map Utility Functions
function initMap(elementId, center, zoom = 13) {
    const mapElement = document.getElementById(elementId);
    if (!mapElement) {
        console.error(`Map element #${elementId} not found`);
        return null;
    }
    
    const map = L.map(elementId).setView(center, zoom);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);
    
    return map;
}

function updateMarker(map, latlng) {
    if (marker) {
        marker.setLatLng(latlng);
    } else {
        marker = L.marker(latlng).addTo(map);
    }
    
    // Update hidden inputs
    const latInput = document.getElementById('latitude');
    const lngInput = document.getElementById('longitude');
    if (latInput) latInput.value = latlng[0];
    if (lngInput) lngInput.value = latlng[1];
}

async function updateAddress(lat, lng, locationSearch) {
    if (!locationSearch) return;
    
    try {
        const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`
        );
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json();
        if (data.display_name) {
            locationSearch.value = data.display_name;
        }
    } catch (error) {
        console.error('Error getting address:', error);
        locationSearch.value = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    }
}

async function searchLocation(query, map) {
    if (!query.trim() || !map) return;
    
    try {
        const response = await fetch(
            `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`
        );
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json();
        if (data && data[0]) {
            const lat = parseFloat(data[0].lat);
            const lng = parseFloat(data[0].lon);
            
            updateMarker(map, [lat, lng]);
            updateAddress(lat, lng, document.getElementById('location-search'));
            map.setView([lat, lng], 15);
        } else {
            showAlert('Location not found. Please try a different search term.', 'warning');
        }
    } catch (error) {
        console.error('Error searching location:', error);
        showAlert('Error searching for location. Please try again.', 'danger');
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
        const response = await fetch(window.dashboardConfig.jobsApiUrl, {
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const jobs = await response.json();
        updateJobList(jobs);
        updateJobMarkers(map, jobs);
        
    } catch (error) {
        console.error('Error loading jobs:', error);
        jobList.innerHTML = `
            <div class="alert alert-danger m-3">
                <i class="bi bi-exclamation-triangle"></i>
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
                <small class="text-muted">Check back later for new opportunities</small>
            </div>
        `;
        return;
    }
    
    jobList.innerHTML = jobs.map(job => `
        <div class="list-group-item list-group-item-action job-item" 
             data-job-id="${job.id}"
             data-lat="${job.latitude}" 
             data-lng="${job.longitude}">
            <div class="d-flex w-100 justify-content-between align-items-start">
                <h6 class="mb-1 job-title">${escapeHtml(job.title)}</h6>
                <small class="text-muted">${formatDate(job.created_at)}</small>
            </div>
            <p class="mb-2 job-description">${escapeHtml(job.description || 'No description provided')}</p>
            <div class="d-flex justify-content-between align-items-center">
                <span class="badge bg-primary">${escapeHtml(job.profession)}</span>
                <strong class="text-success">Ksh ${job.budget ? job.budget.toLocaleString() : 'Negotiable'}</strong>
            </div>
            <div class="mt-2">
                <small class="text-muted job-location">
                    <i class="bi bi-geo-alt"></i> ${escapeHtml(job.location || 'Location not specified')}
                </small>
            </div>
            <div class="mt-2">
                <button class="btn btn-sm btn-outline-primary view-job-btn" data-job-id="${job.id}">
                    <i class="bi bi-eye"></i> View Details
                </button>
                <button class="btn btn-sm btn-success apply-job-btn" data-job-id="${job.id}">
                    <i class="bi bi-check-circle"></i> Apply
                </button>
            </div>
        </div>
    `).join('');
    
    // Add event listeners to new buttons
    document.querySelectorAll('.view-job-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const jobId = btn.getAttribute('data-job-id');
            viewJobDetails(jobId);
        });
    });
    
    document.querySelectorAll('.apply-job-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const jobId = btn.getAttribute('data-job-id');
            applyForJob(jobId);
        });
    });
    
    // Add click event to job items
    document.querySelectorAll('.job-item').forEach(item => {
        item.addEventListener('click', function() {
            const lat = this.getAttribute('data-lat');
            const lng = this.getAttribute('data-lng');
            if (lat && lng) {
                focusOnJob(parseFloat(lat), parseFloat(lng));
            }
        });
    });
}

function updateJobMarkers(map, jobs) {
    if (!map) return;
    
    // Clear existing markers
    map.eachLayer(layer => {
        if (layer instanceof L.Marker) {
            map.removeLayer(layer);
        }
    });
    
    const bounds = L.latLngBounds();
    let hasValidMarkers = false;
    
    // Add new markers
    jobs.forEach(job => {
        if (job.latitude && job.longitude) {
            const marker = L.marker([job.latitude, job.longitude]).addTo(map);
            bounds.extend([job.latitude, job.longitude]);
            hasValidMarkers = true;
            
            marker.bindPopup(`
                <div class="job-popup">
                    <h6>${escapeHtml(job.title)}</h6>
                    <p class="mb-1"><strong>Profession:</strong> ${escapeHtml(job.profession)}</p>
                    <p class="mb-1"><strong>Budget:</strong> Ksh ${job.budget ? job.budget.toLocaleString() : 'Negotiable'}</p>
                    <p class="mb-2"><strong>Location:</strong> ${escapeHtml(job.location || 'Not specified')}</p>
                    <div class="d-grid gap-1">
                        <button class="btn btn-sm btn-primary view-details-btn" data-job-id="${job.id}">
                            View Details
                        </button>
                        <button class="btn btn-sm btn-success apply-btn" data-job-id="${job.id}">
                            Apply Now
                        </button>
                    </div>
                </div>
            `);
            
            // Add event listeners to popup buttons
            marker.on('popupopen', function() {
                const popup = marker.getPopup();
                const popupElement = popup.getElement();
                
                popupElement.querySelector('.view-details-btn').addEventListener('click', function() {
                    const jobId = this.getAttribute('data-job-id');
                    viewJobDetails(jobId);
                });
                
                popupElement.querySelector('.apply-btn').addEventListener('click', function() {
                    const jobId = this.getAttribute('data-job-id');
                    applyForJob(jobId);
                });
            });
        }
    });
    
    // Fit bounds to show all markers
    if (hasValidMarkers) {
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
        
        // Validate required fields
        const title = form.querySelector('#title').value.trim();
        const description = form.querySelector('#description').value.trim();
        const latInput = document.getElementById('latitude');
        const lngInput = document.getElementById('longitude');
        
        if (!title) {
            showAlert('Please enter a job title.', 'warning');
            form.querySelector('#title').focus();
            return;
        }
        
        if (!description) {
            showAlert('Please enter a job description.', 'warning');
            form.querySelector('#description').focus();
            return;
        }
        
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
                
                // Reset map marker
                if (marker) {
                    marker.remove();
                    marker = null;
                }
                
                // Reset location fields
                if (latInput) latInput.value = '';
                if (lngInput) lngInput.value = '';
                if (locationSearch) locationSearch.value = '';
                
            } else {
                throw new Error(data.message || 'Failed to post job');
            }
            
        } catch (error) {
            console.error('Error submitting form:', error);
            showAlert(error.message || 'An error occurred. Please try again.', 'danger');
        } finally {
            submitBtn.disabled = false;
            spinner.classList.add('d-none');
            submitIcon.classList.remove('d-none');
        }
    });
}

// Job Actions
function viewJobDetails(jobId) {
    // In a real app, this would show a modal or navigate to job details
    console.log('Viewing job details for:', jobId);
    showAlert(`Viewing details for job #${jobId}`, 'info');
}

function applyForJob(jobId) {
    // In a real app, this would submit an application
    console.log('Applying for job:', jobId);
    showAlert(`Application submitted for job #${jobId}`, 'success');
}

// Utility Functions
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function formatDate(dateString) {
    if (!dateString) return 'Recently';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffMinutes = Math.floor(diffTime / (1000 * 60));
    const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} week${Math.ceil(diffDays / 7) > 1 ? 's' : ''} ago`;
    return date.toLocaleDateString();
}

function showAlert(message, type) {
    // Remove existing alerts
    document.querySelectorAll('.alert-dismissible').forEach(alert => {
        if (alert.parentElement) alert.remove();
    });
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="bi bi-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentElement) {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }
    }, 5000);
}

function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Global function for job focus
window.focusOnJob = function(lat, lng) {
    const mapElement = document.getElementById('jobs-map');
    if (mapElement && mapElement._leaflet_map) {
        const map = mapElement._leaflet_map;
        map.setView([lat, lng], 15);
        
        // Find and open the marker's popup
        map.eachLayer(layer => {
            if (layer instanceof L.Marker) {
                const markerLatLng = layer.getLatLng();
                if (Math.abs(markerLatLng.lat - lat) < 0.0001 && Math.abs(markerLatLng.lng - lng) < 0.0001) {
                    layer.openPopup();
                }
            }
        });
    }
};