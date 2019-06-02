from flask import Flask, render_template
from npuzzle import api
import os


app = Flask(__name__, root_path='webapp', template_folder='public', static_folder=os.path.abspath('webapp/static'))


@app.route('/')
def npuzzle_web():
    return render_template('index.html')


@app.route('/check_solvability')
def check_solvability():
    print(request.args['inputPuzzle'])
    # return api.check_solvability()
    return 200

if __name__ == "__main__":
    app.run(debug=True)
