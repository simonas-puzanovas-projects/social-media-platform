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
    if (!confirm('Are you sure you want to delete this post?')) return;

    fetch('/delete_post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ post_id: postId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.querySelector(`[data-post-id="${postId}"]`)?.remove();
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
    // Like button toggle
    if (e.target.id?.startsWith('like-button-')) {
        e.target.textContent = e.target.textContent.trim() == "🩶" ? "🩷" : "🩶";
    }

    // Toggle comments
    if (e.target.classList.contains('post-comments-toggle')) {
        const postId = e.target.dataset.postId;
        const section = document.getElementById(`comment-section-${postId}`);
        if (section) section.style.display = section.style.display === 'none' ? 'block' : 'none';
    }

    // Toggle replies
    if (e.target.classList.contains('comment-replies-toggle')) {
        const commentId = e.target.dataset.commentId;
        const repliesDiv = document.getElementById(`replies-${commentId}`);
        if (repliesDiv) {
            const isHidden = repliesDiv.style.display === 'none';
            repliesDiv.style.display = isHidden ? 'flex' : 'none';
            const count = e.target.textContent.match(/\d+/)[0];
            e.target.textContent = `${isHidden ? '▼ ' : ''}${count} ${count == 1 ? 'reply' : 'replies'}`;
        }
    }

    // Toggle reply form
    if (e.target.classList.contains('comment-reply-btn')) {
        const commentId = e.target.dataset.commentId;
        const form = document.getElementById(`reply-form-${commentId}`);
        if (form) {
            form.style.display = form.style.display === 'none' ? 'block' : 'none';
            if (form.style.display === 'block') form.querySelector('input[name="comment"]')?.focus();
        }
    }

    // Cancel reply
    if (e.target.classList.contains('cancel-reply')) {
        document.getElementById(`reply-form-${e.target.dataset.commentId}`).style.display = 'none';
    }
});

function toggleComments(postId) {
    const section = document.getElementById(`comment-section-${postId}`);
    if (section) {
        section.style.display = section.style.display === 'none' ? 'block' : 'none';
    }
}

// HTMX after swap handler
document.body.addEventListener('htmx:afterSwap', function(event) {
    const target = event.detail.target;

    // Top-level comment added
    if (target.id?.startsWith('comments-list-')) {
        const postId = target.id.replace('comments-list-', '');
        const commentToggle = document.getElementById(`comment-toggle-${postId}`);
        if (commentToggle) htmx.trigger(commentToggle, 'load');

        const form = target.closest('.post-comment-section-container')?.querySelector('.post-comment-section-main-form');
        if (form) form.reset();
    }

    // Reply added
    if (target.id?.startsWith('replies-')) {
        const commentId = target.id.replace('replies-', '');
        const form = document.getElementById(`reply-form-${commentId}`);
        if (form) {
            form.style.display = 'none';
            form.querySelector('form')?.reset();
        }

        // Show replies section
        target.style.display = 'flex';

        // Update or create toggle button
        const comment = document.getElementById(`comment-${commentId}`);
        let toggleBtn = comment?.querySelector('.comment-replies-toggle');

        if (toggleBtn) {
            const count = parseInt(toggleBtn.textContent.match(/\d+/)[0]) + 1;
            toggleBtn.textContent = `▼ ${count} ${count == 1 ? 'reply' : 'replies'}`;
        } else {
            const actions = comment?.querySelector('.comment-actions');
            if (actions) {
                toggleBtn = document.createElement('button');
                toggleBtn.className = 'comment-replies-toggle';
                toggleBtn.dataset.commentId = commentId;
                toggleBtn.textContent = '▼ 1 reply';
                actions.insertBefore(toggleBtn, actions.firstChild);
            }
        }
    }
});
