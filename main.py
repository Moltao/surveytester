from os import scandir
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import random
from pathlib import Path
from .Vraagclass import vraag

driver = webdriver.Firefox('C:\Python projects\Survey testbot\geckodriver')
testfile =  Path("C:\Python projects\Survey testbot\scenarios.csv")


#bestand ophalen
def get_testfile(path):
    """Haalt het bestand met testscenario's op.

    Parameters
    ----------
    path: str
    Pad naar het csv bestand met de testscenario's

    Returns
    ----------
    list of dicts
    Geeft een lijst van dicts terug, waarbij iedere dict
    een regel uit de csv is    
    
    """
    if path != "":
        pad = Path(path)
        with open(pad, encoding='utf-8-sig') as infile:
            csv_reader = csv.DictReader(infile, delimiter=";", )
            scenarios = list(csv_reader)

            return scenarios 
    else:
        print("Geen bestand opgegeven!")
        return None
       

def inloggen(url, login):
    """Logt in bij survey via een selenium browser

    Parameters
    ----------
    url: str
        url naar een survey in de Crowdtech tool
    login: str
        email-adres waarmee ingelogd wordt op de survey

    Returns
    ----------
    Geen returns, logt in op de survey

    """
    driver.get(url)
    driver.implicitly_wait(1)
    user = driver.find_element_by_xpath('//*[@id="login-email"]')
    user.send_keys(login)
    driver.find_element_by_id("login-button").click()


def invullen(vraag, gegeven_antwoorden):
    
    if vraag.soort == 'tabel' and gegeven_antwoorden[0] == 'tabel':
        for subvraag in range(1, vraag.subvragen+1):
            #vraag.vraagid = vraag.vraagid + '-' + subvraag
            print(subvraag)
            antwoordoptie = gegeven_antwoorden[1][vraag.vraagid + '-' + str(subvraag)]
            driver.find_element_by_id(f"{vraag.vraagid}_sq-{subvraag}_checkradio-answer-label-{antwoordoptie}").click()
    elif vraag.soort == 'sr' and gegeven_antwoorden[0] == 'sr':
        driver.find_element_by_id(f"{vraag.vraagid}_checkradio-answer-label-{gegeven_antwoorden[1]}").click()
        
    elif vraag.soort == 'mr' and gegeven_antwoorden[0] == 'mr':
        for item in gegeven_antwoorden[1]:
            driver.find_element_by_id(f'{vraag.vraagid}_checkradio-answer-label-{item}').click()
    elif vraag.soort == 'open':
        driver.find_element_by_id(f"{vraag.vraagid}_checkradio-input-answer-1").send_keys("test test test")

    driver.find_element_by_id("button-next-nav").click()

def get_q_id():
    #vraagnummer achterhalen vanuit survey
    element = driver.find_element_by_xpath("//form/div")
    vraagid = element.get_attribute("id")

    return vraagid

def hasXpath(xpath):

        if len(driver.find_elements_by_xpath(xpath)) > 0:
            return True
        else:
            return False


def get_q_type():
    #vraagtype achterhalen
    if hasXpath("//form/div[@table]"):
        vraagtype = 'tabel'
    elif hasXpath("//form/div[@open]"):
        vraagtype = 'open'
    elif hasXpath('//form/div/div/div[1][@data-answer-type="Checkbox"]'):
        vraagtype = 'mr'
    elif hasXpath('//form/div/div/div[1][@data-answer-type="Radiobutton"]'):
        vraagtype = 'sr'
    
    return vraagtype

def get_subvragen():
    if hasXpath("//form/div[@table]"):
        subvragen = len(driver.find_elements_by_xpath("/html/body/div/div/main/form/div/div/div"))
    else:
        subvragen = None
    
    return subvragen


def lookup_qid(testdict, vraag):
    """ Kijkt of de vraagid uit survey in het bestand met testscenario's staat.
        Als dat zo is wordt geprobeerd de opgegeven waarde in te vullen.
        Als de vraagid niet in het bestand staat wordt er een random antwoord gekozen.

        Parameters
        ----------
        testdict: dict.  Gemaakt van een csv met testscenario's. Dit komt uit get_testfile()
        vraag: vraagobject. Vraagobject opgehaald door getvraag()

        Returns
        ----------
        antwoord: tuple(str, list).
                        Type vraag uit de data, om te kunnen checken met type uit survey     
                        Lijst van nummers van de antwoorden die gegeven moeten worden. 
                        Als het om een sr gaat, is dit een lijst van 1

    """
    if vraag.soort == 'tabel':
        gegeven_antwoord = {}
        subs = [vraag.vraagid + '-' + str(x) for x in range(1, vraag.subvragen + 1)]
        for sub in subs:
            if sub in testdict:
                gegeven_antwoord[sub] = testdict[sub]        
            else:
                gegeven_antwoord[sub] = str(random.randint(1, len(vraag.antwoorden)))
        antwoordnummer = ('tabel', gegeven_antwoord)   
    else:
        if vraag.vraagid in testdict:
            gegeven_antwoord = testdict.get(vraag.vraagid)
            if gegeven_antwoord == '':
                antwoordnummer = ('random', '1')
            elif len(gegeven_antwoord) == 1 and gegeven_antwoord.isnumeric():
                antwoordnummer = ('sr', gegeven_antwoord)
            elif len(gegeven_antwoord) > 1 and gegeven_antwoord.replace(',','').isnumeric():
                #meerdere antwoorden, hoort bij MR vraag
                antwoordnummer = ('mr', gegeven_antwoord.split(','))
            elif len(gegeven_antwoord) > 1 and gegeven_antwoord.lower().islower():
                #antwoordlabel opgegeven
                antwoordnummer = ('label', gegeven_antwoord)
        else:
            antwoordnummer = ('random', '1')

    return antwoordnummer

