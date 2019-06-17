import React, { Component} from "react"
import axios from "axios"
import CircularProgress from '@material-ui/core/CircularProgress'
import "./NPuzzle.css"


Array.prototype.move = function(from,to){
	this.splice(to,0,this.splice(from,1)[0]);
	return this;
}


class Visu extends Component{
	constructor(props) {
		super(props)
		this.state = {
			currNPuzzle: [...this.props.baseNPuzzle],
			size: this.props.size,
			heuristic: 'manhattan',
			greedy: false,
			goal: [],
			stats: {},
			isSolving: false,
			isSolvable: true,
			isMoving: false,
			currMove: 0,
			totalMoves: 0
		}
		var solution = []
		this.solvePuzzle = this.solvePuzzle.bind(this)
		this.stopSolving = this.stopSolving.bind(this)
		this.resetPuzzle = this.resetPuzzle.bind(this)
	}


	resetPuzzle(){
		this.setState({
			currNPuzzle: [...this.props.baseNPuzzle],
			size: this.props.size,
			heuristic: 'manhattan',
			greedy: false,
			goal: [],
			stats: {},
			isSolving: false,
			isSolvable: true,
			isMoving: false,
			currMove: 0,
			totalMoves: 0
		})
	}


	stopSolving(){
		axios.get('/stop-solving', {
			params: {}
		})
		.then((response) => {
			console.log(response)
			if (response.data == 'Success') {
				this.setState({isSolving: false})
			}
		})
	}


	makeMove(move){
		let movingSpeed = 100
		if (this.solution.length > 50) {
			movingSpeed = 40
		}
		let nextMove = this.state.currNPuzzle
		let zeroPos = nextMove.indexOf(0)
		if (this.solution.length === 0) {
			this.setState({
				currNPuzzle: this.state.goal,
				isMoving: false,
				currMove: this.state.totalMoves
			})
			return
		}

		if (move == 0) {
			[nextMove[zeroPos], nextMove[zeroPos - this.state.size]] = [nextMove[zeroPos - this.state.size], nextMove[zeroPos]];
		} else if (move == 1) {
			[nextMove[zeroPos], nextMove[zeroPos + this.state.size]] = [nextMove[zeroPos + this.state.size], nextMove[zeroPos]];
		} else if (move == 2) {
			[nextMove[zeroPos], nextMove[zeroPos + 1]] = [nextMove[zeroPos + 1], nextMove[zeroPos]];
		} else {
			[nextMove[zeroPos], nextMove[zeroPos - 1]] = [nextMove[zeroPos - 1], nextMove[zeroPos]];
		}

		this.setState(prevState => ({
			currNPuzzle: nextMove,
			currMove: prevState.currMove + 1
		}), () => {
			setTimeout(() => this.makeMove(this.solution.shift()), movingSpeed)
		})
	}


	solvePuzzle(){
		this.setState({isSolving: true})
		axios.get('/solve', {
			params: {
				baseNPuzzle: this.props.baseNPuzzle.join(' '),
				greedy: this.state.greedy,
				heuristic: this.state.heuristic
			}
		})
		.then((response) => {
			console.log(response)
			this.setState({isSolving: false})
			if (response.data.error == true || response.data.solvable == false) {
				this.setState({
					isSolvable: false,
					stats: response.data.stats
				})
			} else if (response.data.found == true) {
				this.solution = response.data.solution
				this.setState({
					stats: response.data.stats,
					goal: response.data.goal,
					isMoving: true,
					totalMoves: this.solution.length
				}, this.makeMove(this.solution.shift()))
			}
		})
	}


	render(){
		return(
			<React.Fragment>
				<div className="puzzle-container">
					{this.state.currNPuzzle.map((e, index) => {
						return (<div
									key={'puzzle-case_' + index}
									className="puzzle-case"
									style={{
										width: (100 / this.state.size) + "%",
										height: (100 / this.state.size) + "%"
									}}
								>
							<div className="case-number">{e != 0 ? e : ''}</div>
						</div>)
					})}
				</div>
				{!this.state.isSolving && this.state.isSolvable && this.state.currNPuzzle != this.state.goal && !this.state.isMoving &&
					<React.Fragment>
						<div className="input-container">
							<div className="form-caption">Greedy?</div>
							<select
								className="solvable-input"
								onChange={(e) => this.setState({greedy: e.target.value})}
								value={this.state.greedy}
							>
								<option value={true}>Yes</option>
								<option value={false}>No</option>
							</select>
						</div>
						<div className="input-container">
							<div className="form-caption">Choose a heuristic</div>
							<select
								className="solvable-input heuristic-input"
								onChange={(e) => this.setState({heuristic: e.target.value})}
								value={this.state.heuristic}
							>
								<option value="uniform">Uniform</option>
								<option value="manhattan">Manhattan</option>
								<option value="euclidian">Euclidian</option>
								<option value="linear_conflicts">Linear Conflicts</option>
								<option value="hamming_good">Hamming Good</option>
								<option value="hamming_bad">Hamming Bad</option>
								<option value="custom">Custom</option>
							</select>
						</div>
						<button
							className="generic-button"
							onClick={this.solvePuzzle}
						>
							Solve
						</button>
					</React.Fragment>
				}
				{this.state.isSolving &&
					<div className="loading-container">
						<CircularProgress />
						<div className="loading-text">Looking for solution...</div>
						<button
							className="generic-button"
							onClick={this.stopSolving}
						>
							Stop Solving
						</button>
					</div>
				}
				{!this.state.isSolvable &&
					<div className="unsolvable-text">This NPuzzle is unsolvable !</div>
				}
				{(this.state.isMoving || this.state.currNPuzzle == this.state.goal || !this.state.isSolvable) &&
					<React.Fragment>
						{this.state.isSolvable &&
							<div className="moves-text">Current move: {this.state.currMove} / {this.state.totalMoves}</div>
						}
						<div className="stats-container">
							<div className="stats-text">Memory used: <div className="stat-value">{this.state.stats.memory} Mo</div></div>
							<div className="stats-text">Time in seconds: <div className="stat-value">{this.state.stats.time / 1000000}</div></div>
							<div className="stats-text">Nodes created: <div className="stat-value">{this.state.stats.nodes_created}</div></div>
							<div className="stats-text">Memory complexity: <div className="stat-value">{this.state.stats.nodes_stocked}</div></div>
							<div className="stats-text">Time complexity: <div className="stat-value">{this.state.stats.turns}</div></div>
						</div>
						{!this.state.isMoving &&
							<button
							className="generic-button"
							onClick={this.resetPuzzle}
							>
								Retry
							</button>
						}
					</React.Fragment>
				}
				{!this.state.isSolving && !this.state.isMoving &&
					<button
						className="generic-button"
						onClick={this.props.resetStep}
					>
						Reset
					</button>
				}
			</React.Fragment>
		)
	}
}


