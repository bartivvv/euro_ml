import os
import threading
from math import nan
from multiprocessing.pool import ThreadPool
import pandas as pd
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

class Driver:
  def __init__(self):
      options = webdriver.ChromeOptions()
      options.add_argument("--headless")
      options.add_experimental_option('excludeSwitches', ['enable-logging'])
      self.driver = webdriver.Chrome(options=options)

  def __del__(self):
      self.driver.quit()  # clean up driver when we are cleaned up
      # print('The driver has been "quitted".')


threadLocal = threading.local()


def create_driver():
  the_driver = getattr(threadLocal, 'the_driver', None)
  if the_driver is None:
      the_driver = Driver()
      setattr(threadLocal, 'the_driver', the_driver)
  return the_driver.driver

def clean_team_name(team_name):
  """
  This function cleans a team name by removing most special characters,
  replacing spaces and ampersands with hyphens, and ensuring no double hyphens.
  """
  # Remove most special characters and extra spaces
  cleaned_name = re.sub(r"[^\w\- ]", "", team_name.strip())
  # Replace spaces and ampersands with hyphens
  cleaned_name = cleaned_name.lower().replace(" ", "-").replace("&", "-")
  # Remove any double hyphens
  return re.sub(r"--", "-", cleaned_name)

# Define URL, target section selector, and base URL for pagination

browser = create_driver()
def scrape_ids(competition, numPages):
  # all_ids = []
  # country_names = []
  urls = []
  for i in range(1,numPages+1):
    base_url = f"https://www.oddsportal.com/football/europe/{competition}/results/#/page/"
    url = base_url + f"{i}/"

    browser.get(url)
    print(browser.current_url)

    browser.refresh()
    time.sleep(10)
    browser.execute_script("window.scrollTo(0, 3000);")

    time.sleep(10)
    soup = bs(browser.page_source, "lxml")

    # Find all event rows
    event_rows = soup.find_all("div", class_="eventRow flex w-full flex-col text-xs")

    for row in event_rows:
      row_id = row.get('id')
      # if row_id:
      #   all_ids.append(row_id)
      participant_info = row.find("div", class_="group flex")
      if participant_info:  # Check if participant information exists
      # Find all elements with participant names within participant_info
        participant_elements = participant_info.select(".participant-name.truncate")
        team_names = []
        for participant in participant_elements:
            team_names.append(participant.text.strip())
        # country_names.append(team_names)
      urls.append(f"https://www.oddsportal.com/football/europe/{competition}/{clean_team_name(team_names[0])}-{clean_team_name(team_names[1])}-{row_id}/")
  return urls


def scrape_odds_from_url_1x2(urls):
   output = []
   for url in urls:
    url = url + '#1X2;2'
    browser.get(url)
    print(browser.current_url)
    browser.refresh()
    browser.execute_script("window.scrollTo(0, 3000);")
    time.sleep(3)
    soup = bs(browser.page_source, "lxml")
    average_row = soup.find("div", class_="border-black-borders bg-gray-light flex h-9 border-b border-l border-r text-xs")
    values = []
    for value_element in average_row.find_all("div", class_="text-black-main"):
      values.append(value_element.find("p").text.strip())
    output.append(values)
   return output

def scrape_odds_from_url_OU(urls):
   output = []
   for url in urls:
    url = url + '#over-under;2'
    browser.get(url)
    print(browser.current_url)
    browser.refresh()
    browser.execute_script("window.scrollTo(0, 3000);")
    time.sleep(3)
    soup = bs(browser.page_source, "lxml")
    elements = soup.find_all("div", class_="border-black-borders hover:bg-gray-light flex h-9 cursor-pointer border-b border-l border-r text-xs")

    # Process each element
    for element in elements:
      # Extract text (assuming it's in the first paragraph with class not containing "breadcrumbs-m")
      text = element.find("p", class_=lambda c: c and not c.startswith("breadcrumbs-m")).text.strip()

      # Extract values (assuming they are within elements with class "height-content")
      values = []
      for value_element in element.find_all("div", class_="flex-center border-black-borders min-w-[60px] flex-col gap-1 pb-0.5 pt-0.5 relative"):
        value_p = value_element.find("p", class_="height-content")
        values.append(text)
        values.append(value_p.text.strip())
      output.append(values)
   return output

urls = scrape_ids('euro-2024', 1)
# ids2020, countries = scrape_ids('euro-2020', 7) 

# print(urls)
print(len(urls))

out = scrape_odds_from_url_OU(urls[0:2])
print(out)
browser.quit()