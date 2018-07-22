
$('.search-button').click(function(){
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