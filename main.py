from flask import Flask, render_template, request,redirect, url_for
from bs4 import BeautifulSoup
import requests   #request library will be used to fetch a specific web page
import sys
import re
from collections import Counter
import math
import string
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')
from nltk.tokenize import word_tokenize




app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    global globalResult
    errors = []
    results = {}
    if request.method == "POST":
# ******************************************** Requirement # 1 Part A ********************************************
        if (request.values.get("frequencyCalculate") == 'frequencyCalculate'):
            errors.append(request.values.get("frequencyCalculate"))    
            try:
                url = request.form['url']
                globalResult =  getListofWebContent(url)
                return redirect(url_for('displayOutPut'))
            except:
                errors.append(
                    "Unable to get URL. Are you sure it's a valid URL"
                )    
# ******************************************** Requirement # 1 Part B ********************************************                
        elif(request.values.get("keywordCalculate") == 'keywordCalculate'):
            url = request.form['url']
            results = getListofWebContent(url)
            newResults = getCleanTextFromList(results)
            newResults = removeStopingWordsFromList(newResults)
            counter = Counter(newResults)
            most_occur = counter.most_common(10)
            rk = []
            c = 1
            for i in most_occur:
                s = str(c) + ". '"+i[0]+"'" + " is repeated " + str(i[1]) + " times."
                c += 1
                rk.append(s)
            return render_template('keywords.html', result = rk)
# ******************************************** Requirement # 2  **************************************************      
        elif(request.values.get("similarityCalculator") == 'similarityCalculator'):
            url1 = request.form['urlR1']
            url2 = request.form['urlR2']
            return render_template('similarity.html',result = documentSimilarity(url1,url2))        
# ******************************************** Requirement # 3  **************************************************      
        elif(request.values.get("getcontent") == 'getcontent'):
            url = request.form['urlR1']
            result = getListofWebContent(url)
            l = getClusterFromURL(url)
            result1 = getListofWebContent(l[0])
            result2 = getListofWebContent(l[1])
            result2 = getCleanTextFromList(result2)
            result = getCleanTextFromList(result)
            result1 = getCleanTextFromList(result1)
            similarity = documentSimilarity(l[0],l[1])
            return render_template('pagecontent.html', result = result, result1 = result1, result2 = result2, sim = similarity )


# ******************************************** Return the main menue page *************************************            
    return render_template('wordCounter.html', errors = errors)        


@app.route('/displayOutPut')
def displayOutPut(): 
            errors=[]
            newResults = getCleanTextFromList(globalResult)
            orderOfFrequency =[]
            # set unique_words will be initialized i.e set only has unique words 
            unique_words = set(newResults)
            unique_words = removeStopingWordsFromList(unique_words)
            for words in unique_words :
             strin = "Frequency of      "+ words , '     is :     '+ str(newResults.count(words))   
             orderOfFrequency.append(strin)       
            return render_template('frequencyOccurence.html',orderOfFrequency=orderOfFrequency, errors = errors)

def getListofWebContent(f):       
    url = f
    r = requests.get(url)
    soup = BeautifulSoup(r.content , "html.parser")
    results = soup.text
    results = results.split(" ")
    return results

def dotProduct(V1,V2):
	res = 0.0
	for i in V1:
		if i in V2:
			res += (V1[i] * V2[i])
	return res

def documentSimilarity(url1,url2):
    w1 = getListofWebContent(url1)
    w1 = removeStopingWordsFromList(w1)
    w2 = getListofWebContent(url2)
    w2 = removeStopingWordsFromList(w2)
    V1 = Counter(w1)
    V2 = Counter(w2)
    distance = math.acos(dotProduct(V1, V2) / math.sqrt(dotProduct(V1, V1)*dotProduct(V2, V2)))
    return "The distance between the documents is: % 0.6f (radians)"% distance

def getCleanTextFromList(ls):
    newResults = []
    for k in ls:
        r = re.sub('[\W_]+', '', k) 
        if r != '':  
            newResults.append(r)
    return newResults        

def removeStopingWordsFromList(ls):
    stop_words = set(stopwords.words('english')) 
    return [word for word in ls if not word in stopwords.words()]

def getClusterFromURL(url):
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    l = []
    for link in soup.find_all('a'):
        l.append(link.get('href'))
    k = []
    z = 0
    for j in l:
        if z == 3:
            break
        if "https://" in j:
            k.append(j)
            z += 1
    return k

if __name__ == '__main__':
     app.debug = True
     app.run()