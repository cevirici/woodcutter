
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
                <div className='card-label'>
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
            <div className='stack-label'>{this.props.stackName}</div>
            {output}
        </div>
    }
}


class Board extends React.Component {
    render(){
        var boardString = boards.split('~')[this.props.index + 1];
        var cardStacks = boardString.split('|');
        var inPlays = (cardStacks[4] ? cardStacks[4] : cardStacks[5]);
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
                <div className='label top'>{players[0]}</div>
                <div className='label bot'>{players[1]}</div>
            </div>
        );
    }
}


class StoryLabel extends React.Component{
    isDark(){
        var color = interiors[this.props.index];
        var sum = 0;
        for (var i = 0; i < 5; i += 2){
            sum += parseInt(color.slice(i, i + 2), 16);
        }
        return sum < 384;
    }

    render(){
        var style = {
                     'background': '#' + interiors[this.props.index],
                     'borderColor': '#' + borders[this.props.index],
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
        let style = {'width': (90 - indent * 5).toString() + '%'};
        let raw = this.props.line.split('>')[1].split('|');
        let output = [raw.shift()];
        let i = 0;
        while (raw.length > 0){
            output.push(<StoryLabel text={raw.shift()} index={raw.shift()} key={i} />);
            output.push(raw.shift());
            i++ ;
        }

        let className = 'story-line' + (this.props.num == this.props.index ? ' highlight' : '');
        return(
            <div className={className} style={style} onClick={this.clickEvent}>
                {output}
            </div>
        );
    }
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
        this.state = {index: 0};
        this.changeIndex=this.changeIndex.bind(this);
        this.buttonShift=this.buttonShift.bind(this);
    }
    changeIndex(i){
        this.setState({index: i});
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
                var newIndex = (this.state.index > n - 1 ? n - 1 : this.state.index + 1);
                this.changeIndex(newIndex);
                break;
            case 'forward-step':
                var newIndex = (this.state.index > n - 1 ? n - 1 : this.state.index + 1);
                while ((!stepPoints.includes(newIndex)) && newIndex < n - 1){
                    newIndex++;
                }
                this.changeIndex(newIndex);
                break;
            case 'forward-turn':
                var newIndex = (this.state.index > n - 1 ? n - 1 : this.state.index + 1);
                while ((!turnPoints.includes(newIndex)) && newIndex < n - 1){
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
                <div className='base-container'>
                    <div className='controls'>
                        <ControlButton name='back-turn' buttonShift={this.buttonShift} />
                        <ControlButton name='back-step' buttonShift={this.buttonShift} />
                        <ControlButton name='back' buttonShift={this.buttonShift} />
                        <ControlButton name='forward' buttonShift={this.buttonShift} />
                        <ControlButton name='forward-step' buttonShift={this.buttonShift} />
                        <ControlButton name='forward-turn' buttonShift={this.buttonShift} />
                    </div>
                </div>
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

const mainContainer = document.querySelector('.content');
ReactDOM.render(<Container />, mainContainer);