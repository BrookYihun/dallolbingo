// Wait for the page to fully load
const fullscreen = document.getElementById('full-screen');

const allSideMenu = document.querySelectorAll('#sidebar .side-menu.top li a');

// TOGGLE SIDEBAR
const menuBar = document.querySelector('#content nav .bx.bx-menu');
const sidebar = document.getElementById('sidebar');

var numberElements = document.querySelectorAll('.number');
var calledNumbers = [];
var callednumberdisplay = document.getElementById('called-numbers');
var lastletter = document.getElementById('last-letter');
var lastnum = document.getElementById('last-num');
var callingSpeedRange = document.getElementById('callingSpeed');
var callingSpeedTxt = document.getElementById('callingSpeedTxt');
var callinginterval = 5000;
var autoIntervalId = null;
var autoPlaying = false;
var selectedLanguage = "am";
let speech = new SpeechSynthesisUtterance();
let voices = [];
let bonus_c = document.getElementById('bonus_animation');
let bonus_t = document.getElementById('bonus_text');
let free_c = document.getElementById('free_hit');
let free_t = document.getElementById('free_hit_text');
let jackpot_c = document.getElementById('jackpot');
let jackpot_t = document.getElementById('jackpot_text');

menuBar.addEventListener('click', function () {
	sidebar.classList.toggle('hide');
})


if(window.innerWidth < 768) {
	sidebar.classList.add('hide');
}

const switchMode = document.getElementById('switch-mode');

switchMode.addEventListener('change', function () {
    deleteCookie("mode");
    setCookie("mode",this.checked,7);
	if(this.checked) {
		document.body.classList.remove('dark');
	} else {
		document.body.classList.add('dark');
	}
})
window.addEventListener('load', function() {
    // Get the loader element
    var loader = document.getElementById('loader');

    // Hide the loader element
    loader.style.display = 'none';

    var footer = document.getElementById('footer');
    var bingo_con = document.getElementById('bingo-container');
    var index_a = this.document.getElementById('index');

    index_a.classList.add('active');
    footer.style.display = "block";
    bingo_con.style.display = "block";

    var cookieLanguage = getCookie("selectedLanguage");
    if (cookieLanguage!=null){
        if (cookieLanguage == "am"){
        callerLanguageSelect.selectedIndex = 0;
        selectedLanguage = "am";
        }else if (cookieLanguage == "mm"){
        callerLanguageSelect.selectedIndex = 1;
        selectedLanguage = "mm";
        }else if (cookieLanguage == "mm2"){
        callerLanguageSelect.selectedIndex = 2;
        selectedLanguage = "mm2";
		}else{
        selectedLanguage = 0;
        callerLanguageSelect.selectedIndex = 5;
        }
    }
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

    var speed = getCookie("speed");
    if(speed != null){
        callingSpeedRange.value = speed;
        const invertedValue = 12 - (speed - 2);
        callinginterval = invertedValue *1000;
        callingSpeedTxt.textContent = "Auto call " + invertedValue +" secounds";
    }

});

// Function to toggle light mode and dark mode

// Function to toggle full screen mode
function toggleFullScreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
    }
}

// Event listener for clicking on full screen image
fullscreen.addEventListener("click", toggleFullScreen);

var callerLanguageSelect = document.getElementById('lang');

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

callerLanguageSelect.addEventListener('change', function() {
    // Update the language for call-out-loud
    const selectedLanguage = callerLanguageSelect.value;
    deleteCookie("selectedLanguage");
    setCookie("selectedLanguage", selectedLanguage, 7);

    if (!['am', 'mm', 'mm2'].includes(selectedLanguage)) {
        speech.voice = voices[0];
    }
});

callingSpeedRange.addEventListener('input', function() {
    var newSpeed = callingSpeedRange.value;
    const invertedValue = 12 - (newSpeed - 2);
    callinginterval = invertedValue *1000;
    callingSpeedTxt.textContent = "Auto call " + invertedValue +" secounds";
    deleteCookie("speed");
    setCookie("speed",newSpeed,7);
    // Convert speed to milliseconds
});

