const container = document.getElementById('container');
const numbers = [];
let selectedNumbers=[];
const moreNumber = document.getElementById('more');
const clearbtn = document.getElementById('clear');
const main_sec = document.getElementById('main');
const pay = document.getElementById('pay');
var other_selected = [];
var stake = 0;

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
            if (response.message === 'None') {
                main.classList.add('inactive');
            }else if(response.message === 'PLAYING'){
                main.classList.add('inactive');
                pay.style.display = 'block';

                pay.innerHTML = '';

                // Create a container for the cashier stats
                const container = document.createElement('div');
                container.classList.add('cashier-container');

                // Create the stat boxes for each cashier
                response.cashiers.forEach(cashier => {
                    const cashierBox = document.createElement('div');
                    cashierBox.classList.add('cashier-box');

                    const name = document.createElement('h3');
                    name.textContent = cashier.name;

                    const collected = document.createElement('p');
                    collected.textContent = `Collected: ${cashier.collected}`;

                    const paid = document.createElement('p');
                    paid.textContent = `Paid: ${cashier.paid}`;

                    cashierBox.appendChild(name);
                    cashierBox.appendChild(collected);
                    cashierBox.appendChild(paid);

                    container.appendChild(cashierBox);

                    clearInterval(intervalId);
                });

                // Append the container to the pay div
                pay.appendChild(container);

            }else {
                main.classList.remove('inactive');
                pay.style.display = 'none';
                document.getElementById('acc').value =response.balance;
                document.getElementById('game').value = response.game.id;
                other_selected = Array.isArray(response.other_selected) ? response.other_selected : [];
                selectedNumbers = Array.isArray(response.selected_players) ? response.selected_players : [];
                stake = response.game.stake;
                document.getElementById('noplayer').value = selectedNumbers.length;
                document.getElementById('collected').value = selectedNumbers.length * stake;
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
    var selectedNumbersS = selectedNumbers;
    var other_selectedS = other_selected;
    boxes.forEach(function(box) {
        var innerText = box.innerText.trim(); // Get inner text and trim whitespace
        
        // Check if inner text is in the numbersToMatch array
        if (selectedNumbersS.includes(innerText)) {
            // Do something with the matching box element, e.g., add a class
            box.classList.add('selected');
        }else if(other_selectedS.includes(innerText)){
            box.classList.add('selected');
            box.classList.add('blured');
        }else {
            box.classList.remove('selected');
            box.classList.remove('blured');
        }
    });
}

function remove_player(card){
    var game = document.getElementById('game').value;
    $.ajax({
        url:  "/cashier/remove_player/",  // Replace with your Django view URL
        type: "GET",
        data: {
            card: card,
            game: game,
            // Add more parameters as needed
        },
        success: function(response) {
            if (response.status === 'success') {

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
    var game = document.getElementById('game').value;
    $.ajax({
        url:  "/cashier/add_player/",  // Replace with your Django view URL
        type: "GET",
        data: {
            card: card,
            game: game,
            // Add more parameters as needed
        },
        success: function(response) {
            if (response.status === 'success') {

            } else if (response.status === 'failure' || response.status === 'error') {
                alert(response.message);
            }
        },
        error: function(xhr, status, error) {
          alert("Failed to get data");
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
            if (selectedNumbers.includes(box.textContent)) {
                selectedNumbers = selectedNumbers.filter(num => num !== i);
                box.classList.remove('selected');
                remove_player(i);
            } else {
                selectedNumbers.push(i);
                box.classList.add('selected');
                add_player(i);
                console.log(selectedNumbers);
            }
        });

        container.appendChild(box);
    }

    intervalId = setInterval(get_game_stat, 1000);

  };
