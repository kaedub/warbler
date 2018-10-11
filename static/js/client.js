$(document).ready(function() {
    const BASE_URL = 'http://localhost:5000';


    $('#messages').on('click', 'a', function(evt) {
        evt.preventDefault();
        let $clicked = $(evt.target);

        let action;
        if (/far/.test($clicked.attr('class'))) {
            action = 'add';
        } else {
            action = 'remove';
        }

        $clicked.toggleClass('far fas');
        let message_id = $clicked.attr('data-message-id');

        // send request to server to like post
        $.ajax({
            url: `${BASE_URL}/like/${action}`, 
            method: 'post',
            data: {
                message_id, 
            },
            dataType: 'json',
            success: (res) => {
                console.log('success! received response:', res);
            }
        });
    })
});