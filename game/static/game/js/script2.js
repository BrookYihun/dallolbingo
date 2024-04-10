const gamediv = document.getElementById("gameid");
const gameid = gamediv.innerText;
const carddiv = document.getElementById("cardid");
const cardid = carddiv.innerText; 
var calledNumbers = [];
var intervalId;
const calledNumbersElement = document.getElementById("called-numbers");
const lastCalledNumberElement = document.getElementById("last-called");
var countindex  = 0;
const serverUrl = '5.75.175.113';
let speech = new SpeechSynthesisUtterance();
let voices = [];
const startButton = document.getElementById("start-game");
const bingoButton = document.getElementById("bingoButton");
let time = 60; // Initial time in seconds
const timerDisplay = document.getElementById('timer');
var timerInterval;

window.speechSynthesis.onvoiceschanged = () => {
  voices = window.speechSynthesis.getVoices();
  speech.voice = voices [0];
};

speech.voice = voices[0];
// Host Code

let socket = null;

// Function to start the game and create WebSocket server
function connetToGame() {
    // Generate a unique game ID

    // Create WebSocket server
    socket = new WebSocket(`wss://${serverUrl}/ws/game-socket/${gameid}/`);

    // WebSocket event listeners
    socket.onopen = function(event) {
        console.log('WebSocket connection established.');
    };

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        // Handle messages received from players
        if (data.type == 'game_start'){
          startButton.disabled = true;
        }
        if (data.type == 'random_number') {
          randomNumbers = data.random_number;
          calledNumbers.push(randomNumbers);
          startButton.style.display = 'none';
          bingoButton.style.display = 'inline';
          updateCalledNumbersView();
        }
        if(data.type == 'result'){
          var message = data.data;
          var result = message[0];
          generateResultHTML(result);
        }
        if(data.type == 'timer_message'){
          startButton.disabled = true;
          var start_time = new Date(data.message);
          var current_time = new Date();
          var dif_time = (current_time.getTime() - start_time.getTime()) / 1000;
          time = time - dif_time;
          time = Math.floor(time);
          if (time<0){
            socket.close();
            window.location.href = 'http://5.75.175.113/';
          }
          timerInterval = setInterval(updateTimer, 1000);
        }
    };

    socket.onclose = function(event) {
        console.log('WebSocket connection closed.');
    };
}

window.onload = function() {
  connetToGame();
};

startButton.addEventListener("click", function () {
  const message = {
    type: 'game_start'
  }; 
  socket.send(JSON.stringify(message));
});

bingoButton.addEventListener("click",function(){
  const message = {
    type: 'bingo',
    card_id: cardid
  }; 
  socket.send(JSON.stringify(message));
});

