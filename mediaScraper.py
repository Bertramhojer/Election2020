# Import modules
import requests
import re
from bs4 import BeautifulSoup
import demjson, json
import numpy as np
import pandas as pd
from datetime import datetime
from requests_html import HTMLSession
from urllib.parse import urlparse, urljoin


# define functions for getting articles from politico
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
        if len(re.findall('https://www.politico.com/news/2020/09', i['href'])) > 0:
            list_links.append(link)

    for n in np.arange(0, len(list_links)):

        article = requests.get(list_links[n])
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')
        body_p = soup_article.find_all('p', class_='story-text__paragraph')

        # get title
        title = str(soup_article.find_all('h2', class_='headline'))
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

def get_polit_politico():

    # url-specification
    url = "https://www.politico.com/politics"

    # request
    r1 = requests.get(url)
    r1.status_code

    # save cover-page content
    coverpage = r1.content

    # create soup objects
    soup = BeautifulSoup(coverpage, 'html5lib')

    # identify articles
    news = soup.find_all('a', href=True)
    # news is a list of soup-objects - 1 objects pr. article

    # create empty lists for handling the data
    news_contents = []
    list_links = []
    list_titles = []

    for i in news:
        link = i['href']
        if len(re.findall('https://www.politico.com/news/2020/09', i['href'])) > 0:
            list_links.append(link)

    for n in np.arange(0, len(list_links)):

        article = requests.get(list_links[n])
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')
        body_p = soup_article.find_all('p', class_='story-text__paragraph')

        # get title
        title = str(soup_article.find_all('h2', class_='headline'))
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


# define functions for getting articles from CNN
def get_news_cnn():
    # request url
    req = requests.get("https://edition.cnn.com")

    # create soup objects
    soup = BeautifulSoup(req.content, 'html5lib')

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
        if link.startswith('/2020/09/'):
            links.append(link)
            list_titles.append(title)

    for n in np.arange(0, len(links)):

        # producing links
        initial_link = 'https://edition.cnn.com'
        link = initial_link + links[n]
        list_links.append(link)

        article = requests.get(link)
        article_content = article.content
        soup = BeautifulSoup(article_content, 'html5lib')

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

def get_polit_cnn():
    # url-specification
    req = requests.get("https://edition.cnn.com/politics")

    soup = BeautifulSoup(req.text, 'html5lib')

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


# define functions for getting articles from FOX
def get_news_fox():
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

        # reading the content
        article = requests.get(link)
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')

        #getting the title
        title = str(soup_article.find_all('h1', class_='headline'))
        title = str(re.findall('>(.+?)<', title))
        list_titles.append(title[2:-2])

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
        final_article = re.sub("\\xa0", " ", final_article)

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

def get_polit_fox():

    # initialize the set of links (unique links)
    urls = set()

    def is_valid(url):
        """
        Checks whether `url` is a valid URL.
        """
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def get_all_website_links(url):
        """
        Returns all URLs that is found on `url` in which it belongs to the same website
        """
        # all URLs of `url`
        urls = []
        # domain name of the URL without the protocol
        domain_name = urlparse(url).netloc
        # initialize an HTTP session
        session = HTMLSession()
        # make HTTP request & retrieve response
        response = session.get(url)
        # execute Javascript
        try:
            response.html.render()
        except:
            pass
        soup = BeautifulSoup(response.html.html, "html.parser")
        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                # href empty tag
                continue
            # join the URL if it's relative (not absolute link)
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            # remove URL GET parameters, URL fragments, etc.
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if not is_valid(href):
                # not a valid URL
                continue
            if href in urls:
                # already in the set
                continue
            if '/category/' in href:
                continue
            if href.endswith('/executive'):
                continue
            if href.endswith('/senate'):
                continue
            if href.endswith('/house-of-representatives'):
                continue
            if href.endswith('/judiciary'):
                continue
            if href.endswith('/foreign-policy'):
                continue
            if href.endswith('/elections'):
                continue
            if domain_name not in href:
                continue
            if len(re.findall('/politics/', href)) > 0:
                urls.append(href)

        return urls

    list_links = get_all_website_links('https://www.foxnews.com/politics')

    # create empty lists for handling the data
    news_contents = []
    list_titles = []

    for n in np.arange(0, len(list_links)):

        # reading the content
        article = requests.get(list_links[n])
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')

        title = str(soup_article.find_all('h1', class_='headline'))
        title = str(re.findall('>(.+?)<', title))
        list_titles.append(title[2:-2])

        body_speakable = soup_article.find_all('p', class_='speakable')
        body_none = soup_article.find_all('p', class_='')

        # unifying the paragraphs into a single text
        list_paragraphs = []

        # unifying paragraphs of class 'speakable'
        for p in np.arange(0, len(body_speakable)):
            paragraph = body_speakable[p].get_text()
            list_paragraphs.append(paragraph)

        # unifying paragraphs of no class
        for p in np.arange(0, len(body_none)):
            paragraph = body_none[p].get_text()
            list_paragraphs.append(paragraph)

        final_article = " ".join(list_paragraphs)

        # Removing special characters
        final_article = re.sub("\\xa0", " ", final_article)

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


