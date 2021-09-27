from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Firefox('./geckodriver')

driver.get("https://q.crowdtech.com/r5r11EDq_k6lcp_I87yPWQ")
driver.implicitly_wait(10)


user = driver.find_element_by_xpath('//*[@id="login-email"]')
user.send_keys("test4@mwm2.nl")

login = driver.find_element_by_id("login-button").click()

driver.find_element_by_id("question-1_checkradio-answer-label-1").click()
driver.find_element_by_id("button-next-nav").click()
driver.find_element_by_id("question-2_checkradio-answer-label-4").click()


print(driver.title)