
class Container extends React.Component{
    constructor(props) {
        super(props);
        let index = (logIndex >= boards.length - 1 ? boards.length - 2 : logIndex);
        this.state = {index: index, showKingdom: false};
        this.changeIndex=this.changeIndex.bind(this);
        this.buttonShift=this.buttonShift.bind(this);
    }
    changeIndex(i){
        this.setState({index: i});
        let ypos = document.querySelectorAll('.story-line')[i].offsetTop - window.innerHeight / 3;
        document.querySelector('.story-container').scrollTo({
            top: ypos, 
            behavior: "smooth"
        });
    }
    componentDidMount() {
        let ypos = document.querySelectorAll('.story-line')[this.state.index].offsetTop - window.innerHeight / 3;
        document.querySelector('.story-container').scrollTo({
            top: ypos,
        });
    }
    buttonShift(name){
        let n = boards.length;
        switch (name) {
            case 'back-turn':
                var newIndex = (this.state.index < 1 ? 0 : this.state.index - 1);
                while ((!turnPoints.includes(newIndex)) && newIndex > 0){
                    newIndex--;
                }
                this.changeIndex(newIndex);
                break;
            case 'back-step':
                var newIndex = (this.state.index < 1 ? 0 : this.state.index - 1);
                while ((!stepPoints.includes(newIndex)) && newIndex > 0){
                    newIndex--;
                }
                this.changeIndex(newIndex);
                break;
            case 'back':
                var newIndex = (this.state.index < 1 ? 0 : this.state.index - 1);
                this.changeIndex(newIndex);
                break;
            case 'forward':
                var newIndex = (this.state.index > n - 3 ? n - 2 : this.state.index + 1);
                this.changeIndex(newIndex);
                break;
            case 'forward-step':
                var newIndex = (this.state.index > n - 3 ? n - 2 : this.state.index + 1);
                while ((!stepPoints.includes(newIndex)) && newIndex < n - 2){
                    newIndex++;
                }
                this.changeIndex(newIndex);
                break;
            case 'forward-turn':
                var newIndex = (this.state.index > n - 3 ? n - 2 : this.state.index + 1);
                while ((!turnPoints.includes(newIndex)) && newIndex < n - 2){
                    newIndex++;
                }
                this.changeIndex(newIndex);
                break;
        }
    }
    render(){
        return (
            <React.Fragment>
                <StoryLegend index={this.state.index} changeIndex={this.changeIndex}/>
                <div className='title-container'>{ titlestring }</div>
                <Board decision={this.state.index}/>
                <div className='story-container'>
                    <Story changeIndex={this.changeIndex} index={this.state.index}/>
                </div>
                <BaseContainer buttonShift={this.buttonShift} />
                <BottomTabs index={this.state.index} />
            </React.Fragment>
        );
    }
}

// Cards

class Card extends React.Component {
    constructor(props){
        super(props);
        this.containerRef = React.createRef();
        this.hoverEvent = this.hoverEvent.bind(this);
    }
    divStyle() {
        let suffix;
        switch(this.props.size){
            case 'big':
                suffix = '.jpg)';
            break;
            case 'tiny':
                suffix = '-tiny.jpg)';
            break;
            case 'mid':
            case 'small':
            default:
                suffix = '-mid.jpg)';
            break;
        }
        return {backgroundImage: 'url(' + staticRoot + '/card_images/' + urls[this.props.index] + suffix}
    }

    borderStyle() {
        return {background: '#' + borders[this.props.index]}
    }

    hoverEvent() {
        if (this.props.hover){
            this.props.hover(this.containerRef.current.offsetLeft + this.containerRef.current.offsetWidth,
                             this.containerRef.current.offsetTop)();
        }
    }

