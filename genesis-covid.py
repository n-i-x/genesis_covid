#! /usr/bin/python3

import json
import requests
import sys

from bs4 import BeautifulSoup

# CREDS_FILE should be a json dict of usernames as keys and passwords as values
CREDS_FILE = '/etc/genesis_creds'

BASE_URL = 'https://parents.freeholdtwp.k12.nj.us'
FORM_SUBMIT = BASE_URL + '/genesis/parents?tab1=studentdata&tab2=forms&tab3=fill&studentid=%s&formId=%s&action=saveAnswers'
LOGIN_URL = BASE_URL + '/genesis/sis/j_security_check'

COVID_FORM_ID = '365FB95D163E421C96C70E565219D523'

USER_AGENT = 'Mozilla/5.0 (X11; CrOS x86_64 13597.94.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.186 Safari/537.36'


class Genesis(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.students = []

        self.session = requests.Session()
        self.session.headers['User-Agent'] = USER_AGENT

        self.login() 
    
    def login(self):
        payload = {'j_username': self.username, 'j_password': self.password}
        r = self.session.post(LOGIN_URL, data=payload)

        soup = BeautifulSoup(r.content, 'html.parser')
        self.students = [x['value'] for x in soup.find(id="fldStudent").findAll("option")]
    
    def submit_covid_forms(self):
        payload = {
            'fldFinalize': 'YES',
            'fldQuestion_48159F9B94B2409BAF899C57039D3759_C3E2410FA55F43CA84D9FA6426910A93': 'FB37C80E5F4D46E9A87FD15AC2798C60',
            'fldQuestion_E89A1899D0524EE6BB599DCC77961A94_A9B60E30C87740548A8459B6C70E8833': 'CFFB99C9FB074BC29C1A8ECA6A35203F'
        }
        for student in self.students:
            r = self.session.post(FORM_SUBMIT % (student, COVID_FORM_ID), data=payload)

def main(creds_file):
    with open(creds_file) as f:
        creds = json.load(f)
    
    for username, password in creds.items():
        g = Genesis(username, password)
        #print(g.students)
        g.submit_covid_forms()

if __name__ == '__main__':
    creds_file = CREDS_FILE
    if len(sys.argv) > 1:
        creds_file = sys.argv[1]

    main(creds_file)