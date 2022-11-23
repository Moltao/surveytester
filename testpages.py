import csv
import random
import time
import re


from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager



driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
driver.get("https://q.crowdtech.com/b43b0207-a2f7-428d-ba95-38044cf73c01/84faebe7-3beb-4cbe-b8cd-52fd0a048d6d?alin=ja")

##slicer
slicer = driver.find_element(By.ID,'question-8_sq-1_slider-1')
slicer