class InputForm extends Component{
	constructor(props) {
		super(props)
		this.state = {
			inputPuzzle: '',
			size: 3,
			isSolvable: true,
			iterations: 3000,
		}
	}


	handleSizeInput(value){
		let size = value

		if (value > 8) {
			size = 8
		} else if (value < 3) {
			size = 3
		}
		this.setState({size: size})
	}


	handleIterationsInput(value){
		let iterations = value

		if (value > 10000) {
			iterations = 10000
		} else if (value < 0) {
			iterations = 0
		}
		this.setState({iterations: iterations})
	}


	render(){
		return(
			<div className="input-form-container">
				<div className="form-caption section-title">Input list of numbers separated by space</div>
				<input
					type="text"
					name="puzzle"
					className="puzzle-input"
					onChange={(e) => this.setState({inputPuzzle: e.target.value})}
				>
				</input>
				<button className="input-validation" onClick={() => this.props.sendInputPuzzle(this.state.inputPuzzle)}>Validate</button>
				<div className="form-separator">OR</div>
				<div className="form-caption section-title">Generate a random puzzle</div>
				<div className="form-generator-container">
					<div className="input-container">
						<div className="form-caption">Size between 3 and 8</div>
						<input
							className="size-input"
							type="number"
							min="3"
							max="8"
							onChange={(e) => this.handleSizeInput(e.target.value)}
							value={this.state.size}
						>
						</input>
					</div>
					<div className="input-container">
						<div className="form-caption">Solvable?</div>
						<select
							className="solvable-input"
							onChange={(e) => this.setState({isSolvable: e.target.value})}
							value={this.state.isSolvable}
						>
							<option value={true}>Yes</option>
							<option value={false}>No</option>
						</select>
					</div>
					<div className="input-container">
						<div className="form-caption">Number of iteration between 0 and 10000</div>
						<input
							className="iterations-input"
							type="number"
							min="0"
							step="1000"
							max="10000"
							onChange={(e) => this.handleIterationsInput(e.target.value)}
							value={this.state.iterations}
						>
						</input>
					</div>
					<button className="input-validation" onClick={() => this.props.sendGenParams(this.state.size, this.state.isSolvable, this.state.iterations)}>Validate</button>
				</div>
			</div>
		)
	}
}


class NPuzzle extends Component{
	constructor(props) {
		super(props)
		this.state = {
			size: 3,
			stepNumber: 0,
			baseNPuzzle: []
		}
		this.sendInputPuzzle = this.sendInputPuzzle.bind(this)
		this.sendGenParams = this.sendGenParams.bind(this)
		this.resetStep = this.resetStep.bind(this)
	}


	resetStep() {
		this.setState({stepNumber: 0})
	}


	sendInputPuzzle(inputPuzzle){
		axios.get('/check_solvability', {
			params: {
				inputPuzzle: inputPuzzle
			}
		})
		.then((response) => {
			if (response.data.error == true) {
				alert("Error: " + response.data.data)
			} else {
				this.setState({
					stepNumber: 1,
					baseNPuzzle: response.data.npuzzle,
					size: response.data.size
				})
			}
		})
	}


	sendGenParams(size, isSolvable, iterations){
		axios.get('/make_random', {
			params: {
				size: size,
				isSolvable: isSolvable,
				iterations: iterations
			}
		})
		.then((response) => {
			if (response.data.error == true) {
				alert("Error: " + response.data.data)
			} else {
				this.setState({
					stepNumber: 1,
					baseNPuzzle: response.data.npuzzle,
					size: response.data.size
				})
			}
		})
	}


	render(){
		return(
			<div className="main-container">
				<h1>NPuzzle Web</h1>
				{this.state.stepNumber == 0 &&
					<InputForm
						sendInputPuzzle={this.sendInputPuzzle}
						sendGenParams={this.sendGenParams}
					/>
				}
				{this.state.stepNumber > 0 &&
					<Visu
						resetStep={this.resetStep}
						baseNPuzzle={this.state.baseNPuzzle}
						size={this.state.size}
					/>
				}
			</div>
		)
	}
}

export default NPuzzle;