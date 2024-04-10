document.addEventListener("DOMContentLoaded", function () {
  const buttonsContainer = document.getElementById("buttons-container");
  const prevButton = document.getElementById("prev-btn");
  const nextButton = document.getElementById("next-btn");
  const playButton = document.getElementById("play-btn");
  const gamediv = document.getElementById("gameid");
  const gameid = gamediv.innerText;
  let startIndex = 0;
  const buttonsPerPage = 100;
  var selectedCardNumber = 0;
  let time = 60; // Initial time in seconds
  const timerDisplay = document.getElementById('timer');
  var timerInterval;

  if (selectedCardNumber == 0){
    playButton.disabled = true;
  }

  function generateButtons() {
      buttonsContainer.innerHTML = ""; // Clear previous buttons

      for (let i = startIndex; i < startIndex + buttonsPerPage && i < 1000; i++) {
          const button = document.createElement("button");
          button.type = "button";
          button.className = "btn btn-primary custom-btn";
          button.innerText = i + 1;
          button.addEventListener("click", function () {
            selectedCardNumber = i+1;
            fetchBingoCard(i + 1);
            playButton.disabled = false; // Call handleButtonClick function with button value
          });
          buttonsContainer.appendChild(button);
      }
  }

  generateButtons();

  // Function to disable buttons based on selected numbers
  function disableButtons(selectedNumbers) {
      const buttons = buttonsContainer.querySelectorAll(".custom-btn");
      buttons.forEach(button => {
          const number = parseInt(button.innerText);
          if (selectedNumbers.includes(number)) {
              button.disabled = true;
          } else {
              button.disabled = false;
          }
      });
  }

  prevButton.addEventListener("click", function () {
      if (startIndex >= buttonsPerPage) {
          startIndex -= buttonsPerPage;
          generateButtons();
      }
  });

  nextButton.addEventListener("click", function () {
      if (startIndex + buttonsPerPage < 1000) {
          startIndex += buttonsPerPage;
          generateButtons();
      }
  });

  playButton.addEventListener("click", function () {
    var form = document.createElement('form');
    form.method = 'POST';
    form.action = '/pick/'+gameid+'/'; // Replace with your Django view URL

    var csrftoken = getCookie('csrftoken');

    // Create a hidden input element for the CSRF token
    var csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrftoken;

    // Add the CSRF token input to the form
    form.appendChild(csrfInput);

    // Create an input element for the selected number
    var input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'selected_number';
    input.value = selectedCardNumber;

    // Add the input element to the form
    form.appendChild(input);

    // Append the form to the document body
    document.body.appendChild(form);

    // Submit the form
    form.submit();
    
  });

  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Sample array of selected numbers
  selectedNumbers = [];

  function fetchSelectedNumbers() {
    // Make an AJAX request to your Django view to fetch the updated list of selected numbers
    $.ajax({
      url:  "/get-selected-numbers/?paramName=" + gameid,  // Replace with your Django view URL
      type: "GET",
      success: function(response) {
        // Disable buttons based on the received list of selected numbers
        selectedNumbers = response.selectedNumbers;
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
        console.log(gameData);
        if (gameData.time_started != "0"){
          var start_time = new Date(gameData.time_started);
          var current_time = new Date();
          var dif_time = (current_time.getTime() - start_time.getTime()) / 1000;
          time = time - dif_time;
          time = Math.floor(time);
          if (time<0){
            window.location.href = 'http://5.75.175.113/';
          }
          timerInterval = setInterval(updateTimer, 1000);
        }
        disableButtons(selectedNumbers);
        
      },
      error: function(xhr, status, error) {
        console.error("Failed to fetch selected numbers:", error);
      }
    });
  }

  function fetchBingoCard(number) {
    // Make an AJAX request to your Django view to fetch the updated list of selected numbers
    $.ajax({
      url:  "/get-bingo-card/?paramName=" + number,  // Replace with your Django view URL
      type: "GET",
      success: function(response) {
        var bingoTable = JSON.parse(response);

        // Generate HTML table from the received bingo table data
        var tableHtml = "<table><tr><th>B</th><th>I</th><th>N</th><th>G</th><th>O</th></tr>";
        for (var i = 0; i < bingoTable.length; i++) {
          tableHtml += "<tr>";
          for (var j = 0; j < bingoTable[i].length; j++) {
            if(i==2&&j==2){
              tableHtml += "<td>" + "★" + "</td>";
            }else{
              tableHtml += "<td>" + bingoTable[i][j] + "</td>";
            }
          }
          tableHtml += "</tr>";
        }
        tableHtml += "</table>";

        // Display the HTML table
        document.getElementById("bingo-table-container").innerHTML = tableHtml;
      },
      error: function(xhr, status, error) {
        console.error("Failed to fetch card numbers:", error);
      }
    });
  }
  
  // Call the function to fetch selected numbers initially and then set up interval for real-time updates
  fetchSelectedNumbers();
  setInterval(fetchSelectedNumbers, 3000);
});

function updateTimer() {
  timerDisplay.innerText = time;
  if (time > 0) {
    time--;
  } else {
    clearInterval(timerInterval);
     // You can replace this with any other action when the timer reaches 0
  }
}