# define function for getting articles from Breitbart
def get_news_breitbart():

    # request url-access
    req = requests.get('https://www.breitbart.com')

    # create soup object
    soup = BeautifulSoup(req.content, 'html5lib')

    # find relevant elements
    news = soup.find_all('h2')

    # create empty lists for handling the data
    news_contents = []
    list_links = []
    list_titles = []

    for i in news:
        base_link = 'https://www.breitbart.com'
        try:
            link = i.find('a')['href']
        except:
            pass
        if link.startswith('/clips/') or link.startswith('https'):
            pass
        else:
            link = base_link + link
            list_links.append(link)

    for n in np.arange(0, len(list_links)):

        article = requests.get(list_links[n])
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')

        title = str(soup_article.find_all('h1'))
        title = title[5:-6]
        list_titles.append(title)

        body = soup_article.find_all('p')
        body = body[:-5]

        # unifying the paragraphs into a single text
        list_paragraphs = []

        for p in np.arange(0, len(body)):
            paragraph = body[p].get_text()
            list_paragraphs.append(paragraph)
            final_article = " ".join(list_paragraphs)

        # Removing special characters
        final_article = re.sub("\\xa0", " ", final_article)

        # appending them to the overall list
        news_contents.append(final_article)

    # create dataframe
    data = pd.DataFrame(
    {'Title': list_titles,
    'Content': news_contents,
    'Link': list_links,
    'Date': datetime.date(datetime.now()),
    'Organization': 'Breitbart'}
    )

    return data

# define function
def get_polit_breitbart():

    # request url-access
    req = requests.get('https://www.breitbart.com/politics')

    # create soup object
    soup = BeautifulSoup(req.content, 'html5lib')

    # find relevant elements
    news = soup.find_all('h2')

    # create empty lists for handling the data
    news_contents = []
    list_links = []
    list_titles = []

    for i in news:
        base_link = 'https://www.breitbart.com'
        try:
            link = i.find('a')['href']
        except:
            pass
        if link.startswith('/clips/') or link.startswith('https'):
            pass
        else:
            link = base_link + link
            list_links.append(link)

    for n in np.arange(0, len(list_links)):

        article = requests.get(list_links[n])
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')

        title = str(soup_article.find_all('h1'))
        title = title[5:-6]
        list_titles.append(title)

        body = soup_article.find_all('p')
        body = body[:-5]

        # unifying the paragraphs into a single text
        list_paragraphs = []

        for p in np.arange(0, len(body)):
            paragraph = body[p].get_text()
            list_paragraphs.append(paragraph)
            final_article = " ".join(list_paragraphs)

        # Removing special characters
        final_article = re.sub("\\xa0", " ", final_article)

        # appending them to the overall list
        news_contents.append(final_article)

    # create dataframe
    data = pd.DataFrame(
    {'Title': list_titles,
    'Content': news_contents,
    'Link': list_links,
    'Date': datetime.date(datetime.now()),
    'Organization': 'Breitbart'}
    )

    return data


