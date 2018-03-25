from linkedin_scraper import Scraper
from ConfigParser import SafeConfigParser
import logging
logging.basicConfig()


config = SafeConfigParser()
config.read('linkedin_parser.ini')

LOGIN_EMAIL = config.get('main', 'login_email')
LOGIN_PASSWORD = config.get('main', 'login_password')

scraper = Scraper()
scraper.signin(LOGIN_EMAIL,LOGIN_PASSWORD)
scraper.person("lokkju")
scraper.close()
