# FoxFinder
#
# MIT License
#
# Copyright (c) 2024 Leo Simensen (github.com/s0uthw3st)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import itertools
import math
import random
import time

foxes = [
    [0,1,2],
    [1,2,3],
    [4,5,6],
    [5,6,7],
    [8,9,10],
    [9,10,11],
    [12,13,14],
    [13,14,15],
    [0,4,8],
    [4,8,12],
    [1,5,9],
    [5,9,13],
    [2,6,10],
    [6,10,14],
    [3,7,11],
    [7,11,15],
    [0,5,10],
    [1,6,11],
    [4,9,14],
    [5,10,15],
    [2,5,8],
    [3,6,9],
    [6,9,12],
    [7,10,13]
]
gameState = list()
tileBag = (5,6,5)
tiles = ("F","O","X")

def fac(num):
    return math.factorial(num)
    
def roundPlaces(num):
    return math.floor(10000*num)/100
    
def stringToGame(gameString):
    game = list()
    for i in range(len(gameString)):
        game.append(gameString[i])
    return game
    
def gameToString(game):
    gameString = ""
    for i in range(len(game)):
        gameString = gameString + game[i]
    return gameString
    
def getLetterCounts(game):
    counts = list((0,0,0))
    for letter in game:
        if letter == "F": counts[0] = counts[0] + 1
        elif letter == "O": counts[1] = counts[1] + 1
        elif letter == "X": counts[2] = counts[2] + 1
    return counts
    
def formatStats(total,tilesLeft,win,loss):
    valid = win + loss
    winPercent = roundPlaces(win/valid)
    lossPercent = roundPlaces(loss/valid)
    print("There are",total,"possible arrangements of the remaining",tilesLeft,"fox tiles:")
    print("  ",valid,"of them are valid game states, and of those:")
    print("    ",win,"(",winPercent,"% ) of them end with 16 tiles fox-free")
    print("    ",loss,"(",lossPercent,"% ) of them end early due to foxes\n")
    
def printGame(game):
    for row in range(4):
        rowText = ""
        if row*4 < len(game):
            for column in range(4):
                index = row*4+column
                if index < len(game):
                    rowText = rowText + game[index]
        print(rowText)
    print("")

def findFoxes(game):
    failedFox = False
    for fox in foxes:
        if len(game) > max(fox): # list long enough for the fox being checked
            if game[fox[1]] == "O":
                if (game[fox[0]] == "F" and game[fox[2]] == "X") or (game[fox[0]] == "X" and game[fox[2]] == "F"):
                    failedFox = True
                    break
    return failedFox

def addTile(games,silentMode):
    successes = list()
    failures = 0
    deadEndFlag = False
    if len(games) == 0: # we're starting from nothing
        if not silentMode: print("There are currently no games of length 0, drawing the first tile")
        successes.append(["F"])
        successes.append(["O"])
        successes.append(["X"])
    else:
        if not silentMode: print("There are currently:",len(games),"games of length",len(games[0]))
        if not silentMode: print("  Drawing all possible new tiles")
        for letter in range(3):
            for game in games:
                newGame = game[:]
                if getLetterCounts(game)[letter] < tileBag[letter]:
                    newGame.append(tiles[letter])
                    if findFoxes(newGame):
                        failures = failures + 1
                    else:
                        successes.append(newGame)
    if len(successes) == 0: # we found a dead end with no valid games
        if not silentMode: print("There are now no valid games of length",len(games[0])+1)
        if not silentMode: print("We've found nothing but foxes!\n")
        deadEndFlag = True
    else:
        if not silentMode: print("There are now:",len(successes),"valid games of length",len(successes[0]))
        if not silentMode: print("Foxes were found in:",failures,"games")
        if not silentMode: print("Percentage of additions that created foxes:",roundPlaces(failures/(len(successes)+failures)),"\n")
    return(successes, failures, deadEndFlag)
    
