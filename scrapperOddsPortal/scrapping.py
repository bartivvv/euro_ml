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

def scrape_odds_from_url_1x2(url):
  output = []
  url = url + '#1X2;2'
  browser.get(url)
  browser.refresh()
  browser.execute_script("window.scrollTo(0, 3000);")
  time.sleep(3)
  soup = bs(browser.page_source, "lxml")
  average_row = soup.find("div", class_="border-black-borders bg-gray-light flex h-9 border-b border-l border-r text-xs")
  if len(average_row) == 0:
    return None
  for value_element in average_row.find_all("div", class_="text-black-main"):
    output.append(value_element.find("p").text.strip())
  return output[0:3]

def scrape_odds_from_url_OU(url):
  output = []
  url = url + '#over-under;2'
  browser.get(url)
  browser.refresh()
  browser.execute_script("window.scrollTo(0, 3000);")
  time.sleep(3)
  soup = bs(browser.page_source, "lxml")
  elements = soup.find_all("div", class_="border-black-borders hover:bg-gray-light flex h-9 cursor-pointer border-b border-l border-r text-xs")
  if len(elements) == 0:
    return None

  # Process each element
  for element in elements:
    # Extract text (assuming it's in the first paragraph with class not containing "breadcrumbs-m")
    text = element.find("p", class_=lambda c: c and not c.startswith("breadcrumbs-m")).text.strip()
    if text in ['Over/Under +0.5', 'Over/Under +1.5', 'Over/Under +2.5', 'Over/Under +3.5', 'Over/Under +4.5', 'Over/Under +5.5', 'Over/Under +6.5']:

      # Extract values (assuming they are within elements with class "height-content")
      values = []
      for value_element in element.find_all("div", class_="flex-center border-black-borders min-w-[60px] flex-col gap-1 pb-0.5 pt-0.5 relative"):
        value_p = value_element.find("p", class_="height-content")
        values.append(text)
        values.append(value_p.text.strip())
      output.append(values)
    else:
      pass
  return output

def scrape_odds_from_url_handicap(url):
  output = []
  url = url + '#eh;2'
  browser.get(url)
  browser.refresh()
  browser.execute_script("window.scrollTo(0, 3000);")
  time.sleep(3)
  soup = bs(browser.page_source, "lxml")
  elements = soup.find_all("div", class_="border-black-borders hover:bg-gray-light flex h-9 cursor-pointer border-b border-l border-r text-xs")
  if len(elements) == 0:
    return None

  # Process each element
  for element in elements:
    # Extract text (assuming it's in the first paragraph with class not containing "breadcrumbs-m")
    text = element.find("p", class_=lambda c: c and not c.startswith("breadcrumbs-m")).text.strip()
    if text in ['European Handicap -3','European Handicap -2','European Handicap -1','European Handicap +1','European Handicap +2', 'European Handicap +3',]:

      # Extract values (assuming they are within elements with class "height-content")
      values = []
      for value_element in element.find_all("div", class_="flex-center border-black-borders min-w-[60px] flex-col gap-1 pb-0.5 pt-0.5 relative"):
        value_p = value_element.find("p", class_="height-content")
        values.append(text)
        values.append(value_p.text.strip())
      output.append(values)
    else:
      pass
  return output

def scrape_odds_from_url_bts(url):
  output = []
  url = url + '#bts;2'
  browser.get(url)
  browser.refresh()
  browser.execute_script("window.scrollTo(0, 3000);")
  time.sleep(3)
  soup = bs(browser.page_source, "lxml")
  average_row = soup.find("div", class_="border-black-borders bg-gray-light flex h-9 border-b border-l border-r text-xs")
  if len(average_row) == 0:
    return None
  for value_element in average_row.find_all("div", class_="text-black-main"):
    output.append(value_element.find("p").text.strip())
  return output[0:2]


def save_list_to_txt_join(data, filename, mode='a'):
  """Saves a list of elements to a text file, joining them with a newline character.

  Args:
      data: The list of elements to save.
      filename: The name of the text file to write to.
      mode: The file open mode ('a' for appending, defaults to 'w' for writing).
  """
  with open(filename, mode) as f:
    f.write('\n'.join(str(item) for item in data) + '\n') 

def scrape_ids(region, competition, numPage1, numPage2, teams):
  # all_ids = []
  # country_names = []
  urls = []
  for i in range(numPage1, numPage2+1):
    base_url = f"https://www.oddsportal.com/football/{region}/{competition}/results/#/page/"
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
        if (team_names[0] in teams) or (team_names[1] in teams):
          urls.append(f"https://www.oddsportal.com/football/{region}/{competition}/{clean_team_name(team_names[0])}-{clean_team_name(team_names[1])}-{row_id}/")
  return urls

def scrape_dates(url):
  url = url + '#bts;2'
  browser.get(url)
  print(browser.current_url)
  browser.refresh()
  browser.execute_script("window.scrollTo(0, 3000);")
  time.sleep(3)
  soup = bs(browser.page_source, "lxml")
  container = soup.find('div', class_="text-gray-dark font-main item-center flex gap-1 text-xs font-normal")
  output = [p.text.strip() for p in container.find_all('p')]
  return output[1][:-1] 


# def scrape_books_details(urls):
#   for url in urls:
#     date = scrape_dates(url)
#     odds_1x2 = scrape_odds_from_url_1x2(url)
#     odds_OU = scrape_odds_from_url_OU(url)
#     odds_bts = scrape_odds_from_url_bts(url)

teams_available = ['Albania',
'Austria',
'Belgium',
'Croatia',
'Czech Republic',
'Denmark',
'England',
'France',
'Georgia',
'Germany',
'Hungary',
'Italy',
'Netherlands',
'Poland',
'Portugal',
'Romania',
'Scotland',
'Serbia',
'Slovakia',
'Slovenia',
'Spain',
'Switzerland',
'Turkey',
'Ukraine',
'Wales',
'Finland',
'Russia',
'North Macedonia',
'Sweden'
]
region = 'world'
competitions = 'friendly-international-2019'
# urls = scrape_ids(region, competitions, 6, 10, teams_available)
# file_urls = save_list_to_txt_join(urls, 'urls_friendly')
# print(len(urls))

test_url = scrape_ids(region, competitions, 1, 2, teams_available)[0]
test_date = scrape_dates(test_url)
test_1x2 = scrape_odds_from_url_1x2(test_url)
test_OU = scrape_odds_from_url_OU(test_url)
test_bts = scrape_odds_from_url_bts(test_url)
test_handi = scrape_odds_from_url_handicap(test_url)
print(test_date, test_1x2, test_OU, test_bts, test_handi)
# urls2 = scrape_ids('euro-2016', 7)
# print(len(urls2))
# file_urls = save_list_to_txt_join(urls2, 'urls-europe')

# out = scrape_odds_from_url_bts(urls[0:2])
# print(out)
browser.quit()