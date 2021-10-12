from selenium import webdriver
from selenium.webdriver.common.keys import Keys
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
    driver.implicitly_wait(0)
    user = driver.find_element_by_xpath('//*[@id="login-email"]')
    user.send_keys(login)
    driver.find_element_by_id("login-button").click()


def vraag_antwoord(vraagnummer, antwoord):
    #verwacht een key:value set van een dict als input
    #voert vraag in en klikt op volgende
    driver.find_element_by_id(f"{vraagnummer}_checkradio-answer-label-{antwoord}").click()
    driver.find_element_by_id("button-next-nav").click()


def get_q_id():
    #vraagnummer achterhalen vanuit survey
    element = driver.find_element_by_xpath("//form/div")
    vraagid = element.get_attribute("id")

    return vraagid

def hasXpath(xpath):

        if len (driver.find_elements_by_xpath(xpath)) > 0:
            return True
        else:
            return False


def get_q_type():
    #vraagtype achterhalen
    if hasXpath("//form/div[@table]"):
        vraagtype = 'tabel'
        subvragen = len(driver.find_elements_by_xpath("/html/body/div/div/main/form/div/div/div"))
    elif hasXpath("//form/div[@open]"):
        vraagtype = 'open'
    elif hasXpath('//form/div/div/div[1][@data-answer-type="Checkbox"]'):
        vraagtype = 'mr'
    elif hasXpath('//form/div/div/div[1][@data-answer-type="Radiobutton"]'):
        vraagtype = 'sr'

    if vraagtype == 'tabel':
        return (vraagtype, subvragen)
    else:
        return vraagtype

def lookup_qid(testdict, vraagid):
    if vraagid in testdict:
        antwoord = testdict.get(vraagid)
        if antwoord == '':
            return 'geen waarde gegeven!'
        elif len(antwoord) == 1 and antwoord.isnumeric():
            antwoordnummer = ('sr', antwoord)
        elif len(antwoord) > 1 and antwoord.replace(',','').isnumeric():
            #meerdere antwoorden, hoort bij MR vraag
            antwoordnummer = ('mr', antwoord.split(','))
        elif len(antwoord) > 1 and antwoord.lower().islower():
            #antwoordlabel opgegeven
            antwoordnummer = ('label', antwoord)
    else:
        antwoordnummer = ('random', '1')

    return antwoordnummer



def getvraag(driver):
    #ophalen van pagina:
    #vraagnummer
    #vraagsoort
    #aantal antwoorden + labels
    #aantal subvragen
    #escape of niet
    vraagnummer = get_q_id()
    vraagsoort = get_q_type()

    return vraag(vraagnummer, vraagsoort)


    










#get test scenarios
with open("C:\Python projects\Survey testbot\scenarios.csv", encoding='utf-8-sig') as infile:
    csv_reader = csv.DictReader(infile, delimiter=";", )
    tests = list(csv_reader)
    print(tests)
tests[0]



# driver.get("https://q.crowdtech.com/r5r11EDq_k6lcp_I87yPWQ")
# driver.implicitly_wait(10)


"""
Dit gedeelte gaat alle regels af in de csv en vult de waarde in.
Waarchijnlijk efficienter om andersom te werken en het vraagnummer op te halen uit survey
en kijken of daar een waarde voor is. Zo ja, dan invullen, zo nee dan random invullen.

"""
for schema in tests:
    for k,v in schema.items():
        if k.startswith('question'):
            if len(v) == 0:
                count_divs = len(driver.find_elements_by_xpath("/html/body/div/div/main/form/div/div/div"))
                random_antwoord = random.randint(1, count_divs)
                vraag_antwoord(k, random_antwoord)
            else:
                vraag_antwoord(k,v)
        elif k == 'login':
            inloggen("https://q.crowdtech.com/r5r11EDq_k6lcp_I87yPWQ",v)


#checken vanuit survey ipv vanuit csv




"""
    antwoord = f"question-1_checkradio-answer-label-{tests[0]['V1']}"
    driver.find_element_by_id(f"question-1_checkradio-answer-label-{tests[0]['V1']}").click()
    driver.find_element_by_id("button-next-nav").click()
    driver.find_element_by_id("question-2_checkradio-answer-label-4").click()
    driver.find_element_by_id("button-next-nav").click()

    driver.find_element_by_id("question-28_sq-1_checkradio-answer-label-1").click()
    driver.find_element_by_id("question-28_sq-2_checkradio-answer-label-1").click()
    driver.find_element_by_id("question-28_sq-3_checkradio-answer-label-5").click()
    driver.find_element_by_id("button-next-nav").click()

    print(driver.title) 

"""

count_of_divs = len(driver.find_elements_by_xpath("/html/body/div/div/main/form/div/div/div"))
count_of_divs