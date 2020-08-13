#MTG Deck Building GA
#https://www.slightlymagic.net/forum/search.php  - search for 'headless' to run
#Forge without GUI
import json, subprocess, random, os, psutil, time, operator

#the bat file is configured to run 16 person tournaments
popNo = 15 #might need to be changed to 15
#path to forge appdata folder
forgePath = r'C:\Users\Muir7\AppData\Roaming\Forge'
#take eliteNo to be 4
eliteNo = 5
mutationRate = 0.001
popLeft = popNo - eliteNo

#create deck class 
class Deck:
    def __init__(self, path, setName, noCard, colour, types):
        self.path = path
        self.setName = setName
        self.noCard = noCard
        self.colour = colour
        self.types = types
        self.fitness = 0
        colours = ['B', 'G', 'R', 'U', 'W', '']
        counted = {'B':0,'G':0,'R':0,'U':0,'W':0,'':0}
        #print(self.colour)
        for x in range(0, len(self.colour)):
            for i in range(0, len(colours)):
                counted[colours[i]] += self.colour[x].count(colours[i])
        #print(counted)
        colourList = sorted(counted.items(), key=operator.itemgetter(1), reverse = True)
        self.mainColour = colourList[0]
    def __repr__(self):
        a = ''
        for x in range(len(self.path)):
            a = a + self.path[x] + ", "
        return a
    
#get pop from MTGjson file that we got through running convertMTGjson
def getPop(popNo):
    population = []
    cardSet = []
    cardNo = []
    colour = []
    types = []
    file = open('MTGjson.json',)
    data = json.load(file)
    deckPath = random.sample(data['cardNames'], popNo)
    for x in range(0, popNo):
        cardSet.append(data['cardSet'][deckPath[x][1]])
        cardNo.append(data['cardCount'][deckPath[x][1]])
        colour.append(data['colours'][deckPath[x][1]])
        types.append(data['types'][deckPath[x][1]])
        population.append(Deck(deckPath[x][0], cardSet[x], cardNo[x], colour[x], types[x]))
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

#This will take in a population and get a fitness value for all members
def fitnessFunction(population, popNo):
    #call subroutine setDecks
    setDecks(population)
    #run runForge.bat
    subprocess.run('runForge.bat')
    #this will search for a process javaw.exe in currently running processes and 
    #return True if it is running, False if it is not.
    a = 'javaw.exe' in (process.name() for process in psutil.process_iter())
    #while loop to wait for javaw.exe/runForge to finish
    while a == True:
        #wait 2s between checks
        time.sleep(2)
        #check again
        a = 'javaw.exe' in (process.name() for process in psutil.process_iter())
    #make list of all files ending with .log in folder forgePath
    fileNames = [x for x in os.listdir(forgePath) if x.endswith(".log")]
    #create/get full path to each file
    filePaths = [os.path.join(forgePath, x) for x in fileNames]
    #select the .log file that has just been written to by checking for the most recent
    #modification time
    File = max(filePaths, key=lambda filePaths: os.path.getmtime(filePaths))
    logFile = open(File)
    #read last 16 lines, where the results are
    text = logFile.readlines()[-popNo:]
    splitNum = []
    fitness = {}
    fitness['popNo'] = []
    fitness['value'] = []
    for x in range(0, len(text)):
        splitNum.append(text[x].split('=>'))
        fitness['popNo'].append(int(splitNum[x][0][4:6]))
        fitness['value'].append(int(splitNum[x][1][:3]))
    logFile.close()
    return fitness

#sort the population
def sortPopulation(population, fitness):
    popSorted = []
    for x in range(0, len(fitness['popNo'])):
        population[fitness['popNo'][x]].fitness = fitness['value'][x]
        popSorted.append(population[fitness['popNo'][x]])
    return popSorted

def selection(sortedPopulation, eliteNo, popLeft):
    results = []
    choices = []
    for x in range(0, eliteNo):
        results.append(sortedPopulation[x])
    del sortedPopulation[:eliteNo]
    choices = weightedSelect(sortedPopulation, popLeft)
    results.extend(choices)
    for x in range(0, len(results)):
        print(len(results[x].path))
    return results

