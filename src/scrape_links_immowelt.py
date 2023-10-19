import json
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.safari.options import Options
import os
import ipywidgets as widgets
import time
#if >1 types of search are selected, multiple instances of search props are generated and plotted in different figures.
#PLZ get coordinates / check if valid
#beta nur diese params, höhere versionen mit mehr filtern

#on return driver closes automatically 
####
#loctype: 0-zip, 1-stadt:stadtteil, 2-stadt, 3-Bundesland, 4-Land
#immo-id: first 3 chars site encode
#immo-id: chars 4th on site's immo id
#immo-id: last char: X-unavailable any more, A-available
#immo-id:

#Planwechsel: ID mit makler, makler 0 für Privatverkaf

####BETA VERSTON SORTING FOR PRICE/QM??
#How to store the location based data?

# if too little data, be more conservative.

class Immo: #for every immo in search a new class is made
    def __init__(self, dic):
        self._dict = dic
    def export(self):
        file_path = ""

'''
{               "url": "",
                "preis": -1,
                "typ": -1, ##0123
                "qm": -1,
                "zimmer": -1, 
                "description": "", 
                "first seen": -1,
                "kpi": -1,
                "id": None,
                "location": None
                }'''

                #immowelt-id-prefix : iwe


class Decoder:
    def __init__(self):
        pass
    @staticmethod
    def get_id(driver, s): 
        if s == "immowelt":
            raw = driver.current_url
            return f"iwe{raw}"
    

    @staticmethod
    def first_seen(id):
        try:
            dirs = os.listdir(f"/Users/a2/Desktop/immo_cache/{id}")
        except FileNotFoundError:
            return None
        else:
            dirs.sort()
            #catch wrong files
            for i in dirs:
                if os.path.isdir(f"/Users/a2/Desktop/immo_cache/{id}/{i}"):
                    return i
    @staticmethod
    def decode_searchpage_immowelt(page_source):
        soup = BeautifulSoup(page_source, "html.parser")
        #soup = soup.prettify()
        wrapper = soup.find("div", {"class" : "SearchList-22b2e"})
        elements = wrapper.find_all("div", recursive=False)
        res = []
        for e in elements:
            a = e.find("a")
            if a is not None:
                res.append(a.get("href"))
        return res
    @staticmethod
    def decode_expose_immowelt(driver, typ) -> dict:
        props = {}
        props["id"] = Decoder.get_id(driver, "immowelt")
        props["url"] = driver.current_url
        props["preis"] = driver.find_element(By.XPATH, "//*[@id=\"aUebersicht\"]/app-hardfacts/div/div/div[1]/div[1]/strong").get_attribute("innerHTML")[:-2]
        props["typ"] = typ
        props["qm"] = int(driver.find_element(By.XPATH, "//*[@id=\"aUebersicht\"]/app-hardfacts/div/div/div[2]/div[1]/span").get_attribute("innerHTML")[:-3])
        props["zimmer"] = int(driver.find_element(By.XPATH, "//*[@id=\"aUebersicht\"]/app-hardfacts/div/div/div[2]/div[2]/span").get_attribute("innerHTML"))
        driver.find_element(By.XPATH, "//*[@id=\"js_innerBody\"]/div[2]/main/app-expose/div[3]/div[3]/sd-container[1]/sd-row[7]/sd-col/app-details/sd-card/app-texts/sd-read-more[1]/a").click()
        props["description"] = driver.find_element(By.XPATH, "//*[@id=\"js_innerBody\"]/div[2]/main/app-expose/div[3]/div[3]/sd-container[1]/sd-row[7]/sd-col/app-details/sd-card/app-texts/sd-read-more[1]/div").text
        props["first seen"]  = Decoder.first_seen(props["id"])
        props["kpi"] = None
        
        return props


from selenium.common import JavascriptException, NoSuchElementException, NoSuchFrameException