    render() {
        let innerText = (this.props.inner ? <div className='inner-text'> {this.props.inner} </div> : '');
        let containerClass = 'card-container' + (this.props.size ?  ' ' + this.props.size : '');
        let innerClass = 'card-inner' + (this.props.pilable && parseInt(this.props.inner) < 3 ? ' low' : '');
        if (this.props.label) {
            containerClass += ' wide';
            return (
                <div className={containerClass} ref={this.containerRef} onMouseLeave={this.props.dehover} onMouseOver={this.hoverEvent}>
                    <div className='card-label noselect'> {this.props.label} </div>
                    <div className={'card'} style={this.borderStyle()}>
                        <div className={innerClass} style={this.divStyle()}>
                        {innerText}
                        </div>
                    </div>
                </div>
            );
        } else {
            return (
                <div className={containerClass} ref={this.containerRef} onMouseLeave={this.props.dehover} onMouseOver={this.hoverEvent}>
                    <div className={'card'} style={this.borderStyle()}>
                        <div className={innerClass} style={this.divStyle()}>
                        {innerText}
                        </div>
                    </div>
                </div>
            );
        }
    }
}

// Board and Parts

class Board extends React.Component{
    constructor(props) {
        super(props);
        this.state = {activePart: '0', tooltip:'',
                      tooltipX: 0, tooltipY: 0};
        this.activate = this.activate.bind(this);
        this.setToolTip = this.setToolTip.bind(this);
    }

    activate(index) {
        if (index == this.state.activePart){
            this.setState({activePart: '0'});
        } else {
            this.setState({activePart: index});
        }
    }

    setToolTip(x, y, content) {
        this.setState({tooltipX: x, tooltipY: y, tooltip: content});
    }

    render(){
        let tooltip = '';
        if (this.state.tooltip != '') {
            let style = {left: this.state.tooltipX, top: this.state.tooltipY};
            tooltip = (
                    <div className='tooltip-box' style={style}>
                        {this.state.tooltip}
                    </div>
                );
        }
        let board = boards[this.props.decision + 1].split('/').map(x => x.split('|'));
        return (
            <div className='board'>
                <BoardComponent structure={['board-container', 
                                                ['board-left',
                                                    ['board-basic-supply'],
                                                    ['board-other-supply'],
                                                    ['board-landscape']
                                                ],
                                                ['board-right',
                                                    ['board-player-top',
                                                        ['board-discard top'],
                                                        ['board-deck top'],
                                                        ['board-hand top'],
                                                        ['board-others top',
                                                            ['board-tavern top'],
                                                            ['board-aside top'],
                                                            ['board-projects top'],
                                                        ],
                                                        ['board-misc top'],
                                                    ],
                                                    ['board-middle',
                                                        ['board-kingdom'],
                                                        ['board-trash'],
                                                    ],
                                                    ['board-inplay-row',
                                                        ['board-inplays'],
                                                        ['board-middle-info']
                                                    ],
                                                    ['board-player-bot',
                                                        ['board-discard bot'],
                                                        ['board-deck bot'],
                                                        ['board-hand bot'],
                                                        ['board-others bot',
                                                            ['board-tavern bot'],
                                                            ['board-aside bot'],
                                                            ['board-projects bot'],
                                                        ],
                                                        ['board-misc bot']
                                                    ]
                                                ]
                                            ]} 
                 activePart={this.state.activePart} decision={this.props.decision}
                 index={'1'} activate={this.activate} tooltip={this.setToolTip}
                 board={board} />
                 {tooltip}
            </div>
        );
    }
}



class BoardComponent extends React.Component {
    constructor(props) {
        super(props);
        this.activate = this.activate.bind(this);
        this.getInner = this.getInner.bind(this);
        this.getStack = this.getStack.bind(this);
    }

    activate() {
        if (this.props.structure.length == 1){
            this.props.activate(this.props.index);
        }
    }

