// Main JavaScript file for Dispute Analysis Tool

// Store session ID
let sessionId = '';

// Document Ready Function
document.addEventListener('DOMContentLoaded', function() {
    // Set up file input event listeners
    setupFileInputs();
    
    // Setup form submission
    setupFormSubmission();
    
    // Check if we're on analyzer page
    if (window.location.pathname.includes('analyzer')) {
        // Get session ID from URL or localStorage
        const urlParams = new URLSearchParams(window.location.search);
        sessionId = urlParams.get('sessionId') || localStorage.getItem('sessionId');
        
        if (sessionId) {
            loadFilterOptions();
        } else {
            showAlert('No session found. Please upload files first.', 'danger');
            setTimeout(() => {
                window.location.href = '/';
            }, 3000);
        }
    }
});

// File Input Setup
function setupFileInputs() {
    const fileInputs = document.querySelectorAll('.file-input');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name || 'No file selected';
            const fileNameElement = e.target.parentElement.querySelector('.file-name');
            if (fileNameElement) {
                fileNameElement.textContent = fileName;
            }
        });
    });
}

// Form Submission
function setupFormSubmission() {
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const uploadBtn = document.getElementById('uploadBtn');
            uploadBtn.disabled = true;
            uploadBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uploading...';
            
            // Create FormData object
            const formData = new FormData(uploadForm);
            
            // Send AJAX request
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('Files uploaded successfully! Redirecting...', 'success');
                    sessionId = data.sessionId;
                    localStorage.setItem('sessionId', sessionId);
                    
                    // Redirect to analyzer after short delay
                    setTimeout(() => {
                        window.location.href = `/analyzer?sessionId=${sessionId}`;
                    }, 1500);
                } else {
                    showAlert(`Error: ${data.message}`, 'danger');
                    uploadBtn.disabled = false;
                    uploadBtn.innerHTML = '<i class="fas fa-upload me-2"></i> Upload and Continue';
                }
            })
            .catch(error => {
                showAlert(`Error: ${error.message}`, 'danger');
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = '<i class="fas fa-upload me-2"></i> Upload and Continue';
            });
        });
    }
}

