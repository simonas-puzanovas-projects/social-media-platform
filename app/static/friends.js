// Friends page JavaScript
// Listen for new friend requests using the socket from base.js
document.addEventListener('DOMContentLoaded', function() {
    // Load friends data when page loads
    loadFriendsAndSentData();
    loadFriendRequestsData();
    
    // Wait for socket to be available from base.js
    if (typeof socket !== 'undefined') {
        socket.on('new_notification', function(notification) {
            if (notification.type === 'friend_request') {
                loadFriendRequestsData(); // Reload just the friend requests
            }
        });
    }
});



// Dashboard JavaScript functionality
function openFriendSearch() {
    document.getElementById('friendSearchModal').style.display = 'block';
    document.getElementById('userSearchInput').focus();
}

function closeFriendSearch() {
    document.getElementById('friendSearchModal').style.display = 'none';
    document.getElementById('userSearchInput').value = '';
    document.getElementById('searchResults').innerHTML = '';
}

let searchTimeout;

function searchUsers() {
    clearTimeout(searchTimeout);
    const query = document.getElementById('userSearchInput').value.trim();
    
    if (query.length < 2) {
        document.getElementById('searchResults').innerHTML = '';
        return;
    }
    
    searchTimeout = setTimeout(() => {
        fetch(`/search_users?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(users => {
                displaySearchResults(users);
            })
            .catch(error => {
                console.error('Error searching users:', error);
            });
    }, 300);
}

function displaySearchResults(users) {
    const resultsContainer = document.getElementById('searchResults');
    
    if (users.length === 0) {
        resultsContainer.innerHTML = '<div class="search-result-item no-results">No users found</div>';
        return;
    }
    
    resultsContainer.innerHTML = users.map(user => {
        let buttonHtml = '';
        let statusText = '';
        
        switch(user.status) {
            case 'none':
                buttonHtml = `<button class="btn btn-secondary btn-sm" onclick="sendFriendRequest(${user.id})">Add Friend</button>`;
                break;
            case 'friends':
                statusText = '<span class="status-badge friends">Friends</span>';
                break;
            case 'request_sent':
                statusText = '<span class="status-badge pending">Request Sent</span>';
                break;
            case 'request_received':
                statusText = '<span class="status-badge received">Request Received</span>';
                break;
        }
        
        return `
            <div class="search-result-item">
                <div class="user-info">
                    <strong>${user.username}</strong>
                    ${statusText}
                </div>
                <div class="user-actions">
                    ${buttonHtml}
                </div>
            </div>
        `;
    }).join('');
}

function sendFriendRequest(userId) {
    fetch('/send_friend_request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            searchUsers(); // Refresh search results
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error sending friend request:', error);
        alert('Error sending friend request');
    });
}

// Friends functionality removed from dashboard

function loadFriendsAndSentData() {
    const combinedList = document.getElementById('friends-combined-list');
    const totalCount = document.getElementById('friends-total-count');
    
    // Load both friends and sent requests simultaneously
    Promise.all([
        fetch('/api/friends').then(response => response.json()),
        fetch('/api/sent_requests').then(response => response.json())
    ])
    .then(([friends, sentRequests]) => {
        const totalItems = friends.length + sentRequests.length;
        totalCount.textContent = totalItems;
        
        if (totalItems === 0) {
            combinedList.innerHTML = '<div class="no-data">You don\'t have any friends yet. Use the "Add Friend" button to send friend requests!</div>';
            return;
        }
        
        let html = '';
        
        // Add accepted friends first
        friends.forEach(friend => {
            html += `
                <div class="friend-item">
                    <div class="friend-info">
                        <a href="/profile/${friend.username}" class="friend-name-link">
                            <strong>${friend.username}</strong>
                        </a>
                        <span class="status-badge ${friend.is_online ? 'online' : 'offline'}">
                            ${friend.is_online ? 'Online' : 'Offline'}
                        </span>
                    </div>
                    <div class="friend-actions">
                        <button class="btn btn-remove btn-sm" onclick="removeFriend(${friend.id}, '${friend.username}', this)">Remove</button>
                    </div>
                </div>
            `;
        });
        
        // Add sent requests with pending status
        sentRequests.forEach(request => {
            html += `
                <div class="friend-item sent-request-item" data-friendship-id="${request.friendship_id}">
                    <div class="friend-info">
                        <strong>${request.username}</strong>
                        <span class="status-badge pending">Pending</span>
                    </div>
                    <div class="request-actions">
                        <button class="btn btn-cancel btn-sm" onclick="cancelFriendRequest(${request.friendship_id}, this)">Cancel</button>
                    </div>
                </div>
            `;
        });
        
        combinedList.innerHTML = html;
    })
    .catch(error => {
        console.error('Error loading friends and sent requests:', error);
        combinedList.innerHTML = '<div class="error">Error loading data</div>';
    });
}

function loadFriendRequestsData() {
    const requestsList = document.getElementById('friend-requests-list');
    const requestsCount = document.getElementById('requests-count');
    
    fetch('/api/friend_requests')
        .then(response => response.json())
        .then(requests => {
            requestsCount.textContent = requests.length;
            
            if (requests.length === 0) {
                requestsList.innerHTML = '<div class="no-data">No pending friend requests.</div>';
                return;
            }
            
            requestsList.innerHTML = requests.map(request => `
                <div class="friend-request-item" data-friendship-id="${request.friendship_id}">
                    <div class="friend-info">
                        <strong>${request.username}</strong>
                        <span class="request-text">sent you a friend request</span>
                    </div>
                    <div class="request-actions">
                        <button class="btn btn-accept btn-sm" onclick="respondToFriendRequest(${request.friendship_id}, 'accept', this)">Accept</button>
                        <button class="btn btn-reject btn-sm" onclick="respondToFriendRequest(${request.friendship_id}, 'reject', this)">Reject</button>
                    </div>
                </div>
            `).join('');
        })
        .catch(error => {
            console.error('Error loading friend requests:', error);
            requestsList.innerHTML = '<div class="error">Error loading friend requests</div>';
        });
}

function respondToFriendRequest(friendshipId, response, buttonElement) {
    const requestItem = buttonElement.closest('.friend-request-item');
    const buttons = requestItem.querySelectorAll('button');
    
    // Disable buttons during request
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
                // Show success message and refresh both lists
                showToast('Friend request accepted!');
                loadFriendsAndSentData(); // Refresh combined friends list
                loadFriendRequestsData(); // Refresh requests list
            } else {
                // Remove the request item
                requestItem.remove();
                // Update count
                const requestsCount = document.getElementById('requests-count');
                requestsCount.textContent = parseInt(requestsCount.textContent) - 1;
                showToast('Friend request rejected');
            }
        } else {
            // Re-enable buttons if there was an error
            buttons.forEach(btn => btn.disabled = false);
            showToast('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error responding to friend request:', error);
        buttons.forEach(btn => btn.disabled = false);
        showToast('Error processing request');
    });
}

function cancelFriendRequest(friendshipId, buttonElement) {
    const requestItem = buttonElement.closest('.sent-request-item');
    const button = requestItem.querySelector('button');
    
    // Disable button during request
    button.disabled = true;
    button.textContent = 'Cancelling...';
    
    fetch('/cancel_friend_request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            friendship_id: friendshipId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Refresh the entire combined list to update counts
            loadFriendsAndSentData();
            showToast('Friend request cancelled');
        } else {
            // Re-enable button if there was an error
            button.disabled = false;
            button.textContent = 'Cancel';
            showToast('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error cancelling friend request:', error);
        button.disabled = false;
        button.textContent = 'Cancel';
        showToast('Error cancelling request');
    });
}

function removeFriend(friendUserId, friendUsername, buttonElement) {
    // Confirm before removing friend
    if (!confirm(`Are you sure you want to remove ${friendUsername} from your friends?`)) {
        return;
    }
    
    const friendItem = buttonElement.closest('.friend-item');
    const button = friendItem.querySelector('.btn-remove');
    
    // Disable button during request
    button.disabled = true;
    button.textContent = 'Removing...';
    
    fetch('/remove_friend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            friend_user_id: friendUserId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Refresh the entire combined list to update counts
            loadFriendsAndSentData();
            showToast(`${friendUsername} removed from friends`);
        } else {
            // Re-enable button if there was an error
            button.disabled = false;
            button.textContent = 'Remove';
            showToast('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error removing friend:', error);
        button.disabled = false;
        button.textContent = 'Remove';
        showToast('Error removing friend');
    });
}

// Event handlers
window.onclick = function(event) {
    const friendSearchModal = document.getElementById('friendSearchModal');
    
    if (event.target === friendSearchModal) {
        closeFriendSearch();
    }
}