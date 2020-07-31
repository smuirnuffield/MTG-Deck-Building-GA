#MTG Deck Building GA

import json, subprocess, random, os, glob

#the bat file is configured to run 16 person tournaments
popNo = 16
#path to forge appdata folder
forgePath = r'C:\Users\Muir7\AppData\Roaming\Forge'

#create deck class 
class Deck:
    def __init__(self, path, setName, noCard):
        self.path = path
        self.setName = setName
        self.noCard = noCard
        self.fitness = 0
    def __repr__(self):
        a = ""
        for x in range(len(self.path)):
            a = a + self.path[x] + ", "
        return a
    
#get pop from MTGjson file that we got through running convertMTGjson
def getPop(popNo):
    population = []
    cardSet = []
    cardNo = []
    file = open('MTGjson.json',)
    data = json.load(file)
    deckPath = random.sample(data['cardNames'], popNo)
    for x in range(0, popNo):
        cardSet.append(data['cardSet'][deckPath[x][1]])
        cardNo.append(data['cardCount'][deckPath[x][1]])
        population.append(Deck(deckPath[x][0], cardSet[x], cardNo[x]))
    file.close()
    return population

#This will open deckA and deckB, and write the deck data into those files so Forge can use them
def setDecks(population):
    for x in range(0, len(population)):
        template = "[metadata]\nName=deck"+str(x)+"\n[Main]\n"
        deck = open(r"C:\Users\Muir7\AppData\Roaming\Forge\decks\constructed\deck"+str(x)+".dck", "w+")
        deck.write(template)
        for i in range(0, len(population[x].path)):
            deck.write(str(population[x].noCard[i]) + " " + population[x].path[i] + "|" + population[x].setName[i] + "\n")
        deck.close()
    r'''
    deckB = open(r"C:\Users\Muir7\AppData\Roaming\Forge\decks\constructed\deck2.dck", "w")
    deckB.write(template2)
    for x in range(0, len(b.path)):
        deckB.write(str(b.noCard[x]) + " " + b.path[x] + "|" + b.setName[x] + "\n")
    deckB.close()
    '''
    
def fitnessFunction(population):
    setDecks(population)
    subprocess.run('runForge.bat')
    fileNames = [x for x in os.listdir(forgePath) if x.endswith(".log")]
    filePaths = [os.path.join(forgePath, x) for x in fileNames]
    File = max(filePaths, key=os.path.getctime)
    logFile = open(File)
    answer = logFile.readlines()[-2]
    logFile.close()
    print(answer)
    
a = getPop(popNo)
fitnessFunction(a)
        
r'''
#Test to see if decks can be written and then used by forge
    fileNames = [x for x in os.listdir(forgePath) if x.endswith(".log")]
    a = getPop(popNo)
    setDecks(a[0], a[1])
    subprocess.run('runForge.bat')
    File = max(key=os.path.getctime)
    logFile = open(File)
    answer = logFile.readlines()[-2]
    logFile.close()
    print(answer)
    
#Test to check if decks can be written
    a = getPop(popNo)
    b = "[metadata]\nName=deck1\n[Main]\n"
    deckA = open(r"C:\Users\Muir7\AppData\Roaming\Forge\decks\constructed\deck1.dck", "w")
    deckA.write(b)
    for x in range(0, len(a[0].path)):
        deckA.write(str(a[0].noCard[x]) + " " + a[0].path[x] + "|" + a[0].setName[x] + "\n")
    deckA.close()

    It works.
    
#Test to check if population can be imported
    a = getPop(popNo)
    print(a[0].path)
    print(a[0].setName)
    print(a[0].noCard)
    
    It works.
'''