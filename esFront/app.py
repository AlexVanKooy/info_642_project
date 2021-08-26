from flask import Flask,render_template, request, redirect
import es_comms
import json

app = Flask(__name__)
def processResults(query):
    response = es_comms.ESsearch(query)
    response = str(response)[2:-1]
    response = str(response.encode(encoding='UTF-8',errors='replace'))[2:-1]
    response = response.replace("""\\\\\\""","")
    response = json.loads(response)
    titles = []
    links = []
    descriptions = []
    timeTaken = response['took']
    totHits = response['hits']['total']['value']
    for i in response['hits']['hits']:
        titles.append(i['_source']['title'])
        try:
            links.append(i['_source']['source']['link'])
        except:
            links.append("this game has no link :)")
        try:
            descriptions.append(i['_source']['description'])
        except:
            descriptions.append("this game has no description :)")
    try:
        if links[0] == "this game has no link :)":
            toplink = "#"
    except:
        return -1,-1,-1,-1
    else:
        toplink  = links[0]
    html = buildPage(titles,links,descriptions)
    return timeTaken,totHits, html, toplink

def buildPage(titles,links,descriptions):
    resultsHTML = []
    for i in range(len(titles)):
        searchHead = """<div class="searchresult">"""
        if links[i] == "this game has no link :)":
            title = f"""<a href="#"><h2>{titles[i]}</h2></a>"""
            link = f"""<a href="#">{links[i]}</a> <button>▼</button>"""
        else:
            title = f"""<a href="{links[i]}"><h2>{titles[i]}</h2></a>"""
            link = f"""<a href="{links[i]}">{links[i]}</a> <button>▼</button>"""
        description = f"""<p>{descriptions[i]}</p>"""
        searchTail = """</div>"""
        resultsHTML.append(searchHead)
        resultsHTML.append(title)
        resultsHTML.append(link)
        resultsHTML.append(description)
        resultsHTML.append(searchTail)
    resultsHTML = '\n'.join(resultsHTML)
    return resultsHTML

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def getQuery():
    if request.method == "POST":
        if request.form['searchBtn'] == 'Gaamle Search':
            text = request.form['text']
            if text != "":
                timeTaken,totHits, html,toplink = processResults(text)
                while totHits == 7660:
                    print("err: retrieved match_all")
                    timeTaken,totHits, html,toplink = processResults(text)
        elif request.form['searchBtn'] == "I'm Feeling Lucky":
            text = request.form['text']
            if text != "":
                timeTaken,totHits, html,toplink = processResults(text)
                while totHits == 7660:
                    print("err: retrieved match_all")
                    timeTaken,totHits, html,toplink = processResults(text)
            if timeTaken == -1:
                return redirect('#')
            else:
                return redirect(toplink)
    if text == "" or timeTaken == -1:
        return render_template('index.html',text=text)
    else:
        return render_template('search.html',text=text,hits=str(totHits),respTime=str(timeTaken),htmlResults=html)



