document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const filterButton = document.getElementById('filterButton');
    const filterPopup = document.getElementById('filterPopup');
    const applyFilters = document.getElementById('applyFilters');
    const searchResults = document.getElementById('searchResults');
    const cardDisplay = document.getElementById('cardDisplay');

    let query = '';
    let costValues = [];
    let powerValues = [];

    filterButton.addEventListener('click', () => {
        filterPopup.style.display = 'block';
    });

    applyFilters.addEventListener('click', () => {
        query = searchInput.value;
        const costCheckboxes = document.querySelectorAll('input[name="cost"]');
        const powerCheckboxes = document.querySelectorAll('input[name="power"]');

        costValues = Array.from(costCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);
        powerValues = Array.from(powerCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);

        fetchPage(1);

        filterPopup.style.display = 'none';
    });

    searchInput.addEventListener('input', () => {
        query = searchInput.value;
        fetchPage(1);
    });

    function fetchPage(page) {
        fetch(`/search_dynamic?query=${query}&cost=${costValues.join(',')}&power=${powerValues.join(',')}&page=${page}`)
            .then(response => response.json())
            .then(data => {
                let resultsHtml = '';
                data.cards.forEach(card => {
                    resultsHtml += `
                        <div class="card">
                            <h2>${card.name}</h2>
                            <img src="${card.image}" alt="${card.name}">
                            <p>Cost: ${card.cost}</p>
                            <p>Power: ${card.power}</p>
                        </div>
                    `;
                });
                searchResults.innerHTML = resultsHtml;

                let pagination = searchResults.querySelector('.pagination');
                if (!pagination) {
                    pagination = document.createElement('div');
                    pagination.classList.add('pagination');
                    searchResults.appendChild(pagination);
                }
                pagination.innerHTML = '';

                if (data.total_pages > 1) {
                    for (let i = 1; i <= data.total_pages; i++) {
                        const pageLink = document.createElement('a');
                        pageLink.href = '#';
                        pageLink.textContent = i;
                        pageLink.addEventListener('click', (event) => {
                            event.preventDefault();
                            fetchPage(i);
                        });
                        pagination.appendChild(pageLink);
                    }
                }

                cardDisplay.style.display = 'none';
                searchResults.style.display = 'block';
            });
    }
});