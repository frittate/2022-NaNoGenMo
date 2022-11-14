from bs4 import BeautifulSoup
import requests
import random
import re

MAIN_LIST = "https://sfy.ru/scripts"
ALL_HEADERS = []
REGEX_FOR_NUMBERS = r'[0-9]'
REGEX_FOR_DOT_WITH_AT_LEAST_TWO_SPACES_AFTER = r'\.\s{2,}'
i = 0
MAX_ITEMS = 80


def all_links():
  content = requests.get(MAIN_LIST).text
  soup = BeautifulSoup(content, "html.parser")
  linklist = soup.find("div", { "class": "two-thirds column" })

  links = []
  for link in linklist.findAll("a", href=True):
    # Format: https://sfy.ru/?script=ace_ventura
      if "/?script=" in link["href"]:
          links.append("https://sfy.ru" + link["href"])

  print("Found number of movies:" + str(len(links)))
  return links

def get_full_text(link):
  content = requests.get(link).text
  soup = BeautifulSoup(content, "html.parser")
  full_text_container = soup.find("pre")
  full_text = ""

  if (full_text_container):
    full_text = full_text_container.get_text()

  return full_text

def get_scene_headers(link):
  full_text_for_link = get_full_text(link)
  full_text_ints = full_text_for_link.split("\n")

  full_text_headers = []

  for single_line in full_text_ints:
    if any(x in single_line for x in ["INT.", "EXT.", "INTERIOR", "EXTERIOR"]):
      single_line = re.sub(REGEX_FOR_NUMBERS, '', single_line)
      single_line = re.sub(REGEX_FOR_DOT_WITH_AT_LEAST_TWO_SPACES_AFTER, '. ', single_line)
      full_text_headers.append(single_line.strip())

  return random.sample(full_text_headers, len(full_text_headers))

links = all_links()
shuffled_links = random.sample(links, len(links))

for link in shuffled_links:
  if (i < MAX_ITEMS):
    print("Scraping link: " + link)
    headers_for_link = get_scene_headers(link)
    ALL_HEADERS.extend(headers_for_link)
    ALL_HEADERS = random.sample(ALL_HEADERS, len(ALL_HEADERS))
    i += 1

with open("headers.txt", "w", encoding="utf-8") as headersFile:
    print("Writing to summary file: summary.txt")
    text_to_write = "\n".join(ALL_HEADERS)
    print(text_to_write)
    headersFile.write(text_to_write)
    headersFile.close()
  

# extract time designators: DAY, MORNING, EVENING, NIGHT, DAWN, DUSK, SUNSET, SUNDOWN
# sort by them
# strip all characters before the int and ext designators