#This program will take the necessary data from MTGJSON decks and create multiple 
#.json file that can be used later

import json, os

#path to json decks used
deckPath = 'template decks'
#this gives a list of all files in the folder ending with .json
fileNames = [x for x in os.listdir(deckPath) if x.endswith(".json")]

#create first files dictionary
files1 = {}
#we want to get the names of the cards and what set they belong to for using Forge later
files1['cardNames'] = []
files1['cardSet'] = []
files1['cardCount'] = []
files1['colours'] = []
files1['types'] = []

#loop through all files in 'template decks' folder
for x in range(0, len(fileNames)):
    #open file [x]
    file1 = open(deckPath + '\\' + fileNames[x], encoding='utf-8')
    print(fileNames[x]) #comment out this line if you want, it just prints the fileNames to terminal
    #load data into variable list - list becomes a dictionary data type
    data = json.loads(file1.read())
    #create a,b,c lists
    a = []
    b = []
    c = []
    d = []
    e = []
    for i in range(0, len(data['data']['mainBoard'])):
        #find data in 'data' dictionary
        a.append(data['data']['mainBoard'][i]['name'])
        b.append(data['data']['mainBoard'][i]['printings'][0])  
        c.append(data['data']['mainBoard'][i]['count'])
        d.append(data['data']['mainBoard'][i]['colors'])
        e.append(data['data']['mainBoard'][i]['types'])
    #append this data to files1 dict
    files1['cardNames'].append([a, x])
    files1['cardSet'].append(b)
    files1['cardCount'].append(c)
    files1['colours'].append(d)
    files1['types'].append(e)
    #close file
    file1.close()
        
#create json file and write data
with open('MTGjson.json', 'w+') as output:
    json.dump(files1, output)

#create second files dictionary
files2 = {}
#we want to get these attributes from AtomicCards to use for mutation in the main program
files2['cardNames'] = []
files2['cardSet'] = []
files2['colours'] = []
files2['types'] = []
#open file
with open('AtomicCards.json', 'r', encoding='utf-8') as AtomicCards:
    data = json.load(AtomicCards)
    #loop through data and append values to files2 dict
    for x in data['data'].values():
        files2['cardNames'].append(x[0]['name'])
        files2['cardSet'].append(x[0]['printings'][0])
        files2['colours'].append(x[0]['colors'])
        files2['types'].append(x[0]['type'])
        
#create json file and write data
with open('MTGjson2.json', 'w+') as output:
    json.dump(files2, output)