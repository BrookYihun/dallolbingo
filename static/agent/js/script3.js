let allRows = []; // This will store all rows data
document.addEventListener("DOMContentLoaded", function () {
    
    add_loader();

    get_shop_stat();

    // Initial table update
    updateTable();

    // Handle "Next" button click
    document.querySelector("#nextButton").addEventListener("click", () => {
        if (currentPage < Math.ceil(dataRows.length / rowsPerPage) - 1) {
            currentPage++;
            updateTable();
        }
    });

    // Handle "Previous" button click
    document.querySelector("#prevButton").addEventListener("click", () => {
        if (currentPage > 0) {
            currentPage--;
            updateTable();
        }
    });

});

var hiddenData = document.querySelector("#hiddenData tbody").innerHTML;
const rowsPerPage = 20;
let currentPage = 0;
let dataRows;

function updateTable() {

    hiddenData = document.querySelector("#hiddenData tbody").innerHTML;

    const tableBody = document.querySelector("#gameTable tbody");
    tableBody.innerHTML = ""; // Clear existing rows

    const start = currentPage * rowsPerPage;
    const end = (currentPage + 1) * rowsPerPage;

    tableBody.innerHTML = hiddenData;
    dataRows = tableBody.querySelectorAll("tr"); // Moved dataRows declaration here

    // Slice the data based on the current page
    dataRows.forEach((row, index) => {
        if (index < start || index >= end) {
            row.style.display = "none";
        } else {
            row.style.display = "";
        }
    });
}

function filterTable() {
    const searchValue = document.getElementById("searchBox").value.toLowerCase();

    // Filter the full data based on the search value
    const filteredRows = allRows.filter(shopStat => {
        return shopStat.name.toLowerCase().includes(searchValue); // Filter by name
    });

    // Update the table with filtered rows
    const tableBody = document.querySelector("#hiddenData tbody");
    tableBody.innerHTML = ""; // Clear existing rows

    filteredRows.forEach(shopStat => {
        const html = generateShopStatHTML(shopStat);
        tableBody.insertAdjacentHTML('beforeend', html);
    });

    updateTable(); // Update the table with pagination
}

function filterTable() {
    const searchValue = document.getElementById("searchBox").value.toLowerCase();
    const tableBody = document.querySelector("#gameTable tbody");
    const rows = tableBody.querySelectorAll("tr");

    rows.forEach(row => {
        const nameCell = row.querySelector("td:first-child"); // Name is in the first column
        if (nameCell) {
            const nameText = nameCell.textContent.toLowerCase();
            if (nameText.includes(searchValue)) {
                row.style.display = ""; // Show row if it matches
            } else {
                row.style.display = "none"; // Hide row if no match
            }
        }
    });
}

var loader = document.getElementById('loader');
var main = document.getElementById('main');

function add_loader(){
    loader.style.display = 'block';

    main.style.display = 'none';
}

function remove_loader(){
    loader.style.display = 'none';

    main.style.display = 'block';
}

$('#filterForm').on('submit', function(event){
    event.preventDefault(); // Prevent the default form submission

    // Get the value from the input field
    var dateFilter = $('input[name="datefilter"]').val();

    // Trigger the AJAX request
    get_shop_stat_filter(dateFilter);
});

function get_shop_stat_filter(dateFilter) {

    add_loader();

    $.ajax({
        url: "get_shops_stat_filter/",  // Replace with your Django view URL
        type: "GET",
        data: {
            datefilter: dateFilter
        },
        success: function(response) {
            // Disable buttons based on the received list of selected numbers
            renderShopsStats(response);
            updateTable();
            remove_loader();
        },
        error: function(xhr, status, error) {
            console.error("Failed to get shops", error);
        }
    });
}

function get_shop_stat(){
    add_loader();
    $.ajax({
        url:  "get_shops_stat/",  // Replace with your Django view URL
        type: "GET",
            // Add more parameters as needed
        success: function(response) {
            // Disable buttons based on the received list of selected numbers
            renderShopsStats(response);
            updateTable();
            remove_loader();
        },
        error: function(xhr, status, error) {
            console.error("Failed to get shops", error);
        }
    });
}

function generateShopStatHTML(userStat) {
    return `
        <tr>
            <td>${userStat.name}</td>
            <td>${userStat.percentage}</td>
            <td>${userStat.prepaid}</td>
            <td>${userStat.account}</td>
            <td>${userStat.total_games_played}</td>
            <td>${userStat.total_earning}</td>
            <td>${userStat.total_games_played_today}</td>
            <td>${userStat.today_earning}</td>
        </tr>
    `;
}

// Function to render user statistics in the table
function renderShopsStats(data) {

    const statsContainer = document.getElementById("stats");
    
    // Update Balance
    statsContainer.querySelector(".stat-box:nth-child(1) p").textContent = data.agent.account;

    // Update Total Shops
    statsContainer.querySelector(".stat-box:nth-child(2) p").textContent = data.num_shops;

    // Update Total Earning
    statsContainer.querySelector(".stat-box:nth-child(3) p").textContent = data.total_earning;

    // Update Today Earning
    statsContainer.querySelector(".stat-box:nth-child(4) p").textContent = data.today_earning;

    const tableBody = document.querySelector("#hiddenData tbody");
    tableBody.innerHTML = ""; // Clear existing rows

    allRows = []; // Reset allRows to avoid duplicates

    // Generate HTML for each user statistic and append it to the table
    data.shops_stat.forEach(function(shopStat) {
        const html = generateShopStatHTML(shopStat);
        tableBody.insertAdjacentHTML('beforeend', html);
        allRows.push(shopStat);
    });

    updateTable(); 

}

const blur_bg = document.getElementById('blur-background');
