#MTG Deck Building GA 2

import json, subprocess, random, os, psutil, time, operator

#important variables
popNo = 15
eliteNo = 5
mutationRate = 0.001
generations = 20
popLeft = popNo - eliteNo

#paths to files
forgePath = r'C:\Users\Muir7\AppData\Roaming\Forge'

#create Deck class
class Deck:
    #run upon creation of Deck object
    def __init__(self, path, setName, noCard, colour, types):
        #create attributes
        self.path = path 
        self.setName = setName
        self.noCard = noCard
        self.colour = colour
        self.types = types
        self.fitness = 0
        #get mainColour
        colours = ['B', 'G', 'R', 'U', 'W', '']
        counted = {'B':0,'G':0,'R':0,'U':0,'W':0,'':0}
        #loop through colours to get colour count
        for x in range(0, len(self.colour)):
            for i in range(0, len(colours)):
                counted[colours[i]] += self.colour[x].count(colours[i])
        #create list of colours sorted by count
        colourList = sorted(counted.items(), key=operator.itemgetter(1), reverse = True)
        self.mainColour = colourList[0] #set mainColour to first element
        
#get pop from MTGjson file that we got through running convertMTGjson
def getPop(popNo):
    #declare lists
    population, cardSet, cardNo, colour, types = [], [], [], [], []
    #read .json deck files
    with open('MTGjson.json',) as file:
        data = json.load(file)
        #get random order of decks
        deckPath = random.sample(data['cardNames'], popNo)
        #create initial population using deckPath
        for x in range(0, popNo):
            cardSet.append(data['cardSet'][deckPath[x][1]])
            cardNo.append(data['cardCount'][deckPath[x][1]])
            colour.append(data['colours'][deckPath[x][1]])
            types.append(data['types'][deckPath[x][1]])
            population.append(Deck(deckPath[x][0][0], cardSet[x], cardNo[x], colour[x], types[x]))
    return population

#This will open deckA and deckB, and write the deck data into those files so Forge can use them
def setDecks(population):
    for x in range(0, len(population)):
        template = "[metadata]\nName=deck"+str(x)+"\n[Main]\n"
        #create and open new deck file
        with open(r"C:\Users\Muir7\AppData\Roaming\Forge\decks\constructed\deck"+str(x)+".dck", "w+") as deck:
            deck.write(template) #write the necessary code at the top
            for i in range(0, len(population[x].path[0])):
                deck.write(str(population[x].noCard[i]) + " " + str(population[x].path[0][i]) + "|" + str(population[x].setName[i]) + "\n")

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
        time.sleep(2)
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
    #loop through every member of the population
    for x in range(0, len(fitness['popNo'])):
        #we append the fitness values to each member of the population
        population[fitness['popNo'][x]].fitness = fitness['value'][x]
        #append the individuals in the population to popSorted starting with the ones
        #with the highest fitness value
        popSorted.append(population[fitness['popNo'][x]])
    return popSorted

#select the individuals who get to breed - This will add eliteNo then use weightedSelect
#to get the rest
def selection(sortedPopulation, eliteNo, popLeft):
    results = []
    choices = []
    #append eliteNo members to results
    for x in range(0, eliteNo):
        results.append(sortedPopulation[x])
    #delete them from sortedPopulation then pass sortedPopulation to weightedSelect
    del sortedPopulation[:eliteNo]
    choices = weightedSelect(sortedPopulation, popLeft)
    #append the returned weighted random choices to results
    results.extend(choices)
    return results

