from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import csv

#get test scenarios
with open("C:\Python projects\Survey testbot\scenarios.csv", encoding='utf-8-sig') as infile:
    csv_reader = csv.DictReader(infile, delimiter=";", )
    tests = list(csv_reader)
    print(tests)


driver = webdriver.Firefox('C:\Python projects\Survey testbot\geckodriver')

driver.get("https://q.crowdtech.com/r5r11EDq_k6lcp_I87yPWQ")
driver.implicitly_wait(10)


user = driver.find_element_by_xpath('//*[@id="login-email"]')
user.send_keys(tests[0]['login'])

login = driver.find_element_by_id("login-button").click()

antwoord = f"question-1_checkradio-answer-label-{tests[0]['V1']}"
driver.find_element_by_id(f"question-1_checkradio-answer-label-{tests[0]['V1']}").click()
driver.find_element_by_id("button-next-nav").click()
driver.find_element_by_id("question-2_checkradio-answer-label-4").click()


print(driver.title)