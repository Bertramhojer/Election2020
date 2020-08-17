# Import modules
import requests
import re
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from datetime import datetime



# define function
def get_polit_fox():
    # url-specification
    req = requests.get("https://www.foxnews.com")

    # create soup objects
    soup = BeautifulSoup(req.content, 'html5lib')

    # identify articles
    soup = soup.find_all('h2', class_='title')
    # news is a list of soup-objects - 1 objects pr. article

    news = []

    for i in soup:
        if i.find('a')['href'].startswith('//www.foxnews.com'):
            news.append(i)

    # create empty lists for handling the data
    news_contents = []
    list_links = []
    list_titles = []


    for n in np.arange(0, len(news)):

        # getting the link
        link = news[n].find('a')['href']
        link = 'https:' + link
        list_links.append(link)

        #getting the title
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

data = get_polit_fox()
data.to_excel('foxNews.xlsx')
