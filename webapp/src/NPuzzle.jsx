import React, { Component } from 'react';
import axios from 'axios';
import './NPuzzle.css';
import InputForm from './InputForm';
import Visu from './Visu';


class NPuzzle extends Component {
  constructor(props) {
    super(props);
    this.state = {
      size: 3,
      stepNumber: 0,
      baseNPuzzle: [],
    };
    this.sendInputPuzzle = this.sendInputPuzzle.bind(this);
    this.sendGenParams = this.sendGenParams.bind(this);
    this.resetStep = this.resetStep.bind(this);
  }

  resetStep() {
    this.setState({ stepNumber: 0 });
  }

  sendInputPuzzle(inputPuzzle) {
    axios.get('/check_solvability', {
      params: {
        inputPuzzle,
      },
    })
      .then((response) => {
        if (response.data.error === true) {
          alert(`Error: ${response.data.data}`);
        } else {
          this.setState({
            stepNumber: 1,
            baseNPuzzle: response.data.npuzzle,
            size: response.data.size,
          });
        }
      });
  }

  sendGenParams(size, isSolvable, iterations) {
    axios.get('/make_random', {
      params: {
        size,
        isSolvable,
        iterations,
      },
    })
      .then((response) => {
        if (response.data.error === true) {
          alert(`Error: ${response.data.data}`);
        } else {
          this.setState({
            stepNumber: 1,
            baseNPuzzle: response.data.npuzzle,
            size: response.data.size,
          });
        }
      });
  }

  render() {
    const { stepNumber, baseNPuzzle, size } = this.state;
    return (
      <div className="main-container">
        <h1>NPuzzle</h1>
        {stepNumber === 0
        && (
        <InputForm
          sendInputPuzzle={this.sendInputPuzzle}
          sendGenParams={this.sendGenParams}
        />
        )
        }
        {stepNumber > 0
          && (
          <Visu
            resetStep={this.resetStep}
            baseNPuzzle={baseNPuzzle}
            size={size}
          />
          )
        }
      </div>
    );
  }
}

export default NPuzzle;