function updateTotalCalled() {
    var totalCalledClock = document.getElementById('total-called');
    totalCalledClock.textContent = calledNumbers.length + " CALLED";
}

function callNumber() {
    var remainingNumbers = getRemainingNumbers();
    callednumberdisplay.style.display = "block";

    if (remainingNumbers.length === 0) {
        alert("All numbers have been called!");
        return;
    }

    var randomIndex = Math.floor(Math.random() * remainingNumbers.length);
    var selectedNumber = remainingNumbers[randomIndex];

    calledNumbers.push(selectedNumber);

    var numberElement = document.querySelector('.number[data-number="' + selectedNumber + '"]');
    if (numberElement) {
        changeBlink(selectedNumber);
    }

    var rowIndex = Math.floor(selectedNumber / 15); // Calculate the row index
    var letter = 'B';
    if(selectedNumber <=15){
        letter='B';
    }
    else if(selectedNumber <=30){
        letter='I';
    }
    else if(selectedNumber <=45){
        letter='N';
    }
    else if(selectedNumber <=60){
        letter='G';
    }
    else if(selectedNumber <=75){
        letter='O';
    }// Get the corresponding letter
    var numStr = selectedNumber.toString();  // Convert the number to a string

      // Create the desired string format by inserting a space between characters
    var resultStr = numStr.split('').join(' ');
    var displayedNumber = letter + (selectedNumber) + ", " + letter + "," + resultStr; // Calculate the displayed number
    // This will log: "1 5"

    selectedLanguage = getLanguage();
    if (selectedLanguage=='am'){
        filePath = "/static/game/audio/Voice "+selectedNumber+".mp3";
        var audio = new Audio(filePath);
        audio.play();
    }else if (selectedLanguage=='mm'){
        filePath = "/static/game/audio/male/"+selectedNumber+".mp3";
        var audio = new Audio(filePath);
        audio.play();
    }else if (selectedLanguage=='mm2'){
        filePath = "/static/game/audio/bingo/"+selectedNumber+".wav";
        var audio = new Audio(filePath);
        audio.play();
    }else{
        speech.voice = voices[0];
        speech.text = displayedNumber;
        window.speechSynthesis.speak(speech);
    }

    //var displayedNumber = letter + (selectedNumber) + ", " + letter + "," + resultStr; // Calculate the displayed number
    lastletter.textContent = letter;
    lastnum.textContent = selectedNumber;

    updateLastCalledNumbers();
    updateTotalCalled();

  }
  
 function changeBlink(number) {
    const container = document.getElementById('bingo-num-container');
    
    // Remove blink class from any previously blinking divs
    if (calledNumbers.length>1) {
        const previousBlinkingDiv = container.querySelector('.blink');
        previousBlinkingDiv.classList.remove('blink');
        previousBlinkingDiv.classList.add('selected');
    }
    
    // Find the div with the specified ID
    const divToBlink = document.querySelector('.number[data-number="' + number + '"]');
    if (divToBlink) {
        // Add the blink class to the specified div
        divToBlink.classList.add('blink');
    } else {
        console.warn(`No div found with ID: ${number}`);
    }
}

function updateLastCalledNumbers() {
    var lastCalledNumbersElement = document.getElementById('lastCalledNumbers');
    lastCalledNumbersElement.innerHTML = '';

    for (var i = Math.max(0, calledNumbers.length - 4); i < calledNumbers.length; i++) {
        var number = calledNumbers[i];
        var numberElement = document.createElement('div');
        numberElement.classList.add('last-called-num');
        var letter = 'B';
        if(number <=15){
            letter='B';
        }
        else if(number <=30){
            letter='I';
        }
        else if(number <=45){
            letter='N';
        }
        else if(number <=60){
            letter='G';
        }
        else if(number <=75){
            letter='O';
        }
        numberElement.textContent = letter+" "+number;
        lastCalledNumbersElement.appendChild(numberElement);
    }
}

