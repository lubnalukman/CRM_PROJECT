
    function openEditModal(id, type, subject, notes) {
        document.getElementById("communication_id").value = id;
        document.getElementById("interaction_type").value = type;
        document.getElementById("subject").value = subject;
        document.getElementById("notes").value = notes;
        document.getElementById("editModal").classList.remove("hidden");
    }

    function closeModal() {
        document.getElementById("editModal").classList.add("hidden");
    }

    document.getElementById("editForm").addEventListener("submit", function (event) {
        event.preventDefault();
        let formData = new FormData(this);
        let communicationId = document.getElementById("communication_id").value;
        let leadId = "{{ lead.id }}"; // Get lead ID from template

        fetch(`/leads/${leadId}/communication/${communicationId}/`, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();  // Reload page to show updated communication
            } else {
                alert("Error updating communication. Please check the form.");
            }
        })
        .catch(error => console.log("Error:", error));
    });

