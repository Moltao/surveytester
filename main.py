from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException
#from selenium.webdriver.support import expected_conditions as EC
import csv
import random
import re
from pathlib import Path
import time
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
    driver: selenium webdriver
    vraag: vraagobject
        aangemaakt door getvraag()
    gegeven_antwoorden: tuple
        de antwoorden uit het bestand met testscenario's zoals aangemaakt door lookup_qid()
     
    Returns
    ----------
    geen return. Vinkt de juiste opties aan en klikt op volgende.

    """
    try:
        if gegeven_antwoorden[0] == 'random':
            if len(vraag.antwoorden) > 0:
                opties = list(vraag.antwoorden.keys())
                gekozen_optie = opties[random.randint(0,len(opties)-1)]
                gegeven_antwoorden = (vraag.soort, str(gekozen_optie))    
            else:
                gegeven_antwoorden = (vraag.soort, '1')

        if vraag.soort == 'tabel' and gegeven_antwoorden[0] == 'tabel':
            for subvraag in vraag.subvragen:
                antwoordoptie = gegeven_antwoorden[1][vraag.vraagid + '-' + subvraag]
                driver.find_element_by_id(f"{vraag.vraagid}_sq-{subvraag}_checkradio-answer-label-{antwoordoptie}").click()
        
        elif vraag.soort == 'invulvelden':
            for veld in range(1, vraag.velden+1):
                vraagid = vraag.vraagid + '-answer-' + str(veld)
                antwoord = gegeven_antwoorden[1][vraagid]
                inputveld = driver.find_element_by_id(f"{vraag.vraagid}_checkradio-input-answer-{veld}")
                if ("getal" in inputveld.get_attribute("placeholder") or 
                    "Nummer" in inputveld.get_attribute("placeholder") or 
                    "number" in inputveld.get_attribute("placeholder")):
                    if inputveld.get_attribute("min") != '':
                        min = int(inputveld.get_attribute("min"))
                    else:
                        min = 1
                    if inputveld.get_attribute("max") != '':
                        max = int(inputveld.get_attribute("max"))
                    else:
                        max = 99
                    randomgetal = str(random.randint(min, max))
                    antwoord = randomgetal
                else:
                    antwoord = "test@test.nl"
                
                #gegeven_antwoorden = (vraagid, antwoord)
                inputveld.send_keys(antwoord)
        
        elif vraag.soort == 'sr':
            try:
                driver.find_element_by_id(f"{vraag.vraagid}_label-{gegeven_antwoorden[1]}").click()
            except ElementClickInterceptedException:
                pass

        
        elif vraag.soort == 'mr':
            for item in gegeven_antwoorden[1]:
                # if vraag.vraagid == 'question-46' and item == '2':
                #     item = '3'
                try:    
                    driver.find_element_by_id(f'{vraag.vraagid}_checkradio-answer-label-{item}').click()
                except:
                    pass
                
        elif vraag.soort == 'open':
            inputveld = driver.find_element_by_id(f"{vraag.vraagid}_checkradio-input-answer-1")
            if "getal" in inputveld.get_attribute("placeholder"):
                if inputveld.get_attribute("min") != '':
                    min = int(inputveld.get_attribute("min"))
                else:
                    min = 1
                if inputveld.get_attribute("max") != '':
                    max = int(inputveld.get_attribute("max"))
                else:
                    max = 99
                randomgetal = str(random.randint(min, max))
                antwoord = randomgetal
            else:
                antwoord = "test@test.nl"

            inputveld.send_keys(antwoord)
            gegeven_antwoorden= (vraag.soort, antwoord)

        elif vraag.soort == 'slider':
            driver.find_element_by_id(f"{vraag.vraagid}_sq-1_checkradio-answer-label-3").click()
            
        elif vraag.soort == 'tussen':
            pass
        
        driver.find_element_by_id("button-next-nav").click()       
        print(gegeven_antwoorden)
    except (NoSuchElementException, ElementNotInteractableException) as exc:
        raise exc


def invulvelden_invullen(driver, vraag, gegeven_antwoorden):
    """ Invulveldenvraag invullen. Deze werkt anders dan de standaardvragen
        dus een aparte functie voor gemaakt.
        Vult het gegeven antwoord in en anders vult het een random antwoord in.    
    
    """
    #aantal invulvelden ophalen
    if vraag.soort == 'invulvelden':
        for veld in range(1, vraag.velden+1):
            vraagid = vraag.vraagid + '_answer' + str(veld)
            antwoord = gegeven_antwoorden[1][vraagid]
            driver.find_element_by_id(f"{vraag.vraagid}_checkradio-input-answer-{veld}").send_keys(antwoord)



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
    while True:
        try:
            element = driver.find_element_by_xpath("//form/div")
        except NoSuchElementException:
            time.sleep(3)
            continue
        break

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
    elif hasXpath(driver, '//*[@data-answer-type="Radiobutton"]'):
        vraagtype = 'sr'
    elif hasXpath(driver, '//form/div[@open]'):
        vraagtype = 'open'
    elif hasXpath(driver, '//*[@data-answer-type="Checkbox"]'):
        vraagtype = 'mr'
    elif hasXpath(driver, '//form/div[@empty]'):
        vraagtype = 'tussen'
    elif hasXpath(driver, '//form/div[@fields]'):
        vraagtype = 'invulvelden'
    elif hasXpath(driver, "//div[@data-answer='Slider']"):
        vraagtype = 'slider'
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
    subvragen: list van de elementen van de subvragen
    
    """
    if hasXpath(driver, "//form/div[@table]"):
        if hasXpath(driver, "//table[@table-matrix='']"):
            subs = driver.find_elements_by_xpath("//label[contains(@id,'checkradio-answer-label-1')]")
            subvragen = [re.search("(sq-)(\d+)", x.get_attribute("id"))[2] for x in subs]
        else:
            subs = driver.find_elements_by_css_selector('div[id^=fold]')
            subvragen = [x.get_attribute('id')[x.get_attribute('id').rindex('-')+1:] for x in subs]
        #subvragen = driver.find_elements_by_css_selector('div[id^=fold]')
    else:
        subvragen = []
    
    return subvragen