var startbtn = document.getElementById('start-auto-play');
var callnextbtn = document.getElementById('call-next');
var finshbtn = document.getElementById('finsh');
var newgamebtn = document.getElementById('start-new-game');
var shuffle_btn = document.getElementById('shuffle');
var check_btn = document.getElementById('check-btn');
var game_id = document.getElementById("game-id");

startbtn.onclick = function(){
    selectedLanguage = getLanguage();
    if (autoPlaying) {
        startbtn.textContent = "START AUTO PLAY";
        if (selectedLanguage=='am'){
            filePath = "/static/game/audio/stop.mp3";
            var audio = new Audio(filePath);
            audio.play();
        }else if (selectedLanguage === 'mm' || selectedLanguage === 'mm2') {
            filePath = "/static/game/audio/male/stop.mp3";
            var audio = new Audio(filePath);
            audio.play();
        }else{
            speech.voice = voices[0];
            speech.text="game paused";
            window.speechSynthesis.speak(speech);
        }
        stopAuto();
    }else {
        startbtn.textContent = "STOP AUTO PLAY";
        if (selectedLanguage=='am'){
            filePath = "/static/game/audio/start.mp3";
            var audio = new Audio(filePath);
            audio.play();
        }else if (selectedLanguage === 'mm' || selectedLanguage === 'mm2') {
            filePath = "/static/game/audio/male/start.mp3";
            var audio = new Audio(filePath);
            audio.play();
        }else{
            speech.voice = voices[0];
            speech.text="game started";
            window.speechSynthesis.speak(speech);
        }
        startAuto();
    }
};

function startAuto() {
    callnextbtn.classList.add('inactive');
    shuffle_btn.classList.add('inactive');
    finshbtn.classList.add('inactive');
    check_btn.classList.add('inactive');

    if (autoIntervalId) {
        clearInterval(autoIntervalId);
        autoIntervalId = null;
        alert("Stopped");
        return;
    }

    autoIntervalId = setInterval(function () {
        callNumber();
        var remainingNumbers = getRemainingNumbers();
        if (remainingNumbers.length === 0) {
            clearInterval(autoIntervalId);
            autoIntervalId = null;
        }
    }, callinginterval);
    autoPlaying = true;
}

function stopAuto() {
    finshbtn.classList.remove('inactive');
    check_btn.classList.remove('inactive');
    clearInterval(autoIntervalId);
    autoIntervalId = null;
    autoPlaying = false;
}

function getRemainingNumbers() {
    var allNumbers = Array.from(document.querySelectorAll('.number'));
    var remainingNumbers = allNumbers.filter(function (numberElement) {
        return !numberElement.classList.contains('selected') && !numberElement.classList.contains('blink');
    });

    return remainingNumbers.map(function (numberElement) {
        return parseInt(numberElement.getAttribute('data-number'));
    });
}


callnextbtn.onclick = function(){
    callNumber();
};

finshbtn.onclick = function(){
    startbtn.style.display = "none";
    callnextbtn.style.display = "none";
    finshbtn.style.display = "none";
    newgamebtn.style.display = "block";
    shuffle_btn.style.display = "block";
    shuffle_btn.classList.remove('inactive');
    $.ajax({
        url:  "/finish/",  // Replace with your Django view URL
        type: "GET",
        data: {
          called: JSON.stringify(calledNumbers),
          game: game_id.innerText,
          // Add more parameters as needed
      },
        success: function(response) {
          // Disable buttons based on the received list of selected numbers
  
          var result = response.result;
          
        },
        error: function(xhr, status, error) {
          console.error("Failed to check result", error);
        }
      });
};