    getInner(supply, cardList, size, pilable) {
        var inner = [];
        let clearHover = (e => {this.props.tooltip(0, 0, '')});
        for (let n in cardList) {
            let card = cardList[n];
            if (card in pairs) {
                let subCards = pairs[card].filter(x => x in supply);
                if (subCards.length == 1) {
                    inner.push(<Card size={size} index={subCards[0]} key={n}
                                inner={supply[subCards[0]]}
                                dehover={clearHover} pilable={pilable} />);
                } else {
                    let total = subCards.reduce((total, x) => {return total + supply[x];}, 0).toString();
                    if (pilable || total > 0) {
                        let tooltipInner = subCards.map((x, i) => <Card size='small' index={x} key={i} inner={supply[x]} />);
                        let hoverFunct = ((x, y) => (e => {this.props.tooltip(x, y, tooltipInner);}));
                        inner.push(<Card size={size} index={card} key={n} inner={total}
                                    hover={hoverFunct} dehover={clearHover} pilable={pilable} />);
                    }
                }

            } else {
                if (pilable || parseInt(card) in supply) {
                    inner.push(<Card size={size} index={card} key={n} pilable={pilable}
                                inner={(parseInt(card) in supply ? supply[parseInt(card)] : '0')} />);
                }
            }
        }
        return inner
    }

    getStack(source, small) {
        let inner = '';
        if (source){
            var cards = source.split('+');
            let size = (small ? 'small' : (cards.length < 7 ? 'mid' : 'small'));
            inner = cards.map((entry, n)  => <Card size={size} index={parseInt(entry.split(':')[1], 16)}
                                              inner={entry.split(':')[0]} key={n}/>);
        }

        return (
            <div className='board-content' key={0}>
                {inner}
            </div>
        );
    }

