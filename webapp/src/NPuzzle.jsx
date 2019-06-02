import React, { Component} from "react"
import "./NPuzzle.css"


class NPuzzle extends Component{
	constructor(props) {
		super(props)
		this.state = {
			basePuzzle: [],
			size: 3,
			stepNumber: 0,
			iterations: 3000
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
			<div className="main-container">
				<h1>NPuzzle Web</h1>
				{this.state.stepNumber == 0 &&
					<div className="input-form-container">
						<div className="form-caption section-title">Input list of numbers separated by space</div>
						<input
							type="text"
							name="puzzle"
							className="puzzle-input"
						>
						</input>
						<div className="form-separator">Or</div>
						<div className="form-caption section-title">Generate a random puzzle</div>
						<div className="form-generator-container">
							<div className="form-input-container">
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
							<div className="form-input-container">
								<div className="form-caption">Solvable?</div>
								<select className="solvable-input">
									<option value={true}>Yes</option>
									<option value={false}>No</option>
								</select>
							</div>
							<div className="form-input-container">
								<div className="form-caption">Number of iteration between 0 and 10000</div>
								<input
									className="iterations-input"
									type="number"
									min="0"
									max="10000"
									onChange={(e) => this.handleIterationsInput(e.target.value)}
									value={this.state.iterations}
								>
								</input>
							</div>
						</div>
					</div>
				}
				{this.state.stepNumber == 1 &&
					<div className="puzzle-container">
						{this.state.basePuzzle.map((e, index) => {
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
				}
			</div>
		)
	}
}

export default NPuzzle;