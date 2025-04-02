document.addEventListener('DOMContentLoaded', function() {
    // Select HTML elements and store them in variables
    const searchInput = document.getElementById('searchInput'); // Input field for search query
    const searchButton = document.getElementById('searchButton'); // Button to trigger search (if needed)
    const filterButton = document.getElementById('filterButton'); // Button to open filter popup
    const filterPopup = document.getElementById('filterPopup'); // Popup containing filter options
    const applyFilters = document.getElementById('applyFilters'); // Button to apply selected filters
    const searchResults = document.getElementById('searchResults'); // Container to display search results
    const cardDisplay = document.getElementById('cardDisplay'); // Container for the default card display

    // Initialize variables to store search and filter values
    let query = ''; // Stores the search query
    let costValues = []; // Stores selected cost filter values
    let powerValues = []; // Stores selected power filter values

    // Event listener for the filter button
    filterButton.addEventListener('click', () => {
        // Show the filter popup when the button is clicked
        filterPopup.style.display = 'block';
    });

    // Event listener for the apply filters button
    applyFilters.addEventListener('click', () => {
        // Get the search query from the input field
        query = searchInput.value;

        // Get selected cost values from checkboxes
        const costCheckboxes = document.querySelectorAll('input[name="cost"]');
        costValues = Array.from(costCheckboxes)
            .filter(checkbox => checkbox.checked) // Filter out unchecked checkboxes
            .map(checkbox => checkbox.value); // Extract the value of checked checkboxes

        // Get selected power values from checkboxes
        const powerCheckboxes = document.querySelectorAll('input[name="power"]');
        powerValues = Array.from(powerCheckboxes)
            .filter(checkbox => checkbox.checked) // Filter out unchecked checkboxes
            .map(checkbox => checkbox.value); // Extract the value of checked checkboxes

        // Fetch the first page of results with the applied filters
        fetchPage(1);

        // Hide the filter popup
        filterPopup.style.display = 'none';
    });

    // Event listener for the search input field
    searchInput.addEventListener('input', () => {
        // Update the search query as the user types
        query = searchInput.value;

        // Fetch the first page of results with the updated query
        fetchPage(1);
    });

    // Function to fetch and display card data
    function fetchPage(page) {
        // Construct the URL with search and filter parameters
        fetch(`/search_dynamic?query=${query}&cost=${costValues.join(',')}&power=${powerValues.join(',')}&page=${page}`)
            .then(response => response.json()) // Parse the response as JSON
            .then(data => {
                let resultsHtml = ''; // Initialize an empty string to store the HTML for card results

                // Loop through the card data and generate HTML for each card
                data.cards.forEach(card => {
                    resultsHtml += `
                        <div class="card">
                            <h2>${card.name}</h2>
                            <img src="${card.art}" alt="${card.name}">
                            <p>Cost: ${card.cost}</p>
                            <p>Power: ${card.power}</p>
                        </div>
                    `;
                });

                // Update the search results container with the generated HTML
                searchResults.innerHTML = resultsHtml;

                // Pagination logic
                let pagination = searchResults.querySelector('.pagination'); // Get the pagination container
                if (!pagination) {
                    // If the pagination container doesn't exist, create it
                    pagination = document.createElement('div');
                    pagination.classList.add('pagination');
                    searchResults.appendChild(pagination);
                }
                pagination.innerHTML = ''; // Clear the pagination container

                // Generate pagination links if there are multiple pages
                if (data.total_pages > 1) {
                    for (let i = 1; i <= data.total_pages; i++) {
                        const pageLink = document.createElement('a'); // Create a link for each page
                        pageLink.href = '#'; // Set the link's href attribute
                        pageLink.textContent = i; // Set the link's text content
                        pageLink.addEventListener('click', (event) => {
                            event.preventDefault(); // Prevent the default link behavior
                            fetchPage(i); // Fetch the corresponding page of results
                        });
                        pagination.appendChild(pageLink); // Add the link to the pagination container
                    }
                }

                // Hide the default card display and show the search results
                cardDisplay.style.display = 'none';
                searchResults.style.display = 'block';
            });
    }
});