# define functions for getting articles from NYTimes
def get_news_nytimes():
    # request url-access
    req = requests.get('https://www.nytimes.com/')

    # create soup object
    soup = BeautifulSoup(req.content, 'html5lib')

    news = soup.find_all('a', href=True)

    # create empty lists for handling the data
    news_contents = []
    list_links = []
    list_titles = []

    for i in news:
        base_link = 'https://www.nytimes.com'
        link = i['href']
        if link.startswith('/2020/09/'):
            if len(re.findall('/podcasts/', link)) > 0:
                pass
            else:
                link = base_link + link
                list_links.append(link)

    headline_classes = ['css-rsa88z e1h9rw200', 'css-hzs6w4 e1h9rw200',
                        'css-19rw7kf e1h9rw200', 'css-1uix9nv e1h9rw200',
                        'css-16kkdku e1h9rw200', 'css-j54zk9 e1h9rw200',
                        'css-x2vhww e1h9rw200', 'css-19x4nmc e1h9rw200',
                        'css-kzuvc5 e1h9rw200', 'css-1o8saeo e1h9rw200',
                        'css-f15pc4 edye5kn2']

    for n in np.arange(0, len(list_links)):

        article = requests.get(list_links[n])
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')

        # get title
        for c in np.arange(0, len(headline_classes)):
            title = str(soup_article.find_all('h1', class_=headline_classes[c]))
            title = str(re.findall('>(.+?)<', title))
            if len(title) > 5:
                break

        list_titles.append(title[2:-2])

        # get body
        body = soup_article.find_all('p', class_='css-158dogj evys1bk0')

        # specify empty list for paragraph pieces
        list_paragraphs = []

        # loop through paragraphs to create coherent content
        for p in np.arange(0, len(body)):
            paragraph = body[p].get_text()
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
    'Organization': 'NYTimes'}
    )

    return data

def get_polit_nytimes():
    # request url-access
    req = requests.get('https://www.nytimes.com/section/politics')

    # create soup object
    soup = BeautifulSoup(req.content, 'html5lib')

    news = soup.find_all('a', href=True)

    # create empty lists for handling the data
    news_contents = []
    list_links = []
    list_titles = []

    for i in news:
        base_link = 'https://www.nytimes.com'
        link = i['href']
        if link.startswith('/2020/09/'):
            if len(re.findall('/politics/', link)) > 0:
                link = base_link + link
                list_links.append(link)

    headline_classes = ['css-rsa88z e1h9rw200', 'css-hzs6w4 e1h9rw200',
                        'css-19rw7kf e1h9rw200', 'css-1uix9nv e1h9rw200',
                        'css-16kkdku e1h9rw200', 'css-j54zk9 e1h9rw200',
                        'css-x2vhww e1h9rw200', 'css-19x4nmc e1h9rw200',
                        'css-kzuvc5 e1h9rw200']

    for n in np.arange(0, len(list_links)):

        article = requests.get(list_links[n])
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')

        # get title
        for c in np.arange(0, len(headline_classes)):
            title = str(soup_article.find_all('h1', class_=headline_classes[c]))
            title = str(re.findall('>(.+?)<', title))
            if len(title) > 5:
                break

        list_titles.append(title[2:-2])

        # get body
        body = soup_article.find_all('p', class_='css-158dogj evys1bk0')

        # specify empty list for paragraph pieces
        list_paragraphs = []

        # loop through paragraphs to create coherent content
        for p in np.arange(0, len(body)):
            paragraph = body[p].get_text()
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
    'Organization': 'NYTimes'}
    )

    return data


# define functions for getting articles from nbc
def get_news_nbc():
    req = requests.get('https://www.nbcnews.com/')

    soup = BeautifulSoup(req.content, 'html5lib')

    news = soup.find_all('a', href=True)

    # create empty lists for handling the data
    news_contents = []
    list_links = []
    list_titles = []

    for i in news:
        link = i['href']
        if len(re.findall('-n[0-9]{7}', link)) > 0:
            if '/deals-and-sales/' in link:
                continue
            elif link not in list_links:
                list_links.append(link)

    headline_classes = ['article-hero__headline f8 f9-m fw3 mb3 mt0 f10-xl founders-cond lh-none',
                            'Theme-StoryTitle Theme-TextSize-small',
                            'article-hero__headline f8 f9-m fw3 mb3 mt0 f10-xl article-hero__shopping-section founders-cond lh-none',
                            'headline', 'Theme-StoryTitle Theme-TextSize-xsmall h-align-center',
                            'article-hero__headline f8 f9-m f9-l f10-xl fw3 mb3 mt0 founders-cond lh-none di']

    for n in np.arange(0, len(list_links)):

        article = requests.get(list_links[n])
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')

        for c in np.arange(0, len(headline_classes)):
            current_class = headline_classes[c]
            title = str(soup_article.find_all('h1', class_=current_class))
            title = str(re.findall('>(.+?)<', title))
            if len(title) > 5:
                break

        list_titles.append(title[2:-2])

        try:
            if current_class == 'Theme-StoryTitle Theme-TextSize-small':
                body = soup_article.find_all('p')
            else:
                body = soup_article.find_all('p', class_='endmarkEnabled')

            # specify empty list for paragraph pieces
            list_paragraphs = []

            # loop through paragraphs to create coherent content
            for p in np.arange(0, len(body)):
                paragraph = body[p].get_text()
                list_paragraphs.append(paragraph)
                final_article = " ".join(list_paragraphs)

            # Removing special characters
            final_article = re.sub("\\xa0", "", final_article)

        except:
            final_article = 'Text not reachable'

        # appending them to the overall list
        if final_article.startswith('Sections TV Featured More from NBC  Follow NBC News'):
            news_contents.append(final_article[52:])
        else:
            news_contents.append(final_article)

    # create dataframe
    data = pd.DataFrame(
    {'Title': list_titles,
    'Content': news_contents,
    'Link': list_links,
    'Date': datetime.date(datetime.now()),
    'Organization': 'NBC'}
    )

    return data