check_btn.onclick = function () {
    const check_num = document.getElementById('check-num').value;
    if (check_num.trim() === "") {
        alert("Input field cannot be empty");
        return false; // Prevent form submission
    }else{
        checkBingo(check_num);
    }
}

function checkBingo(num) {
    // Make an AJAX request to your Django view to fetch the updated list of selected numbers
    let patterns = [];

try {
  const cookieValue = getCookie("Patterns");
  if (cookieValue) {
    patterns = JSON.parse(decodeURIComponent(cookieValue));
  }
} catch (error) {
  console.error("Error parsing patterns cookie:", error);
  patterns = [];
}

console.log(patterns);
    $.ajax({
      url:  "/check/",  // Replace with your Django view URL
      type: "GET",
      data: {
        card: num,
        called: JSON.stringify(calledNumbers),
        game: game_id.innerText,
        patterns: JSON.stringify(patterns),
        // Add more parameters as needed
    },
      success: function(response) {
        // Disable buttons based on the received list of selected numbers

        var result = response.result;

        if (result[0].message == "Bingo" || result[0].message == "No Bingo"){
            generateResultHTML(result[0],response.game);
        }else{
            alert(result[0].message);
        }
        
      },
      error: function(xhr, status, error) {
        console.error("Failed to check result", error);
      }
    });
  }

  function generateResultHTML(cardResult,game) {
    var resultContainer = document.getElementById("blur-background");
    resultContainer.style.display = "block";
    var resultDiv = document.createElement("div");
    resultDiv.className = "result-container";
  
    var innerDiv = document.createElement("div");
    innerDiv.className = "result";
    innerDiv.id = "result";
  
    if (cardResult.message === 'Bingo') {

        if(cardResult.bonus >0){
            bonus_c.style.display = "block";
            bonus_t.innerText = cardResult.bonus + "Price Bonus";
            let count = 0;
            filePath = "/static/game/audio/bonus.mp3";
            var audio = new Audio(filePath);
            audio.play();
            const intervalId = setInterval(() => {
                launchConfetti();
                count++;
                if (count >= 3) {
                    clearInterval(intervalId);
                }
            }, 1000); 
        }

        if(cardResult.free >0 && !cardResult.remaining_numbers){
            free_c.style.display = "block";
            free_t.innerText = "Card Number "+ cardResult.free;
            let count = 0;
            const intervalId = setInterval(() => {
                launchConfetti();
                count++;
                if (count >= 3) {
                    clearInterval(intervalId);
                }
            }, 1000); 
        }

        if(cardResult.jackpot_won){
            jackpot_c.style.display = "block";
            jackpot_t.innerText = "$ "+ cardResult.jackpot_payout + " $";
            let count = 0;
            const intervalId = setInterval(() => {
                launchConfetti();
                count++;
                if (count >= 3) {
                    clearInterval(intervalId);
                }
            }, 1000);
        }

        // Make sure card is complete (no remaining numbers)
        if (!cardResult.remaining_numbers) {

            // All three occur
            if (cardResult.bonus > 0 && cardResult.free > 0 && cardResult.jackpot_won) {
                console.log("Bonus + Free + Jackpot");

                // Example positions for 3 elements
                bonus_c.style.left = '25%';
                free_c.style.left = '50%';
                jackpot_c.style.left = '75%';

            } 
            // Bonus + Free only
            else if (cardResult.bonus > 0 && cardResult.free > 0) {
                console.log("Bonus + Free");

                bonus_c.style.left = '38%';
                free_c.style.left = '62%';
            } 
            // Bonus + Jackpot only
            else if (cardResult.bonus > 0 && cardResult.jackpot_won) {
                console.log("Bonus + Jackpot");

                bonus_c.style.left = '38%';
                jackpot_c.style.left = '62%';

            } 
            // Free + Jackpot only
            else if (cardResult.free > 0 && cardResult.jackpot_won) {
                console.log("Free + Jackpot");

                free_c.style.left = '38%';
                jackpot_c.style.left = '62%';

            }
        }

        // Handle Bingo message
        // Create and append necessary HTML elements
        var tableContainer = document.createElement("div");
        tableContainer.className = "table-container";
  
        var p = document.createElement("p");
        p.className = "bingo";
        var audiotxt = "yesbingo";
        if(cardResult.remaining_numbers){
            p.textContent = cardResult.card_name + " - Bad " + cardResult.message;
            audiotxt = "passbingo";
        }else{
            p.textContent = cardResult.card_name + " - Good " + cardResult.message;
            audiotxt = "yesbingo";
        }
        
        tableContainer.appendChild(p);
  
        var table = document.createElement("table");
        var tr = document.createElement("tr");
        var thLetters = ["B", "I", "N", "G", "O"];
        thLetters.forEach(function(letter) {
            var th = document.createElement("th");
            th.textContent = letter;
            tr.appendChild(th);
        });
        table.appendChild(tr);
        var counter = 1;
        const lastNumber = calledNumbers[calledNumbers.length - 1];
        cardResult.card.forEach(function(row) {
          var tr = document.createElement("tr");
          row.forEach(function(cell) {
              var td = document.createElement("td");
              td.textContent = cell === 0 ? "★" : cell;
              if (cardResult.winning_numbers.includes(counter)) {
                if(cardResult.remaining_numbers){
                    td.className = "miss-winning-row";
                }else{
                    td.className = "winning-row";
                    if(cell === lastNumber){
                        td.classList.add("blink-result");
                    }
                }
              }else if (calledNumbers.includes(cell)) {
                td.className = "remaining-number";
              }
              tr.appendChild(td);
              counter++;
          });
          table.appendChild(tr);
      });
  
      tableContainer.appendChild(table);
      innerDiv.appendChild(tableContainer);
      var closeButton = document.createElement("button");
        closeButton.textContent = "Close";
        closeButton.className = "buttons";
        closeButton.addEventListener("click", function() {
            // Functionality to close the container
            bonus_c.style.display = "none";
            free_c.style.display = "none";
            jackpot_c.style.display = "none";
            while (resultContainer.firstChild) {
                resultContainer.removeChild(resultContainer.firstChild);
            }
            // Remove the tableContainer itself from its parent node
            resultContainer.style.display = "none";
        });
        tableContainer.appendChild(closeButton);

        if(cardResult.remaining_numbers){
            var blockButton = document.createElement("button");
            blockButton.textContent = "Block";
            blockButton.addEventListener("click", function() {
                blockCard(cardResult.card_name,game);
            });
            blockButton.className = "buttons";
            tableContainer.appendChild(blockButton);

        }

        if (selectedLanguage=='am'){
            filePath = "/static/game/audio/male/"+audiotxt+".mp3";
            var audio = new Audio(filePath);
            audio.play();
        }else if (selectedLanguage === 'mm' || selectedLanguage === 'mm2') {
            filePath = "/static/game/audio/male/"+audiotxt+".mp3";
            var audio = new Audio(filePath);
            audio.play();
        }else{
            speech.voice = voices[0];
            if(audiotxt == "yesbingo"){
                speech.text="We have a Winner";
            }else{
                speech.text="No Winner";
            }
            window.speechSynthesis.speak(speech);
        }

        // Appending buttons to the tableContainer
  
    } else {

        // Handle No Bingo message
        var tableContainer = document.createElement("div");
        tableContainer.className = "table-container";
  
        var p = document.createElement("p");
        p.className = "no-bingo";
        p.textContent = cardResult.card_name + " - " + cardResult.message;
        tableContainer.appendChild(p);
  
        var table = document.createElement("table");
        var tr = document.createElement("tr");
        var thLetters = ["B", "I", "N", "G", "O"];
        thLetters.forEach(function(letter) {
            var th = document.createElement("th");
            th.textContent = letter;
            tr.appendChild(th);
        });
        table.appendChild(tr);
  
        cardResult.card.forEach(function(row) {
            var tr = document.createElement("tr");
            row.forEach(function(cell) {
                var td = document.createElement("td");
                td.textContent = cell === 0 ? "★" : cell;
                if (calledNumbers.includes(cell)) {
                    td.className = "remaining-number";
                }else if(cell==0){
                  td.className = "remaining-number";
                }
                tr.appendChild(td);
            });
            table.appendChild(tr);
        });
  
        tableContainer.appendChild(table);
        innerDiv.appendChild(tableContainer);

        var closeButton = document.createElement("button");
        closeButton.textContent = "Close";
        closeButton.className = "buttons";
        closeButton.addEventListener("click", function() {
            // Functionality to close the container
            while (resultContainer.firstChild) {
                resultContainer.removeChild(resultContainer.firstChild);
            }
            // Remove the tableContainer itself from its parent node
            resultContainer.style.display = "none";
        });

        var blockButton = document.createElement("button");
        blockButton.textContent = "Block";
        blockButton.addEventListener("click", function() {
            blockCard(cardResult.card_name,game);
        });
        blockButton.className = "buttons";

        // Appending buttons to the tableContainer
        tableContainer.appendChild(closeButton);
        tableContainer.appendChild(blockButton);

        if (selectedLanguage=='am'){
            filePath = "/static/game/audio/male/nobingo.mp3";
            var audio = new Audio(filePath);
            audio.play();
        }else if (selectedLanguage === 'mm' || selectedLanguage === 'mm2') {
            filePath = "/static/game/audio/male/nobingo.mp3";
            var audio = new Audio(filePath);
            audio.play();
        }else{
            speech.voice = voices[0];
            speech.text="No Bingo";
            window.speechSynthesis.speak(speech);
        }
      
  
    }
  
    resultDiv.appendChild(innerDiv);
    resultContainer.appendChild(resultDiv);
  }
