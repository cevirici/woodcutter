$('.controlbox').not(':eq(0)').addClass('faded');
$('.valuebox').not(':eq(0)').addClass('faded');
$('.graph-container').not(':eq(0)').hide();


$('.box-outline').hover(
	function(){	$(this).addClass('highlight');
			    $('.legendbox[card=\''+$(this).attr('card')+'\']').addClass('highlight')},
	function(){	$(this).removeClass('highlight');
				$('.legendbox[card=\''+$(this).attr('card')+'\']').removeClass('highlight')}
);

$('.legendbox').hover(
	function(){	$(this).addClass('highlight');
			    $('.box-outline[card=\''+$(this).attr('card')+'\']').addClass('highlight')},
	function(){	$(this).removeClass('highlight');
				$('.box-outline[card=\''+$(this).attr('card')+'\']').removeClass('highlight')}
);

$('.story-sidebar-block').hover(
	function(){	$(this).addClass('highlight');},
	function(){	$(this).removeClass('highlight');}
);

$('.legendbox').click(
	function(){
		$(this).toggleClass('faded');
		var dir = ($(this).hasClass('faded') ? 1 : -1)
		var targetCard = $(this).attr('card');
		$('.boxstack').each(function(){
			var killedBoxes = [];
			var vanishedBoxes = [];
			$(this).children('.box-outline[card=\''+targetCard+'\']').each(function(){
				$(this).toggleClass('vanish');
				killedBoxes.push(parseInt($(this).css('order')));
			});

			$(this).children('.vanish').each(function(){
				vanishedBoxes.push(parseInt($(this).css('order')));
			});

			$(this).children('.spacer').each(function(){

				var intOrder = parseInt($(this).css('order'));

				del = 0
				for (k in Object.values(killedBoxes)){
					l = (dir == 1 ? k : killedBoxes.length -k - 1);
					if (killedBoxes[l] < intOrder){
						while (vanishedBoxes.includes(intOrder + del + dir)){
							del +=2 * dir;
						}
						del += 2*dir;
					}
				}
				$(this).css('order', intOrder + del);
			});
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
				$('.graph-container').hide();
				$('.graph-container[graphname=\''+$(this).attr('control')+'\']').show();}
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
	var selector = (i==0?'even':'odd');
	$('.row:'+selector+'').toggleClass('shrunken');
	$('.row:'+selector+'').removeClass('expanded');
	$('.row:not(:'+selector+')').toggleClass('expanded');
	$('.row:not(:'+selector+')').removeClass('shrunken');
	$('.graph-control').not(this).removeClass('highlight');
	$(this).toggleClass('highlight');}
);


const psg = new PerfectScrollbar('.graph', {useBothWheelAxes:true});
const psleg = new PerfectScrollbar('.legend');
const psc = new PerfectScrollbar('.controls');
const pslog = new PerfectScrollbar('.story-container',{suppressScrollX:true});