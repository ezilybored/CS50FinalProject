function isValidDate(e) {
    var elMsg = document.getElementById('feedback');
    // regular expression to match required date format
    var re = /^\d{4}-\d{2}-\d{2}$/;

    if(this.value != '') {
        if(this.value.match(re)) {
            var regs = this.value.split("-");
            console.log(regs);
            if(regs[0] < 1902 || regs[0] > (new Date()).getFullYear()) {
                elMsg.textContent = 'The inputted year is invalid';
            } else if(regs[1] < 1 || regs[1] > 12) {
                elMsg.textContent = 'The inputted month is invalid';
            } else if((regs[1] == 1 || 3 || 5 || 7 || 8 || 10 || 12) && regs[2] < 1 || regs[2] > 31) {
                elMsg.textContent = 'The inputted day is invalid';
            } else if((regs[2] == 4 || 6 || 9 || 11) && regs[2] < 1 || regs[2] > 30) {
                elMsg.textContent = 'The inputted day is invalid';
            } else if((regs[2] == 2) && regs[2] < 1 || regs[2] > 28) {
                elMsg.textContent = 'The inputted day is invalid';
            } else {
                elMsg.textContent = '';
            }
        } else {
            elMsg.textContent = 'Date must be YYYY-MM-DD';
        }
    }
}

var elUsername = document.getElementById('dob');
elUsername.addEventListener('blur', isValidDate, false);