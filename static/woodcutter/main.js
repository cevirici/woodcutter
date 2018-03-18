
/*********** Card Layer Highlighting ***********/

var highlightTimer;

function rehighlight(){
	$('.graph-layer').css('opacity',1);
}

function highlight_layer(targetCard){
	$('.legendbox[card="'+targetCard+'"]').addClass('highlight');
	$('.graph-layer').css('opacity',0.4);
	$('.graph-layer.card'+targetCard).css('opacity',1);
	clearTimeout(highlightTimer);
}

function dehighlight_layer(targetCard){
	$('.legendbox[card='+targetCard+']').removeClass('highlight');
	highlightTimer = setTimeout(rehighlight, 500);
}

$('.box').hover(
	function() {highlight_layer($(this).attr('card'))},
	function() {dehighlight_layer($(this).attr('card'))}
);

$('.vpbox').hover(
	function() {highlight_layer($(this).attr('card'))},
	function() {dehighlight_layer($(this).attr('card'))}
);

$('.legendbox').hover(
	function() {highlight_layer($(this).attr('card'))},
	function() {dehighlight_layer($(this).attr('card'))}
);


/*********** Card Hiding ***********/

function toggleVisibility(dir, targetCard){
	let length = $('.axislabel').length;

	$('.graph-container').each((i,graph) => {
		if ($(graph).attr('graphname') != 'vp'){
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

					actualHeight = (0.5*Math.floor(currentY/5)+currentY*1.75).toString();
					$(x).css(dirString, actualHeight+'vh');
				});
			}
		}
	});
}

$('.legendbox').on('mousedown',
	function(e){
		var targetCard = $(this).attr('card');
		longClick = false;
		e.preventDefault()

		longClickTimer = setTimeout(function(){
				longClick = true;
				$(".legendbox[card='" + targetCard + "']").addClass('glow');
			},
			500
		)
	}
).on('mouseup',
	function(){
		clearTimeout(longClickTimer);
		$(this).removeClass('glow');

		if (longClick){
			var targetCard = $(this).attr('card');
			$('.legendbox').each((i, legend)=>{
				if ($(legend).attr('card') == targetCard){
					if ($(legend).hasClass('faded')){
						$(legend).toggleClass('faded');

						let thisCard = $(legend).attr('card');
						toggleVisibility(1, thisCard);
					}
				} else {
					if (!($(legend).hasClass('faded'))){
						$(legend).toggleClass('faded');

						let thisCard = $(legend).attr('card');
						toggleVisibility(-1, thisCard);
					}						
				}
			});
		} else {
			$(this).toggleClass('faded');
			$(this).removeClass('glow');

			let dir = ($(this).hasClass('faded') ? -1 : 1);
			let targetCard = $(this).attr('card');
			toggleVisibility(dir, targetCard);
		}
	}
).on('mouseout',
	function(){
		clearTimeout(longClickTimer);
		longClick = false;
		$(this).removeClass('glow');
	}
);


$('.settingsbox.visibility').click(	function(){
	$('.legendbox').each((i, legend)=>{
		if ($(legend).hasClass('faded')){
			$(legend).toggleClass('faded');

			let thisCard = $(legend).attr('card');
			toggleVisibility(1, thisCard);
		}
	});
});


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
		$('.graph').toggleClass('topshifted');
		$('.graph').removeClass('downshifted');
	}
	else{
		$('.graph').toggleClass('downshifted');
		$('.graph').removeClass('topshifted');
	}

	$('.graph-control').not(this).removeClass('highlight');
	$(this).toggleClass('highlight');}
);


/*********** Scrollbars ***********/

const psg = new PerfectScrollbar('.graph-window', {useBothWheelAxes:true, suppressScrollY:true});
const psleg = new PerfectScrollbar('.legend');
const psc = new PerfectScrollbar('.controls');
const pslog = new PerfectScrollbar('.story-container', {suppressScrollX:true});


/*********** Graph Scaling ***********/

var scaling = false;
var clickStart = 0;
var startY = 0;

var minY = $('.scale-nub').offset().top;
var maxY = $('.scale-nub').offset().top + $('.scale-bg').height();

$('.scale-nub')
	.on('mousedown', function(e){
		scaling = true;
		clickStart = e.pageY;
		startY = $(this).offset().top;
		e.preventDefault()
	});

$('body')
	.on('mousemove', function(e){
		if (scaling){
			pos = Math.min(maxY, Math.max(minY,startY + e.pageY - clickStart));
			val = (pos - minY)/(maxY - minY);
			$('.scale-nub').offset({top: pos});
			$('.graph-container > .row').css('transform', 'scaleY(' + (1/(1+val)) + ')');
			$('.vplabel').css('transform', 'scaleY(' + (1+val) + ')');
		}
	})
	.on('mouseup', function(){
		scaling = false;
	});