    render() {
        let className = 'board-component ' + this.props.structure[0];
        if (this.props.activePart.search(this.props.index) == 0){
            className += ' expanded';
        }

        // Lastmove Highlighting
        let lastMove = this.props.board[1][11].split('+');
        let partMap = {'board-basic-supply': 'SUPPLY',
                       'board-other-supply': 'SUPPLY',
                       'board-kingdom': 'SUPPLY',
                       'board-trash': 'TRASH',
                       'board-inplays': 'INPLAYS',
                       'board-deck top': 'DECKS0',
                       'board-deck bot': 'DECKS1',
                       'board-discard top': 'DISCARDS0',
                       'board-discard bot': 'DISCARDS1',
                       'board-hand top': 'HANDS0',
                       'board-hand bot': 'HANDS1',
                       'board-tavern top': 'TAVERN0',
                       'board-tavern bot': 'TAVERN1',
                       'board-aside top': 'OTHERS0',
                       'board-aside bot': 'OTHERS1'}
        if (partMap[this.props.structure[0]] == lastMove[0]) {
            className += ' source';
        }
        if (partMap[this.props.structure[0]] == lastMove[1]) {
            className += ' destination';
        }

        let children = [];
        let childIndex;
        for (let i = 1; i < this.props.structure.length; i++){
            childIndex = this.props.index + i.toString();
            children.push(<BoardComponent structure={this.props.structure[i]} activePart={this.props.activePart}
                           decision={this.props.decision} index={childIndex} activate={this.props.activate}
                           tooltip={this.props.tooltip} key={childIndex} board={this.props.board}/>);
        }


        // Labels

        var label = '';
        if (children.length == 0){
            className += ' node';
            switch (this.props.structure[0]){
                case 'board-basic-supply':
                    label = <div className='board-component-label'> Basic Supply
                            </div>;
                break;

                case 'board-other-supply':
                    label = <div className='board-component-label'> Nonsupply
                            </div>;
                break;

                case 'board-landscape':
                    label = <div className='board-component-label'> Landscapes
                            </div>;
                break;

                case 'board-kingdom':
                    label = <div className='board-component-label'> Kingdom
                            </div>;
                break;

                case 'board-deck top':
                case 'board-deck bot':
                    label = <div className='board-component-label'> Deck
                            </div>;
                break;

                case 'board-discard top':
                case 'board-discard bot':
                    label = <div className='board-component-label'> Discard
                            </div>;
                break;

                case 'board-hand top':
                case 'board-hand bot':
                    label = <div className='board-component-label'> Hand
                            </div>;
                break;

                case 'board-tavern top':
                case 'board-tavern bot':
                    label = <div className='board-component-label'> Tavern
                            </div>;
                break;

                case 'board-aside top':
                case 'board-aside bot':
                    label = <div className='board-component-label'> Aside
                            </div>;
                break;

                case 'board-projects top':
                case 'board-projects bot':
                    label = <div className='board-component-label'> Projects
                            </div>;
                break;

                case 'board-inplays':
                    label = <div className='board-component-label'> In Play
                            </div>;
                break;

                case 'board-trash':
                    label = <div className='board-component-label'> Trash
                            </div>;
                break;

                case 'board-misc top':
                case 'board-misc bot':
                case 'board-middle-info':
                    label = <div className='board-component-label'> Info
                            </div>;
                break;
            }
        }

        // Content

        let content = '';
        switch (this.props.structure[0]){
            case 'board-basic-supply':
                var supply = this.props.board[0][12].split('+');
                var supplySize = {};
                for (let entry of supply) {
                    supplySize[parseInt(entry.split(':')[1], 16)] = parseInt(entry.split(':')[0]);
                }

                inner = this.getInner(supplySize, kingdom[1], 'mid', true);

                content = (
                    <div className='board-content' key={0}>
                        {inner}
                    </div>
                );
            break;

            case 'board-other-supply':
                var supply = this.props.board[0][12].split('+');
                var supplySize = {};
                for (let entry of supply) {
                    supplySize[parseInt(entry.split(':')[1], 16)] = parseInt(entry.split(':')[0])
                }

                inner = this.getInner(supplySize, kingdom[2], 'small', false);

                content = (
                    <div className='board-content' key={0}>
                        {inner}
                    </div>
                );
            break;

            case 'board-landscape':
                var inner = kingdom[3].map((x, n) => <Card size='mid' index={x} key={n} />);
                content = (
                    <div className='board-content' key={0}>
                        {inner}
                    </div>
                );
            break;

            case 'board-kingdom':
                let temp = [];
                let l = ~~((kingdom[0].length) / 2)
                for (let i = 0; i < kingdom[0].length - l; i++) {
                    if (i < l){
                        temp.push(kingdom[0][i]);
                    }
                    temp.push(kingdom[0][i + l]);
                }
                var supply = this.props.board[0][12].split('+');
                var supplySize = {};
                for (let entry of supply) {
                    supplySize[parseInt(entry.split(':')[1], 16)] = parseInt(entry.split(':')[0])
                }
                inner = this.getInner(supplySize, kingdom[0], 'mid', true);
                content = (
                    <div className='board-content' key={0}>
                        {inner}
                    </div>
                );
            break;

            case 'board-deck top':
                content = this.getStack(this.props.board[0][0], false);
            break;

            case 'board-deck bot':
                content = this.getStack(this.props.board[0][1], false);
            break;

            case 'board-hand top':
                content = this.getStack(this.props.board[0][2], false);
            break;

            case 'board-hand bot':
                content = this.getStack(this.props.board[0][3], false);
            break;

            case 'board-discard top':
                content = this.getStack(this.props.board[0][6], false);
            break;

            case 'board-discard bot':
                content = this.getStack(this.props.board[0][7], false);
            break;

            case 'board-tavern top':
                content = this.getStack(this.props.board[0][8], true);
            break;

            case 'board-tavern bot':
                content = this.getStack(this.props.board[0][9], true);
            break;

            case 'board-aside top':
                content = this.getStack(this.props.board[0][10], true);
            break;

            case 'board-aside bot':
                content = this.getStack(this.props.board[0][11], true);
            break;

            case 'board-projects top':
                var inner = '';
                if (this.props.board[1][12]){
                    var cards = this.props.board[1][12].split('+');
                    inner = cards.map((entry, n)  => <Card size='small' index={parseInt(entry)} key={n}/>);
                }

                content = (
                    <div className='board-content' key={0}>
                        {inner}
                    </div>
                );
            break;

            case 'board-projects bot':
                var inner = '';
                if (this.props.board[1][13]){
                    var cards = this.props.board[1][13].split('+');
                    inner = cards.map((entry, n)  => <Card size='small' index={parseInt(entry)} key={n}/>);
                }

                content = (
                    <div className='board-content' key={0}>
                        {inner}
                    </div>
                );
            break;

            case 'board-misc top':
                var info = [3, 5, 7, 9].map(x => this.props.board[1][x]);
                info.unshift(scoreTotals[this.props.decision + 1][0]);
                info = info.map((x, n) => <div className='info-label' key={n}> {x} </div>);
                content = (
                    <div className='board-content'>
                        <div className='col' key={0}>
                            <img src={staticRoot + "/hud-icons/points.png"} />
                            <img src={staticRoot + "/hud-icons/vp.png"} />
                            <img src={staticRoot + "/hud-icons/debt.png"} />
                            <img src={staticRoot + "/hud-icons/coffers.png"} />
                            <img src={staticRoot + "/hud-icons/villagers.png"} />
                        </div>
                        <div className='col' key={1}>
                            { info }
                        </div>
                    </div>
                )
            break;

            case 'board-misc bot':
                var info = [4, 6, 8, 10].map(x => this.props.board[1][x]);
                info.unshift(scoreTotals[this.props.decision + 1][1]);
                info = info.map((x, n) => <div className='info-label' key={n}> {x} </div>);
                content = (
                    <div className='board-content'>
                        <div className='col' key={0}>
                            <img src={staticRoot + "/hud-icons/points.png"} />
                            <img src={staticRoot + "/hud-icons/vp.png"} />
                            <img src={staticRoot + "/hud-icons/debt.png"} />
                            <img src={staticRoot + "/hud-icons/coffers.png"} />
                            <img src={staticRoot + "/hud-icons/villagers.png"} />
                        </div>
                        <div className='col' key={1}>
                            { info }
                        </div>
                    </div>
                )
            break;

            case 'board-trash':
                content = this.getStack(this.props.board[0][13]);
            break;

            case 'board-inplays':
                inner = '';
                if (this.props.board[0][14]){
                    var cards = this.props.board[0][14].split('+');
                    let size = (cards.length < 10 ? 'mid' : 'small');
                    inner = cards.map((entry, n) => <Card size={size} index={parseInt(entry)} key={n}/>);
                }

                content = (
                    <div className='board-content' key={0}>
                        {inner}
                    </div>
                );
            break;

            case 'board-middle-info':
                var info = this.props.board[1].slice(0, 3).map((x, n) => <div className='info-label' key={n}> {x} </div>);
                content = (
                    <div className='board-content'>
                        <div className='row' key={0}>
                            <img src={staticRoot + "/hud-icons/actions.png"} />
                            <img src={staticRoot + "/hud-icons/buys.png"} />
                            <img src={staticRoot + "/hud-icons/coins.png"} />
                        </div>
                        <div className='row' key={1}>
                            { info }
                        </div>
                    </div>
                )
            break;

            case 'board-player-top':
                content = <div className='player-label noselect'> {players[0]} </div>;
            break;

            case 'board-player-bot':
                content = <div className='player-label noselect'> {players[1]} </div>;
            break;

            default:
                if (children.length == 0){
                    content = <div className='board-content' key={0}>
                            </div>;
                }
        }

        return (
            <div className={className} onClick={this.activate}>
                {label}
                {content}
                {children}
            </div>
        );
    }
}

