// Base JavaScript for Social Media Platform
// Socket.IO and notification functionality

const socket = io();
let notificationCount = 0;

// Socket connection
socket.on('connect', function() {
    console.log('Connected to server');
});

// Handle new notifications
socket.on('new_notification', function(notification) {
    console.log('New notification:', notification);
    
    // Update notification badge
    notificationCount++;
    updateNotificationBadge();
    
    // Show toast notification
    showToast(notification.message);
    
    // Add to notification list
    addNotificationToList(notification);
});

// Update notification badge
function updateNotificationBadge() {
    const badge = document.getElementById('notification-badge');
    if (notificationCount > 0) {
        badge.textContent = notificationCount;
        badge.style.display = 'inline';
    } else {
        badge.style.display = 'none';
    }
}



// Toggle notification window
function toggleNotifications() {
    const window = document.getElementById('notification-window');
    if (window.style.display === 'none') {
        openNotificationWindow();
    } else {
        closeNotificationWindow();
    }
}

// Open notification window
function openNotificationWindow() {
    const window = document.getElementById('notification-window');
    window.style.display = 'block';
    loadNotifications();
    document.body.style.overflow = 'hidden'; // Prevent background scroll
}

// Close notification window
function closeNotificationWindow() {
    const window = document.getElementById('notification-window');
    window.style.display = 'none';
    document.body.style.overflow = 'auto'; // Restore background scroll
}

// Load notifications
function loadNotifications() {
    fetch('/notifications')
        .then(response => response.json())
        .then(notifications => {
            const notificationList = document.getElementById('notification-list');
            notificationList.innerHTML = '';
            
            if (notifications.length === 0) {
                notificationList.innerHTML = '<div class="no-notifications">No notifications yet</div>';
                return;
            }
            
            notifications.forEach(notification => {
                const notificationElement = createNotificationElement(notification);
                notificationList.appendChild(notificationElement);
            });
            
            // Clear the badge when notifications are loaded
            notificationCount = 0;
            updateNotificationBadge();
        })
        .catch(error => {
            console.error('Error loading notifications:', error);
        });
}

// Create notification element
function createNotificationElement(notification) {
    const notificationElement = document.createElement('div');
    notificationElement.className = 'notification-item';
    notificationElement.dataset.notificationId = notification.id;
    
    let actionsHTML = '';
    if (notification.type === 'friend_request' && notification.data) {
        actionsHTML = `
            <div class="notification-actions">
                <button class="btn btn-accept" onclick="handleFriendRequest(${notification.data.friendship_id}, 'accept', this)">
                    Accept
                </button>
                <button class="btn btn-reject" onclick="handleFriendRequest(${notification.data.friendship_id}, 'reject', this)">
                    Reject
                </button>
            </div>
        `;
    }
    
    notificationElement.innerHTML = `
        <div class="notification-content">
            <p>${notification.message}</p>
            <small>${new Date(notification.created_at).toLocaleString()}</small>
            ${actionsHTML}
        </div>
    `;
    
    return notificationElement;
}

// Add notification to list
function addNotificationToList(notification) {
    const notificationList = document.getElementById('notification-list');
    const notificationElement = createNotificationElement(notification);
    notificationList.insertBefore(notificationElement, notificationList.firstChild);
}

// Handle friend request
function handleFriendRequest(friendshipId, response, buttonElement) {
    const notificationItem = buttonElement.closest('.notification-item');
    const actionsDiv = buttonElement.closest('.notification-actions');
    
    // Disable buttons during request
    const buttons = actionsDiv.querySelectorAll('button');
    buttons.forEach(btn => btn.disabled = true);
    
    fetch('/respond_friend_request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            friendship_id: friendshipId,
            response: response
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (response === 'accept') {
                // Update the notification to show it was accepted
                actionsDiv.innerHTML = '<span class="status-accepted">✓ Friend request accepted</span>';
                showToast('Friend request accepted!');
            } else {
                // Remove the notification item for rejected requests
                notificationItem.remove();
                showToast('Friend request rejected');
            }
        } else {
            // If the request doesn't exist anymore, remove the notification
            if (data.message && data.message.includes('not found')) {
                notificationItem.remove();
                showToast('This friend request no longer exists');
            } else {
                // Re-enable buttons if there was an error
                buttons.forEach(btn => btn.disabled = false);
                showToast('Error: ' + data.message);
            }
        }
    })
    .catch(error => {
        console.error('Error handling friend request:', error);
        buttons.forEach(btn => btn.disabled = false);
        showToast('Error processing request');
    });
}