def iterateGameState(startingState,tileCount,randomGames,useCaching,silentMode):

# This function is the heart of the program, iterates through placing every possible tile from a starting board state
#   startingState:  a string (e.g. "FOOXXO") representing a board state you want to test out
#   tileCount:      the number of tiles you want the program to compute, from 0 to 16
#   randomGames:    how many random fox-free games to print at the end
#   useCaching:     use cached data for 0, 1, and 2 tile starts - it's about 9x faster with this on
#   silentMode:     silence a bunch of the output printing
#                       0 shows everything (each iteration of the game state, plus end stats) 
#                       1 hides the individual prints for each iteration
#                       2 hides everything (mostly for use as part of other functions like playRandomGame)

    global gameState
    deadEnd = False
    
    # Do some input validation
    if tileCount > 16 or tileCount < 0 or randomGames < 0:
        print("The tile count and/or random games count values are invalid")
        return
    if type(startingState) != type("") or not all(c in "FOX" for c in startingState):
        print("The starting state string is invalid")
        return
    
    # Set the game state, and more validation (no existing foxes, length lines up right)
    if startingState != "": # if there's a board string ready to load...
        game = stringToGame(startingState)
        gameState = list([game[:]])
        if tileCount < len(game):
            print("The requested tile count is smaller than the starting state")
            return
        if findFoxes(game):
            print("This game already has a fox in it!")
            return
    else:
        gameState = list() # reset the game state to empty
        
    # Save some info about the initial game state for later
    gameLength = len(gameState)
    gameInit = list()
    totalFoxes = 0
    if gameLength > 0:
        gameInit = gameState[0][:]
        
    # Iterate the game as far as requested
    if gameLength == 0: # we're starting from nothing - use cached info
        if useCaching:
            if silentMode != 2:
                print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n")
                print("From the starting state of:")
                printGame(gameInit)
                formatStats(2018016,16,255304,302116)
            gameLength = -1
        else:
            gameState, foxes, deadEnd = addTile(gameState,silentMode)[:]
            totalFoxes = totalFoxes + foxes
            for i in range(tileCount-len(gameState[0])):
                gameState, foxes, deadEnd = addTile(gameState,silentMode)[:]
                totalFoxes = totalFoxes + foxes
                if deadEnd:
                    break 
    elif len(gameState[0]) == 1 and useCaching: # we're starting from one tile, use cached info
        if silentMode != 2:
            print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n")
            print("From the starting state of:")
            printGame(gameInit)
            if gameState[0] != "O": # F or X
                formatStats(630630,15,65364,82456)
            else: # O
                formatStats(756756,15,124576,137204)
        gameLength = -1
        
    elif len(gameState[0]) == 2 and useCaching: # we're starting from two tiles, use cached info
        if silentMode != 2:
            print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n")
            print("From the starting state of:")
            printGame(gameInit)
            if gameState[0][0] == "F":
                if gameState[0][1] == "F":
                    formatStats(168168,14,16513,21572)
                elif gameState[0][1] == "O":
                    formatStats(252252,14,25685,29683)
                else:
                    formatStats(210210,14,23166,31201)
            elif gameState[0][0] == "O":
                if gameState[0][1] == "F":
                    formatStats(252252,14,35049,41707)
                elif gameState[0][1] == "O":
                    formatStats(252252,14,54478,53790)
                else:
                    formatStats(252252,14,35049,41707)
            else:
                if gameState[0][1] == "F":
                    formatStats(210210,14,23166,31201)
                elif gameState[0][1] == "O":
                    formatStats(252252,14,25685,29683)
                else:
                    formatStats(168168,14,16513,21572)
        gameLength = -1
        
    else:
        for i in range(tileCount-len(gameState[0])):
            gameState, foxes, deadEnd = addTile(gameState,silentMode)[:]
            totalFoxes = totalFoxes + foxes
            if deadEnd:
                break
            
    # Generate interesting statistics
    initCounts = getLetterCounts(gameInit)
    if tileCount == 16 and silentMode != 2 and gameLength >= 0: # only show stats for max-length games
        print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n")
        if deadEnd:
            print("From the starting state of:")
            printGame(gameInit)
            print("Every possible outcome leads to a fox, of which there are",totalFoxes,"total")
        else:
            totalBoards = int(fac(16-len(gameInit))/(fac(tileBag[0]-initCounts[0])*fac(tileBag[1]-initCounts[1])*fac(tileBag[2]-initCounts[2])))
            print("From the starting state of:")
            printGame(gameInit)
            formatStats(totalBoards,tileCount-len(gameInit),len(gameState),totalFoxes)
        
    # Print games if requested
    if randomGames > 0 and not deadEnd:
        print("Printing:",randomGames,"random fox-free games of length",tileCount)
        for i in range(randomGames):
            printGame(random.choice(gameState))

