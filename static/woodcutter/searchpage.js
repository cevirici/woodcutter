
$('.search-button').click(function(){
    $('.results-container').css('width', '50%');
    $.post('findlogs',
        {
            'cards': $('#searchcards').val(),
            'optionals': $('#optionalcards').val(),
            'players': $('#players').val()
        },
        function (data, status){
            $('.results-container > p').html(data);
        }
    ).fail(function(jqXHR, textStatus, errorThrown){
        console.log(errorThrown);
        console.log(jqXHR.responseText);
    });
});