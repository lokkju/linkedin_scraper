from linkedin_scraper import Scraper
from linkedin_scraper.scraper import ProfileNotFoundException
from ConfigParser import SafeConfigParser
import logging
import os
import json
from tqdm import tqdm
logging.basicConfig()

logger = logging.getLogger(__name__)

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

config = SafeConfigParser()
config.read(os.path.join(SCRIPT_DIR,'cli.ini'))

LOGIN_EMAIL = config.get('main', 'login_email')
LOGIN_PASSWORD = config.get('main', 'login_password')


scraper = Scraper()
scraper.signin(LOGIN_EMAIL,LOGIN_PASSWORD)
with open("/home/lokkju/Downloads/con_emails.txt") as f:
    for line in tqdm(f):
        try:
            email = line.strip()
            logger.info("fetching: %s", email)
            p = scraper.person(email)
            p.email = email
            p.status = 'found'
            print json.dumps(p)
        except ProfileNotFoundException:
            print json.dumps({'email': email, 'status': 'not_found'})

scraper.close()