// Story

class Story extends React.Component {
    render(){
        var lines = story.split('~').map((x, n) => <StoryLine line={x} key={n} num={n}
                                                    phase={phases[n + 1]}
                                                    changeIndex={this.props.changeIndex} index={this.props.index}/>);
        return <div className='story'>
            {lines}
        </div>;
    }
}

class StoryLine extends React.Component {
    constructor(props){
        super(props);
        this.clickEvent = this.clickEvent.bind(this);
    }
    clickEvent(){
        this.props.changeIndex(this.props.num);
    }
    render(){
        let indent = this.props.line.split('>')[0];
        indent = (parseInt(indent) < 7 ? parseInt(indent) : 7);
        let style = {'paddingLeft': (5 + indent * 5).toString() + '%',
                     'width': (95 - indent * 5).toString() + '%'};
        let raw = this.props.line.split('>')[1].split('|');

        let output = [raw.shift()];
        let i = 0;
        while (raw.length > 0){
            output.push(<StoryLabel text={raw.shift()} index={raw.shift()} key={i} />);
            output.push(raw.shift());
            i++ ;
        }

        let className = 'story-line' 
        if (this.props.num == this.props.index){
            className += ' highlight';
        }
        switch (this.props.phase) {
            case '0': className += ' phase-start'; break;
            case '1': className += ' phase-action'; break;
            case '2': className += ' phase-buy'; break;
            case '3': className += ' phase-night'; break;
            case '4': className += ' phase-cleanup'; break;
        }
        return(
            <div className='story-line-container'>
                <div className={className} style={style} onClick={this.clickEvent}>
                    {output}
                </div>
            </div>
        );
    }
}


