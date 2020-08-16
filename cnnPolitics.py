# Import modules
import requests
import re
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import demjson, json
from datetime import datetime


def get_news_cnn():
    # url-specification
    req = requests.get("https://edition.cnn.com/politics")

    soup = BeautifulSoup(req.text, 'html.parser')

    script = None
    for i in soup.find_all("script"):
        if "window.CNN" in i.text:
            script = i.get_text(strip=True)
    if script is None: print("No data found")
    else:
        data = script.partition("CNN.contentModel")[-1].partition("FAVE.settings")[0]
        json_data = demjson.decode(data[data.index('{'):-1])

        with open("data.json", "w") as f:
            json.dump(json_data, f)

    # create empty lists for handling the data
    news_contents = []
    links = []
    list_links = []
    list_titles = []

    for article in json_data['siblings']['articleList']:
        link = article['uri']
        title = article['headline']
        if len(re.findall('/politics/', link)) > 0:
            links.append(link)
            list_titles.append(title)


    for n in np.arange(0, len(links)):

        # producing links
        initial_link = 'https://edition.cnn.com'
        link = initial_link + links[n]
        list_links.append(link)

        article = requests.get(link)
        article_content = article.content
        soup = BeautifulSoup(article_content, 'html.parser')

        type0 = soup.find_all('p', class_='zn-body__paragraph speakable')
        type1 = soup.find_all('div', class_='zn-body__paragraph speakable')
        type2 = soup.find_all('div', class_='zn-body__paragraph')

        list_paragraphs = []

        for p in np.arange(0, len(type0)):
            paragraph = type0[p].get_text()
            list_paragraphs.append(paragraph)

        for p in np.arange(0, len(type1)):
            paragraph = type1[p].get_text()
            list_paragraphs.append(paragraph)

        for p in np.arange(0, len(type2)):
            paragraph = type2[p].get_text()
            list_paragraphs.append(paragraph)

        final_article = " ".join(list_paragraphs)
        final_article = re.sub("\\xa0", "", final_article)

        news_contents.append(final_article)


    data = pd.DataFrame(
    {'Title': list_titles,
    'Content': news_contents,
    'Link': list_links,
    'Date': datetime.date(datetime.now()),
    'Organization': 'CNN'}
    )

    return data

data = get_news_cnn()
data.to_excel('cnnNews.xlsx')
