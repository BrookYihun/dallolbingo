const setting_a = document.getElementById('setting');
const dash_a = document.getElementById('dashboard');
const switchMode = document.getElementById('switch-mode');
const menuBar = document.querySelector('#content nav .bx.bx-menu');
const saveButton = document.getElementById("start-button");
const toggleCheckbox = document.querySelector(".toggle-checkbox");
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
setting_a.classList.add('active');

function setCookie(cookieName, cookieValue, expirationDays) {
    const d = new Date();
    d.setTime(d.getTime() + (expirationDays * 24 * 60 * 60 * 1000));
    const expires = `expires=${d.toUTCString()}`;
    document.cookie = `${cookieName}=${cookieValue}; ${expires}; path=/`;
}

function getCookie(cookieName) {
    const name = `${cookieName}=`;
    const cookies = document.cookie.split(';');
    for(let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].trim();
        if (cookie.indexOf(name) === 0) {
            return cookie.substring(name.length, cookie.length);
        }
    }
    return null;
}

function deleteCookie(cookieName) {
    document.cookie = `${cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

function getLanguage(){
    selectedLanguage = callerLanguageSelect.value;
    return selectedLanguage;
}


menuBar.addEventListener('click', function () {
	sidebar.classList.toggle('hide');
})


if(window.innerWidth < 768) {
	sidebar.classList.add('hide');
}


switchMode.addEventListener('change', function () {
	deleteCookie("mode");
    setCookie("mode",this.checked,7);
	if(this.checked) {
		document.body.classList.remove('dark');
	} else {
		document.body.classList.add('dark');
	}
});

window.addEventListener('load', function() {
	var modeCookie = getCookie("mode");
    if(modeCookie !=null){
        if(modeCookie=='true') {
            document.body.classList.remove('dark');
            switchMode.checked = true;
        } else {
            document.body.classList.add('dark');
            switchMode.checked = false;
        }
    }
});

document.addEventListener("DOMContentLoaded", function () {

    // Handle save button click
    document.getElementById("start-button").addEventListener("click", function () {
        const toggleCheckbox = document.getElementById("display_checkbox"); 
        const displayGameInfo = toggleCheckbox.checked; 
        const jackpotPercent = document.getElementById("jackpot_percent").value;
        const jackpotAmount = document.getElementById("jackpot_amount").value;
    
        // Prepare data for submission
        const data = {
            jackpot_percent: jackpotPercent,
            jackpot_amount: jackpotAmount,
            display_info: displayGameInfo
        };
    
        // Send AJAX request to Django API
        fetch("/account/save-game-settings/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken() // Include CSRF token for security
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(responseData => {
            if (responseData.success) {
                alert("Game settings saved successfully!");
    
                // 1. Update display text for game info toggle
                document.getElementById("display_text").textContent = displayGameInfo ? "ON" : "OFF";
    
                // 2. Update checkbox state
                toggleCheckbox.checked = displayGameInfo;
                
                // 3. Optionally, you can also update other parts of the UI if needed
                jackpotAmount.value = responseData.jackpot_amount;
                jackpotPercent.value = responseData.jackpot_percent;
    
            } else {
                alert("Error saving game settings.");
            }
        })
        .catch(error => console.error("Error:", error));
    });

    // Function to get CSRF token from cookies
    function getCSRFToken() {
        const name = "csrftoken";
        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                return cookie.substring(name.length + 1);
            }
        }
        return "";
    }
});

