var profile_user = null

function init_posts_socket(){
    if (typeof socket !== 'undefined') {

        socket.on('new_post', function(data) {
            if (profile_user == data.owner || profile_user == null){
                var element = document.getElementsByClassName("posts-grid")[0]
                element.insertAdjacentHTML("afterbegin", data.html)
                button = document.getElementById("data-post-id-"+data.post_id)
                htmx.process(button);
            }
        });
    }
    else{
        setTimeout(init_posts_socket, 100)
    }
}
init_posts_socket()

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

document.addEventListener('click', function(e) {
    if (e.target.id && e.target.id.startsWith('like-button-')) {
        if (e.target.textContent.trim() == "🩶"){
            e.target.textContent = "🩷"
        }
        else {
            e.target.textContent = "🩶"
        }
    }
})

// Toggle comments section visibility
function toggleComments(postId) {
    const commentSection = document.getElementById(`comment-section-${postId}`);
    if (commentSection) {
        if (commentSection.style.display === 'none') {
            commentSection.style.display = 'block';
        } else {
            commentSection.style.display = 'none';
        }
    }
}

// Toggle reply form visibility
function toggleReplyForm(commentId, postId) {
    const replyForm = document.getElementById(`reply-form-${commentId}`);
    if (replyForm) {
        if (replyForm.style.display === 'none') {
            replyForm.style.display = 'block';
            // Focus on the input field
            const input = replyForm.querySelector('input[name="comment"]');
            if (input) input.focus();
        } else {
            replyForm.style.display = 'none';
        }
    }
}

// Toggle comment replies visibility
function toggleCommentReplies(commentId) {
    const repliesSection = document.getElementById(`comment-replies-${commentId}`);
    const toggleButton = event.target;

    if (repliesSection) {
        if (repliesSection.style.display === 'none') {
            repliesSection.style.display = 'flex';
            // Update button text to indicate expanded state
            const replyCount = toggleButton.textContent.match(/\d+/)[0];
            toggleButton.innerHTML = `▼ ${replyCount} ${replyCount == 1 ? 'reply' : 'replies'}`;
        } else {
            repliesSection.style.display = 'none';
            // Update button text to indicate collapsed state
            const replyCount = toggleButton.textContent.match(/\d+/)[0];
            toggleButton.innerHTML = `${replyCount} ${replyCount == 1 ? 'reply' : 'replies'}`;
        }
    }
}

// Update comment count after successful comment submission
document.body.addEventListener('htmx:afterSwap', function(event) {
    // Check if this was a comment submission (top-level comment)
    if (event.detail.target.id && event.detail.target.id.startsWith('comments-list-')) {
        const postId = event.detail.target.id.replace('comments-list-', '');

        // Update comment count
        const commentToggle = document.getElementById(`comment-toggle-${postId}`);
        if (commentToggle) {
            htmx.trigger(commentToggle, 'load');
        }

        // Clear the main comment form
        const mainForm = event.detail.target.closest('.post-comment-section-container').querySelector('.post-comment-section-main-form');
        if (mainForm) {
            mainForm.reset();
        }
    }

    // Check if this was a reply submission (inline reply form)
    if (event.detail.target.id && event.detail.target.id.startsWith('reply-form-inline-')) {
        const commentId = event.detail.target.id.replace('reply-form-inline-', '');

        // Clear the inline reply form
        const form = event.detail.target.querySelector('form');
        if (form) {
            form.reset();
        }

        // Make sure the replies section is visible
        const repliesSection = document.getElementById(`comment-replies-${commentId}`);
        if (repliesSection && repliesSection.style.display === 'none') {
            repliesSection.style.display = 'flex';
        }

        // Update the reply count button
        const toggleButton = document.querySelector(`[onclick="toggleCommentReplies(${commentId})"]`);
        if (toggleButton) {
            // Extract current count and increment
            const match = toggleButton.textContent.match(/\d+/);
            if (match) {
                const newCount = parseInt(match[0]) + 1;
                const hasArrow = toggleButton.textContent.includes('▼');
                toggleButton.innerHTML = `${hasArrow ? '▼ ' : ''}${newCount} ${newCount == 1 ? 'reply' : 'replies'}`;
            } else {
                // First reply - create the button
                toggleButton.innerHTML = `▼ 1 reply`;
            }
        } else {
            // No toggle button exists yet - create one
            const commentActions = document.querySelector(`#comment-${commentId} > .comment-actions`);
            if (commentActions) {
                const newToggleButton = document.createElement('button');
                newToggleButton.className = 'comment-replies-toggle';
                newToggleButton.setAttribute('onclick', `toggleCommentReplies(${commentId})`);
                newToggleButton.innerHTML = '▼ 1 reply';
                commentActions.insertBefore(newToggleButton, commentActions.firstChild);
            }
        }
    }
});