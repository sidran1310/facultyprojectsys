// Initialize Bootstrap tooltips (if you use them)
document.addEventListener('DOMContentLoaded', function () {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    console.log("Custom script loaded. Bootstrap tooltips initialized if any.");

    // Auto-close alerts after a delay (e.g., 5 seconds)
    const autoDismissAlerts = document.querySelectorAll('.alert-dismissible.fade.show');
    autoDismissAlerts.forEach(alert => {
        // Only auto-dismiss success/info alerts, keep errors/warnings visible longer or indefinitely
        if (alert.classList.contains('alert-success') || alert.classList.contains('alert-info')) {
            setTimeout(() => {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                if (bsAlert) {
                    bsAlert.close();
                }
            }, 5000); // 5 seconds
        }
    });

});

// Add any other custom JavaScript functions needed for your portal below
// For example:
// - AJAX form submissions
// - Dynamic content loading/filtering without page reload
// - More complex UI interactions