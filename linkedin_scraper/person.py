import requests
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .functions import time_divide
from .objects import Experience, Education, Scraper
import os
import re
import logging
logger = logging.getLogger(__name__)

class Person(Scraper):
    name = None
    experiences = []
    educations = []
    contact_info = []
    also_viewed_urls = []
    linkedin_url = None
    photo_url = None

    def __init__(self, linkedin_url = None, name = None, experiences = [], educations = [], contact_info = [], photo_url = None, driver = None, get = True, scrape = True):
        self.linkedin_url = linkedin_url
        self.name = name
        self.photo_url = photo_url
        self.experiences = experiences
        self.educations = educations
        self.contact_info = contact_info

        if driver is None:
            try:
                if os.getenv("CHROMEDRIVER") == None:
                    driver_path = os.path.join(os.path.dirname(__file__), 'drivers/chromedriver')
                else:
                    driver_path = os.getenv("CHROMEDRIVER")

                driver = webdriver.Chrome(driver_path)
            except:
                driver = webdriver.Chrome()

        if get:
            driver.get(linkedin_url)

        self.driver = driver

        if scrape:
            self.scrape()


    def add_experience(self, experience):
        self.experiences.append(experience)

    def add_education(self, education):
        self.educations.append(education)

    def add_contact_info(self, ci):
        self.contact_info.append(ci)

    def scrape(self, close_on_complete = True):
        if self.is_signed_in():
            self.scrape_logged_in(close_on_complete = close_on_complete)
        else:
            self.scrape_not_logged_in(close_on_complete = close_on_complete)

    def scrape_logged_in(self, close_on_complete = True):
        driver = self.driver
        self.name = driver.find_element_by_class_name("pv-top-card-section__name").text
        self.location = driver.find_element_by_class_name("pv-top-card-section__location").text
        self.photo_url = re.findall(r"url\(\"(.*?)\"\)", driver.find_element_by_class_name("pv-top-card-section__photo").get_attribute("style"))

        # get contact info
        try:
            driver.find_element_by_class_name("contact-see-more-less").click()
            _ = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "pv-profile-section__section-info")))
            for info in driver.find_elements_by_class_name("pv-contact-info__contact-type"):
                info_type = re.findall(r"ci-(\w+)",info.get_attribute("class"))
                for d in info.find_elements_by_class_name("pv-contact-info__contact-link"):
                    self.contact_info.append({'info_type': info_type, 'text': d.text, 'link': d.get_attribute("href")})
                for d in info.find_elements_by_class_name("pv-contact-info__contact-item"):
                    self.contact_info.append({'info_type': info_type, 'text': d.text, 'link': None})

        except TimeoutException:
            logger.warn("no contact info section found for %s", self.linkedin_url)


        # get experience
        driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));")
        try:
            _ = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "experience-section")))
            exp = driver.find_element_by_id("experience-section")
            for position in exp.find_elements_by_class_name("pv-position-entity"):
                position_title = position.find_element_by_tag_name("h3").text
                company = position.find_element_by_class_name("pv-entity__secondary-title").text

                try:
                    times = position.find_element_by_class_name("pv-entity__date-range").text
                    from_date, to_date, duration = time_divide(times)
                except:
                    from_date, to_date = (None, None)
                experience = Experience( position_title = position_title , from_date = from_date , to_date = to_date)
                experience.institution_name = company
                self.add_experience(experience)
        except TimeoutException:
            logger.warn("no experience section found for %s", self.linkedin_url)


        # get education
        driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight/1.5));")
        try:
            _ = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "education-section")))
            edu = driver.find_element_by_id("education-section")
            for school in edu.find_elements_by_class_name("pv-profile-section__sortable-item"):
                try:
                    university = school.find_element_by_class_name("pv-entity__school-name").text
                except:
                    university = None
                try:
                    degree = school.find_element_by_class_name("pv-entity__degree-name").text
                except:
                    degree = None
                try:
                    times = school.find_element_by_class_name("pv-entity__dates").text
                    from_date, to_date, duration = time_divide(times)
                except:
                    from_date, to_date = (None, None)
                education = Education(from_date = from_date, to_date = to_date, degree=degree)
                education.institution_name = university
                self.add_education(education)
        except TimeoutException:
            logger.warn("no education section found for %s", self.linkedin_url)

        if close_on_complete:
            driver.close()


    def scrape_not_logged_in(self, close_on_complete=True, retry_limit = 10):
        driver = self.driver
        retry_times = 0
        while self.is_signed_in() and retry_times <= retry_limit:
            page = driver.get(self.linkedin_url)
            retry_times = retry_times + 1


        # get name
        self.name = driver.find_element_by_id("name").text

        # get experience
        exp = driver.find_element_by_id("experience")
        for position in exp.find_elements_by_class_name("position"):
            position_title = position.find_element_by_class_name("item-title").text
            company = position.find_element_by_class_name("item-subtitle").text

            try:
                times = position.find_element_by_class_name("date-range").text
                from_date, to_date, duration = time_divide(times)
            except:
                from_date, to_date = (None, None)
            experience = Experience( position_title = position_title , from_date = from_date , to_date = to_date)
            experience.institution_name = company
            self.add_experience(experience)

        # get education
        edu = driver.find_element_by_id("education")
        for school in edu.find_elements_by_class_name("school"):
            university = school.find_element_by_class_name("item-title").text
            degree = school.find_element_by_class_name("original").text
            try:
                times = school.find_element_by_class_name("date-range").text
                from_date, to_date, duration = time_divide(times)
            except:
                from_date, to_date = (None, None)
            education = Education(from_date = from_date, to_date = to_date, degree=degree)
            education.institution_name = university
            self.add_education(education)

        # get
        if close_on_complete:
            driver.close()

    def __repr__(self):
        return "{name}\n\nExperience\n{exp}\n\nEducation\n{edu}".format(name = self.name, exp = self.experiences, edu = self.educations)
