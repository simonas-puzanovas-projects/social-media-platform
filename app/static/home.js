// Home page JavaScript functionality

// Delete post function
function deletePost(postId) {
    if (!confirm('Are you sure you want to delete this post?')) {
        return;
    }

    fetch('/delete_post', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            post_id: postId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove the post element from the DOM
            const postElement = document.querySelector(`[data-post-id="${postId}"]`);
            if (postElement) {
                postElement.remove();
            }
            showToast('Post deleted successfully');
        } else {
            showToast('Error deleting post: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error deleting post');
    });
}

// Auto-refresh posts every 30 seconds
setInterval(() => {
    // Only refresh if user is still on the page and not interacting
    if (document.visibilityState === 'visible') {
        location.reload();
    }
}, 30000);