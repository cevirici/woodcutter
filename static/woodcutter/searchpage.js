
$('.search-button').click(function(){
    $('.results-container').css('width', '50%');
    $.post('findlogs',
        {
            'cards': $('#searchcards').val(),
            'optionals': $('#optionalcards').val(),
            'players': $('#players').val(),
            'errors': $('.error-selector').attr('state')
        },
        function (data, status){
            $('.results-container > p').html(data);
        }
    ).fail(function(jqXHR, textStatus, errorThrown){
        console.log(errorThrown);
        console.log(jqXHR.responseText);
    });
});


$('.error-selector').click(function(){
    currState = $('.error-selector').attr('state');
    currState = (currState + 1) % 3;
    $('.error-selector').html(['No', 'All', 'Yes'][currState]);
    $('.error-selector').attr('state', currState);
});
