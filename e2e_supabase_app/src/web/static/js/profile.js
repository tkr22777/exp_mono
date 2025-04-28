// Profile page script
document.addEventListener('DOMContentLoaded', function() {
    // Load the user profile data
    loadUserProfile();
    
    // Setup event listeners
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    document.getElementById('logout-btn-secondary').addEventListener('click', handleLogout);
    
    // Profile edit functionality
    document.getElementById('edit-profile-btn').addEventListener('click', showEditForm);
    document.getElementById('cancel-edit-btn').addEventListener('click', hideEditForm);
    document.getElementById('profile-edit-form').addEventListener('submit', handleProfileUpdate);
});

// Current profile data
let currentProfile = null;

/**
 * Get the auth token from either localStorage or cookies
 * @returns {string|null} The authentication token or null if not found
 */
function getAuthToken() {
    // First try localStorage
    let token = localStorage.getItem('access_token');
    
    // If not in localStorage, try to extract from cookies
    if (!token) {
        const cookieArray = document.cookie.split(';');
        for (let i = 0; i < cookieArray.length; i++) {
            const cookiePair = cookieArray[i].trim().split('=');
            
            if (cookiePair[0] === 'access_token') {
                token = cookiePair[1];
                break;
            }
            
            // Also check for Supabase token
            if (cookiePair[0] === 'supabase-auth-token') {
                token = cookiePair[1];
                break;
            }
        }
    }
    
    return token;
}

// Load user profile data
function loadUserProfile() {
    // Get authentication token
    const token = getAuthToken();
    
    // Prepare headers with authentication if token exists
    const headers = {};
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    fetch('/api/profiles/me', {
        method: 'GET',
        headers: headers,
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
        if (data.success && data.profile) {
            currentProfile = data.profile;
            displayUserProfile(data.profile);
        } else {
            console.error('Invalid profile data received');
            window.location.href = '/login';
        }
    })
    .catch(error => {
        console.error('Profile error:', error);
        window.location.href = '/login';
    });
}

// Display user profile information
function displayUserProfile(profile) {
    // Set user name in header (using first name, last name, or email username)
    let displayName = profile.email.split('@')[0];
    if (profile.first_name) {
        displayName = profile.first_name;
        if (profile.last_name) {
            displayName += ' ' + profile.last_name;
        }
    } else if (profile.display_name) {
        displayName = profile.display_name;
    }
    document.getElementById('user-name').textContent = displayName;
    
    // Update profile details
    document.getElementById('profile-email').textContent = profile.email || '';
    document.getElementById('profile-id').textContent = profile.id || '';
    
    // Set new profile fields
    const firstName = document.getElementById('profile-first-name');
    const lastName = document.getElementById('profile-last-name');
    const phone = document.getElementById('profile-phone');
    const location = document.getElementById('profile-location');
    
    // Update display with values or default "Not specified" text
    firstName.textContent = profile.first_name || 'Not specified';
    lastName.textContent = profile.last_name || 'Not specified';
    phone.textContent = profile.phone_number || 'Not specified';
    location.textContent = profile.location || 'Not specified';
    
    // Format and display creation date
    const createdDate = new Date(profile.created_at).toLocaleString();
    document.getElementById('profile-created').textContent = createdDate;
    
    // Pre-populate edit form fields
    document.getElementById('edit-first-name').value = profile.first_name || '';
    document.getElementById('edit-last-name').value = profile.last_name || '';
    document.getElementById('edit-phone').value = profile.phone_number || '';
    document.getElementById('edit-location').value = profile.location || '';
}

// Show profile edit form
function showEditForm() {
    document.getElementById('profile-view').classList.add('hidden');
    document.getElementById('profile-edit').classList.remove('hidden');
}

// Hide profile edit form
function hideEditForm() {
    document.getElementById('profile-edit').classList.add('hidden');
    document.getElementById('profile-view').classList.remove('hidden');
    
    // Reset any error messages
    document.getElementById('profile-edit-error').classList.add('hidden');
}

// Handle profile update submission
function handleProfileUpdate(e) {
    e.preventDefault();
    
    // Hide any previous error messages
    const errorElement = document.getElementById('profile-edit-error');
    errorElement.classList.add('hidden');
    errorElement.textContent = '';
    
    // Get form values
    const updateData = {
        first_name: document.getElementById('edit-first-name').value.trim(),
        last_name: document.getElementById('edit-last-name').value.trim(),
        phone_number: document.getElementById('edit-phone').value.trim(),
        location: document.getElementById('edit-location').value.trim()
    };
    
    // Remove empty fields to avoid overwriting with empty strings
    Object.keys(updateData).forEach(key => {
        if (!updateData[key]) {
            delete updateData[key];
        }
    });
    
    // Get authentication token
    const token = getAuthToken();
    
    // Prepare headers with authentication
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Submit update to server
    fetch('/api/profiles/me', {
        method: 'PATCH',
        headers: headers,
        body: JSON.stringify(updateData),
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update current profile data
            currentProfile = data.profile;
            
            // Update the display
            displayUserProfile(data.profile);
            
            // Hide the edit form
            hideEditForm();
            
            // Show success message
            alert('Profile updated successfully!');
        } else {
            // Show error message
            errorElement.textContent = data.error || 'Failed to update profile. Please try again.';
            errorElement.classList.remove('hidden');
        }
    })
    .catch(error => {
        console.error('Profile update error:', error);
        errorElement.textContent = 'An error occurred while updating your profile. Please try again.';
        errorElement.classList.remove('hidden');
    });
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