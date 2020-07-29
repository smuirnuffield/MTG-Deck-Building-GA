#Convert MTGjson decklist to other format

import json, os

#path to json decks used
pathToJson = r'C:\Users\Muir7\Desktop\Nuffield Research Placement\deck building plan\template decks'
#this gives a list of all files in the folder ending with .json
fileNames = [x for x in os.listdir(pathToJson) if x.endswith(".json")]

#create files dictionary
files = {}
#we want to get the names of the cards and what set they belong to for using Forge later
files['cardNames'] = []
files['cardSet'] = []

for x in range(0, len(fileNames)):
    file = open('template decks\\' + fileNames[x], encoding='utf-8')
    print(fileNames[x])
    data = json.loads(file.read())
    a = []
    b = []
    for i in range(0, len(data['data']['mainBoard'])):
        a.append(data['data']['mainBoard'][i]['name'])
        b.append(data['data']['mainBoard'][i]['printings'][0])   
    files['cardNames'].append(a)
    files['cardSet'].append(b)
    file.close()
        
with open('MTGjson.json', 'w') as output:
    json.dump(files, output)