// Define a function to generate the HTML dynamically
function generateResultHTML(cardResult) {
  var resultContainer = document.getElementById("blur-background");
  resultContainer.style.display = "block";
  var resultDiv = document.createElement("div");
  resultDiv.className = "result-container";

  var innerDiv = document.createElement("div");
  innerDiv.className = "result";
  innerDiv.id = "result";

  if (cardResult.message === 'Bingo') {
      // Handle Bingo message
      // Create and append necessary HTML elements
      var tableContainer = document.createElement("div");
      tableContainer.className = "table-container";

      var p = document.createElement("p");
      p.className = "bingo";
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
      var counter = 1;
      console.log(cardResult.winning_numbers);
      cardResult.card.forEach(function(row) {
        var tr = document.createElement("tr");
        row.forEach(function(cell) {
            var td = document.createElement("td");
            td.textContent = cell === 0 ? "★" : cell;
            if (cardResult.winning_numbers.includes(counter)) {
                td.className = "winning-row";
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

    socket.close();
    setTimeout(function() {
      window.location.href = 'http://5.75.175.113/';
      // Code to execute after 10 seconds
  }, 10000);

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

      socket.close();
      setTimeout(function() {
        window.location.href = 'http://5.75.175.113/';
        // Code to execute after 10 seconds
    }, 10000);
  }

  resultDiv.appendChild(innerDiv);
  resultContainer.appendChild(resultDiv);
}

function fetchBigoStat() {
  // Make an AJAX request to your Django view to fetch the updated list of selected numbers
  $.ajax({
    url:  "/get-bingo-stat/?paramName=" + gameid,  // Replace with your Django view URL
    type: "GET",
    success: function(response) {
      // Disable buttons based on the received list of selected numbers
      var gameData = JSON.parse(response.game);

      var gameStatRow = document.getElementById('game-stat');
      // Remove existing <td> elements
      while (gameStatRow.firstChild) {
        gameStatRow.removeChild(gameStatRow.firstChild);
      }
      // Add new <td> elements with game data
      gameStatRow.innerHTML += '<td>' + gameData.game_id + '</td>';
      gameStatRow.innerHTML += '<td>' + gameData.stake + '</td>';
      gameStatRow.innerHTML += '<td>' + gameData.number_of_players + '</td>';
      gameStatRow.innerHTML += '<td>' + gameData.winner_price + '</td>';
      
    },
    error: function(xhr, status, error) {
      console.error("Failed to fetch bigo stat:", error);
    }
  });
}

document.addEventListener("DOMContentLoaded", function () {

  calledNumbers.forEach((number, index) => {
    const numberElement = document.createElement("div");
    numberElement.classList.add("called-number");
    numberElement.textContent = number;
    if (index == calledNumbers.length-1) {
      numberElement.classList.add("recent-called");
      lastCalledNumberElement.appendChild(numberElement);
    }else{
      calledNumbersElement.appendChild(numberElement);
    }
  });
  fetchBigoStat();
  setInterval(fetchBigoStat, 3000);
});

function updateCalledNumbersView() {
  // Clear the existing numbers from the DOM
  calledNumbersElement.innerHTML = "";
  lastCalledNumberElement.innerHTML = "";

  // Define the ranges and corresponding letters
  const ranges = [
    { min: 1, max: 15, letter: "B" },
    { min: 16, max: 30, letter: "I" },
    { min: 31, max: 45, letter: "N" },
    { min: 46, max: 60, letter: "G" },
    { min: 61, max: 75, letter: "O" }
  ];

  // Determine the number of recent numbers to display
  const recentNumbersCount = Math.min(calledNumbers.length, 7);

  // Rebuild the list based on the updated calledNumbers array
  for (let i = 0; i < recentNumbersCount; i++) {
    const number = calledNumbers[calledNumbers.length - recentNumbersCount + i];
    const numberElement = document.createElement("div");
    numberElement.classList.add("called-number");
    
    // Determine the corresponding letter based on the number's range
    let letter = "";
    for (const range of ranges) {
      if (number >= range.min && number <= range.max) {
        letter = range.letter;
        break;
      }
    }
    
    // Add the letter and number to the element's text content
    numberElement.textContent = letter + "-" + number;

    // Add the appropriate class for the most recent called number
    if (i == recentNumbersCount - 1) {
      numberElement.classList.add("recent-called");
      lastCalledNumberElement.appendChild(numberElement);
      speech.text= numberElement.textContent;
            window.speechSynthesis.speak(speech);
    } else {
      calledNumbersElement.appendChild(numberElement);
    }
  }
}
var bingo_numbers = document.getElementsByClassName("bingo-number");

    // Add event listener to each button
    for (var i = 0; i < bingo_numbers.length; i++) {
        bingo_numbers[i].addEventListener("click", function() {
            // Your event handling code here
            if (this.classList.contains("highlighted")) {
              this.classList.remove("highlighted");
          } else {
              this.classList.add("highlighted");
          }
        });
    }
    window.onbeforeunload = function() {
      socket.close();
    };

function updateTimer() {
  timerDisplay.innerText = time;
  if (time > 0) {
    time--;
  } else {
    clearInterval(timerInterval);
     // You can replace this with any other action when the timer reaches 0
  }
}




