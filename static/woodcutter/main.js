
/*********** Card Layer Highlighting ***********/

var highlightTimer;

function rehighlight(){
	$('.graph-layer').css('opacity',1);
}

function highlight_layer(targetCard){
	$('.legendbox[card='+targetCard+']').addClass('highlight');
	$('.graph-layer').css('opacity',0.4);
	$('.graph-layer.card'+targetCard).css('opacity',1);
	clearTimeout(highlightTimer);
}

function dehighlight_layer(targetCard){
	$('.legendbox[card='+targetCard+']').removeClass('highlight');
	highlightTimer = setTimeout(rehighlight,500);
}

$('.box').hover(
	function() {highlight_layer($(this).attr('card'))},
	function() {dehighlight_layer($(this).attr('card'))}
);

$('.legendbox').hover(
	function() {highlight_layer($(this).attr('card'))},
	function() {dehighlight_layer($(this).attr('card'))}
);


/*********** Card Hiding ***********/

$('.legendbox').click(
	function(){
		$(this).toggleClass('faded');

		let dir = ($(this).hasClass('faded') ? -1 : 1)
		let targetCard = $(this).attr('card');
		let length = $('.axislabel').length;

		$('.graph-container').each((i,graph) => {
			for (let side=0; side<2; ++side){
				let row = $(graph).children('.row:eq('+side+')');
				let dirString = ['bottom','top'][side];

				let killedCount = [];
				for(let i=0; i<length; ++i) killedCount.push([]);

				row.find('.graph-layer.card'+targetCard+' .box').each((i,x) => {
						killedCount[$(x).attr('xcoord')].push(parseInt($(x).attr('ycoord')));
				});

				row.find('.graph-layer.card'+targetCard).toggle();

				row.find('.box').each((i,x) => {
					let currentY = parseInt($(x).attr('currenty'));
					let rootY = parseInt($(x).attr('ycoord'));
					let	columnKills = killedCount[$(x).attr('xcoord')];
					currentY += dir * columnKills.filter(x => x <rootY).length;

					$(x).attr('currenty', currentY.toString());

					actualHeight = (0.5*Math.floor(currentY/5)+currentY*2).toString();
					$(x).css(dirString,actualHeight+'%');
				});
			}
		});
	}
);


/*********** Scrolling ***********/

function scrollTo(storylineIndex){
	$('.story-container').scrollTop($('.story-line[turn=\''+storylineIndex+'\']').get(0).offsetTop-10);
}

$('.axislabel').click( function(){
	scrollTo($(this).index())
});

$('.story-sidebar-block').click( function(){
	scrollTo($(this).index())
});


/*********** Controls Hovering ***********/

$('.controlbox').click(function(){ 
	$('.controlbox').addClass('faded');
	$(this).removeClass('faded');

	$('.graph-container').css('display','none');
	$('.graph-container[graphname=\''+$(this).attr('control')+'\']').css('display','flex');
});

$('.modalcontrolbox').click(function(){
	$(this).toggleClass('faded');
	$('.modal.'+$(this).attr('control')).css('opacity', 1-$('.modal.'+$(this).attr('control')).css('opacity'));
});

$('.graph-control').click(function(){		
	if ($(this).index('.graph-control')==0){
		$('.row').toggleClass('topshifted');
		$('.axis').toggleClass('topshifted');
		$('.row').removeClass('downshifted');
		$('.axis').removeClass('downshifted');
	}
	else{
		$('.row').toggleClass('downshifted');
		$('.axis').toggleClass('downshifted');
		$('.row').removeClass('topshifted');
		$('.axis').removeClass('topshifted');
	}

	$('.graph-control').not(this).removeClass('highlight');
	$(this).toggleClass('highlight');}
);


const psg = new PerfectScrollbar('.graph', {useBothWheelAxes:true, suppressScrollY:true});
const psleg = new PerfectScrollbar('.legend');
const psc = new PerfectScrollbar('.controls');
const pslog = new PerfectScrollbar('.story-container', {suppressScrollX:true});