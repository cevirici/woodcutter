
class Card extends React.Component {
    divStyle() {
        return {backgroundImage: 'url(' + staticRoot + '/card_images/' + urls[this.props.index] + '-mid.jpg)'}
    }

    borderStyle() {
        return {background: '#' + borders[this.props.index]}
    }

    render() {
        return (
            <div className='card-container'>
                <div className='card-label noselect'>
                    {this.props.amount}
                </div>
                <div className='card-small' style={this.borderStyle()}>
                    <div className='card-small-inner' style={this.divStyle()}>
                    </div>
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


class Board extends React.Component {
    render(){
        var boardString = boards.split('~')[this.props.index + 1].split('/')[0];
        var cardStacks = boardString.split('|');
        var inPlays = (turnOwners[this.props.index] == 0 ? cardStacks[4] : cardStacks[5]);
        return(
            <div className='board'>
                <CardStack cards={cardStacks[0]} classes='decks top' stackName='DECK'/>
                <CardStack cards={cardStacks[1]} classes='decks bot' stackName='DECK'/>
                <CardStack cards={cardStacks[2]} classes='hands top' stackName='HAND'/>
                <CardStack cards={cardStacks[3]} classes='hands bot' stackName='HAND'/>
                <CardStack cards={inPlays} classes='inplays' stackName='IN PLAY'/>
                <CardStack cards={cardStacks[6]} classes='discards top' stackName='DISCARD'/>
                <CardStack cards={cardStacks[7]} classes='discards bot' stackName='DISCARD'/>
                <CardStack cards={cardStacks[8]} classes='tavern top' stackName='TAVERN'/>
                <CardStack cards={cardStacks[9]} classes='tavern bot' stackName='TAVERN'/>
                <CardStack cards={cardStacks[10]} classes='others top' stackName='ASIDE'/>
                <CardStack cards={cardStacks[11]} classes='others bot' stackName='ASIDE'/>
                <CardStack cards={cardStacks[12]} classes='supply' stackName='SUPPLY'/>
                <CardStack cards={cardStacks[13]} classes='trash' stackName='TRASH'/>
                <div className='label top noselect'>{players[0]}</div>
                <div className='label bot noselect'>{players[1]}</div>
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
        let style = {'padding-left': (5 + indent * 5).toString() + '%'};
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
        return(
            <div className='story-line-container'>
                <div className={className} style={style} onClick={this.clickEvent}>
                    {output}
                </div>
            </div>
        );
    }
}


function BaseContainer(props){
    let boardString = boards.split('~')[props.index + 1].split('/')[1];
    let data = boardString.split('|');
    return  (
        <div className='base-container'>
            <div className='controls'>
                <ControlButton name='back-turn' buttonShift={props.buttonShift} />
                <ControlButton name='back-step' buttonShift={props.buttonShift} />
                <ControlButton name='back' buttonShift={props.buttonShift} />
                <ControlButton name='forward' buttonShift={props.buttonShift} />
                <ControlButton name='forward-step' buttonShift={props.buttonShift} />
                <ControlButton name='forward-turn' buttonShift={props.buttonShift} />
            </div>
            <div className='info'>
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
                        <div className='top-label noselect'>{data[11]}</div>
                        <div className='bot-label noselect'>{data[12]}</div>
                    </div>
                </div>
            </div>
        </div>);
}



class Story extends React.Component {
    render(){
        var lines = story.split('~').map((x, n) => <StoryLine line={x} key={n} num={n} changeIndex={this.props.changeIndex} index={this.props.index}/>);
        return <div className='story'>
            {lines}
        </div>;
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


class Container extends React.Component{
    constructor(props) {
        super(props);
        this.state = {index: 0, showKingdom: false};
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
                rowDat.push(row.split('|').map((i, n) => <BigCard index={parseInt(i)} key={n} />));
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

const mainContainer = document.querySelector('.content');
ReactDOM.render(<Container />, mainContainer);
const bottomContainer = document.querySelector('.bottom-tabs');
ReactDOM.render(<BottomTabs />, bottomContainer);
