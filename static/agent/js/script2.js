document.addEventListener("DOMContentLoaded", function () {
    
    add_loader();

    get_agent_stat();

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
let allRows = [];

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
    get_agent_stat_filter(dateFilter);
});

function get_agent_stat_filter(dateFilter) {

    add_loader();

    $.ajax({
        url: "get_agents_stat_filter/",  // Replace with your Django view URL
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

function get_agent_stat(){

    add_loader();

    $.ajax({
        url:  "get_agent_stat/",  // Replace with your Django view URL
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
            <td>${userStat.total_shops}</td>
            <td>${userStat.total_earning}</td>
            <td>${userStat.total_net}</td>
            <td>${userStat.today_game}</td>
            <td>${userStat.today_earning}</td>
            <td>
                <button class="action-btn" onclick="activate_deactivate(${userStat.id})" >${userStat.active}</button>
                <button class="action-btn" onclick="add_balance(${userStat.id})" >Add Balance</button>
                <button class="action-btn" onclick="edit_shop(${userStat.id})" >Edit</button>
                <a class="action-btn" href="view_agent/${userStat.id}/">View</a>
            </td>
        </tr>
    `;
}

// Function to render user statistics in the table
function renderShopsStats(data) {

    const statsContainer = document.getElementById("stats");
    
    // Update Balance
    statsContainer.querySelector(".stat-box:nth-child(1) p").textContent = data.num_agent;

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
    data.agents_stat.forEach(function(shopStat) {
        const html = generateShopStatHTML(shopStat);
        tableBody.insertAdjacentHTML('beforeend', html);
        allRows.push(shopStat);
    });

}

function activate_deactivate(id){

    add_loader();

    $.ajax({
        url:  "activate_deactivate/",  // Replace with your Django view URL
        type: "GET",
        data: { user: id },
            // Add more parameters as needed
        success: function(response) {
            // Disable buttons based on the received list of selected numbers
            var result = response.message;
            alert(result);
            get_agent_stat();
            updateTable();
            remove_loader();
        },
        error: function(xhr, status, error) {
            console.error("Failed to add shop", error);
        }
    });
}

const blur_bg = document.getElementById('blur-background');
const add_new_shop_btn = document.getElementById('add-new-shop-btn');
const add_new_shop = document.getElementById('add-new-shop');
const close_add_shop = document.getElementById('close-add-shop');
const add_new_shop_submit = document.getElementById('add-new-shop-submit');
const add_balance_form = document.getElementById('add-balance');
const close_add_balance = document.getElementById('close-add-balance');
const add_balance_btn = document.getElementById('add-balance-submit');
const edit_shop_con = document.getElementById('edit-shop');
const close_edit_shop = document.getElementById('close-edit-shop');
const edit_shop_submit =document.getElementById('edit-shop-submit');

function add_balance(id){

    $.ajax({
        url:  "get_agent_info/",  // Replace with your Django view URL
        type: "GET",
        data: { user: id },
            // Add more parameters as needed
        success: function(response) {
            // Disable buttons based on the received list of selected numbers

            blur_bg.style.display = 'block';
            add_balance_form.style.display ='block';

            document.getElementById('add-balance-name').value = response.name;
            document.getElementById('add-balance-id').value = id;

        },
        error: function(xhr, status, error) {
            console.error("Failed to add shop", error);
        }
    });

}

add_balance_btn.onclick = function(){
    var form = document.getElementById('add-balance-form');
    let isFormValid = true;
    form.querySelectorAll('input, select, textarea').forEach(function(field) {
        if (!field.value.trim()) {
            isFormValid = false;
            // Optionally, you can add some visual feedback for the user
            field.classList.add('error'); // Add error class to empty fields
        } else {
            field.classList.remove('error'); // Remove error class if field has value
        }
    });

    if (!isFormValid) {
        // Optionally, you can display an error message to the user
        alert('Please fill in all fields.');
        return; // Exit function if any field is empty
    }

    let serializedData = {};
    const formData = new FormData(form);
    for (const [key, value] of formData.entries()){
        serializedData[key] = value;
    }

    add_loader();

    $.ajax({
        url:  "add_balance/",  // Replace with your Django view URL
        type: "GET",
        data: serializedData,
            // Add more parameters as needed
        success: function(response) {
            // Disable buttons based on the received list of selected numbers
            blur_bg.style.display = 'none';
            add_balance_form.style.display = 'none';
            var result = response.message;
            alert(result);
            get_agent_stat();
            updateTable();
            remove_loader();
        },
        error: function(xhr, status, error) {
            console.error("Failed to add Balance", error);
        }
    });
}

function edit_shop(id){
    $.ajax({
        url:  "get_agent_info/",  // Replace with your Django view URL
        type: "GET",
        data: { user: id },
            // Add more parameters as needed
        success: function(response) {
            // Disable buttons based on the received list of selected numbers

            blur_bg.style.display = 'block';
            edit_shop_con.style.display ='block';

            document.getElementById('edit-shop-form').innerHTML +=`
                <div class="form-group">
                    <label for="name">Name:</label>
                    <input type="text" name="id" value="${id}" required hidden>
                    <input type="text" name="name" value="${response.name}" required>
                </div>
                <div class="form-group">
                    <label for="user_name">User Name:</label>
                    <input type="text" name="user_name" value="${response.user_name}"  required>
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="text" name="password" value="${response.password}" required>
                </div>
                <div class="form-group">
                    <label for="phone_number">Phone Number:</label>
                    <input type="text" name="phone_number" value="${response.phone_number}"  required>
                </div>
                <div class="form-group">
                    <label for="prepaid">Prepaid:</label>
                    <input type="checkbox" name="prepaid" ${response.prepaid} >
                </div>
                <div class="form-group">
                    <label for="percentage">Percentage:</label>
                    <input type="number" step="0.01" name="percentage" value="${response.percentage}"  required>
                </div>
                <div class="form-group">
                    <label for="balance">Balance:</label>
                    <input type="number" step="0.01" name="balance" value="${response.balance}" required>
                </div>
            `;

        },
        error: function(xhr, status, error) {
            console.error("Failed to add shop", error);
        }
    });
}

add_new_shop_btn.onclick = function () {
    blur_bg.style.display = 'block';
    add_new_shop.style.display = 'block';
};

close_add_shop.onclick = function () {
    blur_bg.style.display = 'none';
    add_new_shop.style.display = 'none';
};

close_add_balance.onclick = function () {
    blur_bg.style.display = 'none';
    add_balance_form.style.display = 'none';
};

close_edit_shop.onclick = function () {
    blur_bg.style.display = 'none';
    edit_shop_con.style.display = 'none';
    var form = document.getElementById('edit-shop-form');
    while (form.children.length > 1) {
        form.removeChild(form.lastChild);
    }
};

add_new_shop_submit.onclick = function(){
    var form = document.getElementById('add-new-shop-form');
    let isFormValid = true;
    form.querySelectorAll('input, select, textarea').forEach(function(field) {
        if (!field.value.trim()) {
            isFormValid = false;
            // Optionally, you can add some visual feedback for the user
            field.classList.add('error'); // Add error class to empty fields
        } else {
            field.classList.remove('error'); // Remove error class if field has value
        }
    });

    if (!isFormValid) {
        // Optionally, you can display an error message to the user
        alert('Please fill in all fields.');
        return; // Exit function if any field is empty
    }

    let serializedData = {};
    const formData = new FormData(form);
    for (const [key, value] of formData.entries()){
        serializedData[key] = value;
    }

    add_loader();

    $.ajax({
        url:  "add_agent/",  // Replace with your Django view URL
        type: "GET",
        data: serializedData,
            // Add more parameters as needed
        success: function(response) {
            // Disable buttons based on the received list of selected numbers
            blur_bg.style.display = 'none';
            add_new_shop.style.display = 'none';
            var result = response.message;
            alert(result);
            get_agent_stat();
            updateTable();
            remove_loader();
        },
        error: function(xhr, status, error) {
            console.error("Failed to add shop", error);
        }
    });
};

edit_shop_submit.onclick = function(){
    var form = document.getElementById('edit-shop-form');
    let isFormValid = true;
    form.querySelectorAll('input, select, textarea').forEach(function(field) {
        if (!field.value.trim()) {
            isFormValid = false;
            // Optionally, you can add some visual feedback for the user
            field.classList.add('error'); // Add error class to empty fields
        } else {
            field.classList.remove('error'); // Remove error class if field has value
        }
    });

    if (!isFormValid) {
        // Optionally, you can display an error message to the user
        alert('Please fill in all fields.');
        return; // Exit function if any field is empty
    }

    let serializedData = {};
    const formData = new FormData(form);
    for (const [key, value] of formData.entries()){
        serializedData[key] = value;
    }

    add_loader();

    $.ajax({
        url:  "edit_agent/",  // Replace with your Django view URL
        type: "GET",
        data: serializedData,
            // Add more parameters as needed
        success: function(response) {
            // Disable buttons based on the received list of selected numbers
            blur_bg.style.display = 'none';
            edit_shop_con.style.display = 'none';
            var form = document.getElementById('edit-shop-form');
            while (form.children.length > 1) {
                form.removeChild(form.lastChild);
            }
            var result = response.message;
            alert(result);
            get_agent_stat();
            updateTable();
            remove_loader();
        },
        error: function(xhr, status, error) {
            console.error("Failed to edit shop", error);
        }
    });
};