def get_velden(driver, vraagid):
    """ Aantal invulvelden ophalen van een invulveldenvraag
    
    """
    velden = len(driver.find_elements_by_css_selector(f'div[id^="{vraagid}_answer-"'))

    return velden

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
        subs = [vraag.vraagid + '-' + x for x in vraag.subvragen]
        for sub in subs:
            if sub in testdict:
                print('Vraag zit WEL in testscenario')
                gegeven_antwoord[sub] = testdict[sub]        
            else:
                print('Vraag zit niet in testscenario')
                gegeven_antwoord[sub] = str(random.randint(1, len(vraag.antwoorden)))
        antwoordnummer = ('tabel', gegeven_antwoord)
    elif vraag.soort == 'invulvelden':
        gegeven_antwoord = {}
        velden = [vraag.vraagid + '-answer-' + str(x) for x in range(1, vraag.velden + 1)]
        for veld in velden:
            if veld in testdict:
                print('Vraag zit WEL in testscenario')
                gegeven_antwoord[veld] = testdict[veld]
            else:
                print('Vraag zit niet in testscenario')
                gegeven_antwoord[veld] = 'tekst tekst tekst'
        antwoordnummer = ('invulvelden', gegeven_antwoord)  
    else:
        if vraag.vraagid in testdict:
            print('Vraag zit WEL in testscenario')
            gegeven_antwoord = testdict.get(vraag.vraagid)
            if gegeven_antwoord == '':
                antwoordnummer = ('random', '99')
            elif len(gegeven_antwoord) > 2 and gegeven_antwoord.replace(',','').isnumeric():
                #meerdere antwoorden, hoort bij MR vraag
                antwoordnummer = ('mr', list(filter(None,gegeven_antwoord.split(','))))
            elif len(gegeven_antwoord) > 1 and gegeven_antwoord.lower().islower():
                #antwoordlabel opgegeven
                antwoordnummer = ('label', gegeven_antwoord)
            else:
                antwoordnummer = ('sr', gegeven_antwoord)
        else:
            print('Vraag zit niet in testscenario')
            if len(vraag.antwoorden) > 0:
                antwoordnummer = ('random', str(random.randint(1, len(vraag.antwoorden))))
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
    antwoorden: dict met k,v = antwoornummer, label
    
    """
    antwoorden ={}

    if vraagsoort == 'tabel':
        #if hasXpath(driver, "//form/div[@table]"):  
            #pass
        #else:
        surveyantwoorden = driver.find_elements_by_xpath('//form/div/div/div[1]/div[@data-option-list=""]/div')
        for x in surveyantwoorden:                                  
            k = x.find_element_by_xpath('.//input').get_attribute('id')
            k = k[k.rindex('-')+1:]
            v = x.find_element_by_xpath('.//input').get_attribute('value')
            antwoorden[k]=v
    elif vraagsoort == 'open':
        antwoorden = {}
    elif vraagsoort == 'tussen':
        antwoorden = {}
    elif vraagsoort == 'invulvelden':
        surveyantwoorden = driver.find_elements_by_css_selector('div[id^="question-1_answer-"')
        for x in surveyantwoorden:
            k = x.find_element_by_css_selector('label').get_attribute('id')
            k = k[k.rindex('-')+1:]
            v = x.find_element_by_css_selector('label span[data-label=""]').text
            antwoorden[k]=v
    else:
        surveyantwoorden = driver.find_elements_by_xpath('//*[@data-answer=""]')
        for x in surveyantwoorden:                                  
            k = x.find_element_by_xpath('.//label').get_attribute('id')
            k = k[k.rindex('-')+1:]
            v = x.find_element_by_xpath('.//label/span').text
            antwoorden[k]=v

    return antwoorden

def get_open_escape(driver, vraagsoort):
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
    if vraagsoort =='open':
        if hasXpath(driver, '//div[@data-outerfield="true"]'):
            escape = True
        else:
            escape = False
    else:
        escape = False

    return escape    

#get_antwoordopties(get_q_type())

class vraag:

    def __init__(self, vraagid, soort, subvragen=None, velden=None ,antwoorden=None, escape=False) -> None:
        self.vraagid = vraagid
        self.soort = soort
        self.antwoorden = antwoorden
        self.subvragen = subvragen
        self.velden = velden
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
        subvragen = 0

    antwoorden = get_antwoordopties(driver, vraagsoort)

    if vraagsoort == 'invulvelden':
        velden = get_velden(driver, vraagid)
    else:
        velden = 0

    if vraagsoort == 'open':
        escape = get_open_escape(driver, vraagsoort)
    else:
        escape = False

    return vraag(vraagid, vraagsoort, subvragen, velden, antwoorden, escape)


#-----------------------------------------------------------------------#
# runnen van het script                                                 #
#-----------------------------------------------------------------------#

driver = webdriver.Firefox('C:\Python projects\surveytester\geckodriver')
driver.implicitly_wait(1)
bestand = get_testfile(r"C:\Thuiswerken\SK123\NSE2022\Invulinator\NSE2022 Input InvulBot - invullinator test3 csv - server1.csv")
counter = 0

for scenario in bestand:
    counter += 1
    if counter < 223 :
         continue
    print('login ' + str(counter))
    #inloggen(driver, 'https://q.crowdtech.com/WKG1f3C-aEScDWnNZA_MJw',scenario['Login'])
    driver.get(scenario['Loginlinks'])
    endpage = hasXpath(driver, 'html/body/div/div[@endpage=""]')
    while endpage == False:
        vx = getvraag(driver)
        antwoord = lookup_qid(scenario,vx)
        print(vx.vraagid + ' ' + str(antwoord))
        try:
            invullen(driver, vx, antwoord)
            endpage = hasXpath(driver, 'html/body/div/div[@endpage=""]')
        except (NoSuchElementException, ElementNotInteractableException) as exc:
            with open('C:\Python projects\surveytester\errors_nse_test3.log', 'a') as log:
                log.write(f"Login {counter} --- {scenario['Loginlinks']} --- antwoordoptie {antwoord} voor {vx.vraagid} niet gevonden \n")

            endpage = True
            
        
# # bestand = get_testfile(r"C:\Python projects\Survey testbot\data\[oud]\testnocases.csv")
# # inloggen(driver, 'https://q.crowdtech.com/r5r11EDq_k6lcp_I87yPWQ',bestand[0]['Login'])

# driver.get("https://q.crowdtech.com/GkBIPyYOsUerI9Ro732l7Q")
# vx = getvraag(driver)
# vx.soort
# # inputveld = driver.find_element_by_id(f"{vx.vraagid}_checkradio-input-answer-1")
# # inputveld.get_attribute("min")
# # get_antwoordopties(driver, vx.soort)
# # antwoorden = lookup_qid(bestand[51], vx)
# # invullen(driver, vx, antwoorden)

# elements = driver.find_elements_by_xpath("//form/div")
# for x in elements:
#     print(x.get_attribute('id'))