import json
import os
import glob
from flask import Flask, render_template, request
import webbrowser
import argparse
from layout.extractor import worker

app = Flask(__name__)
output = []  # final output
outputForTree = []
hierachies = []  # storing temporary hierachies of pages
parent = []  # storing temporary parent record of each page
# configuring arguments for the script to take as input
ap = argparse.ArgumentParser()
ap.add_argument('-u', '--url', required=True,
                help='website url to analyse layout')
ap.add_argument('-l', '--level', required=True,
                help='what should be depth level to check')
ap.add_argument('-m', '--max', required=False,
                help='maximum number of pages to scrap')
args = ap.parse_args()
directory_path = worker(args.url, int(args.max))
# configuring folder path for loading all json
path = f'{directory_path}*.json'
# fetching the file names of all json present in the folder
files = glob.glob(path)


# recursive function to extract tags from each json, do not alter as it uses global variable
def extractGivenLevelTags(obj, level):
    global parent
    if level == 1:
        for items in obj['child']:
            parent.append(obj['tag'])
            hierachies.append({"parent": parent.copy(), "child": items['tag']})
            parent.pop()
        return
    if len(obj['child']):
        parent.append(obj['tag'])
    else:
        return
    for items in obj['child']:
        extractGivenLevelTags(items, level-1)
    if len(parent):
        parent.pop()


# compares two layout and generate the final output
def compareLayout(file1, file2, data1, data2):
    final_data1 = []  # used to store unique tags on given level with different parents
    final_data2 = []
    for value in data1:  # logic to remove duplicate tags with similar parents
        if value not in final_data1:
            final_data1.append(value)
    for value in data2:
        if value not in final_data2:
            final_data2.append(value)
    # extract similar tags between two page and dissimilar tags for each page
    similarTags = [d for d in final_data1 if d in final_data2]
    dissimilarTagsForData1 = [d for d in final_data1 if d not in similarTags]
    dissimilarTagsForData2 = [d for d in final_data2 if d not in similarTags]
    # computing similarity of percentage between two page
    try:
        percentageSimilarity = (len(
            similarTags) / (len(dissimilarTagsForData1) + len(dissimilarTagsForData2))) * 100
    except:
        percentageSimilarity = 100
    # appending every object to final output
    output.append({
        "pages": file1 + " <-> " + file2,
        "similarHierarchies": similarTags,
        "dissimilarTags": [
            {
                "name": file1,
                "tags": dissimilarTagsForData1
            },
            {
                "name": file2,
                "tags": dissimilarTagsForData2
            }
        ],
        "percentageSimilarity": percentageSimilarity
    })


# extracting each page and comparing it with all other pages.
def startWorker(level):
    for i in range(len(files)):
        hierachies.clear()
        with open(files[i], "r", encoding="utf8") as read_file:
            extractGivenLevelTags(json.load(read_file), level-1)
        first_data = hierachies[:]
        hierachies.clear()
        for j in range(i+1, len(files)):
            with open(files[j], "r", encoding="utf8") as read_file:
                extractGivenLevelTags(json.load(read_file), level-1)
            second_data = hierachies[:]
            hierachies.clear()
            compareLayout(os.path.splitext(os.path.basename(files[i]))[0], os.path.splitext(
                os.path.basename(files[j]))[0], first_data, second_data)
    return output


x = startWorker(int(args.level))


@app.route('/')
def dashboard():
    return render_template('dashboard.html', url=args.url, level=args.level, maxpages=args.max,  filterValue=0, data=x)


@app.route('/', methods=['POST'])
def filter():
    return render_template('dashboard.html', url=args.url, level=args.level, maxpages=args.max,  filterValue=int(request.form['filter']), data=x)


@app.route('/tree/<pageName>')
def showTree(pageName):
    page1TreeTemp = []
    page2TreeTemp = []
    page1Dict = []
    page2Dict = []
    page1 = pageName.split(' ', 1)[0]
    page2 = pageName.split(' ', 2)[2]

    def dictToList(obj):  # converts list of dicts to a single list
        res = []
        for z in obj:
            for k, v in z.items():
                if(isinstance(v, list)):
                    for i in v:
                        res.append(i)
                else:
                    res.append(v)
        return res
    for file in files:
        if os.path.splitext(os.path.basename(file))[0] == page1:
            with open(file, "r", encoding="utf8") as read_file:
                hierachies.clear()
                extractGivenLevelTags(json.load(read_file), int(args.level)-1)
                page1TreeTemp = hierachies[:]
        if os.path.splitext(os.path.basename(file))[0] == page2:
            with open(file, "r", encoding="utf8") as read_file:
                hierachies.clear()
                extractGivenLevelTags(json.load(read_file), int(args.level)-1)
                page2TreeTemp = hierachies[:]
        for value in page1TreeTemp:  # logic to remove duplicate tags with similar parents
            if value not in page1Dict:
                page1Dict.append(value)
        for value in page2TreeTemp:
            if value not in page2Dict:
                page2Dict.append(value)
    page1List = dictToList(page1Dict)
    page2List = dictToList(page2Dict)
    listData = [page1List, page2List]
    return render_template('testtree.html', url=args.url, level=args.level, maxpages=args.max, pageName=pageName.replace('@', '/'), data=json.dumps(listData))


if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:5000/')
    app.run()
