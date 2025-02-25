// Global variables
var hoverEnabled = false;
var animationPolling = null;
var isAnimating = false;

$(document).ready(function() {
    // Set up event handlers
    setupEventHandlers();
});

function setupEventHandlers() {
    // Toggle functionality
    $("#clearAllBtn").click(function() {
        $.post('/clear_all', {}, function(response) {
            if (response.success) {
                $(".segment, .dp").removeClass('on');
                showToast('All segments cleared', 'success');
            }
        });
    });

    $("#hoverToggleBtn").click(function() {
        hoverEnabled = !hoverEnabled;
        $(this).text(hoverEnabled ? 'Disable Hover' : 'Enable Hover');
        $(this).toggleClass('active');
        
        showToast(hoverEnabled ? 'Hover mode enabled' : 'Hover mode disabled', 'info');
    });
    
    $("#animateBtn").click(function() {
        const $this = $(this);
        const isCurrentlyAnimating = $this.text() === 'Stop Animation';
        
        if (isCurrentlyAnimating) {
            $.post('/stop_animation', {}, function(response) {
                if (response.success) {
                    $this.text('Start Animation');
                    $this.removeClass('btn-danger').addClass('btn-success');
                    
                    // Stop polling when animation stops
                    isAnimating = false;
                    if (animationPolling) {
                        clearInterval(animationPolling);
                        animationPolling = null;
                    }
                    
                    // Make one final request to get the current state after stopping
                    setTimeout(function() {
                        $.getJSON('/get_grid_state', function(stateResponse) {
                            if (stateResponse.success) {
                                updateDisplayFromGrid(stateResponse.grid);
                                showToast('Animation stopped', 'info');
                            }
                        });
                    }, 300); // Wait a moment for the server to process the stop command
                }
            });
        } else {
            $.post('/start_animation', {}, function(response) {
                if (response.success) {
                    $this.text('Stop Animation');
                    $this.removeClass('btn-success').addClass('btn-danger');
                    showToast('Animation started', 'success');
                    
                    // Start polling when animation starts
                    isAnimating = true;
                    animationPolling = setInterval(pollGridState, 200); // Poll every 200ms
                }
            });
        }
    });

    $(".segment, .dp").click(function() {
        if (!hoverEnabled) {
            toggleSegment($(this));
        }
    });

    $(".segment, .dp").hover(debounce(function() {
        if (hoverEnabled) {
            toggleSegment($(this));
        }
    }, 50), function() {});

    // Preset management functionality
    $("#savePresetBtn").click(function() {
        const name = $("#presetName").val().trim();
        if (!name) {
            showToast('Please enter a preset name', 'warning');
            return;
        }

        $.post('/save_preset', { name: name }, function(response) {
            if (response.success) {
                // Update preset dropdown
                updatePresetDropdown(response.presets);
                $("#presetName").val('');
                showToast(`Preset "${name}" saved successfully`, 'success');
            } else {
                showToast(`Error: ${response.error}`, 'error');
            }
        });
    });

    $("#loadPresetBtn").click(function() {
        const name = $("#presetSelect").val();
        if (!name) {
            showToast('Please select a preset', 'warning');
            return;
        }

        $.post('/load_preset', { name: name }, function(response) {
            if (response.success) {
                // Update all segments based on loaded state
                updateDisplayFromGrid(response.grid);
                showToast(`Preset "${name}" loaded`, 'success');
            } else {
                showToast(`Error: ${response.error}`, 'error');
            }
        });
    });

    $("#deletePresetBtn").click(function() {
        const name = $("#presetSelect").val();
        if (!name) {
            showToast('Please select a preset', 'warning');
            return;
        }

        if (confirm(`Are you sure you want to delete preset "${name}"?`)) {
            $.post('/delete_preset', { name: name }, function(response) {
                if (response.success) {
                    updatePresetDropdown(response.presets);
                    showToast(`Preset "${name}" deleted`, 'info');
                } else {
                    showToast(`Error: ${response.error}`, 'error');
                }
            });
        }
    });
}

// Toast notification function
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container');
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Set icon based on type
    let iconClass = '';
    switch(type) {
        case 'success':
            iconClass = 'fa-solid fa-check';
            break;
        case 'error':
            iconClass = 'fa-solid fa-xmark';
            break;
        case 'warning':
            iconClass = 'fa-solid fa-triangle-exclamation';
            break;
        default:
            iconClass = 'fa-solid fa-info';
    }
    
    // Create toast content
    toast.innerHTML = `
        <div class="toast-icon"><i class="${iconClass}"></i></div>
        <div class="toast-message">${message}</div>
        <div class="toast-progress"></div>
    `;
    
    // Add to container
    toastContainer.appendChild(toast);
    
    // Show toast with animation
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    // Remove toast after animation duration
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

// Function to update the display based on current grid state
function updateDisplayFromGrid(grid) {
    $(".segment, .dp").removeClass('on');
    grid.forEach((pcb, pcbIndex) => {
        pcb.forEach((state, segmentIndex) => {
            if (state === 1) {
                $(`.segment[data-pcb="${pcbIndex}"][data-segment="${segmentIndex}"], .dp[data-pcb="${pcbIndex}"][data-segment="${segmentIndex}"]`).addClass('on');
            }
        });
    });
}

// Function to poll the current state during animation
function pollGridState() {
    $.getJSON('/get_grid_state', function(response) {
        if (response.success) {
            updateDisplayFromGrid(response.grid);
        }
    });
}

function toggleSegment(segmentElement) {
    var pcb = segmentElement.data('pcb');
    var segment = segmentElement.data('segment');
    $.post('/toggle_segment', { pcb: pcb, segment: segment }, function(response) {
        if (response.success) {
            segmentElement.toggleClass('on');
        }
    });
}

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

function updatePresetDropdown(presets) {
    const $select = $("#presetSelect");
    $select.empty();
    $select.append($('<option>', {
        value: '',
        text: 'Select a preset...'
    }));
    presets.forEach(preset => {
        $select.append($('<option>', {
            value: preset,
            text: preset
        }));
    });
}