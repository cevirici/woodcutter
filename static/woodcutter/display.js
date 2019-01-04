

class Container extends React.Component{
    constructor(props) {
        super(props);
        let index = (logIndex >= boards.split('~').length - 1 ? boards.split('~').length - 2 : logIndex);
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
        let n = boards.split('~').length;
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
                <BaseContainer buttonShift={this.buttonShift} index={this.state.index} />
                <div className='board-container'>
                    <Board index={this.state.index}/>
                </div>
                <div className='story-container'>
                    <Story changeIndex={this.changeIndex} index={this.state.index}/>
                </div>
            </React.Fragment>
        );
    }
}

// Board

class Board extends React.Component {
    render(){
        var boardString = boards.split('~')[this.props.index + 1].split('/')[0];
        var emptyString = empties.split('~')[this.props.index + 1];
        var cardStacks = boardString.split('|');
        var inPlays = inplays.split('~')[this.props.index + 1];
        return(
            <div className='board'>
                <CardStack cards={cardStacks[0]} classes='decks top' stackName='DECK'/>
                <CardStack cards={cardStacks[1]} classes='decks bot' stackName='DECK'/>
                <CardStack cards={cardStacks[2]} classes='hands top' stackName='HAND'/>
                <CardStack cards={cardStacks[3]} classes='hands bot' stackName='HAND'/>
                <InplayStack cards={inPlays} classes='inplays' stackName='IN PLAY'/>
                <CardStack cards={cardStacks[6]} classes='discards top' stackName='DISCARD'/>
                <CardStack cards={cardStacks[7]} classes='discards bot' stackName='DISCARD'/>
                <CardStack cards={cardStacks[8]} classes='tavern top' stackName='TAVERN'/>
                <CardStack cards={cardStacks[9]} classes='tavern bot' stackName='TAVERN'/>
                <CardStack cards={cardStacks[10]} classes='others top' stackName='ASIDE'/>
                <CardStack cards={cardStacks[11]} classes='others bot' stackName='ASIDE'/>
                <CardStack cards={cardStacks[12]} classes='supply' stackName='SUPPLY'/>
                <CardStack cards={cardStacks[13]} classes='trash' stackName='TRASH'/>
                <EmptyStack cards={emptyString} />
                <div className='label top noselect'>{players[0]}</div>
                <div className='label bot noselect'>{players[1]}</div>
            </div>
        );
    }
}


class CardStack extends React.Component {
    cardList(){
        return this.props.cards.split('+').map(c => c.split(':'));
    }

    render() {
        var output = '';
        if (this.props.cards){
            var output = this.cardList().map((n, i) => <Card amount={parseInt(n[0])} index={parseInt(n[1], 16)} key={i}/>);
        }
        var className = 'card-stack ' + this.props.classes;
        return <div className={className}>
            <div className='stack-label noselect'>{this.props.stackName}</div>
            {output}
        </div>
    }
}


function InplayStack(props) {
    var output = '';
    if (props.cards){
        var output = props.cards.split('|').map((n, i) => <Card amount={0} index={parseInt(n)} key={i}/>);
    }
    return <div className='card-stack inplays'>
            <div className='stack-label noselect'>IN PLAY</div>
        {output}
    </div>
}


function EmptyStack(props) {
    var output = '';
    if (props.cards){
        var output = props.cards.split('|').map((n, i) => <Card amount={0} index={parseInt(n)} key={i}/>);
    }
    return <div className='empties'>
            <div className='stack-label noselect'>EMPTY</div>
        {output}
    </div>
}


class Card extends React.Component {
    divStyle() {
        return {backgroundImage: 'url(' + staticRoot + '/card_images/' + urls[this.props.index] + '-mid.jpg)'}
    }

    borderStyle() {
        return {background: '#' + borders[this.props.index]}
    }

    render() {
        let innerText = (this.props.label ? <div className='inner-text'> {this.props.label} </div> : '');
        if (this.props.amount == 0){
            return (
                <div className='card-small' style={this.borderStyle()}>
                    <div className='card-small-inner' style={this.divStyle()}>
                    </div>
                </div>
            );
        } else {
            return (
                <div className='card-container'>
                    <div className='card-label noselect'>
                        {this.props.amount}
                    </div>
                    <div className='card-small' style={this.borderStyle()}>
                        <div className='card-small-inner' style={this.divStyle()}>
                        {innerText}
                        </div>
                    </div>
                </div>
            );
        }
    }
}


