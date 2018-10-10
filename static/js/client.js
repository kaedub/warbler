$(document).ready(function() {
    const BASE_URL = 'http://localhost:5000';


    $('#interactions').on('click', 'a', function(evt) {
        $(this).toggleClass('far fas');
        let message_id = $(this).attr('id');

        // send request to server to like post
        $.ajax({
            url: `${BASE_URL}/like`, 
            data: {
                message_id, },
            dataType: 'json',
            success: (res) => {
                console.log('success! received response:', res);
            }
        });
    })
});