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
import itertools
import csv

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
  if average_row is None:
    return [None, None, None]
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
  output_list = [[None, None, None, None, None], [None, None, None, None, None]]
  if elements is None or elements == "":
    return output_list

  # Process each element
  for element in elements:
    # Extract text (assuming it's in the first paragraph with class not containing "breadcrumbs-m")
    text = element.find("p", class_=lambda c: c and not c.startswith("breadcrumbs-m")).text.strip()
    if text in ['Over/Under +0.5', 'Over/Under +1.5', 'Over/Under +2.5', 'Over/Under +3.5', 'Over/Under +4.5']:

      # Extract values (assuming they are within elements with class "height-content")
      values = []
      for i, value_element in enumerate(element.find_all("div", class_="flex-center border-black-borders min-w-[60px] flex-col gap-1 pb-0.5 pt-0.5 relative")):
        value_p = value_element.find("p", class_="height-content")
        if text == 'Over/Under +0.5':
          output_list[i][0] = value_p.text.strip()
        elif text == 'Over/Under +1.5':
          output_list[i][1] = value_p.text.strip()
        elif text == 'Over/Under +2.5':
          output_list[i][2] = value_p.text.strip()
        elif text == 'Over/Under +3.5':
          output_list[i][3] = value_p.text.strip()
        elif text == 'Over/Under +4.5':
          output_list[i][4] = value_p.text.strip()
    else:
      pass
  return output_list

def scrape_odds_from_url_handicap(url):
  output = []
  url = url + '#eh;2'
  browser.get(url)
  browser.refresh()
  browser.execute_script("window.scrollTo(0, 3000);")
  time.sleep(3)
  soup = bs(browser.page_source, "lxml")
  elements = soup.find_all("div", class_="border-black-borders hover:bg-gray-light flex h-9 cursor-pointer border-b border-l border-r text-xs")
  output_list = [[None, None, None, None], [None, None, None, None], [None, None, None, None]]
  if elements is None or elements == "":
    return output_list

  # Process each element
  for element in elements:
    # Extract text (assuming it's in the first paragraph with class not containing "breadcrumbs-m")
    text = element.find("p", class_=lambda c: c and not c.startswith("breadcrumbs-m")).text.strip()
    if text in ['European Handicap -2','European Handicap -1','European Handicap +1','European Handicap +2']:

      # Extract values (assuming they are within elements with class "height-content")
      values = []
      for i, value_element in enumerate(element.find_all("div", class_="flex-center border-black-borders min-w-[60px] flex-col gap-1 pb-0.5 pt-0.5 relative")):
        value_p = value_element.find("p", class_="height-content")
        if text == 'European Handicap -2':
          output_list[i][0] = value_p.text.strip()
        elif text == 'European Handicap -1':
          output_list[i][1] = value_p.text.strip()
        elif text == 'European Handicap +1':
          output_list[i][2] = value_p.text.strip()
        elif text == 'European Handicap +2':
          output_list[i][3] = value_p.text.strip()
    else:
      pass
  return output_list

def scrape_odds_from_url_bts(url):
  output = []
  url = url + '#bts;2'
  browser.get(url)
  browser.refresh()
  browser.execute_script("window.scrollTo(0, 3000);")
  time.sleep(3)
  soup = bs(browser.page_source, "lxml")
  average_row = soup.find("div", class_="border-black-borders bg-gray-light flex h-9 border-b border-l border-r text-xs")
  if average_row is None or average_row == "":
    return [None, None]
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
        # if (team_names[0] in teams) or (team_names[1] in teams):
        urls.append(f"https://www.oddsportal.com/football/{region}/{competition}/{clean_team_name(team_names[0])}-{clean_team_name(team_names[1])}-{row_id}/")
  return urls

def scrape_dates(url):
  url = url + '#1X2;2'
  browser.get(url)
  browser.refresh()
  browser.execute_script("window.scrollTo(0, 3000);")
  time.sleep(3)
  soup = bs(browser.page_source, "lxml")
  container = soup.find('div', class_="text-gray-dark font-main item-center flex gap-1 text-xs font-normal")
  if container is None or container =="":
    return None
  else:
    output = [p.text.strip() for p in container.find_all('p')]
    return output[1][:-1] 

def extract_info_from_url(url):
  """
  Extracts the last three values (assuming team names and match ID) from a URL.

  Args:
      url: The URL string containing team names and a match ID.

  Returns:
      A tuple containing three strings: team1, team2, and match_id.
  """
  parts = url.split("/")
  return ([parts[-2]])

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

def read_urls_from_file(filename):
  """
  Reads URLs from a text file and returns a list of strings.

  Args:
      filename: The path to the text file containing URLs.

  Returns:
      A list of strings where each element is a URL from the file.
  """
  urls = []
  with open(filename, "r") as file:
    for line in file:
      # Remove trailing newline character if present
      url = line.strip()
      urls.append(url)
  return urls

def scrape_books_details(filename, file_to_write):
  urls = read_urls_from_file(filename)
  output_list = []
  for i, url in enumerate(urls):
    url_details = extract_info_from_url(url)
    date = [scrape_dates(url)]
    odds_1x2 = scrape_odds_from_url_1x2(url)
    odds_OU = list(itertools.chain.from_iterable(scrape_odds_from_url_OU(url)))
    odds_bts = scrape_odds_from_url_bts(url)
    odds_handi = list(itertools.chain.from_iterable(scrape_odds_from_url_handicap(url)))
    flist = [url_details, date, odds_1x2, odds_bts, odds_OU, odds_handi]
    output_list.append(list(itertools.chain.from_iterable((flist))))
    if i% 10 == 0 and i != 0:
      print(i)
  with open(file_to_write, "a", newline="") as csvfile:
    for l in output_list:
      writer = csv.writer(csvfile)
      writer.writerow(l)

# region = 'europe'
# competitions = 'euro-2024'
# urls = scrape_ids(region, competitions, 4, 5, teams_available)
# # print(scrape_odds_from_url_handicap(urls[0]))
# file_urls = save_list_to_txt_join(urls, 'urls_europe_2024')
# print(len(urls))
# result = scrape_books_details('urls_world_2014', "odds_data_worlds_2014.csv")
# urls2 = scrape_ids('euro-2016', 7)
# print(len(urls2))
# file_urls = save_list_to_txt_join(urls2, 'urls-europe')

# out = scrape_odds_from_url_bts(urls[0:2])
# print(out)

# test = read_urls_from_file('odds_data_europe_2020.csv')
# print(test)
browser.quit()