#weighted select will weigh the individuals of sortedPopulation, and use this weight to
#'randomly' choose which other individuals get to breed
def weightedSelect(sortedPopulation, popLeft):
    weight = []
    choice = []
    total = 0
    #loop through population to get total
    for x in range(0, len(sortedPopulation)):
        if sortedPopulation[x].fitness > 0:
            total = total + sortedPopulation[x].fitness
        else:
            total = total + 1
    #if fitness value == 0, change to 1, just to give the unlucky decks a chance
    for x in range(0, len(sortedPopulation)):
        if sortedPopulation[x].fitness == 0:
            sortedPopulation[x].fitness = 1
        weight.append(sortedPopulation[x].fitness/total)
    #loop for popLeft//2 so that we don't have too many members to breed
    for x in range(0, popLeft//2):
        #choose 1 member of the population and append them
        chosen = random.choices(population = sortedPopulation, weights = weight)
        choice.append(chosen[0])
        #remove that member of the population, and loop to make new choice
        index = sortedPopulation.index(choice[x])
        sortedPopulation.remove(choice[x])
        weight.pop(index)
    return choice

#Take two decks with the same mainColour and use them to create offspring
def breed(deck1, deck2):
    child = {'path':[], 'setName':[], 'noCard':[], 'colour':[], 'types':[], 'mainColour':''}
    child['mainColour'] = deck1.mainColour
    deck1Copy, deck2Copy = deck1, deck2   
    tempPath, deckIndex  = [], []
    for x in range(0, len(deck1.path)): #add all land cards to child deck
        if deck1.types[x] == 'Land':
            child = appendChild(child, deck1, x, True)
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
    for x in range(1, len(deckIndex)+1):
        deck1Copy.path.pop(deckIndex[-x])
    for x in range(0, len(deck1Copy.path)):
        deck1Copy.path[x] = [deck1Copy.path[x], x]
    randPath = random.sample(deck1Copy.path, len(deck1Copy.path)) #randomise deck
    if len(deck1Copy.path) > 60:
        length = 60 #max length of MTG deck
    else:
        length = len(randPath)
    #print(randPath)
    for x in range(0, length):
        i = randPath[x][1]
        child = appendChild(child, deck1Copy, i, False)
    return child

#append cards to child
def appendChild(child, deck, x, flag):
    #print(deck.path[x][0])
    if flag == True:
        child['path'].append(deck.path[x])
    else:
        child['path'].append(deck.path[x][0])
    child['setName'].append(deck.setName[x])
    child['noCard'].append(deck.noCard[x])
    child['colour'].append(deck.colour[x])
    child['types'].append(deck.types[x])
    return child

#breed all the population
def breedPopulation(population, eliteNo, popNo):
    children = []
    #append selected members to children
    for x in range(0, popNo-eliteNo):
        children.append(population[x])
    pool = random.sample(population, popNo-len(population))
    #loop to create children - try to make sure that the parents have the same mainColour
    for x in range(0, len(pool)):
        while pool[x].mainColour[0] != pool[-(x+1)].mainColour[0]:
            pool = random.sample(population, popNo-len(population))
        child = breed(pool[x], pool[-(x+1)])
        children.append(Deck(child['path'], child['setName'], child['noCard'], child['colour'], child['types']))
    return children

#Test to see if crossover works
population = getPop(popNo)
fitness = {'popNo':[12, 10, 8, 14, 11, 9, 1, 13, 0, 2, 6, 3, 7, 4, 5], 
         'value':[9, 9, 9, 9, 6, 6, 6, 6, 6, 6, 3, 3, 3, 3, 0]}
sortedPop = sortPopulation(population, fitness)
selectedPop = selection(sortedPop, eliteNo, popLeft)
children = breedPopulation(selectedPop, eliteNo, popNo)
#child = breed(selectedPop[0], selectedPop[1])
#print(child['path'])
for x in range(0, len(children)):
    #while len(children[x].path[0]) == 2:
     #   children[x].path[0] = children[x].path[0][0]
    print(children[x].path)
    print(children[x].mainColour)
    print('----------------------')

r'''
#Test to see if selection works
    population = getPop(popNo)
    fitness = {'popNo':[12, 10, 8, 14, 11, 9, 1, 13, 0, 2, 6, 3, 7, 4, 5], 
             'value':[9, 9, 9, 9, 6, 6, 6, 6, 6, 6, 3, 3, 3, 3, 0]}
    sortedPop = sortPopulation(population, fitness)
    selectedPop = selection(sortedPop, eliteNo, popLeft)
    for x in range(0, len(selectedPop)):
        print(selectedPop[x].path)
        print(selectedPop[x].mainColour)
        print('-----------------')
    print(len(selectedPop))
    
    It works.
    
#Test to see if sorting the population works
    population = getPop(popNo)
    fitness = {'popNo':[12, 10, 8, 14, 11, 9, 1, 13, 0, 2, 6, 3, 7, 4, 5], 
             'value':[9, 9, 9, 9, 6, 6, 6, 6, 6, 6, 3, 3, 3, 3, 0]}
    sortedPop = sortPopulation(population, fitness)
    for x in range(0, len(sortedPop)):
        print(sortedPop[x].fitness)
        print(sortedPop[x].path)
        print('-----------------')

    It works.

#Test to see if the fitness function works
    population = getPop(popNo)
    fitness = fitnessFunction(population, popNo)
    print(fitness['popNo'])
    print(fitness['value'])
    
    It works.
    
#Test to see if getting the population works
    population = getPop(popNo)
    for x in range(0, len(population)):
        print(population[x].path)
        print(population[x].mainColour)
        print(population[x].path[0])
        print('--------------------')
    
    It works.
'''