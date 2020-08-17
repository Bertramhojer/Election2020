# Import modules
import requests
import re
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from datetime import datetime



def get_news_politico():

    # url-specification
    req = requests.get("https://www.politico.com")

    # create soup objects
    soup = BeautifulSoup(req.content, 'html5lib')

    # identify articles
    news = soup.find_all('a', href=True)
    # news is a list of soup-objects - 1 objects pr. article

    # create empty lists for handling the data
    news_contents = []
    list_links = []
    list_titles = []

    for i in news:
        link = i['href']
        if len(re.findall('https://www.politico.com/news/2020/08', i['href'])) > 0:
            list_links.append(link)

    for n in np.arange(0, len(list_links)):

        article = requests.get(list_links[n])
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')
        body_p = soup_article.find_all('p', class_='story-text__paragraph')

        # get title
        title = soup_article.find_all('h2', class_='headline')
        title = str(title)
        title = str(re.findall('>(.+?)<', title))
        list_titles.append(title[2:-2])

        # unifying the paragraphs into a single text
        list_paragraphs = []

        for p in np.arange(0, len(body_p)):
            paragraph = body_p[p].get_text()
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
    'Organization': 'Politico'}
    )

    return data


data = get_news_politico()
data = data.drop_duplicates()
data.to_excel('politicoNews.xlsx')