function blockCard(card_id,game){
$.ajax({
    url:  "/block/",  // Replace with your Django view URL
    type: "GET",
    data: {
      card: card_id,
      game: game,
      // Add more parameters as needed
  },
    success: function(response) {
      // Disable buttons based on the received list of selected numbers
      var resultContainer = document.getElementById("blur-background");
      while (resultContainer.firstChild) {
        resultContainer.removeChild(resultContainer.firstChild);
    }
    // Remove the tableContainer itself from its parent node
    resultContainer.style.display = "none";
      
    },
    error: function(xhr, status, error) {
      alert("Failed to  Block user");
    }
  });
}


let shuffleInterval;
// Variable to store the shuffle interval

// Function to shuffle the class of numbers
function shuffleNumbers() {
    // Remove the "selected" class from all numbers
    numberElements.forEach((numberElement) => {
        numberElement.classList.remove('selected');
        numberElement.classList.remove('blink');
    });

    // Randomly select one number and add the "selected" class to it
    const randomIndex = Math.floor(Math.random() * numberElements.length);
    const selectedNumber = numberElements[randomIndex];
    const selectedNumber2 = numberElements[randomIndex - 3];
    const selectedNumber3 = numberElements[randomIndex * 2];
    const selectedNumber4 = numberElements[randomIndex * 3];
    const selectedNumber5 = numberElements[randomIndex + 7];

    // Adding the "selected" class to the selected numbers
    if (selectedNumber) selectedNumber.classList.add('selected');
    if (selectedNumber2) selectedNumber2.classList.add('selected');
    if (selectedNumber3) selectedNumber3.classList.add('selected');
    if (selectedNumber4) selectedNumber4.classList.add('selected');
    if (selectedNumber5) selectedNumber5.classList.add('selected');
}

