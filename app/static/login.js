// Login page JavaScript
// Toggle between login and register forms

function showLogin() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const toggleBtns = document.querySelectorAll('.toggle-btn');

    loginForm.classList.add('active');
    registerForm.classList.remove('active');

    toggleBtns[0].classList.add('active');
    toggleBtns[1].classList.remove('active');
}

function showRegister() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const toggleBtns = document.querySelectorAll('.toggle-btn');

    registerForm.classList.add('active');
    loginForm.classList.remove('active');

    toggleBtns[1].classList.add('active');
    toggleBtns[0].classList.remove('active');
}

// Handle form submissions with AJAX
document.addEventListener('DOMContentLoaded', function() {
    // Handle login form submission
    const loginForm = document.querySelector('#login-form form');
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(this);

        fetch(this.action, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.redirected) {
                // If response is a redirect (successful login), follow it
                window.location.href = response.url;
            } else {
                // If response is JSON (error), parse and show toast
                return response.json();
            }
        })
        .then(data => {
            if (data && !data.success) {
                showToast(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('An error occurred. Please try again.');
        });
    });

    // Handle register form submission
    const registerForm = document.querySelector('#register-form form');
    registerForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(this);

        fetch(this.action, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.redirected) {
                // If response is a redirect (successful registration), follow it
                window.location.href = response.url;
            } else {
                // If response is JSON (error), parse and show toast
                return response.json();
            }
        })
        .then(data => {
            if (data && !data.success) {
                showToast(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('An error occurred. Please try again.');
        });
    });
});