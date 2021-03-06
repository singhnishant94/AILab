#!/usr/bin/python2.7
graphemeTophoneme = True
Threegram = False

fTrain = open("trainData.txt", 'r')
fStates = open("states.txt", 'r')
if not graphemeTophoneme:
    fStates = open("states2.txt", 'r')
    
states = fStates.readlines()    
states.insert(0, "^")

if Threegram:
    states.insert(0, "^^")

states = [state.strip() for state in states]
lines = fTrain.readlines()
lines = [line.strip() for line in lines]

lexicalFreq = {}
transitionFreq = {}
lexicalProb = {}
transitionProb = {}
def getStates():
    return states
def init_freq():
    for state in states:
        lexicalFreq[state] = {}
        transitionFreq[state] = {}
        for state2 in states:
            if (Threegram):
                transitionFreq[state][state2] = {}
                for state3 in states:
                    transitionFreq[state][state2][state3] = 0
            else :
                transitionFreq[state][state2] = 0


def fillFrequency():
    for line in lines:
        tokens = line.split(" ")
        graphemes = []
        phonemes = []
        if graphemeTophoneme:
            graphemes = [char for char in tokens[0]]
            phonemes = tokens[1:]
        else :
            phonemes = [char for char in tokens[0]]
            graphemes = tokens[1:]          
        if len(phonemes) != len(graphemes):
            print "Len(phoneme)!=Len(Grapheme)\n"
            continue
        else:
            for i in range(len(phonemes)):
                if Threegram:
                    if (i == 0):
                        transitionFreq["^^"]["^"][phonemes[i]] += 1
                    elif (i == 1):
                        transitionFreq["^"][phonemes[i-1]][phonemes[i]] += 1
                    else :
                        transitionFreq[phonemes[i-2]][phonemes[i-1]][phonemes[i]] += 1
                else:
                    for i in range(len(phonemes)):
                        if (i == 0):
                            transitionFreq["^"][phonemes[i]] += 1
                        else :
                            transitionFreq[phonemes[i-1]][phonemes[i]] += 1
                
                if graphemes[i] in lexicalFreq[phonemes[i]]:
                    lexicalFreq[phonemes[i]][graphemes[i]]+=1
                else :
                    lexicalFreq[phonemes[i]][graphemes[i]] = 1

def getTransitionProb(transitionFreq):
    transitionProb = {}
    for state in states:
        transitionProb[state] = {}
        for state2 in states:
            if Threegram:
                transitionProb[state][state2] = {}
                for state3 in states:
                    transitionProb[state][state2][state3] = 0.0
            else:
                transitionProb[state][state2] = 0.0

    for state in states:
        if Threegram:
            for state2 in states:
                mySum = sum(transitionFreq[state][state2].values())
                for state3 in states:
                    if mySum != 0:
                        transitionProb[state][state2][state3] = float(transitionFreq[state][state2][state3])/mySum                
        else :
            mySum = sum(transitionFreq[state].values())
            for state2 in states:
                if mySum != 0:
                    transitionProb[state][state2] = float(transitionFreq[state][state2])/mySum
    return transitionProb

def getLexicalProb(lexicalFreq):
    lexicalProb = {}
    for state in states:
        lexicalProb[state] = {}
        for grapheme in lexicalFreq[state]:
            lexicalProb[state][grapheme] = 0.0

    for state in states:
        mySum = sum(lexicalFreq[state].values())
        for grapheme in lexicalFreq[state]:
            if mySum !=0:
                lexicalProb[state][grapheme] = float(lexicalFreq[state][grapheme])/mySum
    return lexicalProb

def generateTables():
    global  transitionProb
    global lexicalProb
    init_freq()
    fillFrequency()
    transitionProb =  getTransitionProb(transitionFreq)
    lexicalProb = getLexicalProb(lexicalFreq)
    print "TRANSITION Freq"
    #print transitionFreq

    print "LEXICAL Freq"
    #print lexicalFreq

   

def getTranistionProbState(state1, state2):
    return transitionProb[state1][state2]

def getTranistionProbState2(state3, state2, state): #for trigrams
    return transitionProb[state3][state2][state]

def getEmissionProbState(state, phoneme):
    if phoneme in lexicalProb[state]:
        return lexicalProb[state][phoneme]
    else:
        return 0.0

def phonemesFromParent(parent, graphemes, last):
    phonemes = []
    graphemes.reverse()
    for grapheme in graphemes:
        last = parent[grapheme][last]
        phonemes.append(last)
    phonemes.reverse()
    return phonemes
        
        
    
def getPhonemes(graphemes):
    curState = "^"
    maxProb = {}
    parent = {}
    for state in states:
        if Threegram:
            maxProb[state] = getTranistionProbState2("^^", "^", state)                
        else:
            maxProb[state] = getTranistionProbState("^", state)
    if Threegram:
        for grapheme in graphemes:
            newMaxProb = {}
            parent[grapheme] = {}
            for state in states:
                maxi = -1
                maxState2 = ""
                for state2 in states:
                    for state3 in states:
                        curProb = maxProb[state2]
                        prob = curProb*getTranistionProbState2(state3, state2, state)*getEmissionProbState(state3, grapheme)
                        if (maxi < prob):
                            maxi = prob
                            maxState2 = state3
                    newMaxProb[state] = maxi;
                    parent[grapheme][state] = maxState2
            maxProb = newMaxProb
    else:
        for grapheme in graphemes:
            newMaxProb = {}
            parent[grapheme] = {}
            for state in states:
                maxi = -1
                maxState2 = ""
                for state2 in states:
                    curProb = maxProb[state2]
                    prob = curProb*getTranistionProbState(state2, state)*getEmissionProbState(state2, grapheme)
                    if (maxi < prob):
                        maxi = prob
                        maxState2 = state2
                newMaxProb[state] = maxi;
                parent[grapheme][state] = maxState2
            maxProb = newMaxProb
    maxi = -1
    finalState = ""
    for state in states:
        if (maxi < maxProb[state]):
            maxi = maxProb[state]
            finalState = state
    return phonemesFromParent(parent, graphemes, finalState)
def getPhonemesFromInputList(inputList):
    # graphemes = [char for char in word]
    phonemes = getPhonemes(inputList)
    return phonemes
