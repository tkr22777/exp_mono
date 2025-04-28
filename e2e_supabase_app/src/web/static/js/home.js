// Home page script
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in
    checkAuthStatus();
});

// Check user authentication status
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
            // User is logged in, update the navigation
            updateNavForLoggedInUser(data.user);
        }
    })
    .catch(error => {
        console.log('Not logged in:', error);
        // User is not logged in, ensure nav shows login button (default state)
    });
}

// Update navigation for logged in user
function updateNavForLoggedInUser(user) {
    const navAuthSection = document.getElementById('nav-auth-section');
    if (navAuthSection) {
        navAuthSection.innerHTML = `
            <a href="/profile" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-2">
                My Profile
            </a>
            <button id="nav-logout-btn" class="bg-red-100 hover:bg-red-200 text-red-600 font-semibold py-2 px-4 rounded-md">
                Logout
            </button>
        `;
        
        // Add event listener to the logout button
        document.getElementById('nav-logout-btn').addEventListener('click', handleLogout);
    }
}

// Handle logout
function handleLogout() {
    fetch('/auth/logout', {
        method: 'POST',
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Redirect to home page after logout
            window.location.href = '/';
        } else {
            alert(data.error || 'Logout failed');
        }
    })
    .catch(error => {
        console.error('Logout error:', error);
    });
} 