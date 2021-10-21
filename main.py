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
    if gegeven_antwoorden[0] == 'random':
        if len(vraag.antwoorden) > 0:
            gegeven_antwoorden = (vraag.soort, str(random.randint(1, len(vraag.antwoorden))))
        else:
            gegeven_antwoorden = (vraag.soort, '1')

    if vraag.soort == 'tabel' and gegeven_antwoorden[0] == 'tabel':
        for subvraag in vraag.subvragen:
            antwoordoptie = gegeven_antwoorden[1][vraag.vraagid + '-' + subvraag]
            driver.find_element_by_id(f"{vraag.vraagid}_sq-{subvraag}_checkradio-answer-label-{antwoordoptie}").click()
    
    elif vraag.soort == 'invulvelden' and gegeven_antwoorden[0] == 'invulvelden':
        for veld in range(1, vraag.velden+1):
            vraagid = vraag.vraagid + '-answer-' + str(veld)
            antwoord = gegeven_antwoorden[1][vraagid]
            driver.find_element_by_id(f"{vraag.vraagid}_checkradio-input-answer-{veld}").send_keys(antwoord)
    
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

def invulvelden_invullen(driver, vraag, gegeven_antwoorden):
    """ Invulveldenvraag invullen. Deze werkt anders dan de standaardvragen
        dus een aparte functie voor gemaakt.
        Vult het gegeven antwoord in en anders vult het een random antwoord in.    
    
    """
    #aantal invulvelden ophalen
    if vraag.soort == 'invulvelden' and gegeven_antwoorden[0] == 'invulvelden':
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
    elif hasXpath(driver, '//form/div/div/div[1][@data-answer-type="Radiobutton"]'):
        vraagtype = 'sr'
    elif hasXpath(driver, '//form/div[@open]'):
        vraagtype = 'open'
    elif hasXpath(driver, '//form/div/div/div[1][@data-answer-type="Checkbox"]'):
        vraagtype = 'mr'
    elif hasXpath(driver, '//form/div[@empty]'):
        vraagtype = 'tussen'
    elif hasXpath(driver, '//form/div[@fields]'):
        vraagtype = 'invulvelden'
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
                gegeven_antwoord[sub] = testdict[sub]        
            else:
                gegeven_antwoord[sub] = str(random.randint(1, len(vraag.antwoorden)))
        antwoordnummer = ('tabel', gegeven_antwoord)
    elif vraag.soort == 'invulvelden':
        gegeven_antwoord = {}
        velden = [vraag.vraagid + '-answer-' + str(x) for x in range(1, vraag.velden + 1)]
        for veld in velden:
            if veld in testdict:
                gegeven_antwoord[veld] = testdict[veld]
            else:
                gegeven_antwoord[veld] = 'tekst tekst tekst'
        antwoordnummer = ('invulvelden', gegeven_antwoord)  
    else:
        if vraag.vraagid in testdict:
            gegeven_antwoord = testdict.get(vraag.vraagid)
            if gegeven_antwoord == '':
                antwoordnummer = ('random', '1')
            elif len(gegeven_antwoord) < 3 and gegeven_antwoord.isnumeric():
                antwoordnummer = ('sr', gegeven_antwoord)
            elif len(gegeven_antwoord) > 2 and gegeven_antwoord.replace(',','').isnumeric():
                #meerdere antwoorden, hoort bij MR vraag
                antwoordnummer = ('mr', list(filter(None,gegeven_antwoord.split(','))))
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
    antwoorden: dict met k,v = antwoornummer, label
    
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
        surveyantwoorden = driver.find_elements_by_xpath('//form/div/div/div[@data-answer=""]')
        for x in surveyantwoorden:                                  
            k = x.find_element_by_xpath('.//input').get_attribute('id')
            k = k[k.rindex('-')+1:]
            v = x.find_element_by_xpath('.//input').get_attribute('value')
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


driver = webdriver.Firefox('C:\Python projects\Survey testbot\geckodriver')
driver.implicitly_wait(1)
bestand = get_testfile(r"C:\Python projects\Survey testbot\data\NSE2022 testscenarios v0.2_sample5.csv")
bestand

for scenario in bestand:
    #inloggen(driver, 'https://q.crowdtech.com/r5r11EDq_k6lcp_I87yPWQ',scenario['login'])
    driver.get(scenario['Loginlinks'])
    endpage = hasXpath(driver, 'html/body/div/div[@endpage=""]')
    while endpage == False:
        #start_time = time.time()
        vx = getvraag(driver)
        antwoord = lookup_qid(scenario,vx)
        # print(vx.vraagid)
        # print("Process finished --- %s seconds ---" % (time.time() - start_time))
        print(vx.vraagid + ' ' + str(antwoord))
        invullen(driver, vx, antwoord)
        endpage = hasXpath(driver, 'html/body/div/div[@endpage=""]')


# inloggen(driver, 'https://q.crowdtech.com/r5r11EDq_k6lcp_I87yPWQ',scenario['login'])
driver.get(bestand[0]['Loginlinks'])
vx = getvraag(driver)
get_subvragen(driver)
vx.antwoorden
vx.vraagid
vx.subvragen
antwoorden = lookup_qid(bestand[0], vx)
antwoorden
invullen(driver, vx, antwoorden)