def weightedSelect(sortedPopulation, popLeft):
    weight = []
    choice = []
    total = 0
    for x in range(0, len(sortedPopulation)):
        if sortedPopulation[x].fitness > 0:
            total = total + sortedPopulation[x].fitness
        else:
            total = total + 1
    for x in range(0, len(sortedPopulation)):
        if sortedPopulation[x].fitness == 0:
            sortedPopulation[x].fitness = 1
        weight.append(sortedPopulation[x].fitness/total)
    for x in range(0, popLeft//2):
        chosen = random.choices(population = sortedPopulation, weights = weight)
        choice.append(chosen[0])
        index = sortedPopulation.index(choice[x])
        sortedPopulation.remove(choice[x])
        weight.pop(index)
    return choice

#Take two decks with the same mainColour and use them to create offspring
def breed(deck1, deck2):
    child = {'path':[], 'setName':[], 'noCard':[], 'colour':[], 'types':[], 'mainColour':''}
    child['mainColour'] = deck1.mainColour
    deck1Copy = deck1
    deck2Copy = deck2    
    tempPath = []
    deckIndex = []
    for x in range(0, len(deck1.path)): #add all land cards to child deck
        if deck1.types[x] == 'Land':
            child = appendChild(child, deck1, x)
    for x in range(0, len(child['path'])):
        deck1Copy.remove(child['path'][x]) #remove land cards from deck1Copy
    for x in range(0, len(deck2.path)):
        if deck2.types[x] == 'Land':
            tempPath.append(x)
    for x in range(0, len(tempPath)):
        deck2Copy.pop(x) #remove land cards from deck2Copy
    (deck1Copy.path).extend(deck2Copy.path) #add all cards and attributes to deck1Copy
    (deck1Copy.setName).extend(deck2Copy.setName)
    (deck1Copy.noCard).extend(deck2Copy.noCard)
    (deck1Copy.colour).extend(deck2Copy.colour)
    (deck1Copy.types).extend(deck2Copy.types)
    for x in range(0, len(deck1Copy.path)):
        if deck1.colour[x] != child['mainColour'] and len(deck1.colour[x]) != 0:
            deckIndex.append(x)
    #
    for x in range(1, len(deckIndex)+1):
        deck1Copy.path.pop(deckIndex[-x])
    #
    #add to each card an index so we can use random.sample
    for x in range(0, len(deck1Copy.path)):
        deck1Copy.path[x] = [deck1Copy.path, x]
    randPath = random.sample(deck1Copy.path, len(deck1Copy.path)) #randomise deck
    if len(deck1Copy.path) > 60:
        length = 60 #max length of MTG deck
    else:
        length = len(randPath)
    for x in range(0, length):
        i = randPath[x][1]
        child = appendChild(child, deck1Copy, i)
    #
    return child

def appendChild(child, deck, x):
    child['path'].append(deck.path[x][0])
    child['setName'].append(deck.setName[x])
    child['noCard'].append(deck.noCard[x])
    child['colour'].append(deck.colour[x])
    child['types'].append(deck.types[x])
    return child

def breedPopulation(population, eliteNo, popNo):
    children = []
    pool = random.sample(population, len(population))
    length = popNo - len(population)
    for x in range(0, eliteNo):
        children.append(population[x])
    #loop to create children - try to make sure that the parents have the same mainColour
    for x in range(0, len(pool)):
        while pool[x].mainColour[0] != pool[-(x+1)].mainColour[0]:
            pool = random.sample(population, len(population))
        child = breed(pool[x], pool[-(x+1)])
        children.append(Deck(child['path'], child['setName'], child['noCard'], child['colour'], child['types']))
    return children

def mutatePop(population, mutationRate):
    newPop = []
    for x in range(0, len(population)):
        mutatedInd = mutate(population[x], mutationRate)
        newPop.append(Deck(mutatedInd['path'], mutatedInd['setName'], mutatedInd['noCard'], mutatedInd['colour'], mutatedInd['types']))
    #return mutated population
    return newPop
  
def mutate(individual, mutationRate):
    mutatedInd = {'path':[], 'setName':[], 'noCard':[], 'colour':[], 'types':[]}
    for x in range(len(individual.path)):
        mutatedInd['path'].append(individual.path[x])
        mutatedInd['setName'].append(individual.setName[x])
        mutatedInd['noCard'].append(individual.noCard[x])
        mutatedInd['colour'].append(individual.colour[x])
        mutatedInd['types'].append(individual.types[x])
        if random.random() < mutationRate:
            types = 'abc'
            colour = 'abc'
            i = 0
            with open('mtgjson2.json', 'r') as file:
                data = json.load(file)
                while types != mutatedInd['types'][x] or colour != mutatedInd['colour'][x]:
                    if i == 21005:
                        break
                    colour = data['colours'][i]
                    types = data['types'][i]
                    i += 1
                if i != 21005:
                    mutatedInd['path'][x] = data['cardName'][i-1]
                    mutatedInd['setName'][x] = data['cardSet'][i-1]
                    mutatedInd['colour'][x] = data['colours'][i-1]
                    mutatedInd['types'][x] = data['types'][i-1]
    return mutatedInd

def nextGeneration(population, popNo, eliteNo, popLeft, mutationRate):
    #b = fitnessFunction(a)
    fitness = {'popNo':[12, 10, 8, 14, 11, 9, 1, 13, 0, 2, 6, 3, 7, 4, 5], 
         'value':[9, 9, 9, 9, 6, 6, 6, 6, 6, 6, 3, 3, 3, 3, 0]}
    popRanked = sortPopulation(population, fitness)
    popSelected = selection(popRanked, eliteNo, popLeft)
    popOffspring = breedPopulation(popSelected, eliteNo, popNo)
    mutatedPop = mutatePop(popOffspring, mutationRate)
    return mutatedPop

population = getPop(popNo)
for x in range(0, len(population[0].path)):
    print(len(population[0].path))
mutatedPop = nextGeneration(population, popNo, eliteNo, popLeft, mutationRate)

#the error does not occur in getPop. I think it might be in sortPopulation or selection

r'''

#Test to see if nextGeneration works





#Test to see if the mutation works.
    a = getPop(popNo)
    #b = fitnessFunction(a)
    b = {'popNo':[12, 10, 8, 14, 11, 9, 1, 13, 0, 2, 6, 3, 7, 4, 5], 
         'value':[9, 9, 9, 9, 6, 6, 6, 6, 6, 6, 3, 3, 3, 3, 0]}
    c = sortPopulation(a, b)
    d = selection(c, eliteNo, popLeft)
    e = breedPopulation(d, eliteNo, popNo)
    f = mutatePop(e, mutationRate)
    print(f[0].path[0])

    It works.

#Note changed from popNo = 16, to popNo = 15 here so changed b test.

#Test to see if the selection works
    a = getPop(popNo)
    #b = fitnessFunction(a)
    b = {'popNo':[12, 10, 8, 14, 11, 9, 1, 13, 0, 2, 6, 3, 7, 4, 5], 
         'value':[9, 9, 9, 9, 6, 6, 6, 6, 6, 6, 3, 3, 3, 3, 0]}
    c = sortPopulation(a, b)
    d = selection(c, eliteNo, popLeft)
    print(d[1].path)
    print(d[6].path)
    print(len(d))
    
    It works.

#Test to see if the population could be sorted
    a = getPop(popNo)
    #b = fitnessFunction(a)
    b = {'popNo':[2,3,6,13,9,8,14,1,12,5,15,11,10,7,4,0], 
         'value':[12,9,9,9,9,6,6,6,6,6,6,3,3,3,3,0]}
    c = sortPopulation(a, b)
    for x in range(0, len(c)):
        print(c[x].colour)

    It works.
    
#New Test to see if the log file can be read
    a = getPop(popNo)
    b = fitnessFunction(a)
    print(b['popNo'])
    print(b['value'])
    
    It works.
    
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
    
    It works.
    
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