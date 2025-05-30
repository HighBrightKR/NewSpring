from flask import Flask, render_template
import firebase_admin
from firebase_admin import credentials, firestore
app = Flask(__name__)

cred = credentials.Certificate("key.json")  # 파일 경로
firebase_admin.initialize_app(cred)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/year')
def year():
    return render_template('year.html')

@app.route('/genre')
def genre():
    return render_template('genre.html')

@app.route('/press')
def press():
    return render_template('press.html')

@app.route('/release')
def release():
    return render_template('release.html')

if __name__ == '__main__':
    app.run(debug=True)
