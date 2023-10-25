#%%
import requests
from bs4 import BeautifulSoup

def get_bundesland(var): # WORKS
    if var == "dict":
        page = requests.get("https://de.wikipedia.org/wiki/Liste_der_Städte_in_Deutschland")
        soup = BeautifulSoup(page.text, "html.parser")
        dds = soup.find_all("dd")
        dictionary = {}
        for dd in dds:
            key = dd.find("a").contents[0]
            temp = dd.get_text()
            dictionary[key] = temp[len(temp)-3:][:-1]
        return dictionary
    else: 
        page = requests.get("https://de.wikipedia.org/wiki/Liste_der_Städte_in_Deutschland")
        soup = BeautifulSoup(page.text, "html.parser")
        dds = soup.find_all("dd")
        staedte = []
        for dd in dds:
            staedte.append(dd.find("a").contents[0])
        return staedte
    
dd = get_bundesland("")

# %%
import json
with open("/Users/a2/code/immo/1v1/src/data/de/stadt_bundesland.json", "w") as f:
    json.dump(dd, f)

# %%
dd
# %%
