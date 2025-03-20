from flask import Flask, render_template, request
from controllers.content_controller import ContentController

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/submit", methods=["POST"])
def submit_content():
    return ContentController.submit_content()

if __name__ == "__main__":
    app.run(debug=True)
