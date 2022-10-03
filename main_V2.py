from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import random
import time
import re
from pathlib import Path

surveylink = "https://q.crowdtech.com/WKG1f3C-aEScDWnNZA_MJw"

class invulinator:
    def __init__(self, surveylink):
        #start browser
        self.browser = webdriver.Firefox()
        self.browser.get(surveylink)
    
    class vraag:
        def __init__(self) -> None:
            self.id = self.get_qid()
            self.type = self.get_qtype()

        def has_xpath(self,xpath):
            if len(self.browser.find_elements_by_xpath(xpath)) > 0:
                return True
            else:
                return False

        def get_qid(self):
            #vraagnummer achterhalen vanuit survey
            element = WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.XPATH, "//form/div")))
            vraagid = element.get_attribute("id")

            return vraagid
    



test1 = invulinator(surveylink)
test1.vraag.get_qid()