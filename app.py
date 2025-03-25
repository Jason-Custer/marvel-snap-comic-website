from flask import Flask, render_template

app = Flask(__name__, static_folder='.', static_url_path='')

card_data = [
    {
        "name": "Iron Man",
        "energy": 5,
        "power": 0,
        "image": "images/iron-man.png"
    },
    {
        "name": "Hulk",
        "energy": 6,
        "power": 12,
        "image": "images/hulk.png"
    }
]

@app.route("/")
def index():
    return render_template("index.html", cards=card_data)

if __name__ == "__main__":
    app.run(debug=True, port=5001)