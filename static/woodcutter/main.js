
/*********** Card Layer Highlighting ***********/

var highlightTimer, longClickTimer;

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
                    let columnKills = killedCount[$(x).attr('xcoord')];
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


$('.settingsbox.visibility').click( function(){
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
const pslog = new PerfectScrollbar('.story-window', {suppressScrollX:true});


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


/*********** Manual Fixing ***********/

var fixMode = false;

$('.story-tool.fix')
    .click(function(){
        fixMode = !fixMode;
        $(this).toggleClass('active');
    });


$('.story-line')
    .click(function(){
        if (fixMode){
            $('.story-edit').remove();
            var editClass = 'story-edit'
            if (!$(this).hasClass('alternate')){
                editClass += ' alternate' 
            }
            $(this).after('<input type = "text" class = "'+editClass+'" value="' + 
                           storyAll[$('.story-line').index(this)] + 
                           '">');
        }
    });


$(document).on('keydown', 'input', function(e) {
    if(e.which == 10 || e.which == 13) {
        var selectedInput = $(this);
        var inputText = selectedInput.val();
        var lineNumber = $('.story-line').index(selectedInput.prev())
        $.post('../../editlog',
            {
                'gameid': gameid,
                'lineNumber': lineNumber,
                'input': inputText
            },
            function (data, status){
                returnData = data.split('~');
                selectedInput.prev().html(returnData[0]);
                selectedInput.prev().css('padding-left',
                    ((parseInt(returnData[2])+2) * 2).toString() + '%');
                storyAll[lineNumber] = returnData[1];
                selectedInput.remove();
            }
        ).fail(function(jqXHR, textStatus, errorThrown){
            console.log(errorThrown);
        });
    }
});


/*********** Story Deck Display ***********/

function drawStandardBox(card){
    innerColor = cardColors[card][0];
    borderColor = cardColors[card][1];
    cardName = cardColors[card][2];
    nameWords = cardName.split(' ');
    cardLabel = ''
    for (i = 0; i < Math.min(2, nameWords.length); i++){
        cardLabel += nameWords[i][0];
    }

    colorSum = 0;
    for (i = 0; i < 6; i+= 2){
        colorSum += parseInt(innerColor.slice(i, i+2), 16);
    }
    isDark = (colorSum > 383);

    innerClass = (isDark ? 'box-inner dark' : 'box-inner');

    innerString = "<div class='"+ innerClass +"' style='background: #"+ innerColor +";'>"
                  + cardLabel + '</div>';
    fullBox = "<div class='decksbox' style='background: #"+ borderColor +";'>"
               + innerString +"</div>";
    return fullBox
}


function updateBoardPosition(chunk){
    for (zoneIndex = 0; zoneIndex < chunk.length; zoneIndex++){
        zone = chunk[zoneIndex];
        for (partIndex = 0; partIndex < zone.length; partIndex++){
            part = zone[partIndex];
            partDiv = $('.decks-row').eq(zoneIndex)
                            .find('.part').eq(partIndex);

            if (part.length > 0){
                partItems = part.split('|');
                partString = '';
                for (itemIndex = 0; itemIndex < partItems.length; itemIndex++){
                    item = partItems[itemIndex].split(':');
                    quantity = parseInt(item[0]);
                    itemID = parseInt(item[1], 16);
                    partString += "<div class = 'deckswrapper'>" +
                                  "<div class='deckslabel'>"+quantity+"</div>" +
                                  drawStandardBox(itemID) +
                                  "</div>";
                }

                partDiv.html(partString);
            } else {
                partDiv.html('');
            }
        }
    }
}


$('.story-line').hover(function(){
    lineIndex = $(this).index('.story-line');
    console.log(lineIndex);
    updateBoardPosition(gameStates[lineIndex + 1]);
    $('.decks-display').css('opacity', '1');
}, function(){
    $('.decks-display').css('opacity', '0');
});