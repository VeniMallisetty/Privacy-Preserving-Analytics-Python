document.addEventListener('DOMContentLoaded', function() {
    // Get all the menu items
    var menuItems = document.querySelectorAll('.dashboard-menu a');

    // Add click event listener to each menu item
    menuItems.forEach(function(item) {
        item.addEventListener('click', function(event) {
            // Prevent the default behavior of the anchor tag
            event.preventDefault();

            // Hide all the content sections
            document.querySelectorAll('.dashboard-content .content').forEach(function(content) {
                content.style.display = 'none';
            });

            // Get the target content section based on the data-content attribute
            var targetContentId = item.getAttribute('data-content');
            var targetContent = document.getElementById(targetContentId);

            // Display the target content section
            if (targetContent) {
                targetContent.style.display = 'block';
            }
        });
    });
});
