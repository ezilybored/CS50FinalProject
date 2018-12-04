// A basic on event function edited to use an ajax request to check if the username is already taken

function retrievePost() {
    console.log('is this thing on?');
    // A new AJAX object
    const ajax = new XMLHttpRequest();
    // The target of the event listener passed in to the function as e
    const date = document.querySelector('#dateofpost').value;
    console.log(date);


    // Sends the ajax POST request to the server to run the function at /votecheck
    ajax.open('POST', '/retrieveposts');

    // When the request is complete, and ajax returns, run this function
    ajax.onload = function () {
        console.log('returned ajax')
        // Pasrses the JSON file and extracts the text from the response
        const data = JSON.parse(ajax.responseText);

        if (data.success) {
            console.log('else statement happened ok');
            const post = `${data.post}`
            //const stringpost = JSON.stringify(post);
            console.log(post);
            //var text = document.getElementById('postedit').innerHTML;
            //console.log(text);
            document.getElementById('postedit').innerText = post;
            //console.log(text);
        } else {
            alert(`Unfortunately there were no story posts on that date`);
        }
    }

    const data = new FormData();
    data.append('date', date)
    console.log(data);

    ajax.send(data);
    console.log('ajax sent?');
    return false;
};

var elDateofpost = document.getElementById('submitdate');
elDateofpost.addEventListener('click', retrievePost, false)
