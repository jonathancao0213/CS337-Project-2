import requests
import bs4
from bs4 import BeautifulSoup as soup
import json
import pandas as pd
from pandas import DataFrame

import spacy
from spacy import displacy
from spacy.matcher import Matcher
from spacy.tokens import Span
nlp = spacy.load('en_core_web_sm')
from string import punctuation
from collections import defaultdict
import itertools

def get_ld_json(url: str) -> dict:
    parser = "html.parser"
    req = requests.get(url)
    page = soup(req.text, parser)
    return json.loads("".join(page.find("script", {"type":"application/ld+json"}).contents))

def get_ingredientScript(url):
    jsonld = get_ld_json(url)
    useful = jsonld[1]
    ingredients = useful["recipeIngredient"]
    return ingredients

def parse_ingredients(url):
    ingredients = get_ingredientScript(url)
    df = DataFrame (ingredients,columns=['ingredients'])
    # 2 cases
    # "number" ("()") ("unit") (adjective) "noun/subject - ingredient" (, other)
    # contains "to taste"
    df = df["ingredients"]
    df_taste = df[df.str.contains('to taste', case = False)]
    
    df_unit = df[~df.str.contains('to taste', case = False)]
    
    # array of arrays: each array is amount, unit, ingredient, descriptor, preparation
    ingredients_parsed = []
    
    for i in df:
        curr_arr = ["", "", "", "", ""]
        print(i)
        if 'to taste' not in i:
            # before we look at POS, remove everything after the comma and put it in prep
            split_string = i.lower().split(", ", 1)
            root_phrase = split_string[0]
            if len(split_string) > 1:
                other_piece = split_string[1]
            else:
                other_piece = ""

            curr_arr[4] = other_piece

            split_string2 = root_phrase.split("(", 1)
            if len(split_string2) > 1:
                split_string3 = split_string2[1].split(")", 1)
                curr_arr[3] = split_string3[0]
                root_phrase = split_string2[0].strip() + split_string3[1]
            doc = nlp(root_phrase)
            index = 0
            for token in doc:
                found_num = False
                # only get first number if it matches criteria
                #if found_num == False and token.pos_ == "NOUN" and not token.is_alpha or token.pos_ == "NUM":
                if index == 0:
                    curr_arr[0] = token.text
                elif index == 1:
                    if token.pos_ != "ADJ":
                        curr_arr[1] = token.text
                    else:
                        curr_arr[3] = token.text
                elif token.dep_ == "ROOT":
                    curr_arr[2] = token.text
                else: 
                    curr_arr[3] = curr_arr[3] + " " + token.text
                    curr_arr[3] = curr_arr[3].strip()
                index+=1
        else:
            i = i.replace("to taste", "")
            doc = nlp(i)
            curr_arr[0] = "to taste"
            for token in doc:
                if token.dep_ == "ROOT":
                    curr_arr[2] = token.text
                else:
                    curr_arr[3] = curr_arr[3] + " " + token.text
                    curr_arr[3] = curr_arr[3].strip()
        ingredients_parsed.append(curr_arr)
        #print(token.text, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha, token.is_stop, token.children, token.head)
        #displacy.render(doc, style="dep") # change to serve when we go to python


    print(ingredients_parsed)
    return ingredients_parsed

def to_vegetarian (ingredients):
    vegetarian_dict = {'beef':'beyond beef', 'chicken':'tofu', 'fish':'Gardein fishless filet', 'lamb':'tofu', 'duck':'tofu', 'pork':'tofu',
                   'turkey':'tofu', 'meat':'tofu', 'veal':'tempeh', 'ham':'tofu', 'liver':'black beans',
                   'goose':'tofu', 'salami':'jackfruit', 'bologna':'jackfruit', 'salmon':'marinated carrots',
                   'mahi mahi':'Gardein fishless filet','tilapia':'Gardein fishless filet',
                   'yellowtail':'Gardein fishless filet', 'trout':'Gardein fishless filet',
                   'cod':'Gardein fishless filet', 'venison': 'tofu',
                   'lobster':'Gardein fishless filet', 'shrimp':'Gardein fishless filet', 'crab':'Gardein fishless filet',
                   'eel':'edamame', 'meatball':'chickpea',
                   'sausage':'Beyond sausage', 'bratwurst':'jackfruit', 'hotdog':'Beyond sausage',
                  'hamburger':'impossible burger', 'kielbasa':'chickpeas', 'bacon':'Eggplant', 'chuck':'Beyond beef'}
    for i in ingredients:
        curr_ingredient = i[2]
        if curr_ingredient in vegetarian_dict.keys():
            subst = vegetarian_dict[curr_ingredient]
            subst = subst.strip()
            i[2] = subst
        curr_descr = i[3]
        if curr_descr in vegetarian_dict.keys():
            subst = vegetarian_dict[curr_descr]
            subst = subst.strip()
            i[3] = subst
    print(ingredients)
    return ingredients

