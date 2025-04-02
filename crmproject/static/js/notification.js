document.addEventListener("DOMContentLoaded", function () {
    const notificationBtn = document.getElementById("notificationBtn");
    const notificationDropdown = document.getElementById("notificationDropdown");
    const notificationCount = document.getElementById("notificationCount");

    // Toggle dropdown on bell click
    notificationBtn.addEventListener("click", function () {
        notificationDropdown.classList.toggle("hidden");

        // Mark notifications as read when the dropdown opens
        if (!notificationDropdown.classList.contains("hidden")) {
            markNotificationsAsRead();
        }
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", function (event) {
        if (!notificationBtn.contains(event.target) && !notificationDropdown.contains(event.target)) {
            notificationDropdown.classList.add("hidden");
        }
    });

    // Function to send an AJAX request to mark notifications as read
    function markNotificationsAsRead() {
        fetch("{% url 'mark_notifications_read' %}", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "Content-Type": "application/json",
            },
            body: JSON.stringify({}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // If there are no unread notifications, hide the notification count
                if (data.unread_count === 0) {
                    notificationCount.style.display = "none"; // Hide notification count if no unread notifications
                } else {
                    notificationCount.textContent = data.unread_count; // Update count if unread notifications exist
                    notificationCount.style.display = "inline-block"; // Make sure the count is visible
                }
            }
        })
        .catch(error => console.error("Error:", error));
    }

    // Function to get CSRF token
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split("; ")
            .find(row => row.startsWith("csrftoken="))
            ?.split("=")[1];
        return cookieValue || "";
    }
});
