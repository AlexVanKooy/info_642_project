from flask import Flask,render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def getQuery():
    if request.method == "POST":
        if request.form['searchBtn'] == 'Gaamle Search':
            text = request.form['text']
            print("gamle search - ",text)
        elif request.form['searchBtn'] == "I'm Feeling Lucky":
            text = request.form['text']
            print("feelin lucky - ", text)
    return render_template('index.html',text=text)