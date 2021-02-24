import requests
import bs4
from bs4 import BeautifulSoup as soup
import json

def get_ld_json(url: str) -> dict:
    parser = "html.parser"
    req = requests.get(url)
    page = soup(req.text, parser)
    return json.loads("".join(page.find("script", {"type":"application/ld+json"}).contents))


# # urls = ["https://www.allrecipes.com/recipe/%d" % s for s in range(100000)]
url = "https://www.allrecipes.com/recipe/232549"

# r = requests.get(url)
# con = r.content

# page = soup(con, "html.parser")

# jsonld = page.find_all("script", {"type":"application/ld+json"})

# jsonld = jsonld[0]
# print(jsonld)

jsonld = get_ld_json(url)
useful = jsonld[1]
ingredients = useful["recipeIngredient"]

print(useful["recipeIngredient"])