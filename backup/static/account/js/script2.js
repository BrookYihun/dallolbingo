const setting_a = document.getElementById('setting');
const dash_a = document.getElementById('dashboard');
const switchMode = document.getElementById('switch-mode');
const menuBar = document.querySelector('#content nav .bx.bx-menu');
const saveButton = document.getElementById("start-button");
const selectedPatterns = document.getElementById("selectedPatterns");
const options = document.querySelectorAll(".option");
const toggleCheckbox = document.querySelector(".toggle-checkbox");

let patterns = [];
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
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


document.querySelector('.select-box').addEventListener('click', function () {
    const selectBox = this.parentElement;
    selectBox.classList.toggle('open'); // Toggle open class to show/hide options
});

function getPatternName(patternId) {
    const PATTERN_MAP = {
        "1": "Lines",
        "2": "Diagonals",
        "3": "Outside Box",
        "4": "Inside Box"
    };
    return PATTERN_MAP[patternId] || "Unknown Pattern";
}

// Handle selecting an option
document.querySelectorAll('.option').forEach(option => {
    option.addEventListener('click', function () {
        // Toggle 'selected' class on the clicked option
        this.classList.toggle('selected');

        // Update the displayed selected patterns
        const selectedPatterns = Array.from(document.querySelectorAll('.option.selected')).map(option => option.textContent).join(', ');
        document.getElementById('selectedPatterns').textContent = selectedPatterns || 'Choose Patterns';
        
        // Optionally save the selected values to cookies or send to server
        patterns = Array.from(document.querySelectorAll('.option.selected')).map(option => option.dataset.value);
        
    });
});

document.addEventListener("DOMContentLoaded", function () {

    // Handle save button click
    document.getElementById("start-button").addEventListener("click", function () {
        const toggleCheckbox = document.getElementById("display_checkbox"); 
        const displayGameInfo = toggleCheckbox.checked; 
        const selectedPatternsElements = document.querySelectorAll(".option.selected");
        const selectedPatterns = Array.from(selectedPatternsElements).map(option => option.dataset.value);
    
        // Prepare data for submission
        const data = {
            patterns: selectedPatterns,
            display_info: displayGameInfo
        };
    
        // Send AJAX request to Django API
        fetch("/backup/account/save-game-settings/", {
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
    
                // 3. Update the displayed list of selected patterns
                const patternList = document.getElementById("selectedPatternsList");
                patternList.innerHTML = ""; // Clear previous list
    
                if (selectedPatterns.length > 0) {
                    selectedPatterns.forEach(pattern => {
                        const li = document.createElement("li");
                        li.textContent = getPatternName(pattern); // Convert pattern ID to name
                        patternList.appendChild(li);
                    });
                } else {
                    patternList.innerHTML = "<li>No patterns selected.</li>";
                }
    
                // 4. Highlight selected options in the dropdown
                document.querySelectorAll(".option").forEach(option => {
                    if (selectedPatterns.includes(option.dataset.value)) {
                        option.classList.add("selected");
                    } else {
                        option.classList.remove("selected");
                    }
                });
    
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

