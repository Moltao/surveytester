from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import csv

#get test scenarios
with open("C:\Python projects\Survey testbot\scenarios.csv", encoding='utf-8-sig') as infile:
    csv_reader = csv.DictReader(infile, delimiter=";", )
    tests = list(csv_reader)
    print(tests)
tests[0]

driver = webdriver.Firefox('C:\Python projects\Survey testbot\geckodriver')

driver.get("https://q.crowdtech.com/r5r11EDq_k6lcp_I87yPWQ")
driver.implicitly_wait(10)


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

for schema in tests:
    for k,v in schema.items():
        if k == 'login':
            inloggen("https://q.crowdtech.com/r5r11EDq_k6lcp_I87yPWQ",v)
        if k.startswith('question'):
            vraag_antwoord(k,v)
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

count_of_divs = len(driver.find_elements_by_xpath("/html/body/div/div/main/form/div/div/div"))
count_of_divs


print(driver.title) """