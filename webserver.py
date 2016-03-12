# -*- coding: utf-8 -*-

from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def hello():
    return

if __name__ == "__main__":
    app.run()