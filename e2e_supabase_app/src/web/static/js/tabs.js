document.addEventListener('DOMContentLoaded', function() {
    // Set up tab switching
    const tabs = document.querySelectorAll('[data-tab]');
    const tabContents = document.querySelectorAll('[role="tabpanel"]');
    
    // Function to switch tabs
    function switchTab(tabId) {
        // Hide all tab contents
        tabContents.forEach(content => {
            content.classList.add('hidden');
            content.classList.remove('block');
        });
        
        // Deactivate all tabs
        tabs.forEach(tab => {
            tab.classList.remove('text-blue-500', 'border-b-2', 'border-blue-500');
            tab.classList.add('text-gray-500');
        });
        
        // Show selected tab content
        const selectedContent = document.getElementById(tabId);
        if (selectedContent) {
            selectedContent.classList.remove('hidden');
            selectedContent.classList.add('block');
        }
        
        // Activate selected tab
        const selectedTab = document.querySelector(`[data-tab="${tabId}"]`);
        if (selectedTab) {
            selectedTab.classList.remove('text-gray-500');
            selectedTab.classList.add('text-blue-500', 'border-b-2', 'border-blue-500');
        }
    }
    
    // Add click event listeners to tabs
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabId = tab.getAttribute('data-tab');
            switchTab(tabId);
        });
    });
    
    // Set default active tab
    if (tabs.length > 0) {
        const defaultTabId = tabs[0].getAttribute('data-tab');
        switchTab(defaultTabId);
    }
}); 