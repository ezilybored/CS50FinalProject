

function selectionMessage(e){
    console.log('is this thing on?');
    // A new AJAX object
    const ajax = new XMLHttpRequest();
    // The target of the event listener passed in to the function as e
    var target = e.target;

    // Sends the ajax POST request to the server to run the function at /postcheck
    ajax.open('POST', '/votecheck', true);
    ajax.send();
    console.log('is this thing still on?');

    // When the request is complete, and ajax returns, run this function
    ajax.onload = function () {
        // Pasrses the JSON file and extracts the text from the response
        const vote = JSON.parse(ajax.responseText);
        console.log(vote.success);
        // If the user has not voted
        if (vote.success == true) {
            // Set the voted message with the value they chose
            var selection = target.value;
            alert(`Thanks for choosing. This week you chose option: ${selection}`);
        } else {
            // Else say this
            alert(`You have already chosen this week. Try again after the next installment on Sunday`);
        }
    };
}


// Adds an event listener to each of the buttons
var pressedButton = document.getElementsByTagName('Button');
for (i = 0; i < pressedButton.length; i++) {
    pressedButton[i].addEventListener('click', selectionMessage, false);
}