document.addEventListener('DOMContentLoaded', function() {
    // Add event listener for the role select element
    document.getElementById('role').addEventListener('change', function() {
        var specializationSelect = document.getElementById('specialization');
        // Show or hide the specialization select element based on the selected role
        if (this.value === 'doctor') {
            specializationSelect.style.display = 'inline-block';
        } else {
            specializationSelect.style.display = 'none';
        }
    });

    // Add event listener for the login form submission
    document.getElementById('loginForm').addEventListener('submit', function() {
        var role = document.getElementById('role').value;
        // If the selected role is doctor, update the form action to include the specialization
        if (role === 'doctor') {
            var specialization = document.getElementById('specialization').value;
            this.action = '/specialized_dashboard/' + specialization;
        }
    });
});