function shuffleBoard() {
    const audioPlayer = document.getElementById("audioPlayer");
    audioPlayer.loop = true; // Set audio to loop
    audioPlayer.play();
    
    shuffleInterval = setInterval(shuffleNumbers, 115); // Shuffle every 115 milliseconds
    calledNumbers.length = 0;
    updateLastCalledNumbers();
}

function stopShuffleBoard() {
    const audioPlayer = document.getElementById("audioPlayer");
    audioPlayer.pause();
    audioPlayer.currentTime = 0;
    clearInterval(shuffleInterval); // Clear the shuffle interval
    numberElements.forEach((numberElement) => {
        numberElement.classList.remove('selected');
    });
}

shuffle_btn.onclick = function () {
    if (shuffle_btn.innerText === "SHUFFLE") {
        shuffleBoard();
        shuffle_btn.innerText = "STOP";
        callnextbtn.classList.add('inactive');
        startbtn.classList.add('inactive');
        finshbtn.classList.add('inactive');
        check_btn.classList.add('inactive');
    } else {
        stopShuffleBoard();
        shuffle_btn.innerText = "SHUFFLE";
        callnextbtn.classList.remove('inactive');
        startbtn.classList.remove('inactive');
        finshbtn.classList.remove('inactive');
        check_btn.classList.remove('inactive');
    }
};
function launchConfetti() {
    const canvas = document.getElementById('confetti-canvas');
    const myConfetti = confetti.create(canvas, {
        resize: true,
        useWorker: true
    });

    // Launch confetti from the left-bottom
    myConfetti({
        particleCount: 100,
        spread: 70,
        origin: { x: 0, y: 1 }
    });

    // Launch confetti from the right-bottom
    myConfetti({
        particleCount: 100,
        spread: 70,
        origin: { x: 1, y: 1 }
    });

    // Launch confetti from behind the div
    setTimeout(() => {
        myConfetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 }
        });
    }, 500);

    // Repeat the confetti effect 3 times
    for (let i = 1; i < 3; i++) {
        setTimeout(() => {
            myConfetti({
                particleCount: 100,
                spread: 70,
                origin: { x: 0, y: 1 }
            });
            myConfetti({
                particleCount: 100,
                spread: 70,
                origin: { x: 1, y: 1 }
            });
            setTimeout(() => {
                myConfetti({
                    particleCount: 100,
                    spread: 70,
                    origin: { y: 0.6 }
                });
            }, 500);
        }, i * 2000);
    }
}

