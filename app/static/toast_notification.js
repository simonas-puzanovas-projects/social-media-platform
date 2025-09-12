// Show toast notification
function showToast(message) {
    const toast = document.getElementById('toast-notification');
    const toastMessage = document.getElementById('toast-message');
    toastMessage.textContent = message;
    toast.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(hideToast, 5000);
}

// Hide toast notification
function hideToast() {
    document.getElementById('toast-notification').style.display = 'none';
}