def get_polit_nbc():

    req = requests.get('https://www.nbcnews.com/politics')

    soup = BeautifulSoup(req.content, 'html5lib')

    news = soup.find_all('a', href=True)

    # create empty lists for handling the data
    news_contents = []
    list_links = []
    list_titles = []

    for i in news:
        link = i['href']
        if len(re.findall('-n[0-9]{7}', link)) > 0:
            if '/deals-and-sales/' in link:
                continue
            elif link not in list_links:
                list_links.append(link)

    headline_classes = ['article-hero__headline f8 f9-m fw3 mb3 mt0 f10-xl founders-cond lh-none',
                            'Theme-StoryTitle Theme-TextSize-small',
                            'article-hero__headline f8 f9-m fw3 mb3 mt0 f10-xl article-hero__shopping-section founders-cond lh-none',
                            'headline', 'Theme-StoryTitle Theme-TextSize-xsmall h-align-center',
                            'article-hero__headline f8 f9-m f9-l f10-xl fw3 mb3 mt0 founders-cond lh-none di']

    for n in np.arange(0, len(list_links)):

        article = requests.get(list_links[n])
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')

        for c in np.arange(0, len(headline_classes)):
            title = str(soup_article.find_all('h1', class_=headline_classes[c]))
            title = str(re.findall('>(.+?)<', title))
            if len(title) > 5:
                break

        list_titles.append(title[2:-2])

        try:
            body = soup_article.find_all('p', class_='endmarkEnabled')

            # specify empty list for paragraph pieces
            list_paragraphs = []

            # loop through paragraphs to create coherent content
            for p in np.arange(0, len(body)):
                paragraph = body[p].get_text()
                list_paragraphs.append(paragraph)
                final_article = " ".join(list_paragraphs)

            # Removing special characters
            final_article = re.sub("\\xa0", "", final_article)

        except:
            final_article = 'Text not reachable'

        # appending them to the overall list
        if final_article.startswith('Sections TV Featured More from NBC  Follow NBC News'):
            news_contents.append(final_article[52:])
        else:
            news_contents.append(final_article)

    # create dataframe
    data = pd.DataFrame(
    {'Title': list_titles,
    'Content': news_contents,
    'Link': list_links,
    'Date': datetime.date(datetime.now()),
    'Organization': 'NBC'}
    )

    return data


politico = get_news_politico()
cnn = get_news_cnn()
fox = get_news_fox()
nytimes = get_news_nytimes()
nbc = get_news_nbc()
breitbart = get_news_breitbart()

frontpages = [politico, cnn, fox, nytimes, nbc, breitbart]
frontpageData = pd.concat(frontpages)
frontpageData = frontpageData.drop_duplicates()

politicoPol = get_polit_politico()
cnnPol = get_polit_cnn()
foxPol = get_polit_fox()
nytimesPol = get_polit_nytimes()
nbcPol = get_polit_nbc()
breitbartPol = get_polit_breitbart()

politics = [politicoPol, cnnPol, foxPol, nytimesPol, nbcPol, breitbartPol]
politicsData = pd.concat(politics)
politicsData = politicsData.drop_duplicates()


frontpageData.to_excel('/Users/hojer/Desktop/projects/Election2020/frontpage/09_09_20.xlsx')
politicsData.to_excel('/Users/hojer/Desktop/projects/Election2020/politics/09_09_20.xlsx')
