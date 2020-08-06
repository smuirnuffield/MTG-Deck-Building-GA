#This program will take the necessary data from MTGJSON decks and create a new 
#.json file that can be used later

import json, os

#path to json decks used
deckPath = 'template decks'
#this gives a list of all files in the folder ending with .json
fileNames = [x for x in os.listdir(deckPath) if x.endswith(".json")]

#create files dictionary
files = {}
#we want to get the names of the cards and what set they belong to for using Forge later
files['cardNames'] = []
files['cardSet'] = []
files['cardCount'] = []
files['colours'] = []
files['types'] = []

#loop through all files in 'template decks' folder
for x in range(0, len(fileNames)):
    #open file [x]
    file = open(deckPath + '\\' + fileNames[x], encoding='utf-8')
    print(fileNames[x]) #comment out this line if you want, it just prints the fileNames to terminal
    #load data into variable list - list becomes a dictionary data type
    data = json.loads(file.read())
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
    #append this data to filenames dict
    files['cardNames'].append([a, x])
    files['cardSet'].append(b)
    files['cardCount'].append(c)
    files['colours'].append(d)
    files['types'].append(e)
    #close file
    file.close()
        
#create json file and write data
with open('MTGjson.json', 'w+') as output:
    json.dump(files, output)