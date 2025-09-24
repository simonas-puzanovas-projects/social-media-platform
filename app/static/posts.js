var profile_user = null

function init_posts_socket(){
    if (typeof socket !== 'undefined') {

        socket.on('new_post', function(html) {
            var element = document.getElementsByClassName("posts-grid")[0] 
            element.insertAdjacentHTML("afterbegin", html)
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