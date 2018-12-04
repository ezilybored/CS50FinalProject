// A basic on event function edited to use an ajax request to check if the username is already taken
document.addEventListener('DOMContentLoaded', () => {

    document.querySelector('#enterdate').onsubmit = () => {

        const ajax = new XMLHttpRequest();
        const date = document.querySelector('#dateofpost').value;
        ajax.open('POST', '/retrieveposts');

        ajax.onload = () => {
            const data = JSON.parse(ajax.responseText);

            if (data.success) {
                const post = `${data.post}`
                const postid = `${data.postid}`
                console.log(post);
                console.log(postid);
                document.getElementById('postedit').innerHTML = post;
                document.getElementById('postid').innerHTML = postid;
            } else {
                document.getElementById('postedit').innerHTML = `Unfortunately there were no story posts on that date`;
            }
        }

        const data = new FormData();
        data.append('date', date)
        console.log(data);

        ajax.send(data);
        console.log('ajax sent?');
        return false;
    };
});

