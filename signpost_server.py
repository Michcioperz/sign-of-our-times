#!/usr/bin/env python3
from signpost_solver import *
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('form.html', solver=dict(names=["" for _ in range(10)], directions=["" for _ in range(10)]), smallest_size=4, biggest_size=7)

@app.route('/analyze')
def analyze():
    size = request.args.get('size')
    if size is None:
        raise ValueError("unknown size")
    print(size)
    size = int(size)
    directions = [[request.args.get("direction_{}_{}".format(i, j), "") for j in range(size)] for i in range(size)]
    names = [[request.args.get("name_{}_{}".format(i, j), 0) for j in range(size)] for i in range(size)]
    solver = Signpost(directions=directions, names=names)
    solver.reduce()
    return render_template("analysis.html", svg=svg_of_digraph(solver.to_digraph()), solver=solver)

if __name__ == '__main__':
    app.run(debug=True)
