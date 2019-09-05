import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { isMobileOnly } from 'react-device-detect';
import Slider from '@material-ui/core/Slider';


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

  componentDidMount() {
    const { baseNPuzzle } = this.props;

    this.setState({ inputPuzzle: baseNPuzzle });
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
    const { sendInputPuzzle, sendGenParams, baseNPuzzle } = this.props;
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
          defaultValue={baseNPuzzle}
        />
        <button
          type="button"
          className="input-validation"
          onClick={() => sendInputPuzzle(inputPuzzle)}
        >
          Validate
        </button>
        <div className="form-separator">OR</div>
        <div className="form-caption section-title">Generate a random puzzle</div>
        <div className="form-generator-container">
          <div className="input-container">
            <div className="form-caption">{`Size between 3 and ${(isMobileOnly ? 5 : 8)}`}</div>
            <Slider
              defaultValue={3}
              step={1}
              min={3}
              max={(isMobileOnly ? 5 : 8)}
              onChange={(e, value) => this.setState({ size: value })}
              valueLabelDisplay="on"
              style={(isMobileOnly ? { width: '80%' } : {})}
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
  baseNPuzzle: PropTypes.string.isRequired,
  sendInputPuzzle: PropTypes.func.isRequired,
  sendGenParams: PropTypes.func.isRequired,
};

export default InputForm;
