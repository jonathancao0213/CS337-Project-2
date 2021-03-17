import requests
import bs4
from bs4 import BeautifulSoup as soup
import json
import pandas as pd
from pandas import DataFrame

def get_ld_json(url: str) -> dict:
    parser = "html.parser"
    req = requests.get(url)
    page = soup(req.text, parser)
    return json.loads("".join(page.find("script", {"type":"application/ld+json"}).contents))

def loadIngredientsAndTitle():
    global url
    global ingredients
    global title
    jsonld = get_ld_json(url)
    useful = jsonld[1]
    ingredients = useful["recipeIngredient"]
    title = useful["name"]

def getStarted(inputStr):
    global url
    userInput = input(inputStr)
    if "recipe" in userInput:
        url = input("Sure. Please specify url: ")
        getUrl()
    else:
        getStarted("Sorry, I only help with recipes. Type recipe if that's what you want: ")

def getUrl():
    global url
    global title
    if "http" in url:
        loadIngredientsAndTitle()
        print("Alright. So let's start cheffing up " + title)
        recipeHelper("What would you like to do? [1] go over ingredient list or [2] go over recipe steps")
    else:
        url = input("Sorry, I can only read recipies from AllRecipies.com. Please enter a url: ")
        getUrl()

def recipeHelper(inputStr):
    global ingredients
    global steps
    userInput = input(inputStr)
    if '1' in userInput:
        for ingredient in ingredients:
            print(ingredient)
        userInput = input("Would you like to go over recipe steps now? [y/n]")
        if "y" in userInput:
            steps = loadSteps()
            mainBody("The first step is " + steps[0])
    elif '2' in userInput:
        #JUN AND JONATHAN: IMPLEMENT LOAD STEPS
        #SHOULD CONTAIN AN ARRAY OF STEPS
        steps = loadSteps()
        
        mainBody("The first step is " + steps[0])
    else:
        recipeHelper("Please specify 1 or 2")
    

def loadSteps():
    jsonld = get_ld_json(url)
    
    try:
        instructions = jsonld["recipeInstructions"]
    except:
        instructions = jsonld[1]["recipeInstructions"]

    steps = []

    for step in instructions:
        step = step['text'].split(".")[:-1]
        for s in step:
            steps.append(s)
            
    return steps


ytSearch = "https://www.youtube.com/results?search_query="
gglSearch = "https://www.google.com/search?q="
punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    
def mainBody(inputStr):
    global currStep

    userInput = input(inputStr)
    if "how" in userInput:
        gglLink = gglSearch
        ytLink = ytSearch
        if len(userInput) <= 4 or "do " in userInput:
            nopuncstep = ""
            for char in steps[currStep]:
                if char not in punctuations:
                    nopuncstep = nopuncstep + char
            
            for word in nopuncstep.split():
                gglLink += word + "+"
                ytLink += word + "+"
                
            gglLink = gglLink[:-1]
            ytLink = ytLink[:-1]
        else:
            for word in userInput.split():
                gglLink += word + "+"
                ytLink += word + "+"

            gglLink = gglLink[:-1]
            ytLink = ytLink[:-1]
            
        
        mainBody("Here's a google reference for you: %s, and here's a youtube link for you: %s" % (gglLink, ytLink))
    elif "next" in userInput or "forward" in userInput or "yes" in userInput:
        if currStep < len(steps) - 1:
            currStep = currStep + 1
            mainBody("The next step is " + steps[currStep] + " ")
        else:
            print("There is no next step! Congrats, the recipe is complete!")
    elif "previous" in userInput or "back" in userInput:
        if currStep == 0:
            mainBody("There is no previous instruction. Would you like the next step? ")
        else:
            currStep = currStep - 1
            mainBody("The previous step is " + steps[currStep])
    elif "step" in userInput and "take" in userInput or "bring" in userInput or "go" in userInput:
        found = False
        for key in dictKeys:
            if found == False and key in userInput or str(numDict[key]) in userInput:
                found = True
                stepWanted = numDict[key] - 1
        if found:
            if stepWanted < len(steps):
                currStep = stepWanted
                mainBody("Step "+ str(currStep+1) + " is " + steps[currStep] + " ")
            else:
                mainBody("That step doesn't exist in this recipe. Would you like the next step? ")
        else:
            mainBody("Sorry, I didn't get that. Would you like the next step? ")
    elif "ingredients" in userInput:
        print("Here are the ingredients")
        for ingredient in ingredients:
            print(ingredient)
        mainBody("Would you like the next step? ")
    else:
        mainBody("Would you like the next step? ")

ingredients = []
steps = ["step1", "step2", "step3", "step4"]
url = ''
currStep = 0
numDict = {"first":1, "second":2, "third":3, "fourth":4, "fifth":5, "sixth":6, "seventh":7, "eighth":8, "ninth":9,
          "tenth":10, "eleventh":11, "twelfth":12, "thirteenth":13, "fourteenth":14, "fiftheenth":15}
dictKeys = numDict.keys()
getStarted("Hello, I am BotForPeopleWhoCantRead, although it's useless to tell you that. How can I help you today?: ")