from flask import Flask, render_template, request, jsonify
from npuzzle import api
import os

app = Flask(
        __name__,
        root_path='webapp',
        template_folder='templates',
        static_folder=os.path.abspath('webapp/static')
        )


@app.route('/')
def npuzzle_web():
    return render_template('index.html')


@app.route('/check_solvability')
def check_solvability():
    inputPuzzle = request.args.get('inputPuzzle')
    dataJson = api.check_solvability(
            'snale',
            list(map(int, inputPuzzle.split()))
            )
    return jsonify(dataJson)


@app.route('/make_random')
def make_random():
    size = request.args.get('size')
    isSolvable = request.args.get('isSolvable')
    isSolvable = True if isSolvable == "true" else False
    iterations = request.args.get('iterations')
    dataJson = api.make_random('snale', int(size), isSolvable, int(iterations))
    return jsonify(dataJson)


@app.route('/solve')
def solve():
    baseNPuzzle = request.args.get('baseNPuzzle')
    greedy = request.args.get('greedy')
    greedy = True if greedy == "true" else False
    heuristic = request.args.get('heuristic')
    dataJson = api.solve(
            'snale',
            list(map(int, baseNPuzzle.split())), greedy, heuristic
            )
    api.wait_solving()
    return jsonify(dataJson)


@app.route('/stop-solving')
def stop_solving():
    if api.stop_solving():
        return 'Success'
    else:
        return 'Failure'


@app.route('/get-heuristics')
def get_heuristics():
    dataJson = api.get_available_heuristics()
    return jsonify(dataJson)


if __name__ == "__main__":
    app.run(debug=True)
