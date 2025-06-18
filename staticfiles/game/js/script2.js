const container = document.getElementById('container');
const startButton = document.getElementById('start-button');
const gameForm = document.getElementById('game-form');
const numbers = [];
let selectedNumbers=[];
var other_selected = [];
const moreNumber = document.getElementById('more');
const clearbtn = document.getElementById('clear');
const bonus = document.getElementById('bonus');
const free = document.getElementById('free');
const cashier = document.getElementById('cashier').innerText;

function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + encodeURIComponent(JSON.stringify(value)) + expires + "; path=/";
  }

  function getCookie(name) {
    var nameEQ = name + "=";
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i];
        while (cookie.charAt(0) == ' ') {
            cookie = cookie.substring(1, cookie.length);
        }
        if (cookie.indexOf(nameEQ) == 0) {
            var cookieValue = cookie.substring(nameEQ.length, cookie.length);
            return JSON.parse(decodeURIComponent(cookieValue));
        }
    }
    return null;
  }

  function deleteCookie(cookieName) {
      document.cookie = `${cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
  }

clearbtn.addEventListener('click',()=>{
    deleteCookie("selectedPlayers");
    var divs = container.querySelectorAll(".box");
    var boundary = 100;
    if(buttonText=="1-100"){
        boundary = 200;
    }
    for (var i = 0; i <boundary; i++) {
        if (selectedNumbers.includes(i+1)){
            divs[i].classList.remove('selected');
        }
    }
    selectedNumbers=[];
});

moreNumber.addEventListener('click',()=>{
    var buttonText = moreNumber.textContent;
    if(buttonText=="100-200"){
        moreNumber.textContent = "1-100";
        add();
    }else{
        moreNumber.textContent = "100-200";
        remove();
    }
    
});

function add(){
      for (let i = 101; i <= 200; i++) {
      const box = document.createElement('div');
      box.textContent = i;
      box.classList.add('box');

      box.addEventListener('click', () => {
          if (selectedNumbers.includes(i)) {
              selectedNumbers = selectedNumbers.filter(num => num !== i);
              box.classList.remove('selected');
              if(cashier=="True"){
                remove_player(i);
              }
          } else {
              selectedNumbers.push(i);
              box.classList.add('selected');
              if(cashier=="True"){
                add_player(i);
              }
          }
          startButton.disabled = selectedNumbers.length === 0;
          updateTotalSelected();
      });

      container.appendChild(box);
  }
}
function remove(){
    var divs = container.querySelectorAll(".box");
    for (var i = 100; i <200; i++) {
      container.removeChild(divs[i]);
    }
}

// Create number boxes


// ... Your existing JavaScript ...

// Inside the form submission event listener
const game_id = document.getElementById('game').innerText;
gameForm.addEventListener('submit', (e) => {
    e.preventDefault();

    if (selectedNumbers.length === 0) {
        return;
    }

    // Create a hidden input element for each selected number
    selectedNumbers.forEach(number => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'players';
        input.value = number;
        gameForm.appendChild(input);
    });

    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'game';
    input.value = game_id;
    gameForm.appendChild(input);
    deleteCookie("Stake");
    var v = document.getElementById("stake").value;
    setCookie("Stake",v,7);

    deleteCookie("Bonus");
    var b = bonus.checked;
    setCookie("Bonus",b,7);

    deleteCookie("Free");
    var f = free.checked;
    setCookie("Free",f,7);

    // Submit the form to the 'bingo' URL
    gameForm.method = 'POST';
    gameForm.submit();
});

function updateTotalSelected() {
    deleteCookie("selectedPlayers");
    setCookie("selectedPlayers",selectedNumbers,7);
    //document.getElementById('win').value = selectedNumbers.length * document.getElementById('stake').value;
}

function get_game_stat(){
    $.ajax({
        url:  "/get_game_stat/",  // Replace with your Django view URL
        type: "GET",
        data:{
            game: game_id
        },
        success: function(response) {
            if (response.message === 'None') {
                
            } else {
                other_selectedStr = Array.isArray(response.selected_players) ? response.selected_players : [];
                other_selected = other_selectedStr.map(str => parseInt(str, 10));
                selectedNumbersStr = Array.isArray(response.main_selected) ? response.main_selected : [];
                selectedNumbers = selectedNumbersStr.map(str => parseInt(str, 10));
                update_view();
            }
        },
        error: function(xhr, status, error) {
          alert("Failed to get data");
        }
      });
}

function update_view(){
    var boxes = document.querySelectorAll('.box');

    boxes.forEach(function(box) {
        var innerTextStr = box.innerText.trim(); // Get inner text and trim whitespace
        var innerText = parseInt(innerTextStr, 10);
        // Check if inner text is in the numbersToMatch array
        if (selectedNumbers.includes(innerText)) {
            // Do something with the matching box element, e.g., add a class
            box.classList.add('selected');
        }else if (other_selected.includes(innerText)) {
            // Do something with the matching box element, e.g., add a class
            box.classList.add('selected');
            box.classList.add('blured');
        }
        else {
            box.classList.remove('selected');
            box.classList.remove('blured');
        }
    });

    document.getElementById('num').innerHTML = selectedNumbers.length;
}

window.onload = function() {
    for (let i = 1; i <= 100; i++) {
        const box = document.createElement('div');
        box.textContent = i;
        box.classList.add('box');
    
        box.addEventListener('click', () => {
            if (selectedNumbers.includes(i)) {
                selectedNumbers = selectedNumbers.filter(num => num !== i);
                box.classList.remove('selected');
                if(cashier=="True"){
                    remove_player(i);
                }
            } else {
                selectedNumbers.push(i);
                box.classList.add('selected');
                if(cashier=="True"){
                    add_player(i);
                }
            }
            startButton.disabled = selectedNumbers.length === 0;
            updateTotalSelected();
        });
    
        container.appendChild(box);
    }

    var stake = getCookie("Stake");
    if(stake !=null){
        document.getElementById("stake").value = stake;
    }

    var b = getCookie("Bonus");
    if (b!=null){
        bonus.checked = b;
    }

    var f = getCookie("Free");
    if (f!=null){
        free.checked = f;
    }
    if(cashier!="True"){
        var selectedPlayersStr = getCookie("selectedPlayers");
        if (selectedPlayersStr!=null){
            var selectedPlayers = selectedPlayersStr.map(str => parseInt(str, 10));
            selectedNumbers = selectedPlayers;
            const containsInRange = selectedPlayers.some(function(number) {
                return number > 100 && number <= 200;
            });
            startButton.disabled = selectedPlayers.length === 0;
            var bound = 100;
            if(containsInRange){
                bound = 200;
                moreNumber.textContent = "1-100";
                for (let i = 101; i <= 200; i++) {
                    const box = document.createElement('div');
                    box.textContent = i;
                    box.classList.add('box');
              
                    box.addEventListener('click', () => {
                        if (selectedNumbers.includes(i)) {
                            selectedNumbers = selectedNumbers.filter(num => num !== i);
                            box.classList.remove('selected');
                            if(cashier=="True"){
                                remove_player(i);
                            }
                        } else {
                            selectedNumbers.push(i);
                            box.classList.add('selected');
                            if(cashier=="True"){
                                add_player(i);
                            }
                        }
                        startButton.disabled = selectedNumbers.length === 0;
                        updateTotalSelected();
                    });
              
                    container.appendChild(box);
                }
            }
            var divs = container.querySelectorAll(".box");
            for (var i = 0; i < bound; i++) {
                if (selectedPlayers.includes(i+1)){
                    divs[i].classList.add('selected');

                    if(cashier=="True"){
                        add_player(i+1);
                    }
                }
            }
        }
    }

    const inputElement = document.getElementById('stake');

    if(cashier=="True"){
        inputElement.addEventListener('input', (event) => {
            const currentValue = event.target.value;
            // Call your function here
            handleInputChange(currentValue);
        });
    
        setInterval(get_game_stat, 1000);
    }

  };


function handleInputChange(value) {
    // Your logic here
    var game = document.getElementById('game').innerHTML;
    $.ajax({
        url:  "/update_stake/",  // Replace with your Django view URL
        type: "GET",
        data: {
            stake: value,
            game: game,
            // Add more parameters as needed
        },
        success: function(response) {
            if (response.status === 'success') {
                console.log(response.message);
            } else if (response.status === 'failure' || response.status === 'error') {
                alert(response.message);
            }
        },
        error: function(xhr, status, error) {
          alert("Failed to get data");
        }
    });
}


  
function remove_player(card){
    var game = document.getElementById('game').innerHTML;
    $.ajax({
        url:  "/remove_player/",  // Replace with your Django view URL
        type: "GET",
        data: {
            card: card,
            game: game,
            // Add more parameters as needed
        },
        success: function(response) {
            if (response.status === 'success') {
                console.log(response.message);
            } else if (response.status === 'failure' || response.status === 'error') {
                alert(response.message);
            }
        },
        error: function(xhr, status, error) {
          alert("Failed to get data");
        }
      });
}

function add_player(card){
    var game = document.getElementById('game').innerHTML;
    $.ajax({
        url:  "/add_player/",  // Replace with your Django view URL
        type: "GET",
        data: {
            card: card,
            game: game,
            // Add more parameters as needed
        },
        success: function(response) {
            if (response.status === 'success') {
                console.log(response.message);
            } else if (response.status === 'failure' || response.status === 'error') {
                alert(response.message);
            }
        },
        error: function(xhr, status, error) {
          alert("Failed to get data");
        }
      });
}
