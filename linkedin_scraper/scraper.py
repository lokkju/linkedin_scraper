#!/usr/bin/python3

import requests
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import os

from .person import Person
from .objects import Scraper as BaseScraper

LINKEDIN_BASE_URL = "https://www.linkedin.com/"
LINKEDIN_EMAIL_BASE_URL = "https://www.linkedin.com/sales/gmail/profile/viewByEmail/"

class AuthenticationRequiredException(Exception):
    """This functionality requires authentication"""
class ProfileNotFoundException(Exception):
    """A profile could not be found for the provided identifier"""

class Scraper(BaseScraper):
    def __init__(self,driver=None):
        if driver is None:
            try:
                if os.getenv("CHROMEDRIVER") == None:
                    driver_path = os.path.join(os.path.dirname(__file__), 'drivers/chromedriver')
                else:
                    driver_path = os.getenv("CHROMEDRIVER")

                driver = webdriver.Chrome(driver_path)
            except:
                driver = webdriver.Chrome()
        self.driver = driver

    def person(self,id):
        if "@" in id:
            id = self.__findIdForEmail(id)
        elif "http" not in id:
            id = LINKEDIN_BASE_URL + "in/" + id
        p = Person(id, driver=self.driver, scrape=False)
        p.scrape(False)

    def is_signed_in(self):
        try:
            self.driver.find_element_by_id("profile-nav-item")
            return True
        except:
            pass
        return False

    def __find_element_by_class_name__(self, class_name):
        try:
            self.driver.find_element_by_class_name(class_name)
            return True
        except:
            pass
        return False

    def __findIdForEmail(self,email):
        if not self.is_signed_in():
            raise AuthenticationRequiredException()
        self.driver.get(LINKEDIN_EMAIL_BASE_URL + email)
        self.driver.find_element_by_id("login-email")

    def close(self):
        self.driver.close()

    def signin(self,email=None,password=None):
        wait = WebDriverWait(self.driver, 60)
        self.driver.get(LINKEDIN_BASE_URL)
        if self.is_signed_in():
            return
        if email is not None and password is not None:
            uf = self.driver.find_element_by_id("login-email")
            pf = self.driver.find_element_by_id("login-password")
            uf.send_keys(email)
            pf.send_keys(password)
            self.driver.find_element_by_id("login-submit").click()
        else:
            self.driver.execute_script("window.alert('Please sign into LinkedIn');")
            wait.until(EC.alert_is_present())
            wait.until_not(EC.alert_is_present())
        wait.until(EC.presence_of_element_located((By.ID, "profile-nav-item")))
