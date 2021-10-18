from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import random
from pathlib import Path
#from .Vraagclass import vraag

# driver = webdriver.Firefox('C:\Python projects\Survey testbot\geckodriver')
# testfile =  Path("C:\Python projects\Survey testbot\scenarios.csv")


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
       

def inloggen(driver, url, login):
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


def invullen(driver, vraag, gegeven_antwoorden):
    """Vult de vraag in bij survey. Tikt de opties aan en klikt op volgende.

    Parameters
    ----------
    vraag: vraagobject
        aangemaakt door getvraag()
    gegeven_antwoorden: tuple
        de antwoorden uit het bestand met testscenario's zoals aangemaakt door lookup_qid()
     
    Returns
    ----------
    geen return. Vinkt de juiste opties aan en klikt op volgende.

    """
    
    if vraag.soort == 'tabel' and gegeven_antwoorden[0] == 'tabel':
        for subvraag in range(1, vraag.subvragen+1):
            #vraag.vraagid = vraag.vraagid + '-' + subvraag
            antwoordoptie = gegeven_antwoorden[1][vraag.vraagid + '-' + str(subvraag)]
            driver.find_element_by_id(f"{vraag.vraagid}_sq-{subvraag}_checkradio-answer-label-{antwoordoptie}").click()
    elif vraag.soort == 'sr' and gegeven_antwoorden[0] == 'sr':
        driver.find_element_by_id(f"{vraag.vraagid}_checkradio-answer-label-{gegeven_antwoorden[1]}").click()
    elif vraag.soort == 'mr' and gegeven_antwoorden[0] == 'mr':
        for item in gegeven_antwoorden[1]:
            driver.find_element_by_id(f'{vraag.vraagid}_checkradio-answer-label-{item}').click()
    elif vraag.soort == 'open':
        driver.find_element_by_id(f"{vraag.vraagid}_checkradio-input-answer-1").send_keys("test test test")
    elif vraag.soort == 'tussen':
        pass

    driver.find_element_by_id("button-next-nav").click()

def get_q_id(driver):
    """Haalt het id van de vraag op uit survey
    
    Parameters
    ----------
    driver: selenium webdriver

    Returns
    ----------
    vraagid: str. met 'question-1' format van vraagid
    
    """
    #vraagnummer achterhalen vanuit survey
    element = driver.find_element_by_xpath("//form/div")
    vraagid = element.get_attribute("id")

    return vraagid

def hasXpath(driver, xpath):
    """Conrtoleert of een xpath element bestaat. Geeft een lijst van alle gevonden elementen. 
        Als er geen elementen zijn is de lijst 0 items.
    
    Parameters
    ----------
    xpath: str met xpath erin

    Returns
    ----------
    True als lijst met elementen groter is dan 0
    False als lijst met elementen 0 is
    
    """
    if len(driver.find_elements_by_xpath(xpath)) > 0:
        return True
    else:
        return False


def get_q_type(driver):
    """Haalt het vraagtype op van de getoonde vraag in Survey
    
    Parameters
    ----------
    driver: selenium webdriver

    Returns
    ----------
    vraagtype: str. met vraagtype
    
    """
    #vraagtype achterhalen
    if hasXpath(driver, '//form/div[@table]'):
        vraagtype = 'tabel'
    elif hasXpath(driver, '//form/div[@open]'):
        vraagtype = 'open'
    elif hasXpath(driver, '//form/div/div/div[1][@data-answer-type="Checkbox"]'):
        vraagtype = 'mr'
    elif hasXpath(driver, '//form/div/div/div[1][@data-answer-type="Radiobutton"]'):
        vraagtype = 'sr'
    elif hasXpath(driver, '//form/div[@empty]'):
        vraagtype = 'tussen'
    else:
        vraagtype = 'unknown'
    
    return vraagtype

def get_subvragen(driver):
    """Kijkt hoeveel subvragen er zijn bij een tabelvraag
    
    Parameters
    ----------
    driver: selenium webdriver

    Returns
    ----------
    subvragen: int of None
    
    """
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
        als tabelvraag: tuple (str, dict)
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

def get_antwoordopties(driver, vraagsoort):
    """Antwoordlabels achterhalen uit survey. Dit zijn de teksten van de antwoordopties zoals
    "Helemaal mee eens".
    
    Parameters
    ----------
    driver: selenium webdriver
    vraagsoort: str van vraagobject.

    Returns
    ----------
    antwoorden: dict met k,v = vraagnummer, label
    
    """
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
    elif vraagsoort == 'tussen':
        antwoorden = None
    else:
        surveyantwoorden = driver.find_elements_by_xpath('//form/div/div/div[@data-answer=""]')
        for x in surveyantwoorden:                                  
            k = x.find_element_by_xpath('.//input').get_attribute('id')
            k = k[k.rindex('-')+1:]
            v = x.find_element_by_xpath('.//input').get_attribute('value')
            antwoorden[k]=v

    return antwoorden

def get_open_escape(driver, vraag):
    """ Kijkt of er een escape optie is voor een open vraag zodat 
        deze aangevinkt kan worden als dat gewenst is
    
    Parameters
    ----------
    driver: selenium webdriver
    vraag:  vraagobject

    Returns
    ----------
    escape: bool. True als de escape er is, False als deze er niet is of als de vraag geen open vraag is.
    
    """
    if vraag.soort =='open':
        if hasXpath(driver, '//div[@data-outerfield="true"]'):
            escape = True
        else:
            escape = False
    else:
        escape = False

    return escape    

#get_antwoordopties(get_q_type())

class vraag:

    def __init__(self, vraagid, soort, subvragen=None, antwoorden=None, escape=False) -> None:
        self.vraagid = vraagid
        self.soort = soort
        self.antwoorden = antwoorden
        self.subvragen = subvragen
        self.escape = escape

    def __str__(self) -> str:
        if self.soort == "open":
            metzonder = 'met' if self.escape else 'zonder'
            return f"open vraag {metzonder} escape"
        elif self.soort == "tabel":
            return f"tabelvraag met {self.subvragen} subvragen"
        else:
            return f"{self.soort} vraag met {len(self.antwoorden)} antwoorden"


def getvraag(driver):
    """ Haalt alle belangrijke vraaggegevens op uit Survey. Dit zijn
        vraagnummer, vraagsoort, aantal subvragen, aantal antwoorden + labels, escape aanwezig of niet
        bij open antwoord.
    
    Parameters
    ----------
    driver = selenium webdriver

    Returns
    ----------
    vraag: vraagobject
    
    """
    vraagid = get_q_id(driver)
    vraagsoort = get_q_type(driver)
    if vraagsoort == 'tabel':
        subvragen = get_subvragen(driver)
    else:
        subvragen=None
    antwoorden = get_antwoordopties(driver, vraagsoort)
    if vraagsoort == 'open':
        escape = get_open_escape(driver)
    else:
        escape=False

    return vraag(vraagid, vraagsoort, subvragen, antwoorden, escape)


