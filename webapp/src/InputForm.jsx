import React, { Component } from 'react';
import PropTypes from 'prop-types';
import isMobileOnly from 'react-device-detect';

class InputForm extends Component {
  constructor(props) {
    super(props);
    this.props = props;
    this.state = {
      inputPuzzle: '',
      size: 3,
      isSolvable: true,
      iterations: 3000,
    };
  }

  handleSizeInput(value) {
    let size = value;
    const maxSize = (isMobileOnly ? 5 : 8);

    if (value > maxSize) {
      size = maxSize;
    } else if (value < 3) {
      size = 3;
    }
    this.setState({ size });
  }

  handleIterationsInput(value) {
    let iterations = value;

    if (value > 10000) {
      iterations = 10000;
    } else if (value < 0) {
      iterations = 0;
    }
    this.setState({ iterations });
  }

  render() {
    const { sendInputPuzzle, sendGenParams } = this.props;
    const {
      inputPuzzle, size, isSolvable, iterations,
    } = this.state;
    return (
      <div className="input-form-container">
        <div className="form-caption section-title">Input a list of numbers separated by spaces</div>
        <input
          type="text"
          name="puzzle"
          className="puzzle-input"
          onChange={e => this.setState({ inputPuzzle: e.target.value })}
        />
        <button type="button" className="input-validation" onClick={() => sendInputPuzzle(inputPuzzle)}>Validate</button>
        <div className="form-separator">OR</div>
        <div className="form-caption section-title">Generate a random puzzle</div>
        <div className="form-generator-container">
          <div className="input-container">
            <div className="form-caption">{`Size between 3 and ${(isMobileOnly ? 5 : 8)}`}</div>
            <input
              className="size-input"
              type="number"
              min="3"
              max="8"
              onChange={e => this.handleSizeInput(e.target.value)}
              value={size}
            />
          </div>
          <div className="input-container">
            <div className="form-caption">
              Solvable?
            </div>
            <select
              className="solvable-input"
              onChange={e => this.setState({ isSolvable: e.target.value })}
              value={isSolvable}
            >
              <option value>Yes</option>
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
              onChange={e => this.handleIterationsInput(e.target.value)}
              value={iterations}
            />
          </div>
        </div>
        <button type="button" className="input-validation" onClick={() => sendGenParams(size, isSolvable, iterations)}>Validate</button>
      </div>
    );
  }
}

InputForm.propTypes = {
  sendInputPuzzle: PropTypes.func.isRequired,
  sendGenParams: PropTypes.func.isRequired,
};

export default InputForm;
