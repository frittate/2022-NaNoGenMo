from bs4 import BeautifulSoup
import requests
import random
import re
import os
import replicate
from datetime import datetime
from dotenv import load_dotenv

import dialog_sources

load_dotenv()

STABLE_CLIENT = replicate.Client(api_token="")
model = STABLE_CLIENT.models.get("stability-ai/stable-diffusion")

MAIN_LIST = "https://sfy.ru/scripts"
ALL_HEADERS = []
ALL_TEXT = []
REGEX_FOR_NUMBERS = r'[0-9]'
REGEX_FOR_DOT_WITH_AT_LEAST_TWO_SPACES_AFTER = r'\.\s{2,}'
REGEX_FOR_UPPERCASE_LETTERS_AND_PUNCTUATION = r'[^A-Z\.\?\!\,\;\-\s]'

SCENE_TAGS = ["INT.", "EXT.", "INTERIOR", "EXTERIOR"]
LOCATION_TAGS = [" YARD", " BUS", " PORCH"]
NOW = datetime.now()

i = 0
MAX_ITEMS = 29
NEWS_PROBABILITY = 18

date_time = NOW.strftime("%Y-%m-%d--%H-%M")

FILENAME = "INTERIOR_" + date_time + ".md"

def get_all_links():
    content = requests.get(MAIN_LIST).text
    soup = BeautifulSoup(content, "html.parser")
    linklist = soup.find("div", {"class": "two-thirds column"})

    links = []
    for link in linklist.findAll("a", href=True):
        # Format: https://sfy.ru/?script=ace_ventura
        if "/?script=" in link["href"]:
            links.append("https://sfy.ru" + link["href"])

    with open("links.txt", "w") as f:
        f.write("\n".join(links))

    print("Found number of movies:" + str(len(links)))
    return links

def read_links_from_file():
    with open("links.txt", "r") as f:
        links = f.read().splitlines()
    return links

def get_full_text(link):
    content = requests.get(link).text
    soup = BeautifulSoup(content, "html.parser")
    full_text_container = soup.find("pre")
    full_text = ""

    if (full_text_container):
        full_text = full_text_container.get_text()

    return full_text


def get_stable_image(prompt_text):
    print("Prompting AI for: " + prompt_text)

    try:
        images = model.predict(prompt=prompt_text, width=256, height=256)
    except replicate.exceptions.ModelError:
        print("Model error, skipping")
        images = []

    return images


def clean_string(input):
    input = re.sub(REGEX_FOR_NUMBERS, '', input)
    input = re.sub(REGEX_FOR_DOT_WITH_AT_LEAST_TWO_SPACES_AFTER, '. ', input)
    input = re.sub(REGEX_FOR_UPPERCASE_LETTERS_AND_PUNCTUATION, '', input)
    input = input.replace("INTERIOR", "INT.")
    input = input.replace("EXTERIOR", "EXT.")
    input = input.strip()
    return input


def get_scene_headers(link):
    full_text_for_link = get_full_text(link)
    full_text_ints = full_text_for_link.split("\n")

    full_text_headers = []

    for single_line in full_text_ints:
        if any(x in single_line for x in SCENE_TAGS):
            location_line = clean_string(single_line)
            full_text_headers.append(location_line + "\n\n")
            """ if any(x in single_line for x in LOCATION_TAGS):
        for tag in SCENE_TAGS:
          if tag in single_line:
            single_line = single_line.replace(tag, "")

        image_urls = get_stable_image("HYPERREALISTIC FILM STILL OF " + single_line)
        if (len(image_urls) > 0):
          image_url = image_urls[0]
          full_text_headers.append("![](" + image_url + ")" + "\n\n" + single_line + "\n\n")

      else: """


    return random.sample(full_text_headers, len(full_text_headers))

def get_news():
    url = "https://api.newscatcherapi.com/v2/search"
    
    NEWSCATCHER_TOKEN = os.environ.get("NEWSCATCHER_TOKEN")

    querystring = {
        "q": "\"climate change\"",
        "lang": "en",
        "sort_by": "relevancy",
        "page": "3",
        "page_size": 100
    }

    headers = {"x-api-key": NEWSCATCHER_TOKEN}

    try:
      print("Getting news...")
      response = requests.request("GET",
                                url,
                                headers=headers,
                                params=querystring)

    except:
      print("Error making news request")
      return []

    json_response = response.json()
    news_items = json_response["articles"]
    excerpts = []

    if (json_response["status"] == "ok"):
      for item in news_items:
        excerpts.append(item["excerpt"])
    else:
      print("Error getting news")
      
    return excerpts

def get_and_save_news():
    news = get_news()
    if (len(news) > 0):
      news_string = "\n\n".join(news)
      with open("news.txt", "a") as f:
        f.write(news_string)

def generate_lines_from_news():
    dialog_lines = []

    # news_excerpts = get_news()
    with open("news.txt", "r") as f:
      news_excerpts = f.read().split("\n\n")

    for item in news_excerpts:
      #words_in_item = re.findall(r'\w+', item)
      words_in_item = item.split(" ")
      words_in_item = words_in_item[3:-3]
      
      dialog_start_1 = random.choice(dialog_sources.DIALOG_SOURCE) + random.choice(dialog_sources.DIALOG_VERB)
      line_of_dialog_1 = dialog_start_1 + "..." + " ".join(words_in_item) + "..." + "\n\n\n"
      dialog_lines.append(line_of_dialog_1)
      
      dialog_start_2 = random.choice(dialog_sources.DIALOG_END_VERB) + random.choice(dialog_sources.DIALOG_SOURCE)
      line_of_dialog_2 = "..." + " ".join(words_in_item) + "..." + dialog_start_2 + "\n\n\n"
      dialog_lines.append(line_of_dialog_2)

    return dialog_lines

# links = get_all_links()
links = read_links_from_file()
# get_and_save_news()
NEWS_DIALOG = generate_lines_from_news()
shuffled_links = random.sample(links, len(links))

for link in shuffled_links:
    if (i < MAX_ITEMS):
        # print("Scraping link: " + link)
        headers_for_link = get_scene_headers(link)
        ALL_HEADERS.extend(headers_for_link)
        #ALL_HEADERS = random.sample(ALL_HEADERS, len(ALL_HEADERS))
        i += 1

print(len(NEWS_DIALOG), len(ALL_HEADERS))

ALL_TEXT.append("# TELEGRAMS FROM A FUTURE WORLD\n\n")

for i in range(0, len(ALL_HEADERS)):
  ALL_TEXT.append(ALL_HEADERS.pop(random.randrange(len(ALL_HEADERS))))

  if (random.randint(0, 100) > (100 - NEWS_PROBABILITY) and len(NEWS_DIALOG) > 0):
    ALL_TEXT.append(NEWS_DIALOG.pop(random.randrange(len(NEWS_DIALOG))))
  else:
    ALL_TEXT.append(random.choice(dialog_sources.DIALOG_EMPTY) + random.choice(dialog_sources.DIALOG_SILENCE))

with open(FILENAME, "w", encoding="utf-8") as headersFile:
    print("Writing to file")
    text_to_write = ALL_TEXT
    headersFile.writelines(text_to_write)
    headersFile.close()


# extract time designators: DAY, MORNING, EVENING, NIGHT, DAWN, DUSK, SUNSET, SUNDOWN
# sort by them
# strip all characters before the int and ext designators
# add some images from stability