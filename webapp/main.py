from flask import Flask, render_template


app = Flask(__name__)

@app.route('/')
def npuzzle_web():
    return render_template('index.html', size=4)

if __name__ == "__main__":
    app.run(debug=True)
