$('.controlbox').not(':eq(0)').addClass('faded');
$('.valuebox').not(':eq(0)').addClass('faded');
$('.graph-container').not(':eq(0)').css('display','none');

var highlightTimer;

function rehighlight(){
	$('.graph-layer').css('opacity',1);
}

$('.box-outline').hover(
	function(){	targetCard = $(this).attr('card');
				$(this).addClass('highlight');
				$('.graph-layer').css('opacity',0.2);
			    $('.graph-layer.card'+targetCard).css('opacity',1);
			    clearTimeout(highlightTimer)},
	function(){	highlightTimer = setTimeout(rehighlight,500);
				$(this).removeClass('highlight');}
);

$('.legendbox').hover(
	function(){	targetCard = $(this).attr('card');
				$(this).addClass('highlight');
				$('.graph-layer').css('opacity',0.2);
			    $('.graph-layer.card'+targetCard).css('opacity',1);
				clearTimeout(highlightTimer)},
	function(){	highlightTimer = setTimeout(rehighlight,500);
				$(this).removeClass('highlight');}
);

$('.legendbox').click(
	function(){
		$(this).toggleClass('faded');
		var dir = ($(this).hasClass('faded') ? -1 : 1)
		var targetCard = $(this).attr('card');
		length = $('.axislabel').length;
		$('.graph-container').each(function(index,graph){
			for (side=0;side<2;side++){
				row = $(graph).children('.row:eq('+side+')');
				killedCount = [];
				for(var i=0; i<length; ++i) killedCount.push([]);

				$(row).find('.graph-layer.card'+targetCard+' .box-outline').each(function(index,x){
					killedCount[$(x).attr('xcoord')].push(parseInt($(x).attr('ycoord')));
					$(x).toggle();
				});
				
				dirString = ['bottom','top'][side];

				row.find('.box-outline').each(function(index,x){
					t = parseInt($(x).attr('currenty'));
					actualY = parseInt($(x).attr('ycoord'));
					thisKillCount = killedCount[$(x).attr('xcoord')];
					for(i=0;i<thisKillCount.length;i++){
						if (thisKillCount[i]<actualY){
							t += dir
						}
					};
					$(x).attr('currenty',t.toString());
					actualHeight = (0.5*Math.floor(t/5)+t*2).toString();
					$(x).css(dirString,actualHeight+'%');
				});

			}
		});
	}
);

$('.axislabel').click(
	function(){
		console.log('pop');
		$('.story-container').scrollTop($('.story-line[turn=\''+$(this).index()+'\']').get(0).offsetTop-10);
	}
);

$('.story-sidebar-block').click(
	function(){
		console.log('pop');
		$('.story-container').scrollTop($('.story-line[turn=\''+$(this).index()+'\']').get(0).offsetTop-10);
	}
);


$('.controlbox, .axislabel, .valuebox').hover(
	function(){	$(this).addClass('highlight')},
	function(){	$(this).removeClass('highlight')}
);

$('.controlbox').click(
	function(){ $('.controlbox').addClass('faded');
				$(this).removeClass('faded');
				$('.graph-container').css('display','none');
				$('.graph-container[graphname=\''+$(this).attr('control')+'\']').css('display','flex');}
);

$('.valuebox').click(
	function(){ 
		mode = $(this).attr('control');
		switch(mode){
			case 'normal':
				$('.box-outline').each(function(){
					$(this).css('min-height','');
					$(this).css('margin-top','');
					$(this).css('margin-bottom','');
				});
				$('.spacer').show();
				break;
			case 'cost':
				$('.box-outline').each(function(){
					$(this).css('min-height',String(7*$(this).attr('cost'))+'px');
					$(this).css('margin-top','0px');
					$(this).css('margin-bottom','0px');
				});
				$('.spacer').hide();
				break;
		}
		$('.valuebox').addClass('faded');
		$(this).removeClass('faded');
	}
);

$('.graph-control').click(
	function(){	var i = $(this).index('.graph-control');
	if (i==0){
		$('.row').toggleClass('topshifted');
		$('.axis').toggleClass('topshifted');
		$('.row').removeClass('downshifted');
		$('.axis').removeClass('downshifted');
	}else{
		$('.row').toggleClass('downshifted');
		$('.axis').toggleClass('downshifted');
		$('.row').removeClass('topshifted');
		$('.axis').removeClass('topshifted');
	}
	$('.graph-control').not(this).removeClass('highlight');
	$(this).toggleClass('highlight');}
);


const psg = new PerfectScrollbar('.graph', {useBothWheelAxes:true,suppressScrollY:true});
const psleg = new PerfectScrollbar('.legend');
const psc = new PerfectScrollbar('.controls');
const pslog = new PerfectScrollbar('.story-container',{suppressScrollX:true});