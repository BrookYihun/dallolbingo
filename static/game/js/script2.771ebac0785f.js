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
var patterns = [];

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
    var buttonText = moreNumber.textContent;
    if(buttonText=="1-100"){
        boundary = 200;
    }
    for (var i = 0; i <boundary; i++) {
        if (selectedNumbers.includes(i+1)){
            divs[i].classList.remove('selected');
            if(cashier=="True"){
                remove_player(i+1);
            }
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

// // Handle custom select dropdown
// document.querySelector('.select-box').addEventListener('click', function () {
//     const selectBox = this.parentElement;
//     selectBox.classList.toggle('open'); // Toggle open class to show/hide options
// });

// // Handle selecting an option
// document.querySelectorAll('.option').forEach(option => {
//     option.addEventListener('click', function () {
//         // Toggle 'selected' class on the clicked option
//         this.classList.toggle('selected');

//         // Update the displayed selected patterns
//         const selectedPatterns = Array.from(document.querySelectorAll('.option.selected')).map(option => option.textContent).join(', ');
//         document.getElementById('selectedPatterns').textContent = selectedPatterns || 'Choose Patterns';
        
//         // Optionally save the selected values to cookies or send to server
//         patterns = Array.from(document.querySelectorAll('.option.selected')).map(option => option.dataset.value);
        
//     });
// });

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
    
    // deleteCookie("Patterns");
    // setCookie('Patterns', patterns, 7);

    // Submit the form to the 'bingo' URL
    gameForm.method = 'POST';
    gameForm.submit();
});

function updateTotalSelected() {
    deleteCookie("selectedPlayers");
    setCookie("selectedPlayers",selectedNumbers,7);
    document.getElementById('noplayer').value = selectedNumbers.length;
    //document.getElementById('win').value = selectedNumbers.length * document.getElementById('stake').value;
}

function update_view(players){
    var boxes = document.querySelectorAll('.box');
    other_selected = [];

    boxes.forEach(function(box) {
        var innerTextStr = box.innerText.trim(); // Get inner text and trim whitespace
        var innerText = parseInt(innerTextStr, 10);
        // Check if inner text is in the numbersToMatch array
        if (selectedNumbers.includes(innerText)) {
            // Do something with the matching box element, e.g., add a class
            box.classList.add('selected');
        }else {
            box.className = "box";
        }

    });
    var colornum = 1;
    players.forEach(function(cashier){
        var arrayStr = Array.isArray(cashier.selected_players) ? cashier.selected_players : [];
        var array = arrayStr.map(str => parseInt(str, 10));
        other_selected.push(...array);
        var color = "color"+colornum;
        colornum++;
        for (let element of array) {
            boxes[element-1].classList.add('selected');
            boxes[element-1].classList.add(color);
            boxes[element-1].classList.add('blured');
        }

    });

    startButton.disabled = selectedNumbers.length === 0 && other_selected.length === 0;

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
    
    // const selectedPatterns = getCookie("Patterns");
    // if (selectedPatterns) {
    //     const selectedValues = getCookie('Patterns') || '[]';
    
    //     // Loop through all options and mark those that are selected
    //     document.querySelectorAll('.option').forEach(option => {
    //         if (selectedValues.includes(option.dataset.value)) {
    //             option.classList.add('selected'); // Add 'selected' class to pre-selected options
    //         }
    //     });
    
    //     // Update the displayed selected patterns
    //     const selected = selectedValues.map(value => {
    //         return document.querySelector(`.option[data-value="${value}"]`).textContent;
    //     }).join(', ');
        
    //     document.getElementById('selectedPatterns').textContent = selected || 'Choose Patterns';
        
    //      patterns = Array.from(document.querySelectorAll('.option.selected')).map(option => option.dataset.value);
    // }

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

    if (cashier === "True") {
        let shop = document.getElementById('shop').value;
        socket = new WebSocket(`ws://${window.location.host}/ws/game/${shop}/${game_id}/`);
    
        socket.onopen = function (e) {
            console.log("WebSocket connection established.");
    
            // Send create_game message with a random or predefined game ID
            socket.send(JSON.stringify({
                type: "create_game",
                game_id: game_id
            }));
        };
    
        socket.onmessage = function (e) {
            const data = JSON.parse(e.data);
            const cardId = parseInt(data.card, 10);

            if (data.action === 'existing_selected_cards') {
                const cardMap = data.cards_by_cashier;
                const myCards = data.selected_cards || [];
            
                // Update current user's selected cards
                selectedNumbers = myCards;
                
                const newOtherSelected = [];
            
                for (let cashierId in cardMap) {
                    const cards = cardMap[cashierId];
                    cards.forEach((cardId) => {
                        if (!newOtherSelected.includes(cardId) && !selectedNumbers.includes(cardId)) {
                            newOtherSelected.push(cardId);
                        }
                    });
                }
            
                other_selected = newOtherSelected;
                update_visuals();
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
    
        socket.onerror = function (e) {
            console.error("WebSocket error:", e);
        };
    
        socket.onclose = function (e) {
            console.log("WebSocket connection closed.");
        };
    }
};    

  
function add_player(card){
    const cardId = parseInt(card, 10);
    if (!selectedNumbers.includes(cardId)) {
        selectedNumbers.push(cardId);
    }

    if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            type: 'add_player',
            card: card,
            game: game_id
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
            game: game_id,
        }));
    }
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