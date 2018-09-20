#!/usr/local/bin/python3

'''
Script to automatically log in to Telstra Air network. It opens Safari web
browser, fills the login form, clicks 'log in' and closes the browser when
all is done.

Arguments
- username
- password
'''

from argparse import ArgumentParser
from subprocess import getoutput
import re
from time import sleep
from threading import Thread
from urllib.request import urlopen
from urllib.error import URLError

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

'''
We need to kill
'/System/Library/CoreServices/Captive Network Assistant.app/Contents/MacOS/Captive Network Assistant'
(this pop-up window that appears on top of other windows every time when
you're connected to the network that you need to log in)as it blocks all
the network traffic (and is annoying).

Arguments:
- how_often - period in seconds between every kill execution
'''
def captive_portal_killer(how_often = 1):

    while True:
        getoutput('pkill "Captive Network Assistant"')
        sleep(how_often)


'''
Returns True if network connection is established.
'''
def connected_to_network():
    try:
        # If it is able to connect but only to Telstra Captive Portal that means
        # there's no Internet connection.
        if re.search(
            '<title>(.*)</title>',
            urlopen('http://www.freenom.world/').read().decode('utf-8')).group(1) == 'Telstra Air Captive Portal':
            return False
    # UrlOpen throws this error when there's no Internet connection at all.
    except URLError:
        return False

    return True


# If there is connection to outside world - there's no point to execute script.
if connected_to_network():
    exit(0)

argument_parser = ArgumentParser()
argument_parser.add_argument('username',
    action='store',
    help='Telstra air user name.')
argument_parser.add_argument('password',
    action='store',
    help='Telstra air password.')

args = argument_parser.parse_args()

# Get Wi-fi name and run it only if it is Telstra Air.
if re.compile('Current Wi-Fi Network: ').sub(
    '',
    getoutput('/usr/sbin/networksetup -getairportnetwork en0')) == 'Telstra Air':

    # Kill the Captive Portal. It blocks all the network traffic.
    captive_killer_thread = Thread(target=captive_portal_killer)
    captive_killer_thread.daemon = True
    captive_killer_thread.start()

    # Open browser.
    driver = webdriver.Safari()
    driver.get('https://www.telstra.com.au/airconnect#/main')

    # Wait till page is fully loaded ('Log in' button must be visible).
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="loginForm"]/div/p[2]/button')))

    # Fill the form and log in.
    driver.find_element_by_id('username').send_keys(args.username)
    driver.find_element_by_id('password').send_keys(args.password)
    driver.find_element_by_xpath('//*[@id="loginForm"]/div/p[2]/button').click()

    # Wait till next page is loaded ('Return to home' button must be visible).
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[11]/div/a/form/input')))

    # Quit the browser.
    driver.quit()
