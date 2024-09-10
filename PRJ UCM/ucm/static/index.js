let menu = document.querySelector('#menu-btn');
let navbar = document.querySelector('.navbar');

menu.onclick = () => {
    menu.classList.toggle('fa-times');
    navbar.classList.toggle('active');
}

window.onscroll = () => {
    menu.classList.remove('fa-times');
    navbar.classList.remove('active');
}


//query length

document.getElementById('queryForm').addEventListener('submit', function(event) {
    var textarea = document.getElementById('queryMessage');
    var errorMessage = document.getElementById('error-message');
    var words = textarea.value.split(/\s+/);
    if (words.length > 10) {
        errorMessage.textContent = 'The  message should not exceed 10 words.';
        event.preventDefault();
    } else {
        errorMessage.textContent = '';
    }
});

//unicode error in adminsignup page
function validateUnicode() {
    const unicodeInput = document.getElementById('unicode').value;
    const expectedUnicode = 'biher2024admin';
    const errorMessage = document.getElementById('error-message');

    if (unicodeInput !== expectedUnicode) {
        errorMessage.textContent = 'Unicode does not match.';
        return false;
    }
    errorMessage.textContent = '';
    return true;
}



