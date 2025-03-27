document.addEventListener("DOMContentLoaded", function () {
    let searchInput = document.getElementById("search-input");
    let searchButton = document.getElementById("search-button");
    let resultContainer = document.getElementById("search-results-container");

    // Function to perform the search
    function performSearch() {
        let query = searchInput.value.trim();
        console.log("Search query:", query); // Debug
        if (query.length > 0) {
            fetch(`/search/?q=${query}`)
                .then(response => {
                    if (!response.ok) throw new Error("Network response was not ok");
                    return response.json();
                })
                .then(data => {
                    console.log("Fetched Data:", data);
                    resultContainer.innerHTML = '';

                    if (data.leads.length > 0 || data.clients.length > 0 || data.users.length > 0) {
                        let html = '';

                        if (data.leads.length > 0) {
                            html += '<h6 class="dropdown-header">Leads</h6>';
                            data.leads.forEach(lead => {
                                html += `<a class="dropdown-item" href="/leads/lead_details/${lead.id}/">${lead.name}</a>`;
                            });
                        }

                        if (data.clients.length > 0) {
                            html += '<h6 class="dropdown-header">Clients</h6>';
                            data.clients.forEach(client => {
                                html += `<a class="dropdown-item" href="/clients/client_details/${client.id}/">${client.name}</a>`;
                            });
                        }

                        if (data.users.length > 0) {
                            html += '<h6 class="dropdown-header">Users</h6>';
                            data.users.forEach(user => {
                                html += `<a class="dropdown-item" href="/user/${user.id}/">${user.username}</a>`;
                            });
                        }

                        resultContainer.innerHTML = html;
                        resultContainer.classList.add("show");
                    } else {
                        resultContainer.classList.remove("show");
                    }
                })
                .catch(error => {
                    console.error("Error fetching search results:", error);
                });
        } else {
            resultContainer.classList.remove("show");
        }
    }

    // Search input event listener
    searchInput.addEventListener("input", performSearch);

    // Search button event listener
    searchButton.addEventListener("click", performSearch);

    // Click outside to close results
    document.addEventListener("click", function (event) {
        if (!searchInput.contains(event.target) && !resultContainer.contains(event.target)) {
            resultContainer.classList.remove("show");
        }
    });
});