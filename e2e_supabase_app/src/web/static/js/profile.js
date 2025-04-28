// Profile page script
document.addEventListener('DOMContentLoaded', function() {
    // Load the user profile data
    loadUserProfile();
    
    // Setup event listeners
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    document.getElementById('logout-btn-secondary').addEventListener('click', handleLogout);
});

// Load user profile data
function loadUserProfile() {
    fetch('/auth/profile', {
        credentials: 'include'
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        // If not authenticated, redirect to login
        window.location.href = '/login';
        throw new Error('Not authenticated');
    })
    .then(data => {
        if (data.success && data.user) {
            displayUserProfile(data.user);
        } else {
            console.error('Invalid user data received');
            window.location.href = '/login';
        }
    })
    .catch(error => {
        console.error('Profile error:', error);
        window.location.href = '/login';
    });
}

// Display user profile information
function displayUserProfile(user) {
    // Update user name (using email if no name provided)
    const userName = user.email.split('@')[0]; // Extract username from email
    document.getElementById('user-name').textContent = userName;
    
    // Update profile details
    document.getElementById('profile-email').textContent = user.email;
    document.getElementById('profile-id').textContent = user.id;
    
    // Format and display creation date
    const createdDate = new Date(user.created_at).toLocaleString();
    document.getElementById('profile-created').textContent = createdDate;
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
            // Redirect to login page after logout
            window.location.href = '/login';
        } else {
            alert(data.error || 'Logout failed');
        }
    })
    .catch(error => {
        console.error('Logout error:', error);
    });
} 