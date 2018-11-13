(function(){                                                // Creates a function that runs immediately (IIFE)
    var form = document.getElementById("register");         // Gets the register form element using its id and stores as form

    addEvent(form, 'submit', function(e){                   // Adds an event listener using utilities.js listening for the submit button being clicked
        var elements = this.elements;                       // Gets the elements list from the object identified in the function i.e. the form
        var username = elements.username.value;             // Gets the value stored by username and sets it as a js variable username
        alert(`Thanks for joining us on our journey ${username}`)
    });                                                     // Creates an alert window to thank the user for registering
}());