def to_healthy (ingredients):
    healthy_dict = {
    "butter":"almond butter",
    "margarine":"almond butter",
    "sugar":"organic coconut sugar",
    "salt":"Morton salt substitute",
    "frosting":"greek yogurt frosting",
    "chocolate":"carob",
    "cheese":"ricotta",
    "bread":"wheat bread",
    "oil":"oil",
    "cream":"soy milk and olive oil",
    "juice":"coconut water",
    "bacon":"turkey bacon",
    "sausage":"turkey sausage",
    "soda":"sparkling water",
    "mayonnaise":"avocado oil",
    "ranch":"hummus",
    "dressing":"balsamic vinaigrette",
    "cereal":"granola",
    "caramel":"coconut milk caramel",
    "flour":"almond flour",
    "syrup":"honey",
    "eggs":"egg whites",
    "egg":"egg white",
    "pasta":"zucchini noodles",
    "rice":"rice"}
    for i in ingredients:
        curr_i = i[2]
        if curr_i in healthy_dict.keys():
            subst = healthy_dict[curr_i]
            subst = subst.strip()
            if curr_i == "cream":
                if "whipped" in i[3]:
                    subst = "low-fat cream cheese"
                    i[3] = i[3].replace("whipped", "")
                elif "sour" in i[3]:
                    subst = "yogurt"
                    i[3] = i[3].replace("sour", "")
                elif "ice" in curr_i[3]:
                    subst = "Greek yogurt"
                    i[3] = i[3].replace("ice", "")
            elif curr_i == "bread" and "white" in i[3]:
                i[3] = i[3].replace("white", "")
            elif curr_i == "butter" and "peanut" in i[3]:
                i[3] = i[3].replace("peanut", "")
            elif curr_i == "oil" and "vegetable" in i[3]:
                subst = "canola oil"
                i[3] = i[3].replace("vegetable", "")
            elif curr_i == "rice" and "white" in i[3]:
                subst = "cauliflower rice"
                i[3] = i[3].replace("white", "")
                
            i[2] = subst

def find_tool(sentence,filter_list):
    in_list = ['in','into','on','to','with','onto']
    tools =[]
    not_tools = []
    sent = nlp(sentence.lower())
    for chunk in sent.noun_chunks:
#         and chunk.root.head.pos_ != 'VERB' and not chunk.root.is_sent_start
        if chunk.root.text not in filter_list and chunk.root.head.text in in_list:
            tools.append(chunk.text)
#     for token in sent:
#         if token.text not in too and token.pos_ == 'NOUN':
#             not_tools.append(token.text)
    return tools, not_tools

def get_Tools(url):
    json_ld = get_ld_json(url)
    ing = itertools.chain.from_iterable(parse_ingredients(url))
    ing = list(dict.fromkeys(ing))
    filter_list = ['mixture','ingredients','degrees',
                    'temperature','f', 'fahrenheit', 'c', 'celsius']
    name = json_ld[1]['name']
    for ingr in ing:
        for word in ingr.split():
            filter_list.append(word)
    for w in name.lower().split():
        filter_list.append(w)
    filter_list = list(dict.fromkeys(filter_list))
    text = json_ld[1]['recipeInstructions']
    if len(text) > 1:
        new_text = ''
        for t in text:
            new_text = new_text + t['text']
        text = new_text
    else:
        text = text[0]['text']
    # print(text)
    # print(name)

    tools = []
    for sentence in nlp(text).sents:
        print(sentence)
        t,nt = find_tool(str(sentence),filter_list)
        for each in t:
            tools.append(each)
    tools = list(dict.fromkeys(tools))
    print(tools)


url = "https://www.allrecipes.com/recipe/22180"
get_Tools(url)
    