class Search:

    #sites = ["www.immobilienscout24.de", "www.immowelt.de", "www.immonet.de", "www.immobilo.de", "www.engelvoelkers.com", "www.wohnungsboerse.net", "immobilienmarkt.faz.net"]
    sites = ["www.immowelt.de", "www.immonet.de", "www.immobilo.de", "www.engelvoelkers.com", "www.wohnungsboerse.net", "immobilienmarkt.faz.net"]


    def __init__(self, props, typ): #input : dict of
        self.props = props
        self.links_arr = []
        #self.service = Service(executable_path="/Users/a2/Desktop/Projects/Financials/chromedriver")
        #driver = webdriver.Chrome(service=self.service)
        driver = webdriver.Safari()
        #options = webdriver.ChromeOptions()
        #options.add_argument("user-data-dir=/Users/a2/Library/Application Support/Google/Chrome")
        #driver.refresh()
        #driver.add_cookie({"name": "reese84", "value": input_dict["reese84"]})
        driver.implicitly_wait(5)
        driver.maximize_window()
        self.handler(driver, typ)

    @staticmethod
    def decode_bundesland(inp):

        if inp == 0:
            return "Baden-Württemberg"
        if inp == 1:
            return "Bayern"
        if inp == 2:
            return "Berlin"
        if inp == 3:
            return "Brandenburg"
        if inp == 4:
            return "Bremen"
        if inp == 5:
            return "Hamburg"
        if inp == 6:
            return "Hessen"
        if inp == 7:
            return "Mecklenburg-Vorpommern"
        if inp == 8:
            return "Niedersachsen"
        if inp == 9:
            return "Nordrhein-Westfalen"
        if inp == 10:
            return "Rheinland-Pfalz"
        if inp == 11:
            return "Saarland"
        if inp == 12:
            return "Sachsen"
        if inp == 13:
            return "Sachsen-Anhalt"
        if inp == 14:
            return "Schleswig-Holstein"
        if inp == 15:
            return "Thüringen"



    def get_links(self, s, i, driver, typ) -> list: #alles in 1 array

        if s == "www.engelvoelkers.com":
            driver.get("https://www.engelvoelkers.com")
            driver.find_element("xpath", "//*[@id=\"ev-dialog-cookieConsentDialog\"]/div/div/div[3]/button[2]").click()
            driver.find_element("xpath", "/html/body/div[3]/header/div[5]/div[3]/div[4]/div").click()
            time.sleep(2)
            stadt_elem = driver.find_element("xpath", "//*[@id=\"ev-advanced-search-dialog-location-suggest\"]")
            stadt_elem.send_keys(self.props["stadt"])
            stadt_elem.send_keys(Keys.RETURN)
            if self.props["miete"] == 1:
                driver.find_element("xpath", "//*[@id=\"ev-advanced-search-dialog-main\"]/div[5]/div[6]/div/ul/li[3]/span").click()
            if typ == 0: #wohnung
                driver.find_element("xpath", "//*[@id=\"ev-advanced-search-dialog-main\"]/div[5]/div[8]/div/ul/li[5]/span").click()
            if typ == 1: #haus
                driver.find_element("xpath", "//*[@id=\"ev-advanced-search-dialog-main\"]/div[5]/div[8]/div/ul/li[3]/span").click()
            if typ == 2: #grundstück
                driver.find_element("xpath", "//*[@id=\"ev-advanced-search-dialog-main\"]/div[5]/div[8]/div/ul/li[2]/span").click()
            if typ == 3:
                return ""
            time.sleep(1)
            driver.find_element("xpath", "/html/body/div[3]/header/div[7]/div[5]").click() #search
            time.sleep(3)
            page_number = 1
            def get_pages():
                try:
                    driver.find_element("xpath", "/html/body/div[12]/div")
                except BaseException:
                    return 1
                else:
                    wrapper = driver.find_element("xpath", "/html/body/div[12]/div/ul")
                    return int(wrapper.find_elements("tag name", "li")[-2].get_attribute("innerHTML"))
            def decode_urls():
                wrapper = driver.find_element(By.CLASS_NAME, "ev-search-results")
                boxes = wrapper.find_elements(By.TAG_NAME, "div")
                for i in boxes:
                    try:
                        res = i.find_element(By.TAG_NAME, "a").get_attribute("href")
                    except BaseException:
                        pass
                    else:
                        print(res)
                        return res


            n_pages = get_pages()
            while (page_number <= n_pages): #loop through sites
                self.links_arr.append(decode_urls())
                if page_number != n_pages:
                    driver.find_element("xpath", "/html/body/div[12]/div/ul/li[6]/a").click() #next page

            return self.links_arr

        if s == "www.immobilienscout24.de":
            print("working on implementing ")

        if s == "www.immowelt.de":
            driver.get(f"https://{s}")
            def button():
                try:
                    driver.execute_script('document.querySelector("#usercentrics-root").shadowRoot.querySelector("#uc-center-container > div.sc-jJoQJp.iTLtpk > div > div > div > button.sc-gsDKAQ.fILFKg").click()')

                except JavascriptException:
                    button()
            if i==0:
                button()
            if self.props["mieten"]==1:
                if typ == 0: #Wohnung mieten
                    pass
                elif typ == 1: # Haus mieten
                    driver.find_element("xpath", "//*[@id=\"divSearchWhatFlyout\"]/div[1]/ul/li[2]/label/input").click()
                elif typ == 2: # Grundstück mieten
                    driver.find_element("xpath", "//*[@id=\"divSearchWhatFlyout\"]/div[1]/ul/li[7]/label/input").click()
                elif typ == 3: # Garage mieten
                    driver.find_element("xpath", "//*[@id=\"divSearchWhatFlyout\"]/div[1]/ul/li[6]/label/input").click()
            else:
                if typ==0:
                    driver.find_element("xpath", "//*[@id=\"divSearchWhatFlyout\"]/div[2]/ul/li[2]/label/input").click()
                elif typ==1:
                    driver.find_element("xpath", "//*[@id=\"divSearchWhatFlyout\"]/div[2]/ul/li[1]/label/input").click()
                elif typ==2:
                    driver.find_element("xpath", "//*[@id=\"divSearchWhatFlyout\"]/div[2]/ul/li[5]/label/input").click()
                elif typ==3:
                    driver.find_element("xpath", "//*[@id=\"divSearchWhatFlyout\"]/div[2]/ul/li[7]/label/input").click()

            driver.find_element(By.XPATH, "//*[@id=\"tbLocationInput\"]").send_keys(Search.decode_bundesland(i)) #location
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.RETURN)
            # driver.find_element(By.XPATH, "//*[@id=\"btnSearchSubmit\"]").click() #search # maybe return enough?

            def get_pages():
                try:
                    wrapper = driver.find_element(By.CLASS_NAME, "Pagination-190de")
                except NoSuchFrameException:
                    return get_pages()
                else:
                    try:
                        wrapper.find_element(By.CLASS_NAME, "arrowButton-20ae5")
                    except NoSuchElementException:
                        return wrapper.find_elements(By.TAG_NAME, "button")[-1].find_element(By.TAG_NAME, "span").get_attribute("innerHTML")
                    else:
                        return wrapper.find_elements(By.TAG_NAME, "button")[-2].find_element(By.TAG_NAME, "span").get_attribute("innerHTML")

            def decode_urls():
                try:
                    return Decoder.decode_searchpage_immowelt(driver.page_source)
                except AttributeError:
                    driver.refresh()
                    try:
                        return Decoder.decode_searchpage_immowelt(driver.page_source)
                    except AttributeError:
                        print("empty page!!!!")
                        return []


            page_number = 1
            n_pages = int(get_pages())
            base_url = driver.current_url
            while page_number <= n_pages:
                for i in decode_urls():
                    self.links_arr.append(i)
                driver.get(f"{base_url}&sp={page_number}")
                time.sleep(2)
                #driver.get("https://www.google.com")

                page_number += 1

            return self.links_arr

        if s == "www.immonet.de":
            driver.get(f"https://{s}")
            driver.execute_script('document.querySelector("#usercentrics-root").shadowRoot.querySelector("#uc-center-container > div.sc-ikJyIC.gpszuz > div > div > div > button.sc-gsDKAQ.fILFKg").click()')
            if self.props["mieten"] == 1:
                driver.find_element("xpath", "//*[@id=\"btn-insearch-marketingtype-rent\"]").click()
            if self.props["mieten"] ==2:
                driver.find_element("xpath", "//*[@id=\"btn-insearch-marketingtype-buy\"]").click()
            if self.props["typ"] == 0:
                driver.find_element("xpath", "//*[@id=\"estate-type\"]/option[1]").click()
            if self.props["typ"] == 1:
                driver.find_element("xpath", "//*[@id=\"estate-type\"]/option[2]").click()
            if self.props["typ"] == 2:
                driver.find_element("xpath", "//*[@id=\"estate-type\"]/option[8]").click()
            if self.props["typ"] == 3:
                driver.find_element("xpath", "//*[@id=\"estate-type\"]/option[4]").click()
            if self.props["preis"][1] != 0:
                driver.find_element("xpath", "//*[@id=\"price_to\"]").send_keys(self.props["preis"][1])
            if self.props["qm"][0] != 0:
                driver.find_element("xpath", "//*[@id=\"area_from\"]").send_keys(self.props["qm"][0])
            if self.props["zimmer"][0] == 1 and self.props["zimmer"][1] == 1: #zimmer
                driver.find_element("xpath", "//*[@id=\"btn-insearch-rooms-1\"]").click()
            if self.props["zimmer"][0] == 2:
                driver.find_element("xpath", "//*[@id=\"btn-insearch-rooms-2\"]").click()
            if self.props["zimmer"][0] == 3:
                driver.find_element("xpath", "//*[@id=\"btn-insearch-rooms-3\"]").click()
            if self.props["zimmer"][0] == 4:
                driver.find_element("xpath", "//*[@id=\"btn-insearch-rooms-4\"]").click()
            if self.props["zimmer"][0] == 5:
                driver.find_element("xpath", "//*[@id=\"btn-insearch-rooms-5\"]").click()
            if self.props["zimmer"][0] >= 6:
                driver.find_element("xpath", "//*[@id=\"btn-insearch-rooms-5\"]").click()

            driver.find_element("xpath", "//*[@id=\"btn-int-find-immoobjects\"]").click()

        if s == "www.immobilo.de":
            driver.get("https://www.immobilo.de")
            driver.find_element("xpath", "//*[@id=\"consentDialog\"]/div[2]/div[2]/div/div[2]/div/div[1]/div").click()
            if self.props["mieten"]==2:
                driver.find_element("xpath", "/html/body/div[1]/div[4]/div/div[3]/div[2]/div[2]/div/div[1]/div/form/div[1]/div/div[2]").click()
            if self.props["plz"] != 0:
                driver.find_element("xpath", "//*[@id=\"l\"]").send_keys(self.props["plz"])
            else:
                temp = self.props["stadt"]
                temp2 = self.props["stadtteil"]
                driver.find_element("xpath", "//*[@id=\"l\"]").send_keys(f"{temp} {temp2}")
                driver.find_element("xpath", "/html/body").send_keys(Keys.RETURN)
            driver.find_element("xpath", "/html/body/div[1]/div[3]/div/div[3]/div[2]/div[2]/div[1]/div[1]/div/button").click()
            driver.find_element("xpath", "//*[@id=\"modal-extra-filters\"]/form/div[1]/div/div[2]/div[1]/div[2]/div/div[2]/span").click()
            ###Type-select
            if self.props["mieten"] == 1:
                if typ == 0:
                    driver.find_element("xpath", "//*[@id=\"t\"]/optgroup[1]/option[2]")
                if typ == 1:
                    driver.find_element("xpath", "//*[@id=\"t\"]/optgroup[1]/option[4]")
                if typ == 2:
                    driver.find_element("xpath", "//*[@id=\"t\"]/optgroup[1]/option[5]")
                if typ == 3:
                    driver.find_element("xpath", "//*[@id=\"t\"]/optgroup[1]/option[7]")
            else:
                if typ == 0:
                    driver.find_element("xpath", "//*[@id=\"t\"]/optgroup[2]/option[2]")
                if typ == 1:
                    driver.find_element("xpath", "//*[@id=\"t\"]/optgroup[2]/option[3]")
                if typ == 2:
                    driver.find_element("xpath", "//*[@id=\"t\"]/optgroup[2]/option[4]")
                if typ == 3:
                    driver.find_element("xpath", "//*[@id=\"t\"]/optgroup[2]/option[6]")
            driver.find_element("xpath", "//*[@id=\"modal-extra-filters\"]/form/div[1]/div/div[2]/div[1]/div[2]/div/div[2]/div/div[2]/button").click()
            ###Preis
            driver.find_element("xpath", "//*[@id=\"modal-extra-filters\"]/form/div[1]/div/div[2]/div[2]/div[1]/div/span").click()
            if self.props["preis"][1] != 0:
                driver.find_element("xpath", "//*[@id=\"pf\"]").send_keys(self.props["preis"][0])
            if self.props["preis"][1] != 0:
                driver.find_element("xpath", "//*[@id=\"pt\"]").send_keys(self.props["preis"][1])
            driver.find_element("xpath", "//*[@id=\"modal-extra-filters\"]/form/div[1]/div/div[2]/div[2]/div[1]/div/div/div[3]/button").click()
            ###Zimmer
            if self.props["zimmer"]!= [0,0]:
                driver.find_element("xpath", "//*[@id=\"modal-extra-filters\"]/form/div[1]/div/div[2]/div[2]/div[2]/div/span").click()
                if self.props["zimmer"][0]!= 0 and self.props["zimmer"][0]<9:
                    driver.find_element("xpath", f"//*[@id=\"rf\"]/option[{self.props['zimmer'][0]}]").click()
                elif self.props["zimmer"][0]!= 0:
                    driver.find_element("xpath", f"//*[@id=\"rf\"]/option[8]").click()
                    print(f"Auf Seite {s} ist die maximale Anzahl an Zimmern 8.")
                #max
                if self.props["zimmer"][0]!= 0 and self.props["zimmer"][0]<9:
                    driver.find_element("xpath", f"//*[@id=\"rt\"]/option[{self.props['zimmer'][1]}]").click()
                driver.find_element("xpath", "//*[@id=\"modal-extra-filters\"]/form/div[1]/div/div[2]/div[2]/div[2]/div/div/div[3]/button")
            ###Qm
            driver.find_element("xpath", "//*[@id=\"modal-extra-filters\"]/form/div[1]/div/div[2]/div[2]/div[3]/div/span").click()
            if self.props["qm"][1] != 0:
                driver.find_element("xpath", "//*[@id=\"sf\"]").send_keys(self.props["qm"][0])
            if self.props["qm"][1] != 0:
                driver.find_element("xpath", "//*[@id=\"st\"]").send_keys(self.props["qm"][1])
            driver.find_element("xpath", "//*[@id=\"modal-extra-filters\"]/form/div[1]/div/div[2]/div[2]/div[3]/div/div/div[3]/button").click()

        if s == "www.wohnungsboerse.net":
            driver.get("https://www.wohnungsboerse.net")
            driver.execute_script('document.querySelector("#usercentrics-root").shadowRoot.querySelector("div").querySelector("div").querySelector("div").querySelector("div").querySelectorAll("div")[1].querySelector("div > .sc-gWXbKe > div > div > div").querySelectorAll("button")[1].click()')

        if s == "immobilienmarkt.faz.net":
            print("not implemented yet")

    @staticmethod
    def extract_data(s, driver, typ) -> dict:
        if s == "www.immowelt.de":
            return Decoder.decode_expose_immowelt(driver, typ)


    def export_links(self, data): #every search logged with monotonic time
        _time = self.props["time"]
        os.system(f"cd /Users/a2/Desktop/immo_cache && mkdir {_time} && cd {_time} && touch links.json")
        with open(f"/Users/a2/Desktop/immo_cache/{_time}/links.json", "w") as f:
            json.dump(data,f)
        return _time

    @staticmethod
    def export_immo(propys, _time):
        os.system(f"cd /Users/a2/Desktop/immo_cache/{_time} && touch properties.json")
        with open(f"/Users/a2/Desktop/immo_cache/{_time}/properties.json", "w") as f:
            f.write(str(propys))
        return propys["id"]

    #main / site-folder / immo-id:
    #   -immo-id_pic_n.jpg etc.
    #   -immo-id_time.html
    #   -immo-id.py -> dictionary
    @staticmethod
    def export_pics(s, driver, id, time):
        if s == "www.immowelt.de":
            urls = []
            wrapper = driver.find_element(By.ID, "mainGallery")
            img_wrappers = wrapper.find_element(By.TAG_NAME, "div").find_elements(By.TAG_NAME, "div")
            for i in img_wrappers:
                src = i.find_element(By.TAG_NAME, "app-media-item")
                try:
                    src = src.find_element(By.TAG_NAME, "img").get_attribute("src")
                except NoSuchElementException:
                    src = src.find_element(By.TAG_NAME, "sd-loading").find_element(By.TAG_NAME, "img").get_attribute("data-src")
                urls.append(src)
            for i, u in enumerate(urls):
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + 't')
                driver.get(u)
                time.sleep(10)
                os.system(f"touch /Users/a2/Desktop/immo_cache/{id}/{time}/{i}.png")
                with open(f"touch /Users/a2/Desktop/immo_cache/{id}/{time}/{i}.png", "wb") as f:
                    f.write(driver.find_element(By.XPATH, "/html/body/img").screenshot_as_png)

    @staticmethod
    def export_times(times: list):
        with open(f"/Users/a2/.cache/immodynamics/{times[0]}.json", "w") as f:
            json.dump(times, f)

    def handler(self, driver, typ):
        times = [] # every site gets own time, easier merge with times of one search cycle
        for i, s in enumerate(Search.sites): # for every site
            links = []
            if s=="www.immowelt.de":
                for j in range(16):
                    links += self.get_links(s, j, driver, typ)
                    __time = self.props["time"]
                    os.mkdir(f"/Users/a2/.cache/immodynamics/{__time}")
                    with open(f"/Users/a2/.cache/immodynamics/{__time}/links{j}.json", "w") as f:
                        f.write("\n".join(links))
            _time = self.export_links(links)
            print(_time)
            times.append(_time)
            for l in links:
                driver.get(l)
                immo_anzeige = Search.extract_data(s, driver, typ) #
                id = Search.export_immo(immo_anzeige, _time)
                Search.export_pics(s, driver, id, _time)
            Search.export_times(times)
            # return a 2d, sorted array of ID, rentability
            # save : in main folder also search props + site

            assert(0.1+0.2==0.3), "ES KLAPPT"
        driver.close

        #print(self.content)

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
    