def playRandomGame(quietMode):

# Run a random game of Do Not Find The Fox
#   quietMode:      Just toggles between the reduced and silent modes of iterateGameState
#
# Outputs:
#   game won (True/False)
#   length of game (0-16)
#   Game object of the final game (list)

    global tileBag
    global tiles
    
    playerTiles = list()
    for i in range(len(tileBag)):
        for j in range(tileBag[i]):
            playerTiles.append(tiles[i])
    random.shuffle(playerTiles)
    playerTileString = gameToString(playerTiles)
        
    for i in range(1,17):
        if findFoxes(stringToGame(playerTileString[:i])):
            if not quietMode:
                print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n")
                print("Oh no, you've found the fox! Better luck next time")
                printGame(stringToGame(playerTileString[:i]))
            return False, i, stringToGame(playerTileString[:i])
        else:
            iterateGameState(playerTileString[:i],16,0,1,quietMode+1)
            if not quietMode: print("")
    if not quietMode: 
        print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n")
        print("Congratulations, you have not found the fox!\n")
    return True, 16, stringToGame(playerTileString[:])

def profileRandomGames(gamesToPlay,quietMode,showWins):

# Run several random games of Do Not Find The Fox and generate statistics on them
#   gamesToPlay:    how many games to run
#   quietMode:      pass-through to playRandomGame, see above
#   showWins:       show the fox-free games at the end of the run
#
# Outputs:
#   list of Game objects of won games
#   list of Game objects of lost games

    winData = list()
    lossData = list()
    startTime = time.time()
    for i in range(gamesToPlay):
        print("Playing game",i+1,"of",gamesToPlay)
        gameWon, gameLength, gameData = playRandomGame(quietMode)
        if gameWon:
            winData.append(gameData)
        else:
            lossData.append(gameData)
    
    print("Ran",gamesToPlay,"games in",time.time()-startTime,"seconds")
    print("  There were",len(winData),"wins and",len(lossData),"losses")
    
    lossLength = 0
    shortestLoss = 100
    longestLoss = 0
    for game in lossData:
        lossLength = lossLength + len(game)
        if len(game) < shortestLoss: shortestLoss = len(game)
        if len(game) > longestLoss: longestLoss = len(game)
    lossLength = lossLength / (len(lossData) or 1)
    if len(lossData) == 0:
        print("Somehow, no foxes were found")
    else:
        print("The average fox happened after",roundPlaces(lossLength/100),"tiles were placed")
        print("  The earliest fox happened after",shortestLoss,"tiles")
        print("  The latest fox happened after",longestLoss,"tiles")
    print("")
    
    if len(winData) > 0 and showWins:
        print("Printing all fox-free games:")
        for game in winData:
            printGame(game)
    return winData, lossData

# Examples of commands:
#
#iterateGameState("FOOXXO",16,0,1,0)
gameWon, gameLength, gameEnd = playRandomGame(0)
#wins, losses = profileRandomGames(10000,1,0)