import React, { Component } from 'react';
import axios from 'axios';
import CircularProgress from '@material-ui/core/CircularProgress';
import PropTypes from 'prop-types';
import uniqid from 'uniqid';


class Visu extends Component {
  constructor(props) {
    super(props);
    this.props = props;
    this.state = {
      currNPuzzle: [...props.baseNPuzzle],
      size: props.size,
      heuristic: 'manhattan',
      greedy: false,
      goal: [],
      stats: {},
      isSolving: false,
      isSolvable: true,
      isMoving: false,
      currMove: 0,
      totalMoves: 0,
      heuristicsList: [],
    };
    this.solvePuzzle = this.solvePuzzle.bind(this);
    this.stopSolving = this.stopSolving.bind(this);
    this.resetPuzzle = this.resetPuzzle.bind(this);
    this.getHeuristics = this.getHeuristics.bind(this);
    this.solution = [];
    this.getHeuristics();
  }

  getHeuristics() {
    axios.get('/get-heuristics', {
      params: {},
    })
      .then((response) => {
        this.setState({ heuristicsList: response.data });
      });
  }

  resetPuzzle() {
    const { baseNPuzzle, size } = this.props;
    this.setState({
      currNPuzzle: [...baseNPuzzle],
      size,
      goal: [],
      stats: {},
      isSolving: false,
      isSolvable: true,
      isMoving: false,
      currMove: 0,
      totalMoves: 0,
    });
  }

  stopSolving() {
    axios.get('/stop-solving', {
      params: {},
    })
      .then((response) => {
        console.log(response);
        if (response.data === 'Success') {
          this.setState({ isSolving: false });
        }
      });
  }

  makeMove(move) {
    let movingSpeed = 100;
    if (this.solution.length > 50) {
      movingSpeed = 40;
    }
    const {
      currNPuzzle, goal, size, totalMoves,
    } = this.state;
    const nextMove = currNPuzzle;
    const zeroPos = nextMove.indexOf(0);
    if (this.solution.length === 0) {
      this.setState({
        currNPuzzle: goal,
        isMoving: false,
        currMove: totalMoves,
      });
      return;
    }

    if (move === 0) {
      [nextMove[zeroPos], nextMove[zeroPos - size]] = [nextMove[zeroPos - size], nextMove[zeroPos]];
    } else if (move === 1) {
      [nextMove[zeroPos], nextMove[zeroPos + size]] = [nextMove[zeroPos + size], nextMove[zeroPos]];
    } else if (move === 2) {
      [nextMove[zeroPos], nextMove[zeroPos + 1]] = [nextMove[zeroPos + 1], nextMove[zeroPos]];
    } else {
      [nextMove[zeroPos], nextMove[zeroPos - 1]] = [nextMove[zeroPos - 1], nextMove[zeroPos]];
    }

    this.setState(prevState => ({
      currNPuzzle: nextMove,
      currMove: prevState.currMove + 1,
    }), () => {
      setTimeout(() => this.makeMove(this.solution.shift()), movingSpeed);
    });
  }

  solvePuzzle() {
    const { greedy, heuristic } = this.state;
    const { baseNPuzzle } = this.props;
    this.setState({ isSolving: true });
    axios.get('/solve', {
      params: {
        baseNPuzzle: baseNPuzzle.join(' '),
        greedy,
        heuristic,
      },
    })
      .then((response) => {
        console.log(response);
        this.setState({ isSolving: false });
        if (response.data.error === true || response.data.solvable === false) {
          this.setState({
            isSolvable: false,
            stats: response.data.stats,
          });
        } else if (response.data.found === true) {
          this.solution = response.data.solution;
          this.setState({
            stats: response.data.stats,
            goal: response.data.goal,
            isMoving: true,
            totalMoves: this.solution.length,
          }, this.makeMove(this.solution.shift()));
        }
      });
  }

