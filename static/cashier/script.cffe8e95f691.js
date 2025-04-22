const container = document.getElementById('container');
const numbers = [];
let selectedNumbers=[];
const moreNumber = document.getElementById('more');
const clearbtn = document.getElementById('clear');
const main_sec = document.getElementById('main');
const pay = document.getElementById('pay');
var other_selected = [];
var stake = 0;
var mycolor = "";
var gameId = "";

let intervalId;

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

  let shop = document.getElementById('shop').value;
  let socket = null;
  if(shop != ""){
    socket = new WebSocket(`ws://${window.location.host}/ws/game/${shop}/`);

    socket.onopen = function(e) {
        console.log("WebSocket connection established.");
    };
  
    socket.onmessage = function(e) {
      const data = JSON.parse(e.data);
  
      const cardId = parseInt(data.card, 10);

      if (data.action === 'current_game' && data.state === "pending") {
         gameId = data.game_id;
         get_game_stat();
      }
  
      if (data.action === 'player_added') {

          if (!other_selected.includes(cardId) && !selectedNumbers.includes(cardId)) {
              other_selected.push(cardId);
          }
      }
  
      if (data.action === 'player_removed') {
          const index = other_selected.indexOf(cardId);
          if (index !== -1) {
              other_selected.splice(index, 1);
          }
      }
  
      update_visuals();
  };
  
    socket.onerror = function(e) {
        console.error("WebSocket error:", e);
    };
    
    socket.onclose = function(e) {
        console.log("WebSocket connection closed.");
    };
  }

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


clearbtn.addEventListener('click',()=>{
    deleteCookie("selectedPlayers");
    var divs = container.querySelectorAll(".box");
    var boundary = 100;
    var buttonText = moreNumber.textContent;
    if(buttonText=="1-100"){
        boundary = 200;
    }
    for (var i = 0; i <boundary; i++) {
        if (selectedNumbers.includes(i+1)){
            divs[i].className = "box";
            remove_player(i+1);
        }
    }
    selectedNumbers=[];
});


function add_player(card){
    const cardId = parseInt(card, 10);
    if (!selectedNumbers.includes(cardId)) {
        selectedNumbers.push(cardId);
    }

    if (socket.readyState === WebSocket.OPEN ) {
        socket.send(JSON.stringify({
            type: 'add_player',
            card: card,
            game: gameId
        }));
    }
}

function remove_player(card){
    const cardId = parseInt(card, 10);
    const index = selectedNumbers.indexOf(cardId);
    if (index !== -1) {
        selectedNumbers.splice(index, 1);
    }

    if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            type: 'remove_player',
            card: card,
            game: gameId,
        }));
    }
}

function add(){
     for (let i = 101; i <= 200; i++) {
      const box = document.createElement('div');
      box.textContent = i;
      box.classList.add('box');

      box.addEventListener('click', () => {
          if (selectedNumbers.includes(i)) {
              selectedNumbers = selectedNumbers.filter(num => num !== i);
              box.className = "box";
              remove_player(i);
          } else {
              selectedNumbers.push(i);
              box.classList.add('selected');
              add_player(i);
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

function get_game_stat(){
    $.ajax({
        url:  "/cashier/get_game_stat/",  // Replace with your Django view URL
        type: "GET",
        success: function(response) {
            pay.style.display = 'none';
            document.getElementById('acc').value =response.balance;
            document.getElementById('game').value = response.game.id;
            stake = response.game.stake;
        },
        error: function(xhr, status, error) {
          alert("Failed to get data");
        }
      });
}

function arraysEqual(arr1, arr2) {
    if (arr1.length !== arr2.length) return false;
    for (let i = 0; i < arr1.length; i++) {
      if (arr1[i] !== arr2[i]) return false;
    }
    return true;
  }
  

  function update_visuals(){
    const boxes = document.querySelectorAll('.box');

    boxes.forEach(function(box) {
        const number = parseInt(box.innerText.trim(), 10);

        // Clear all extra styles first
        box.className = "box";

        if (selectedNumbers.includes(number)) {
            box.classList.add('selected');
        } else if (other_selected.includes(number)) {
            box.classList.add('blured', 'color2');  // color2 or use dynamic color
        }
    });
}

function update_view(players){
    var boxes = document.querySelectorAll('.box');
    other_selected = [];

    players.forEach(function(cashier){
        var arrayStr = Array.isArray(cashier.selected_players) ? cashier.selected_players : [];
        var array = arrayStr.map(str => parseInt(str, 10));
        var color = "color"+cashier.num;
        if(!arraysEqual(array,selectedNumbers)){
            other_selected.push(...array);
        }
        for (let element of array) {
            boxes[element-1].classList.add('selected');
            if(!selectedNumbers.includes(element)){
                boxes[element-1].classList.add('blured');
                boxes[element-1].classList.add(color);
            }
        }

    });

    boxes.forEach(function(box) {
        var innerTextStr = box.innerText.trim(); // Get inner text and trim whitespace
        var innerText = parseInt(innerTextStr, 10);
        // Check if inner text is in the numbersToMatch array
        if (other_selected.includes(innerText)||selectedNumbers.includes(innerText)) {
            // Do something with the matching box element, e.g., add a class
        }else {
            box.className = "box";
        }

    });

}

// Create number boxes


// ... Your existing JavaScript ...

// Inside the form submission event listener

window.onload = function() {
    for (let i = 1; i <= 100; i++) {
        const box = document.createElement('div');
        box.textContent = i;
        box.classList.add('box');
        
        box.addEventListener('click', () => {
            if (selectedNumbers.includes(i)) {
                if(gameId!=""){
                    selectedNumbers = selectedNumbers.filter(num => num !== i);
                    box.className = "box";
                    remove_player(i);
                }
            } else {
                if(gameId!=""){
                    selectedNumbers.push(i);
                    box.classList.add('selected');
                    add_player(i);
                }
            }
        });

        container.appendChild(box);
    }

    // intervalId = setInterval(get_game_stat, 1000);

  };
