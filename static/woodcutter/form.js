
$('.filetype-selector').not(':eq(0)').addClass('faded');
$('.textarea').not(':eq(0)').hide();

$('.filetype-selector').hover(
	function(){	$(this).addClass('highlight')},
	function(){	$(this).removeClass('highlight')}
);

$('.filetype-selector').click(
	function(){ $('.filetype-selector').addClass('faded');
				$(this).removeClass('faded');
				$('.textarea').hide();
				$('.textarea[assoc=\''+$(this).attr('assoc')+'\']').show();}
);
