from bs4 import BeautifulSoup
import requests
import random

pages_to_scrape = [
    "https://en.wikipedia.org/wiki/Brooklyn_Nine-Nine_(season_1)",
    "https://en.wikipedia.org/wiki/Brooklyn_Nine-Nine_(season_2)",
    "https://en.wikipedia.org/wiki/Brooklyn_Nine-Nine_(season_3)",
    "https://en.wikipedia.org/wiki/Brooklyn_Nine-Nine_(season_4)",
    "https://en.wikipedia.org/wiki/Brooklyn_Nine-Nine_(season_5)",
    "https://en.wikipedia.org/wiki/Brooklyn_Nine-Nine_(season_6)",
    "https://en.wikipedia.org/wiki/Brooklyn_Nine-Nine_(season_7)"
]
"""  "Game of Thrones (season 2)",
    "Game of Thrones (season 3)", "Game of Thrones (season 4)",
    "Game of Thrones (season 5)", "Game of Thrones (season 6)",
    "Game of Thrones (season 7)", "Game of Thrones (season 8)",
    "Futurama (season 1)"
] """

# TODO: Make Summary a list and convert it to a string on write
# TODO: Scramble the order of the episodes in Summary and write in a new file

summary = ""

for page in pages_to_scrape:
    print("Scraping page: " + page)

    content = requests.get(page).text
    soup = BeautifulSoup(content, "html.parser")

    summary_per_episode = ""

    for episode in soup.findAll("td", {"class": "description"}):
        summary_per_episode += episode.get_text()

    summary_split = summary_per_episode.replace("\n", " ").replace("\r", "").split(". ")
    summary_as_bullets = map(lambda x: "- " + x + "\n", summary_split)
    # print(soup_result)
    file_name = page.split("/").pop() + ".txt"

    if len(summary_split) > 1:
        with open(file_name, "w", encoding="utf-8") as summaryFile:
            print("Writing to file: " + file_name)
            summary_for_ep = "".join(summary_as_bullets)
            summary += summary_for_ep
            
            summaryFile.write(summary_for_ep)
            summaryFile.close()
    else:
        print("No summary found for page: " + page)


with open("summary.txt", "w", encoding="utf-8") as summaryFile:
    print("Writing to summary file: summary.txt")
    summaryFile.write(summary)
    summaryFile.close()

with open("summary_scrambled.txt", "w", encoding="utf-8") as summaryScrambled:
    print("Writing to summary scrambled file: summary_scrambled.txt")
    summaryScrambled.write("".join(random.sample(summary, len(summary))))
    summaryFile.close()

print("Done")