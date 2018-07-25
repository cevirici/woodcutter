$('.help-hint').click(function(){
	if ($('.help-container').css('opacity') == 0){
		$('.help-container').css('opacity', 1);
		$('.logo').css('width', '250px');
	} else {
		$('.help-container').css('opacity', 0);
		$('.logo').css('width', '500px');
	}
});


$('.search-button').click(function(){
	window.location.href = '/woodcutter/' + $('.searchbox').val() + '/display';
})

$('.random-log').click(function(){
	window.location.href = '/woodcutter/random';
})

$('.log-search').click(function(){
    window.location.href = '/woodcutter/logsearch';
})