class StoryLabel extends React.Component{
    constructor(props){
        super(props);

        this.innerColor = this.innerColor.bind(this);
        this.borderColor = this.borderColor.bind(this);
    }
    innerColor(){
        if (this.props.index.includes('p')) {
            var playerCol = ['B54F4F', '4644A6']
            return playerCol[parseInt(this.props.index.slice(1))];
        } else {
            return interiors[this.props.index];
        }
    }

    borderColor(){
        if (this.props.index.includes('p')) {
            var playerCol = ['3F1D1D', '1D1C38']
            return playerCol[parseInt(this.props.index.slice(1))];
        } else {
            return borders[this.props.index];
        }
    }

    isDark(){
        let color = this.innerColor();
        let sum = 0;
        for (var i = 0; i < 5; i += 2){
            sum += parseInt(color.slice(i, i + 2), 16);
        }
        return sum < 384;
    }

    render(){
        var style = {
                     'background': '#' + this.innerColor(),
                     'borderColor': '#' + this.borderColor(),
                     'color': '#' + (this.isDark() ? 'FFF' : '000')
                    };
        return <div className='story-label' style={style}> {this.props.text} </div>;
    }
}


class StoryLegend extends React.Component {
    render(){
        let output = [];
        var turnLabels = [];
        if (turnPoints.length > 0){
            var turnLengths = [...Array(turnPoints.length - 1).keys()].map(x => turnPoints[x + 1] - turnPoints[x]);
            turnLengths.push(boards.length - turnPoints.slice(-1)[0]);
            var owners = [];
            var aliases = players.map(x => x.slice(0, 1));
            if (aliases[0] == aliases[1]){
                aliases = players.map(x => x.slice(0, 2));
            }

            let i = 0;
            let last = 1;
            for (let turn of turnPoints){
                if (last != 0 && turnOwners[turn + 1] == 0){
                    i++ ;
                }
                turnLabels.push(aliases[turnOwners[turn + 1]] + i.toString());
                last = turnOwners[turn + 1];
                owners.push(last);
            }

            let highlighted = turnPoints.filter(point => point <= this.props.index).length - 1;
            for (let i = 0; i < turnLabels.length; i++){
                output.push(<LegendEntry key={i} point={turnPoints[i]} length={turnLengths[i]} label={turnLabels[i]} owner={owners[i]} 
                                         highlighted={i==highlighted} changeIndex={this.props.changeIndex}/>);
            }
        }
        return <div className='story-legend'> {output} </div>;
    }
}


class LegendEntry extends React.Component {
    constructor(props){
        super(props);
        this.clickEvent = this.clickEvent.bind(this);
    }
    clickEvent(){
        this.props.changeIndex(this.props.point);
    }
    render() {
        let style = {'flexGrow': this.props.length};
        let endTag = (this.props.owner == 0 ? ' first' : ' second')
        if (this.props.highlighted){
            endTag += ' highlight'
        }
        return <div className={'legend-entry noselect' + endTag} style={style} onClick={this.clickEvent}>{this.props.label}</div>;
    }
}


// Controls