// Load Filter Options for Analyzer
function loadFilterOptions() {
    showLoading(true);
    
    fetch(`/filter-options?sessionId=${sessionId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                populateFilters(data.filterOptions);
            } else {
                showAlert(`Error: ${data.message}`, 'danger');
            }
            showLoading(false);
        })
        .catch(error => {
            showAlert(`Error: ${error.message}`, 'danger');
            showLoading(false);
        });
}

// Populate Filter Dropdowns
function populateFilters(filterOptions) {
    // Markets
    const marketSelect = document.getElementById('market');
    if (marketSelect) {
        filterOptions.markets.forEach(market => {
            const option = document.createElement('option');
            option.value = market;
            option.textContent = market;
            marketSelect.appendChild(option);
        });
    }
    
    // Brands
    const brandSelect = document.getElementById('brand');
    if (brandSelect) {
        filterOptions.brands_pk.forEach(brand => {
            const option = document.createElement('option');
            option.value = brand;
            option.textContent = brand;
            brandSelect.appendChild(option);
        });
    }
    
    // Years
    const yearSelect = document.getElementById('year');
    if (yearSelect) {
        filterOptions.years.forEach(year => {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            yearSelect.appendChild(option);
        });
    }
    
    // Months
    const monthSelect = document.getElementById('month');
    if (monthSelect) {
        filterOptions.months.forEach(month => {
            const option = document.createElement('option');
            option.value = month;
            option.textContent = month;
            monthSelect.appendChild(option);
        });
    }
}

// Clear Filters
function clearFilters() {
    document.getElementById('market').value = '';
    document.getElementById('brand').value = '';
    document.getElementById('year').value = '';
    document.getElementById('month').value = '';
}

// Execute Analysis
function executeAnalysis() {
    const market = document.getElementById('market').value;
    const brand = document.getElementById('brand').value;
    const year = document.getElementById('year').value;
    const month = document.getElementById('month').value;
    
    // Validate inputs
    if (!market || !brand || !year || !month) {
        showAlert('Please select all filter options before running the analysis.', 'warning');
        return;
    }
    
    showLoading(true);
    
    // Prepare request data
    const requestData = {
        sessionId: sessionId,
        market: market,
        brand: brand,
        year: year,
        month: month
    };
    
    // Send AJAX request
    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayResults(data);
            document.getElementById('exportBtn').style.display = 'inline-block';
        } else {
            showAlert(`Error: ${data.error}`, 'danger');
            document.getElementById('noResultsMessage').style.display = 'block';
            document.getElementById('resultsSection').style.display = 'none';
        }
        showLoading(false);
    })
    .catch(error => {
        showAlert(`Error: ${error.message}`, 'danger');
        showLoading(false);
    });
}

// Display Analysis Results
function displayResults(data) {
    // Show results section
    document.getElementById('noResultsMessage').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';
    
    // Update summary stats
    document.getElementById('totalRecords').textContent = data.stats.total_records;
    document.getElementById('perfectMatches').textContent = data.stats.perfect_matches;
    document.getElementById('perfectMatchesPercent').textContent = `${data.stats.percent_matched.toFixed(1)}%`;
    document.getElementById('mismatches').textContent = data.stats.mismatches;
    document.getElementById('missingDeals').textContent = `${data.stats.missing_deals} Missing Deals`;
    document.getElementById('totalVariance').textContent = `$${data.stats.total_variance.toFixed(2)}`;
    
    // Populate results table
    const tableBody = document.querySelector('#resultsTable tbody');
    tableBody.innerHTML = '';
    
    data.data.forEach(row => {
        const tr = document.createElement('tr');
        
        // Set row class based on comment
        if (row.Comment === 'Price mismatch') {
            tr.className = 'mismatch';
        } else if (row.Comment === 'Missing Deal') {
            tr.className = 'missing-deal';
        } else if (row.Comment === 'PPM Only') {
            tr.className = 'ppm-only';
        } else if (row.Comment === '') {
            tr.className = 'perfect-match';
        }
        
        // Add table cells
        Object.keys(row).forEach(key => {
            const td = document.createElement('td');
            
            // Format value based on column
            if (key === 'VAR') {
                const value = parseFloat(row[key]);
                td.textContent = row[key];
                if (value > 0) {
                    td.className = 'var-positive';
                } else if (value < 0) {
                    td.className = 'var-negative';
                }
            } else {
                td.textContent = row[key];
            }
            
            tr.appendChild(td);
        });
        
        tableBody.appendChild(tr);
    });
    
    // Initialize DataTable
    if ($.fn.DataTable.isDataTable('#resultsTable')) {
        $('#resultsTable').DataTable().destroy();
    }
    
    $('#resultsTable').DataTable({
        pageLength: 10,
        lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
        responsive: true
    });
    
    // Create visualizations
    createVisualizations(data.visualizations);
}

// Create Visualizations
function createVisualizations(visualizations) {
    // Match Distribution Pie Chart
    if (visualizations.match_distribution) {
        Plotly.newPlot('matchDistributionChart', 
            visualizations.match_distribution.data, 
            visualizations.match_distribution.layout);
    }
    
    // Variance by Type Chart
    if (visualizations.variance_by_type) {
        Plotly.newPlot('varianceByTypeChart', 
            visualizations.variance_by_type.data, 
            visualizations.variance_by_type.layout);
    }
    
    // Top Materials Chart
    if (visualizations.top_materials) {
        Plotly.newPlot('topMaterialsChart', 
            visualizations.top_materials.data, 
            visualizations.top_materials.layout);
    }
    
    // Bill Back vs PPM Chart
    if (visualizations.billback_vs_ppm) {
        Plotly.newPlot('billbackVsPpmChart', 
            visualizations.billback_vs_ppm.data, 
            visualizations.billback_vs_ppm.layout);
    }
    
    // Variance Distribution Chart
    if (visualizations.variance_distribution) {
        Plotly.newPlot('varianceDistributionChart', 
            visualizations.variance_distribution.data, 
            visualizations.variance_distribution.layout);
    }
}

// Generate Report
function generateReport() {
    if (!sessionId) {
        showAlert('No active session found. Please run analysis first.', 'warning');
        return;
    }
    
    const format = document.querySelector('input[name="reportFormat"]:checked').value;
    
    showLoading(true);
    
    // Send request to generate report
    fetch('/generate-report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            sessionId: sessionId,
            format: format
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayReport(data.report, data.format);
        } else {
            showAlert(`Error: ${data.error}`, 'danger');
        }
        showLoading(false);
    })
    .catch(error => {
        showAlert(`Error: ${error.message}`, 'danger');
        showLoading(false);
    });
}

// Display Generated Report
function displayReport(reportContent, format) {
    const reportContainer = document.getElementById('reportContainer');
    const reportContentElement = document.getElementById('reportContent');
    
    reportContainer.style.display = 'block';
    
    if (format === 'html') {
        reportContentElement.innerHTML = reportContent;
    } else {
        // For markdown or text, preserve formatting with <pre> tag
        reportContentElement.innerHTML = `<pre>${reportContent}</pre>`;
    }
    
    // Scroll to report
    reportContainer.scrollIntoView({ behavior: 'smooth' });
}

// Save Report
function saveReport() {
    const reportContent = document.getElementById('reportContent').innerHTML;
    const format = document.querySelector('input[name="reportFormat"]:checked').value;
    
    let filename = 'dispute_analysis_report';
    let content = '';
    let contentType = '';
    
    if (format === 'html') {
        filename += '.html';
        content = `<!DOCTYPE html><html><head><title>Dispute Analysis Report</title>
                  <style>body{font-family:sans-serif;max-width:800px;margin:0 auto;padding:20px}
                  table{border-collapse:collapse;width:100%}
                  th,td{border:1px solid #ddd;padding:8px}
                  th{background-color:#f2f2f2}</style>
                  </head><body>${reportContent}</body></html>`;
        contentType = 'text/html';
    } else if (format === 'markdown') {
        filename += '.md';
        content = reportContent.replace(/<pre>|<\/pre>/g, '');
        contentType = 'text/markdown';
    } else {
        filename += '.txt';
        content = reportContent.replace(/<pre>|<\/pre>/g, '');
        contentType = 'text/plain';
    }
    
    // Create blob and download
    const blob = new Blob([content], { type: contentType });
    saveAs(blob, filename);
}

// Show/Hide Loading Overlay
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (show) {
        overlay.classList.remove('d-none');
    } else {
        overlay.classList.add('d-none');
    }
}

// Show Alert Message
function showAlert(message, type) {
    const alertContainer = document.querySelector('.alert-container');
    if (!alertContainer) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => {
            alertDiv.remove();
        }, 150);
    }, 5000);
}
