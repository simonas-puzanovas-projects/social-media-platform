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