// Event listeners
// Close notification window when clicking outside
window.onclick = function(event) {
    const notificationWindow = document.getElementById('notification-window');
    const bell = document.querySelector('.notification-bell');
    const windowContent = document.querySelector('.notification-window-content');
    
    if (event.target === notificationWindow && !windowContent.contains(event.target)) {
        closeNotificationWindow();
    }
}

// Close notification window with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const notificationWindow = document.getElementById('notification-window');
        if (notificationWindow.style.display === 'block') {
            closeNotificationWindow();
        }
    }
});

// Mobile touch/swipe support
let touchStartY = 0;
let touchStartX = 0;
let isSwiping = false;

// Touch start handler
document.addEventListener('touchstart', function(event) {
    const notificationWindow = document.getElementById('notification-window');
    const windowContent = document.querySelector('.notification-window-content');
    
    if (notificationWindow && notificationWindow.style.display === 'block' && windowContent.contains(event.target)) {
        touchStartY = event.touches[0].clientY;
        touchStartX = event.touches[0].clientX;
        isSwiping = false;
    }
});

// Touch move handler
document.addEventListener('touchmove', function(event) {
    const notificationWindow = document.getElementById('notification-window');
    
    if (notificationWindow && notificationWindow.style.display === 'block' && touchStartY > 0) {
        const touchY = event.touches[0].clientY;
        const touchX = event.touches[0].clientX;
        const deltaY = touchY - touchStartY;
        const deltaX = touchX - touchStartX;
        
        // Detect if user is swiping
        if (Math.abs(deltaY) > 10 || Math.abs(deltaX) > 10) {
            isSwiping = true;
        }
        
        // Mobile: Swipe down to close (only if swiping down more than 50px)
        if (window.innerWidth <= 768 && deltaY > 50 && Math.abs(deltaX) < Math.abs(deltaY)) {
            event.preventDefault();
            closeNotificationWindow();
        }
        // Desktop: Swipe left to close (only if swiping left more than 100px)
        else if (window.innerWidth > 768 && deltaX < -100 && Math.abs(deltaY) < Math.abs(deltaX)) {
            event.preventDefault();
            closeNotificationWindow();
        }
    }
});

// Touch end handler
document.addEventListener('touchend', function(event) {
    touchStartY = 0;
    touchStartX = 0;
    isSwiping = false;
});

// Responsive behavior detection
function isMobile() {
    return window.innerWidth <= 768;
}

// Enhanced notification window functions with responsive behavior
const originalOpenNotificationWindow = openNotificationWindow;
const originalCloseNotificationWindow = closeNotificationWindow;

// Override open function with responsive enhancements
openNotificationWindow = function() {
    originalOpenNotificationWindow();
    
    // Add responsive class for additional styling if needed
    const notificationWindow = document.getElementById('notification-window');
    if (isMobile()) {
        notificationWindow.classList.add('mobile-mode');
    } else {
        notificationWindow.classList.add('desktop-mode');
    }
    
    // Prevent background scroll on mobile
    if (isMobile()) {
        document.body.style.overflow = 'hidden';
    }
};

// Override close function with responsive cleanup and animations
closeNotificationWindow = function() {
    const notificationWindow = document.getElementById('notification-window');
    const windowContent = document.querySelector('.notification-window-content');
    
    // Add closing animation classes
    notificationWindow.classList.add('closing');
    windowContent.classList.add('closing');
    
    // Wait for animation to complete before hiding
    setTimeout(() => {
        // Clean up responsive classes
        notificationWindow.classList.remove('mobile-mode', 'desktop-mode', 'closing');
        windowContent.classList.remove('closing');
        
        // Hide the window
        notificationWindow.style.display = 'none';
        
        // Restore background scroll
        document.body.style.overflow = '';
    }, 300); // Match the CSS animation duration
};

// Handle window resize to update responsive behavior
window.addEventListener('resize', function() {
    const notificationWindow = document.getElementById('notification-window');
    if (notificationWindow && notificationWindow.style.display === 'block') {
        // Update classes based on new screen size
        notificationWindow.classList.remove('mobile-mode', 'desktop-mode');
        if (isMobile()) {
            notificationWindow.classList.add('mobile-mode');
        } else {
            notificationWindow.classList.add('desktop-mode');
        }
    }
});