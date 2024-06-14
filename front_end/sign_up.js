$(document).ready(function() {
    $('#signupForm').submit(function(e) {
        e.preventDefault();
        $.ajax({
            url: 'http://localhost:5000/signup',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                name: $('#name').val(),
                phone: $('#phone').val(),
                password: $('#password').val()
            }),
            success: function(response, status, xhr) {
                console.log('Signup successful', response);
                alert('Signup successful! You can now sign in.');
                window.location.href = 'sign_in.html';  // Redirect after successful signup
            },
            error: function(xhr, status, error) {
                console.error('Signup failed', xhr.status, xhr.responseText);
                alert('Signup failed: ' + (xhr.responseJSON ? xhr.responseJSON.message : "An error occurred"));
            }
        });
    });
});