class search_props:   ###### WORKS
    # CALLS SEARCH() WITH SOMETHING LIKE
    # {'mieten': 1, 'typ': [1, 0, 0, 0], 'stadt': None, 'plz': None, 'stadtteil': None, 'bundesland': None, 'preis': [None, None], 'qm': [None, None], 'zimmer': [None, None], 'time': '1665658158'}


    staedte = get_bundesland(0)
    dict_bundesl = get_bundesland("dict")
    
    
    
    
    def __init__(self, dictionary: dict):
        self.props = {"mieten" : None,  #1 mieten, 2 kaufen ##
                      "typ" : [0,0,0,0],  #values: [wohnung, haus, grundstück, garage]  ##
                      "stadt" : None,
                      "plz" : None,
                      "stadtteil" : None,
                      "bundesland" : None,  #int OBACHT GEBEN-BESSER DEBUGGEN (array von bundesländern für unterschiedlcihe seiten!!!)
                      "preis" : [None, None],
                      "qm" : [None, None],
                      "zimmer" : [None, None],
                      "time" : str(int(time.time()))}
        self.props = {**self.props, **dictionary}

        self.links_html = []

        Search(self.props, self.props['typ'].index(1)) #search and export


def handle():
    def arri(i):
        ar = [0,0,0,0]
        ar[i] = 1
        return ar
    for i in range(4): # every type of immo (wohnung, haus, ..)
        search_miete = search_props(dictionary=dict(mieten=1, typ=arri(i))) # miete
        search_kauf = search_props(dictionary=dict(miete=2, typ=arri(i))) # kauf



        # export with json file search props
        # -> later with easier backtrace during analysis

    print("done")


if __name__ == "__main__":
    handle()