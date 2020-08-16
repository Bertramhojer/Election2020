# Import modules
import requests
import re
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from datetime import datetime

# define function
def get_news_fox():
    # url-specification
    url = "https://www.foxnews.com/politics"

    # request
    r1 = requests.get(url)
    r1.status_code

    # save cover-page content
    coverpage = r1.content

    # create soup objects
    soup = BeautifulSoup(coverpage, 'html5lib')

    # identify articles
    news = soup.find_all('h2', class_='title')
    # news is a list of soup-objects - 1 objects pr. article


    # create empty lists for handling the data
    news_contents = []
    list_links = []
    list_titles = []



    for n in np.arange(0, len(news)):

        # getting the link
        initial_link = 'https://www.foxnews.com'
        link = news[n].find('a')['href']
        link = initial_link + link
        list_links.append(link)

        # getting the title
        title = news[n].find('a').get_text()
        list_titles.append(title)

        # reading the content
        article = requests.get(link)
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')
        body_speakable = soup_article.find_all('p', class_='speakable')
        body_none = soup_article.find_all('p', class_='')

        # unifying the paragraphs into a single text
        list_paragraphs = []

        # unifying paragraphs of class 'speakable'
        for p in np.arange(0, len(body_speakable)):
            paragraph = body_speakable[p].get_text()
            list_paragraphs.append(paragraph)
            final_article = " ".join(list_paragraphs)

        # unifying paragraphs of no class
        for p in np.arange(0, len(body_none)):
            paragraph = body_none[p].get_text()
            list_paragraphs.append(paragraph)
            final_article = " ".join(list_paragraphs)

        # Removing special characters
        final_article = re.sub("\\xa0", "", final_article)

        # appending them to the overall list
        news_contents.append(final_article)


    # create dataframe
    data = pd.DataFrame(
    {'Title': list_titles,
    'Content': news_contents,
    'Link': list_links,
    'Date': datetime.date(datetime.now()),
    'Organization': 'Fox News'}
    )

    return data

data = get_news_fox()
data.to_excel('foxNews.xlsx')
