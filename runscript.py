
# bestand = get_testfile("C:\Python projects\Survey testbot\scenarios_v2.csv")
# inloggen('https://q.crowdtech.com/r5r11EDq_k6lcp_I87yPWQ',bestand[1]['login'])


# v1 = getvraag(driver)
# answers = lookup_qid(bestand[1], v1.vraagid)

# invullen(v1, answers)

# # # # # # # # # # #  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 



driver = webdriver.Firefox('C:\Python projects\Survey testbot\geckodriver')
driver.implicitly_wait(0)
bestand = get_testfile("C:\Python projects\Survey testbot\\test_nse.csv")


#inloggen('http://q.crowdtech.com/NfxaNcf1pUCwUct7X-SlMA',bestand[0]['login'])


for scenario in bestand:
    inloggen(driver, 'http://q.crowdtech.com/NfxaNcf1pUCwUct7X-SlMA',scenario['login'])
    endpage = hasXpath(driver, 'html/body/div/div[@endpage=""]')
    while endpage == False:
        vx = getvraag(driver)
        invullen(driver, vx, lookup_qid(scenario,vx))
        endpage = hasXpath(driver, 'html/body/div/div[@endpage=""]')


vx = getvraag(driver)
invullen(vx, lookup_qid(bestand[1],vx))
# lookup_qid(bestand[1],vx)

hasXpath('html/body/div/div[@endpage=""]')

#taal instellen
driver.find_element_by_id("language-switcher-dropdown").click()
testdict = {el.text: el for el in driver.find_elements_by_xpath('//ul[@role="listbox"]/li')}
driver.find_element_by_id("button-save").click()

# for scenario in bestand:
#     print(scenario)


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