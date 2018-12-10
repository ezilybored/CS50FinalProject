document.addEventListener('DOMContentLoaded', () => {

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When connected, configure buttons
    socket.on('connect', () => {

        // Each button should emit a "submit vote" event
        document.querySelectorAll('button').forEach(button => {
            button.onclick = () => {
                const ajax = new XMLHttpRequest();
                ajax.open('POST', '/votecheck', true);
                ajax.send();
                console.log('is this thing still on?');

                ajax.onload = function () {
                    // Pasrses the JSON file and extracts the text from the response
                    const vote = JSON.parse(ajax.responseText);
                    console.log(vote.success);
                    // If the user has not voted
                    if (vote.success == true) {
                        // Set the voted message with the value they chose
                        const selection = button.dataset.vote;
                        const selected = button.dataset.vote;
                        alert(`Thanks for choosing. This week you chose option: ${selected}`);
                        socket.emit('submit vote', {'selection': selection});
                    } else {
                        // Else say this
                        alert(`You have already chosen this week. Try again after the next installment on Sunday`);
                    }
                };
            };
        });
    });
});