class BaseContainer extends React.Component {
    constructor(props) {
        super(props);
    }
    render() {
        return  (
            <div className='controls'>
                <ControlButton name='back-turn' buttonShift={this.props.buttonShift} />
                <ControlButton name='back-step' buttonShift={this.props.buttonShift} />
                <ControlButton name='back' buttonShift={this.props.buttonShift} />
                <ControlButton name='forward' buttonShift={this.props.buttonShift} />
                <ControlButton name='forward-step' buttonShift={this.props.buttonShift} />
                <ControlButton name='forward-turn' buttonShift={this.props.buttonShift} />
            </div>
        );
    }  
}

class ControlButton extends React.Component {
    constructor(props) {
        super(props);
        this.clickEvent = this.clickEvent.bind(this);
    }
    clickEvent() {
        this.props.buttonShift(this.props.name);
    }
    render() {
        return <div className='control-button' id={this.props.name} onClick={this.clickEvent}
                style={{backgroundImage : 'url(' + staticRoot + '/' + this.props.name + '.png)'}}/>;
    }
}


// Bottom Tabs

class BottomTabs extends React.Component{
    render() {
        return <div className='bottom-tabs'>
            <BottomTab inner='table' index={this.props.index}/>
        </div>;
    }
}


class BottomTab extends React.Component{
    constructor(props) {
        super(props);
        this.state = {hovered: false, showing: false, shouldShow: false}
        this.hoverAction = this.hoverAction.bind(this);
        this.clickAction = this.clickAction.bind(this);
        this.leaveAction = this.leaveAction.bind(this);
    }
    hoverAction(){
        this.setState({hovered: true});
    }
    leaveAction(){
        this.setState({hovered: false});
    }
    clickAction(){
        this.setState({shouldShow: !this.state.shouldShow, showing: true});
    }
    render() {
        let classes = 'bottom-tab';
        let inner;
        if (this.state.hovered){
                classes += ' hovered';
        }
        if (this.state.shouldShow){
                classes += ' active';
        }
        switch (this.props.inner){
            case 'kingdom':
                inner = <Kingdom showing={this.state.showing} />;
            break;
            case 'table':
                inner = <Table index={this.props.index} showing={this.state.showing}/>;
            break;
        }
        return <div className={classes} onTransitionEnd={() => {this.setState({showing: this.state.shouldShow});}}>
            <img className={this.props.inner + '-tab-icon'} onClick={this.clickAction} onMouseOver={this.hoverAction} onMouseLeave={this.leaveAction}
             src={ staticRoot + "/hud-icons/" + this.props.inner + ".png" } />
            {inner}
        </div>
    }
}



function getDifference(firstTurn, secondTurn) {
    output = [];
    for (i = 0; i < 2; i++){
        let firstPart = firstTurn.split('/')[i];
        let secondPart = firstTurn.split('/')[i];
        let counts = {};
        if (firstPart) {
            let positives = firstPart.split('+').map(x => x.split(':'));
            counts = positives.reduce((count, entry) => {count[entry[1]] = parseInt(entry[0]); return count}, counts);
        }
        if (secondPart) {
            let negatives = secondPart.split('+').map(x => x.split(':'));
            counts = negatives.reduce((count, entry) => {
                count[entry[1]] = (entry[1] in count ? count[entry[1]] : 0) - parseInt(entry[0]);
                return count
            } , counts);
        }
        output.push(counts);
    }
    return output;
}


