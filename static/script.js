const apiUrl = 'http://localhost:8000';
let currentPage = 1;
let currentRangeStart = 1;
const itemsPerPage = 50;
const maxPagesToShow = 5;
const rangeStep = 3;

async function fetchRestaurants(page) {
    try {
        const response = await fetch(`${apiUrl}/all_restaurants?page=${page}`);
        if (!response.ok) {
            throw new Error('Network response was not ok.');
        }
        const restaurants = await response.json();
        displayRestaurants(restaurants);
    } catch (error) {
        console.error('Error fetching restaurants:', error);
    }
}

async function fetchRestaurantCount() {
    try {
        const response = await fetch(`${apiUrl}/restaurants_count`);
        if (!response.ok) {
            throw new Error('Network response was not ok.');
        }
        const data = await response.json();
        const totalPages = Math.ceil(data.count / itemsPerPage);
        setupPagination(totalPages);
    } catch (error) {
        console.error('Error fetching restaurant count:', error);
    }
}

async function searchRestaurants(query) {
    try {
        const response = await fetch(`${apiUrl}/search?query=${query}`);
        if (!response.ok) {
            throw new Error('Network response was not ok.');
        }
        const results = await response.json();
        displaySearchResults(results);
    } catch (error) {
        console.error('Error searching restaurants:', error);
    }
}

function displayRestaurants(restaurants) {
    const restaurantList = document.getElementById('restaurant-list');
    restaurantList.innerHTML = ''; // Clear previous content

    restaurants.forEach((restaurant, index) => {
        setTimeout(() => { // Delay for sequential appearance
            const restaurantDiv = document.createElement('div');
            restaurantDiv.className = 'restaurant-box'; // Full width for each restaurant
            restaurantDiv.innerHTML = `
                <div class="card">
                    <div class="card-body" id="${restaurant.id}">
                        <h5 class="card-title">${restaurant.Restaurant_Name}</h5>
                        <p class="card-text">${restaurant.Address}</p>
                        <div class="dot ${restaurant.Has_Online_delivery === 'Yes' ? 'dot-available' : 'dot-not-available'}"></div>
                        <span class="dot-text">Online Delivery</span>
                    </div>
                </div>
            `;
            restaurantDiv.addEventListener('click', () => {
                window.location.href = `/restaurant_id/${restaurant.id}`;
            });
            restaurantList.appendChild(restaurantDiv);
        }, index * 10); // Adjust timing for smoother effect
    });
}

function setupPagination(totalPages) {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';

    function createPageItem(page, label = page) {
        const pageItem = document.createElement('li');
        pageItem.className = `page-item ${page === currentPage ? 'active' : ''}`;
        pageItem.innerHTML = `<a class="page-link" href="#">${label}</a>`;
        pageItem.addEventListener('click', (event) => {
            event.preventDefault();
            if (page !== currentPage) {
                currentPage = page;
                fetchRestaurants(currentPage);
                setupPagination(totalPages); // Update pagination after data load
            }
        });
        return pageItem;
    }

    const startPage = Math.max(1, currentRangeStart);
    const endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);

    if (startPage > 1) {
        const previousSetPage = Math.max(1, startPage - rangeStep);
        const previousArrow = createPageItem(previousSetPage, '< Prev');
        previousArrow.addEventListener('click', (event) => {
            event.preventDefault();
            currentRangeStart = Math.max(1, currentRangeStart - rangeStep);
            setupPagination(totalPages);
        });
        pagination.appendChild(previousArrow);
    }

    for (let i = startPage; i <= endPage; i++) {
        pagination.appendChild(createPageItem(i));
    }

    if (endPage < totalPages) {
        const nextSetPage = startPage + rangeStep;
        const nextArrow = createPageItem(nextSetPage, 'Next >');
        nextArrow.addEventListener('click', (event) => {
            event.preventDefault();
            if (currentPage !== nextSetPage) {
                currentPage = nextSetPage;
                fetchRestaurants(currentPage);
                setupPagination(totalPages);
            } else {
                currentRangeStart = Math.min(totalPages - maxPagesToShow + 1, currentRangeStart + rangeStep);
                setupPagination(totalPages);
            }
        });
        pagination.appendChild(nextArrow);
    }
}

function displaySearchResults(results) {
    const searchResults = document.getElementById('search-results');
    searchResults.innerHTML = ''; // Clear previous content
    console.log(results);
    searchResults.style.display = 'block';
    results.forEach((restaurant) => {
        const dropdownItem = document.createElement('a');
        dropdownItem.classList.add('dropdown-item');
        dropdownItem.href = `/restaurant_id/${restaurant.id}`;
        dropdownItem.textContent =restaurant.Restaurant_Name+", Rating:"+restaurant.Aggregate_rating+"*";
        dropdownItem.addEventListener('click', () => {
            window.location.href = dropdownItem.href;
        });
        console.log(restaurant.Restaurant_Name);
        searchResults.appendChild(dropdownItem);
    });

    if (results.length === 0) {
        const dropdownItem = document.createElement('div');
        dropdownItem.classList.add('dropdown-item', 'text-muted');
        dropdownItem.textContent = 'No results found';
        searchResults.appendChild(dropdownItem);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    fetchRestaurants(currentPage);
    fetchRestaurantCount();

    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', (event) => {
        const query = event.target.value.trim();
        if (query.length > 0) {
            searchRestaurants(query);
        } else {
            const searchResults = document.getElementById('search-results');
            searchResults.innerHTML = ''; // Clear dropdown if input is empty
            searchResults.style.display = 'none';
        }
    });
});