def get_antwoordopties(vraagsoort):
    antwoorden ={}

    if vraagsoort == 'tabel':
        surveyantwoorden = driver.find_elements_by_xpath('//form/div/div/div[1]/div[@data-option-list=""]/div')
        for x in surveyantwoorden:                                  
            k = x.find_element_by_xpath('.//input').get_attribute('id')
            k = k[k.rindex('-')+1:]
            v = x.find_element_by_xpath('.//input').get_attribute('value')
            antwoorden[k]=v
    elif vraagsoort == 'open':
        antwoorden = None      
    else:
        surveyantwoorden = driver.find_elements_by_xpath("//form/div/div/div")
        for x in surveyantwoorden:                                  
            k = x.find_element_by_xpath('.//input').get_attribute('id')
            k = k[k.rindex('-')+1:]
            v = x.find_element_by_xpath('.//input').get_attribute('value')
            antwoorden[k]=v

    return antwoorden

def get_open_escape(vraagsoort='open'):
    if hasXpath('//div[@data-outerfield="true"]'):
        escape = True
    else:
        escape = False

    return escape    

#get_antwoordopties(get_q_type())

def getvraag(driver):
    #ophalen van pagina:
    #vraagnummer
    #vraagsoort
    #aantal subvragen
    #aantal antwoorden + labels
    #escape of niet
    vraagid = get_q_id()
    vraagsoort = get_q_type()
    if vraagsoort == 'tabel':
        subvragen = get_subvragen()
    else:
        subvragen=None
    antwoorden = get_antwoordopties(vraagsoort)
    if vraagsoort == 'open':
        escape = get_open_escape()
    else:
        escape=False

    return vraag(vraagid, vraagsoort, subvragen, antwoorden, escape)

bestand = get_testfile("C:\Python projects\Survey testbot\scenarios_v2.csv")
inloggen('https://q.crowdtech.com/r5r11EDq_k6lcp_I87yPWQ',bestand[1]['login'])


v1 = getvraag(driver)
answers = lookup_qid(bestand[1], v1.vraagid)

invullen(v1, answers)

# # # # # # # # # # #  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

driver = webdriver.Firefox('C:\Python projects\Survey testbot\geckodriver')
driver.implicitly_wait(1)
bestand = get_testfile("C:\Python projects\Survey testbot\scenarios_v2.csv")

for scenario in bestand:
    inloggen('https://q.crowdtech.com/r5r11EDq_k6lcp_I87yPWQ',scenario['login'])
    vx = getvraag(driver)
    invullen(vx, lookup_qid(scenario,vx))

vx = getvraag(driver)
invullen(vx, lookup_qid(bestand[1],vx))
lookup_qid(bestand[1],vx)

for scenario in bestand:
    print(scenario)


# for schema in tests:
#     for k,v in schema.items():
#         if k.startswith('question'):
#             if len(v) == 0:
#                 count_divs = len(driver.find_elements_by_xpath("/html/body/div/div/main/form/div/div/div"))
#                 random_antwoord = random.randint(1, count_divs)
#                 vraag_antwoord(k, random_antwoord)
#             else:
#                 vraag_antwoord(k,v)
#         elif k == 'login':
#             inloggen("https://q.crowdtech.com/r5r11EDq_k6lcp_I87yPWQ",v)


v2element = driver.find_element_by_id('question-2_checkradio-answer-label-1')
v2element.click()

driver.find_elements_by_css_selector('[table=""]')
driver.find_elements_by_xpath("//form/div[@table]")
getvraag(driver)
driver.find_element_by_id("question-4_sq-1_checkradio-answer-label-1").click()
lookup_qid(bestand[0], v4)

for subvraag in range(1, v4.subvragen+1):
    driver.find_element_by_id(f"{v4.vraagid}_sq-{subvraag}_checkradio-answer-label-1").click()