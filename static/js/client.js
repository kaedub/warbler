$(document).ready(function() {
    const BASE_URL = 'http://localhost:5000';


    $('#messages').on('click', 'a', function(evt) {
        let $clicked = $(this);

        let method;
        if (/far/.test($clicked.attr('class'))) {
            method = 'POST';
        } else {
            method = 'DELETE';
        }

        $clicked.toggleClass('far fas');
        let message_id = $(this).attr('id');

        // send request to server to like post
        $.ajax({
            url: `${BASE_URL}/like`, 
            method,
            data: {
                message_id, },
            dataType: 'json',
            success: (res) => {
                console.log('success! received response:', res);
            }
        });
    })
});