var viewAllCalledButton = document.getElementById("viewAllCalledButton");
var viewAllCalledModal = document.getElementById("viewAllCalledModal");
var closeViewAllCalled = document.getElementById("closeViewAllCalled");
var recentlyCalledNumbers = document.getElementById("recentlyCalledNumbers");

// Function to display the recently called numbers in the pop-up modal
function displayRecentlyCalledNumbers() {
    recentlyCalledNumbers.innerHTML = "";
    for (var i = 0; i < calledNumbers.length; i++) {
        var number = calledNumbers[i];
        var numberElement = document.createElement('div');
        numberElement.classList.add('last-called-num-view-all');
        var letter = 'B';
        if(number <=15){
            letter='B';
        }
        else if(number <=30){
            letter='I';
        }
        else if(number <=45){
            letter='N';
        }
        else if(number <=60){
            letter='G';
        }
        else if(number <=75){
            letter='O';
        }
        numberElement.textContent = letter+" "+number;
        numberElement.setAttribute('data-letter', letter);
        recentlyCalledNumbers.appendChild(numberElement);
    }
}

// Add a click event listener to the "View All Called" button
viewAllCalledButton.addEventListener("click", function () {
    // Display the pop-up modal
    viewAllCalledModal.style.display = "block";
    var resultContainer = document.getElementById("blur-background");
    resultContainer.style.display = "block";
    // Call the function to display recently called numbers
    displayRecentlyCalledNumbers();
});

// Add a click event listener to close the pop-up modal
closeViewAllCalled.onclick = function () {
    viewAllCalledModal.style.display = "none";
    var resultContainer = document.getElementById("blur-background");
    resultContainer.style.display = "none";
};
