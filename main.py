from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import csv
import random

#get test scenarios
with open("C:\Python projects\Survey testbot\scenarios.csv", encoding='utf-8-sig') as infile:
    csv_reader = csv.DictReader(infile, delimiter=";", )
    tests = list(csv_reader)
    print(tests)
tests[0]

driver = webdriver.Firefox('C:\Python projects\Survey testbot\geckodriver')

# driver.get("https://q.crowdtech.com/r5r11EDq_k6lcp_I87yPWQ")
# driver.implicitly_wait(10)


def inloggen(url, login):
    driver.get(url)
    driver.implicitly_wait(10)
    user = driver.find_element_by_xpath('//*[@id="login-email"]')
    user.send_keys(login)
    driver.find_element_by_id("login-button").click()

def vraag_antwoord(vraagnummer, antwoord):
    #verwacht een key:value set van een dict als input
    driver.find_element_by_id(f"{vraagnummer}_checkradio-answer-label-{antwoord}").click()
    driver.find_element_by_id("button-next-nav").click()



"""
Dit gedeelte gaat alle regels af in de csv en vult de waarde in.
Waarchijnlijk efficienter om andersom te werken en het vraagnummer op te halen uit survey
en kijken of daar een waarde voor is. Zo ja, dan invullen, zo nee dan random invullen.

"""
for schema in tests:
    for k,v in schema.items():
        if k == 'login':
            inloggen("https://q.crowdtech.com/r5r11EDq_k6lcp_I87yPWQ",v)
        if k.startswith('question'):
            if len(v) == 0:
                count_divs = len(driver.find_elements_by_xpath("/html/body/div/div/main/form/div/div/div"))
                random_antwoord = random.randint(1, count_divs)
                vraag_antwoord(k, random_antwoord)
            else:
                vraag_antwoord(k,v)


#checken vanuit survey ipv vanuit csv

def get_q_id():
    element = driver.find_element_by_xpath("//form/div")
    vraagid = element.get_attribute("id")

    return vraagid

def get_q_type():
    


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