class MidCard extends Card {
    divStyle() {
        return {backgroundImage: 'url(' + staticRoot + '/card_images/' + urls[this.props.index] + '.jpg)'}
    }
    render() {
        return (
            <div className='card-mid' style={this.borderStyle()}>
                <div className='card-mid-inner' style={this.divStyle()}>
                </div>
            </div>
        );
    }
}


class BigCard extends Card {
    divStyle() {
        return {backgroundImage: 'url(' + staticRoot + '/card_images/' + urls[this.props.index] + '.jpg)'}
    }
    render() {
        return (
            <div className='card-big' style={this.borderStyle()}>
                <div className='card-big-inner' style={this.divStyle()}>
                </div>
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
            turnLengths.push(boards.split('~').length - turnPoints.slice(-1)[0]);
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
        return <div className='story-legend'> {output} </div>
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


// Base

class BaseContainer extends React.Component {
    constructor(props) {
        super(props);
        this.changeMode = this.changeMode.bind(this);
        this.state = {mode: 0};
    }
    changeMode(i){
        this.setState({mode: i});
    }
    render() {
        switch (this.state.mode){
            case 0:
                var panel = <BaseInfo index={this.props.index}/>;
            break;
            case 1:
                var panel = <BaseScore index={this.props.index}/>;
            break;
        }
        return  (
            <div className='base-container'>
                <div className='controls'>
                    <ControlButton name='back-turn' buttonShift={this.props.buttonShift} />
                    <ControlButton name='back-step' buttonShift={this.props.buttonShift} />
                    <ControlButton name='back' buttonShift={this.props.buttonShift} />
                    <ControlButton name='forward' buttonShift={this.props.buttonShift} />
                    <ControlButton name='forward-step' buttonShift={this.props.buttonShift} />
                    <ControlButton name='forward-turn' buttonShift={this.props.buttonShift} />
                </div>
                <div className='mode-switches'>
                    <ModeSwitch active={this.state.mode} index={0} src='info-panel.png' changeMode={this.changeMode}/>
                    <ModeSwitch active={this.state.mode} index={1} src='score-panel.png' changeMode={this.changeMode}/>
                </div>
                {panel}
            </div>);
    }  
}


class BaseInfo extends React.Component {
    render() {
        let boardString = boards.split('~')[this.props.index + 1].split('/')[1];
        let data = boardString.split('|');
        let scoreData = scores.split('~')[this.props.index + 1].split(' ');
        let scoreTotals = [];
        var amount, worth, index;
        for (let player = 0; player < 2; player++) {
            scoreTotals.push(0);
            if (scoreData[player].length > 0){
                for (let entry of scoreData[player].split('/')) {
                    [amount, worth, index] = entry.split('|');
                    scoreTotals[player] += parseInt(amount) * parseInt(worth);
                }
            }
        }
        return <div className='info'>
                    <div className='icon-row'>
                        <img src={staticRoot + "/hud-icons/actions.png"} />
                        <img src={staticRoot + "/hud-icons/buys.png"} />
                        <img src={staticRoot + "/hud-icons/coins.png"} />
                        <img src={staticRoot + "/hud-icons/debt.png"} />
                        <img src={staticRoot + "/hud-icons/coffers.png"} />
                        <img src={staticRoot + "/hud-icons/villagers.png"} />
                        <img src={staticRoot + "/hud-icons/vp.png"} />
                        <img src={staticRoot + "/hud-icons/points.png"} />
                    </div>
                    <div className='label-row'>
                        <div className='single-label noselect'> {data[0]} </div>
                        <div className='single-label noselect'> {data[1]} </div>
                        <div className='single-label noselect'> {data[2]} </div>
                        <div className='double-label'>
                            <div className='top-label noselect'>{data[3]}</div>
                            <div className='bot-label noselect'>{data[4]}</div>
                        </div>
                        <div className='double-label'>
                            <div className='top-label noselect'>{data[5]}</div>
                            <div className='bot-label noselect'>{data[6]}</div>
                        </div>
                        <div className='double-label'>
                            <div className='top-label noselect'>{data[7]}</div>
                            <div className='bot-label noselect'>{data[8]}</div>
                        </div>
                        <div className='double-label'>
                            <div className='top-label noselect'>{data[9]}</div>
                            <div className='bot-label noselect'>{data[10]}</div>
                        </div>
                        <div className='double-label'>
                            <div className='top-label noselect'>{scoreTotals[0]}</div>
                            <div className='bot-label noselect'>{scoreTotals[1]}</div>
                        </div>
                    </div>
                </div>
    }
}


class BaseScore extends React.Component {
    render() {
        let scoreData = scores.split('~')[this.props.index + 1].split(' ');
        var amount, worth, index;
        let outputStrings = [];
        let scoreTotals = [];
        for (let player = 0; player < 2; player++) {
            outputStrings.push([]);
            scoreTotals.push(0);
            if (scoreData[player].length > 0){
                for (let entry of scoreData[player].split('/')) {
                    [amount, worth, index] = entry.split('|');
                    scoreTotals[player] += parseInt(amount) * parseInt(worth);
                    outputStrings[player].push(<Card amount={amount} label={worth} index={parseInt(index)} key={entry}/>);
                }
            }
        }
        return (
        <div className='base-scores'>
            <div className='row first'>{outputStrings[0]}</div>
            <div className='totals first'>{scoreTotals[0]}</div>
            <div className='row second'>{outputStrings[1]}</div>
            <div className='totals second'>{scoreTotals[1]}</div>
        </div>);
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


class ModeSwitch extends React.Component {
    constructor(props) {
        super(props);
        this.clickEvent = this.clickEvent.bind(this);
    }
    clickEvent() {
        this.props.changeMode(this.props.index);
    }
    render() {
        let className = 'mode-switch';
        if (this.props.index == this.props.active) {
            className += ' active'
        }
        return <div onClick={this.clickEvent} className={className}>
            <img src={staticRoot + '/hud-icons/' + this.props.src} />
        </div>;
    }
}

// Bottoms

class BottomTabs extends React.Component{
    constructor(props) {
        super(props);
        this.state = {'kingdomShow': false, 'kingdomHover': false};
        this.moveTab = this.moveTab.bind(this);
    }
    moveTab(tab, action) {
        var updater = {};
        switch (action){
            case 1:
                updater[tab + 'Hover'] = true;
            break;
            case 2:
                updater[tab + 'Show'] = !this.state[tab + 'Show'];
            break;
            case 3:
                updater[tab + 'Hover'] = false;
            break
        }
        this.setState(updater);
    }
    render() {
        return <React.Fragment>
            <Kingdom moveTab={this.moveTab} show={this.state['kingdomShow']} hover={this.state['kingdomHover']} />
        </React.Fragment>;
    }
}


class Kingdom extends React.Component{
    constructor(props) {
        super(props);
        this.hoverAction = this.hoverAction.bind(this);
        this.clickAction = this.clickAction.bind(this);
        this.leaveAction = this.leaveAction.bind(this);
    }
    hoverAction(){
        this.props.moveTab('kingdom', 1);
    }
    leaveAction(){
        this.props.moveTab('kingdom', 3);
    }
    clickAction(){
        this.props.moveTab('kingdom', 2);
    }
    render() {
        let rows = kingdom.split('~');
        let output = [];
        let i = 0;
        for (var row of rows){
            let rowDat = [];
            if (row.length > 0) {
                if (output.length == 0){
                    rowDat.push(row.split('|').map((i, n) => <BigCard index={parseInt(i)} key={n} />));
                } else {
                    rowDat.push(row.split('|').map((i, n) => <MidCard index={parseInt(i)} key={n} />));
                }
            }
            output.push(<div className='kingdom-container' key={i}> {rowDat} </div>);
            i++ ;
        }
        let classes = 'bottom-tab';
        if (this.props.hover){
                classes += ' hovered';
        }
        if (this.props.show){
                classes += ' active';
        }
        return  <div className={classes}>
                    <img className='kingdom-tab-icon' onClick={this.clickAction} onMouseOver={this.hoverAction} onMouseLeave={this.leaveAction} src={ staticRoot + "/hud-icons/kingdom.png" } />
                    <div className='kingdom-tab' onClick={this.clickAction}>
                        {output}
                    </div>
                </div>
    }
}


const mainContainer = document.querySelector('.content');
ReactDOM.render(<Container />, mainContainer);
const bottomContainer = document.querySelector('.bottom-tabs');
ReactDOM.render(<BottomTabs />, bottomContainer);
