document.addEventListener('DOMContentLoaded', function() {
    const loginBtn = document.getElementById('login-btn');
    const signupBtn = document.getElementById('signup-btn');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');

    loginBtn.addEventListener('click', function() {
        document.getElementById('login-section').style.display = 'block';
        document.getElementById('signup-section').style.display = 'none';
    });

    signupBtn.addEventListener('click', function() {
        document.getElementById('login-section').style.display = 'none';
        document.getElementById('signup-section').style.display = 'block';
    });

    // Initially show the login section and hide the signup section
    document.getElementById('login-section').style.display = 'block';
    document.getElementById('signup-section').style.display = 'none';
});
