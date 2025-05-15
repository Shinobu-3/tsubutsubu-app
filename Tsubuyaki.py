from flask import Flask, render_template, request
from datetime import date
import csv

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        today = date.today().isoformat()
        data = {
            'date': today,
            'task': request.form['task'],
            'mistake': request.form['mistake'],
            'tsubutsubu': request.form['tsubutsubu'],
            'tomorrow': request.form['tomorrow']
        }

        with open('C:/Final assignment_iwamoto/records.csv', 'a', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(data)

        return "送信が完了しました！"

    return render_template("Tsubutsubu.html")

if __name__ == "__main__":
    app.run(debug=True)
