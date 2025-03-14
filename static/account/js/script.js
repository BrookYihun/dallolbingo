const menuBar = document.querySelector('#content nav .bx.bx-menu');
const sidebar = document.getElementById('sidebar');
const dash_a = document.getElementById('dashboard');
const switchMode = document.getElementById('switch-mode');

dash_a.classList.add('active');

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
