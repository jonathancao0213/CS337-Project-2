import requests
import bs4
from bs4 import BeautifulSoup as soup
import json
import spacy
from spacy.matcher import Matcher
from spacy.tokens import Span
import en_core_web_sm
nlp = spacy.load('en_core_web_sm')

def get_ld_json(url: str) -> dict:
    parser = "html.parser"
    req = requests.get(url)
    page = soup(req.text, parser)
    return json.loads("".join(page.find("script", {"type":"application/ld+json"}).contents))


# # urls = ["https://www.allrecipes.com/recipe/%d" % s for s in range(100000)]
url = "https://www.allrecipes.com/recipe/25642"

# r = requests.get(url)
# con = r.content

# page = soup(con, "html.parser")

# jsonld = page.find_all("script", {"type":"application/ld+json"})

# jsonld = jsonld[0]
# print(jsonld)

jsonld = get_ld_json(url)
useful = jsonld[1]
ingredients = useful["recipeIngredient"]

instructions = useful["recipeInstructions"]

steps = []

for step in instructions:
    step = step['text'].split(".")[:-1]
    for s in step:
        steps.append(s)


# if len(instructions) == 1:
#     steps = [step['text'].split(".") for step in instructions][0]
#     if steps[-1] == '\n':
#         steps.pop(-1)
# else:
#     steps = [step['text'].split(".") for step in instructions]

print("Steps:")
print(steps)

print("Ingredients:")
print(ingredients)

