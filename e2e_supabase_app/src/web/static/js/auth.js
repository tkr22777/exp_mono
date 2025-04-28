// User state
let currentUser = null;

document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in
    checkAuthStatus();
    
    // Set up authentication event listeners
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
});

// Authentication Functions
function checkAuthStatus() {
    fetch('/auth/profile', {
        credentials: 'include'
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Not authenticated');
    })
    .then(data => {
        if (data.success) {
            // If we're on the login page and already logged in, redirect to profile
            if (window.location.pathname === '/login') {
                window.location.href = '/profile';
            }
            currentUser = data.user;
            updateUIForAuthenticatedUser();
        }
    })
    .catch(error => {
        console.log('Not logged in:', error);
        updateUIForUnauthenticatedUser();
    });
}

function handleLogin(e) {
    e.preventDefault();
    
    // Hide any previous error messages
    const errorElement = document.getElementById('login-error');
    errorElement.classList.add('hidden');
    errorElement.textContent = '';
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    fetch('/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email: email,
            password: password
        }),
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentUser = data.user;
            
            // Redirect to profile page
            window.location.href = '/profile';
        } else {
            // Show error message
            errorElement.textContent = data.error || 'Login failed. Please check your credentials.';
            errorElement.classList.remove('hidden');
        }
    })
    .catch(error => {
        console.error('Login error:', error);
        errorElement.textContent = 'An error occurred during login. Please try again.';
        errorElement.classList.remove('hidden');
    });
}

function handleRegister(e) {
    e.preventDefault();
    
    // Hide any previous error messages
    const errorElement = document.getElementById('register-error');
    errorElement.classList.add('hidden');
    errorElement.textContent = '';
    
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;
    
    if (password !== confirmPassword) {
        errorElement.textContent = 'Passwords do not match!';
        errorElement.classList.remove('hidden');
        return;
    }
    
    fetch('/auth/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email: email,
            password: password
        }),
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentUser = data.user;
            
            // Redirect to profile page
            window.location.href = '/profile';
        } else {
            // Show error message
            errorElement.textContent = data.error || 'Registration failed. Please try again.';
            errorElement.classList.remove('hidden');
        }
    })
    .catch(error => {
        console.error('Registration error:', error);
        errorElement.textContent = 'An error occurred during registration. Please try again.';
        errorElement.classList.remove('hidden');
    });
}

function handleLogout() {
    fetch('/auth/logout', {
        method: 'POST',
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentUser = null;
            updateUIForUnauthenticatedUser();
        } else {
            alert(data.error || 'Logout failed');
        }
    })
    .catch(error => {
        console.error('Logout error:', error);
    });
}

// UI Update Functions
function updateUIForAuthenticatedUser() {
    // Hide auth forms, show profile
    document.getElementById('auth-section').classList.add('hidden');
    document.getElementById('profile-section').classList.remove('hidden');
    
    // Update profile information
    document.getElementById('profile-email').textContent = currentUser.email;
    document.getElementById('profile-id').textContent = currentUser.id;
    const createdDate = new Date(currentUser.created_at).toLocaleString();
    document.getElementById('profile-created').textContent = createdDate;
}

function updateUIForUnauthenticatedUser() {
    // Show auth forms, hide profile
    document.getElementById('auth-section').classList.remove('hidden');
    document.getElementById('profile-section').classList.add('hidden');
} 