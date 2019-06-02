import React, { Component} from "react"
import axios from "axios"
import "./NPuzzle.css"


class Visu extends Component{
	constructor(props) {
		super(props)
		this.state = {
			currNPuzzle: this.props.baseNPuzzle,
			size: this.props.size
		}
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
				<button className="solve-button" onClick={() => this.props.solvePuzzle(this.state.currNPuzzle)}>Solve</button>
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
						<select className="solvable-input" onChange={(e) => this.setState({isSolvable: e.target.value})}>
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
		this.solvePuzzle = this.solvePuzzle.bind(this)
	}


	solvePuzzle(baseNPuzzle){
		axios.get('/solve', {
			params: {
				baseNPuzzle: baseNPuzzle.join(' ')
			}
		})
		.then((response) => {
			console.log(response)
			if (response.data.error == true) {
				alert("Error: " + response.data.data)
			} else {
			}
		})
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
				{this.state.stepNumber == 1 &&
					<Visu
						baseNPuzzle={this.state.baseNPuzzle}
						size={this.state.size}
						solvePuzzle={this.solvePuzzle}
					/>
				}
			</div>
		)
	}
}

export default NPuzzle;