class Table extends React.Component{
    constructor(props) {
        super(props);
        this.state = {value: 'Count', decks: 'All'}
    }
    render() {
        let data = turnDecks.split('~');
        let output = [];
        var turnLabels = [];
        let indexTurn = 0;
        if (this.props.showing){
            var aliases = players.map(x => x.slice(0, 1));
            if (aliases[0] == aliases[1]){
                aliases = players.map(x => x.slice(0, 2));
            }

            let i = 0;
            let last = 1;
            for (let turn of turnPoints){
                if (last != 0 && turnOwners[turn + 1] == 0){
                    i++ ;
                }
                turnLabels.push(aliases[turnOwners[turn + 1]] + i.toString());
                last = turnOwners[turn + 1];
            }

            for (indexTurn = 0; indexTurn < turnPoints.length; indexTurn++){
                if (turnPoints[indexTurn] > this.props.index){
                    break;
                }
            }

            let lowBound = indexTurn - 8;
            lowBound = (lowBound > data.length - 17 ? data.length - 17 : lowBound);
            lowBound = (lowBound < 0 ? 0 : lowBound);
            for (let turn = lowBound; turn < lowBound + 16; turn++){
                if (turn < data.length){
                    let player = turnOwners[turnPoints[turn + 1]];
                    let active = turn == indexTurn - 1;
                    if (this.state.decks == 'all'){
                        var column = data[turn].split('/').map(x => x.split('+').map(y => y.split(':')));
                        output.push(<TableTurn key={turn} data={column} label={turnLabels[turn]} player={player} active={active} doubled={false}/>);
                    } else {
                        // var column = getDifference((turn > 0 ? data[turn - 1] : ''),
                        //                            data[turn]);
                        // output.push(<TableTurn key={turn} data={column} label={turnLabels[turn]} player={player} active={active} doubled={true}/>);
                        var column = data[turn].split('/').map(x => x.split('+').map(y => y.split(':')));
                        output.push(<TableTurn key={turn} data={column} label={turnLabels[turn]} player={player} active={active} doubled={false}/>);
                    }
                }
            }
        }
        return <div className='table-tab'>
                <div className='table'>
                    {output}
                </div>
                <div className='table-controls'>
                    <div className='table-control-row'>
                        <div className='table-control-label noselect'> Cards: </div>
                        <TableControl name='All' active={this.state.decks} clickEvent={() => this.setState({decks: 'All'})}/>
                        <TableControl name='Gains' active={this.state.decks} clickEvent={() => this.setState({decks: 'Gains'})}/>
                    </div>
                    <div className='table-control-row'>
                        <div className='table-control-label noselect'> Value: </div>
                        <TableControl name='Count' active={this.state.value} clickEvent={() => this.setState({value: 'Count'})}/>
                        <TableControl name='Worth' active={this.state.value} clickEvent={() => this.setState({value: 'Worth'})}/>
                        <TableControl name='Score' active={this.state.value} clickEvent={() => this.setState({value: 'Score'})}/>
                    </div>
                </div>
            </div>
    }
}


class TableTurn extends React.Component{
    render() {
        let output = [];
        for (let i = 0; i < 2; i++){
            output.push(<TableCol key={i} player={i} cards={this.props.data[i]} doubled={this.props.doubled} />);
        }
        let labelClass = 'table-turn-label' + (this.props.player == 0 ? ' first' : ' second');
        if (this.props.active){
            labelClass += ' active';
        }
        return <div className='table-turn-container'>
            <div className={labelClass}>{this.props.label}</div>
            <div className='table-turn'>
                {output}
            </div>
        </div>;
    }
}


class TableCol extends React.Component{
    render() {
        let output = (this.props.doubled ? [[], []] : []);
        let j = 0;
        for (let stack of this.props.cards){
            let [amount, index] = stack
            if (this.props.doubled){
                for (let i = 0; i < parseInt(amount); i++){
                    output.push(<Card key={j} size='tiny' index={parseInt(index, 16)} />);
                    j++ ;
                }
            } else {
                for (let i = 0; i < parseInt(amount); i++){
                    output.push(<Card key={j} size='tiny' index={parseInt(index, 16)} />);
                    j++ ;
                }
            }
        }
        let colClass = 'table-col' + (this.props.player == 0 ? ' first' : ' second')

        return <div className={colClass}>
            {output}
        </div>;
    }
}


class TableControl extends React.Component {
    render () {
        let className = 'table-control noselect'
        if (this.props.active == this.props.name){
            className += ' active';
        }
        return (
            <div className={className} onClick={this.props.clickEvent}>
                {this.props.name}
            </div>
        );
    }
}


const mainContainer = document.querySelector('.content');
ReactDOM.render(<Container />, mainContainer);
