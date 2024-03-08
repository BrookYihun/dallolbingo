const gamediv = document.getElementById("gameid");
const gameid = gamediv.innerText;
const carddiv = document.getElementById("cardid");
const cardid = carddiv.innerText; 
const calledNumbers = [];
var intervalId;
const calledNumbersElement = document.getElementById("called-numbers");
const lastCalledNumberElement = document.getElementById("last-called");
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

function fetchRandomNumbers() {
  $.ajax({
      url: "/get-random-numbers/?paramName=" + gameid,  // Replace with the URL of your Django view
      type: "GET",
      success: function(response) {
          // Handle the response (e.g., update UI with the received numbers)
          var newValue = response.random_number;
          calledNumbers.push(newValue);
          updateCalledNumbersView();
      },
      error: function(xhr, status, error) {
          console.error("Failed to fetch random numbers:", error);
      }
  });
}

function checkBingo() {
  $.ajax({
      url: "/checkBingo/",  // Replace with the URL of your Django view
      type: "GET",
      data: {
        game: gameid,
        card: cardid // Replace 'value2' with the second parameter value you want to pass
      },
      success: function(response) {
          // Handle the response (e.g., update UI with the received numbers)
          console.log("Failed to fetch random numbers:", cardid);
      },
      error: function(xhr, status, error) {
          console.error("Failed to fetch random numbers:", error);
      }
  });
}


function startFetchingRandomNumbers() {
  intervalId = setInterval(fetchRandomNumbers, 5000); // Call fetchRandomNumbers every 5 seconds (5000 milliseconds)
}

// Function to stop fetching random numbers
function stopFetchingRandomNumbers() {
  clearInterval(intervalId); // Clear the interval to stop further calls to fetchRandomNumbers
}

document.getElementById("start-game").addEventListener("click", function() {
  startFetchingRandomNumbers(); // Start fetching random numbers when the "Start" button is clicked
});

document.getElementById("bingoButton").addEventListener("click", function() {
  stopFetchingRandomNumbers(); // Stop fetching random numbers when the "Bingo" button is clicked
  checkBingo();
});

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