  render() {
    const {
      currNPuzzle,
      size,
      isSolving,
      isSolvable,
      goal,
      isMoving,
      greedy,
      heuristic,
      currMove,
      totalMoves,
      stats,
      heuristicsList,
    } = this.state;
    const { resetStep } = this.props;
    const {
      memory, time, nodes_created: nodesCreated, nodes_stocked: nodesStocked, turns,
    } = stats;
    return (
      <React.Fragment>
        <div className="puzzle-container">
          {currNPuzzle.map(e => (
            <div
              key={uniqid()}
              className="puzzle-case"
              style={{
                width: `${(100 / size)}%`,
                height: `${(100 / size)}%`,
              }}
            >
              <div className="case-number">{e !== 0 ? e : ''}</div>
            </div>
          ))}
        </div>
        {!isSolving && isSolvable && currNPuzzle !== goal && !isMoving
          && (
          <React.Fragment>
            <div className="input-wrapper">
              <div className="input-container">
                <div className="form-caption">Greedy?</div>
                <select
                  className="solvable-input"
                  onChange={e => this.setState({ greedy: e.target.value })}
                  value={greedy}
                >
                  <option value>Yes</option>
                  <option value={false}>No</option>
                </select>
              </div>
              <div className="input-container">
                <div className="form-caption">Choose a heuristic</div>
                <select
                  className="solvable-input heuristic-input"
                  onChange={e => this.setState({ heuristic: e.target.value })}
                  value={heuristic}
                >
                  {heuristicsList.map(e => <option key={uniqid()} value={e.toLowerCase().replace(' ', '_')}>{e}</option>)}
                </select>
              </div>
            </div>
          </React.Fragment>
          )
        }
        {!isSolvable
          && <div className="unsolvable-text">This NPuzzle is unsolvable !</div>
        }
        {(isMoving || currNPuzzle === goal || !isSolvable)
          && (
          <React.Fragment>
            {isSolvable
              && (
              <div className="moves-text">
                {`Current move: ${currMove} / ${totalMoves}`}
              </div>
              )
            }
            <div className="stats-container">
              <div className="stats-text">
                {'Memory used: '}
                <div className="stat-value">{`${memory} Mo`}</div>
              </div>
              <div className="stats-text">
                Time in seconds:
                {' '}
                <div className="stat-value">{time / 1000000}</div>
              </div>
              <div className="stats-text">
                Nodes created:
                {' '}
                <div className="stat-value">{nodesCreated}</div>
              </div>
              <div className="stats-text">
                Memory complexity:
                {' '}
                <div className="stat-value">{nodesStocked}</div>
              </div>
              <div className="stats-text">
                Time complexity:
                {' '}
                <div className="stat-value">{turns}</div>
              </div>
            </div>
          </React.Fragment>
          )
        }
        <div className="buttons-container">
          {!isSolving && isSolvable && currNPuzzle !== goal && !isMoving
          && (
          <button
            type="button"
            className="generic-button"
            onClick={this.solvePuzzle}
          >
            Solve
          </button>
          )
          }
          {isSolving
            && (
            <div className="loading-container">
              <CircularProgress />
              <div className="loading-text">Looking for solution...</div>
              <button
                type="button"
                className="generic-button"
                onClick={this.stopSolving}
              >
                Stop Solving
              </button>
            </div>
            )
          }
          {!isMoving && (currNPuzzle === goal || !isSolvable)
            && (
              <button
                type="button"
                className="generic-button"
                onClick={this.resetPuzzle}
              >
                Retry
              </button>
            )
          }
          {!isSolving && !isMoving
            && (
              <button
                type="button"
                className="generic-button"
                onClick={resetStep}
              >
                Reset
              </button>
            )
          }
        </div>
      </React.Fragment>
    );
  }
}

Visu.propTypes = {
  baseNPuzzle: PropTypes.arrayOf(PropTypes.number).isRequired,
  size: PropTypes.number.isRequired,
  resetStep: PropTypes.func.isRequired,
};

export default Visu;
