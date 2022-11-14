import random
import requests
import bookseller_dialog
from datetime import timedelta
from ratelimit import limits, sleep_and_retry

GET_RANDOM_BOOK_URL = "http://gutendex.com/books?sort_order=random"
AMOUNT_OF_BOOKS_TO_FETCH = 5
SENTENCES_PER_BOOK = random.randint(8, 15)


response = requests.get(GET_RANDOM_BOOK_URL)
results = response.json()
random_books = random.choices(results["results"], k=AMOUNT_OF_BOOKS_TO_FETCH)

fulltext_list = []

language_list = {
    'en': 'English',
    'fr': 'French',
    'de': 'German',
}


def word_count(string):
    # Here we are removing the spaces from start and end,
    # and breaking every word whenever we encounter a space
    # and storing them in a list. The len of the list is the
    # total count of words.
    return (len(string.strip().split(" ")))

@sleep_and_retry
@limits(calls=1, period=timedelta(seconds=3).total_seconds())
def get_book_excerpt(url):
  print("Fetching excerpt from: " + url)
  return requests.get(url).text.strip().replace("\r", "").replace("\n", " ")

for book in random_books:
    try:
        author = book["authors"][0]["name"]
        author_readable = author.split(", ")[1] + " " + author.split(", ")[0]
    except IndexError:
        author_readable = "an unknown author"

    recommendation_start = random.choice(
        bookseller_dialog.dialog_start)

    recommendation_title = book["title"]

    recommendation_author = " by " + author_readable + ". "

    try:
      language = language_list[book["languages"][0]]
    except IndexError:
      language = "a weird language"
    
    recommendation_lang = random.choice(
        bookseller_dialog.dialog_lang) + language + ". "

    try:
      book_txt_url = book["formats"]["text/plain; charset=utf-8"]
    except KeyError:
      book_txt_url = book["formats"]["text/plain"]

    # print("Getting excerpt from: " + book_txt_url)
    book_txt = get_book_excerpt(book_txt_url)
    quotes = random.choices(book_txt.split(". "), k = SENTENCES_PER_BOOK)

    recommendation_excerpt = random.choice(bookseller_dialog.dialog_excerpt) + ". ".join(quotes) + "."

    recommendation_end = "\nWell, if this is not to your liking, I have plenty more books to recommend. Let's see. He got another book from the shelf. \n"

    fulltext_list.append(recommendation_start + recommendation_title +
                         recommendation_author + recommendation_lang + recommendation_excerpt + recommendation_end)

fulltext = "\n".join(fulltext_list)
# print(fulltext)

with open("reading-recommendation.txt", "w", encoding="utf-8") as summaryFile:
    print("Writing to summary file with word count: " +
          str(word_count(fulltext)))
    summaryFile.write(fulltext)
    summaryFile.close()