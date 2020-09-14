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

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from keys import email, password


filename = input("Enter date (YYYY-MM-DD): ")
mainFilename = f'/Users/hojer/Desktop/projects/Election2020/frontpage/front-{filename}.xlsx'
politicsFilename = f'/Users/hojer/Desktop/projects/Election2020/politics/pol-{filename}.xlsx'


# Specifying unique link-retriever for CNN
def get_links_cnn():
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

    return json_data


def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


# Specifying link-retriever for each media-site
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


def get_links_wsj(url):
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
        if domain_name not in href:
            continue
        if len(re.findall('/articles/', href)) > 0:
            urls.append(href)

    return urls


def get_links_politico(url, tag):

    # url-specification
    req = requests.get(url)
    # create soup objects
    soup = BeautifulSoup(req.content, 'html5lib')
    # identify articles
    news = soup.find_all(tag, href=True)
    # news is a list of soup-objects - 1 objects pr. article
    for i in news:
        link = i['href']
        if len(re.findall('https://www.politico.com/news/2020/09', i['href'])) > 0:
            list_links.append(link)

    return list_links


def get_links_breitbart(url):
    # request url-access
    req = requests.get(url)
    # create soup object
    soup = BeautifulSoup(req.content, 'html5lib')
    # find relevant elements
    news = soup.find_all('h2')

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

    return list_links

def get_links_nyt(url):
    # request url-access
    req = requests.get(url)
    # create soup object
    soup = BeautifulSoup(req.content, 'html5lib')
    news = soup.find_all('a', href=True)

    for i in news:
        base_link = 'https://www.nytimes.com'
        link = i['href']
        if link.startswith('/2020/09'):
            if len(re.findall('/podcasts/', link)) > 0:
                pass
            else:
                link = base_link + link
                list_links.append(link)

    return list_links


def get_links_nbc(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html5lib')
    news = soup.find_all('a', href=True)

    for i in news:
        link = i['href']
        if len(re.findall('-n[0-9]{7}', link)) > 0:
            if '/deals-and-sales/' in link:
                continue
            elif link not in list_links:
                list_links.append(link)

    return list_links



def login_wsj():
    signInPage = 'https://sso.accounts.dowjones.com/login?state=g6Fo2SBxM2VMZ0hJNnhwWUFmR056N0NmMlBPX3hydl9YQmR3WqN0aWTZIEt6WG1Hd3lzRXJwTWM0U2dzUExCVjRuV05QM0N1c1h1o2NpZNkgNWhzc0VBZE15MG1KVElDbkpOdkM5VFhFdzNWYTdqZk8&client=5hssEAdMy0mJTICnJNvC9TXEw3Va7jfO&protocol=oauth2&scope=openid%20idp_id%20roles%20email%20given_name%20family_name%20djid%20djUsername%20djStatus%20trackid%20tags%20prts&response_type=code&redirect_uri=https%3A%2F%2Faccounts.wsj.com%2Fauth%2Fsso%2Flogin&nonce=a3b676cb-4bdf-483d-ada6-3700a992b5f4&ui_locales=en-us-x-wsj-83-2&ns=prod%2Faccounts-wsj&savelogin=on#!/signin'

    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    driver = webdriver.Chrome(executable_path='/Users/hojer/Desktop/projects/chromedriver', options=options)
    driver.get(signInPage)

    loginPageEmail = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'//input[@name="username"]')))
    loginPageEmail.send_keys(email)
    loginPagepassword = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'//input[@name="password"]')))
    loginPagepassword.send_keys(password)
    submitButton = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'//button[@type="submit"]')))
    submitButton.click()


# Specify function for creating a complete data-frame when scraping is done
def make_data(media_site):
    data = pd.DataFrame({'Title': list_titles,
                        'Content': news_contents,
                        'Link': list_links,
                        'Date': datetime.date(datetime.now()),
                        'Organization': media_site}
                        )

    return data


# specify function for creating articles from article paragraphs
def create_article():
    # create the final article by compiling all the paragraphs
    final_article = " ".join(list_paragraphs)
    # Removing special characters
    final_article = re.sub("\\xa0", " ", final_article)
    # appending them to the overall list
    news_contents.append(final_article)

    return news_contents


# all media website links to be visited by the scraper
websites = ['https://www.politico.com/', 'https://www.politico.com/politics',
        'https://edition.cnn.com', 'https://edition.cnn.com/politics',
        'https://www.foxnews.com', 'https://www.foxnews.com/politics',
        'https://www.breitbart.com', 'https://www.breitbart.com/politics',
        'https://www.nytimes.com/', 'https://www.nytimes.com/section/politics',
        'https://www.nbcnews.com/', 'https://www.nbcnews.com/politics',
        'https://www.wsj.com/', 'https://www.wsj.com/news/politics']

# various headlines for different NYT-articles
headlines_nyt = ['css-rsa88z e1h9rw200', 'css-hzs6w4 e1h9rw200',
                    'css-19rw7kf e1h9rw200', 'css-1uix9nv e1h9rw200',
                    'css-16kkdku e1h9rw200', 'css-j54zk9 e1h9rw200',
                    'css-x2vhww e1h9rw200', 'css-19x4nmc e1h9rw200',
                    'css-kzuvc5 e1h9rw200', 'css-1o8saeo e1h9rw200',
                    'css-f15pc4 edye5kn2', 'css-lhw6wc e1h9rw200',
                    'css-1uvwfp1 e1h9rw200', 'css-1xbyom1 edye5kn2']

headlines_nbc = ['article-hero__headline f8 f9-m fw3 mb3 mt0 f10-xl founders-cond lh-none',
                        'Theme-StoryTitle Theme-TextSize-small',
                        'article-hero__headline f8 f9-m fw3 mb3 mt0 f10-xl article-hero__shopping-section founders-cond lh-none',
                        'headline', 'Theme-StoryTitle Theme-TextSize-xsmall h-align-center',
                        'article-hero__headline f8 f9-m f9-l f10-xl fw3 mb3 mt0 founders-cond lh-none di']


for i in np.arange(0, len(websites)):


    # create empty lists for handling the data
    news_contents = []
    list_links = []
    list_titles = []


    if i == 0: # POLITICO - FRONTPAGE

        print('Scraping Politico ...')

        list_links = get_links_politico('https://www.politico.com/', 'a')

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

            # calling function to create article from paragraphs
            create_article()

        politico = make_data(media_site='Politico')




    elif i == 1: # POLITICO - POLITICS

        print('Scraping Politico Politics ...')

        list_links = get_links_politico('https://www.politico.com/politics', 'a')

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

            # calling function to create article from paragraphs
            create_article()

        politico_politics = make_data(media_site='Politico')




    elif i == 2: # CNN

        print('Scraping CNN ...')

        # request url
        req = requests.get("https://edition.cnn.com")
        # create soup objects
        soup = BeautifulSoup(req.content, 'html5lib')

        json_data = get_links_cnn()

        # create empty lists for handling the data
        links = []

        for article in json_data['siblings']['articleList']:
            link = article['uri']
            title = article['headline']
            if link.startswith('/2020/09'):
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

            news_contents = create_article()

        cnn = make_data(media_site='CNN')




    elif i == 3: # CNN - POLITICS

        print('Scraping CNN Politics ...')

        # request url
        req = requests.get("https://edition.cnn.com/politics")
        # create soup objects
        soup = BeautifulSoup(req.content, 'html5lib')

        json_data = get_links_cnn()

        # create empty lists for handling the data
        links = []

        for article in json_data['siblings']['articleList']:
            link = article['uri']
            title = article['headline']
            if link.startswith('/2020/09'):
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

            news_contents = create_article()

        cnn_politics = make_data(media_site='CNN')




    elif i == 4: # FOX

        print('Scraping FOX ...')

        # url-specification
        req = requests.get("https://www.foxnews.com")
        # create soup objects
        soup = BeautifulSoup(req.content, 'html5lib')
        # find all articles
        news = soup.find_all('h2', class_='title')
        for i in news:
            if i.find('a')['href'].startswith('//www.foxnews.com'):
                link = 'https:' + i.find('a')['href']
                list_links.append(link)

        for n in np.arange(0, len(list_links)):

            # reading the content
            article = requests.get(list_links[n])
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

            # unifying paragraphs of no class
            for p in np.arange(0, len(body_none)):
                paragraph = body_none[p].get_text()
                list_paragraphs.append(paragraph)

            news_contents = create_article()

        fox = make_data('Fox News')




    elif i == 5: # FOX - POLITICS

        print('Scraping FOX Politics ...')

        list_links = get_all_website_links(websites[i])

        for n in np.arange(0, len(list_links)):

            # reading the content
            article = requests.get(list_links[n])
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

            # unifying paragraphs of no class
            for p in np.arange(0, len(body_none)):
                paragraph = body_none[p].get_text()
                list_paragraphs.append(paragraph)

            news_contents = create_article()

        fox_politics = make_data('Fox News')




    elif i == 6: # BREITBART

        print('Scraping Breitbart ...')

        list_links = get_links_breitbart('https://www.breitbart.com/')

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

            news_contents = create_article()

        breitbart = make_data('Breitbart')




    elif i == 7: # BREITBART - POLITICS

        print('Scraping Breitbart Politics ...')

        list_links = get_links_breitbart('https://www.breitbart.com/politics')

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

            news_contents = create_article()

        breitbart_politics = make_data('Breitbart')



    elif i == 8: # NEW YORK TIMES

        print('Scraping New York Times ...')

        list_links = get_links_nyt('https://www.nytimes.com/')

        for n in np.arange(0, len(list_links)):

            article = requests.get(list_links[n])
            article_content = article.content
            soup_article = BeautifulSoup(article_content, 'html5lib')

            # get title
            for c in np.arange(0, len(headlines_nyt)):
                title = str(soup_article.find_all('h1', class_=headlines_nyt[c]))
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

            news_contents = create_article()

        nyt = make_data('NYTimes')




    elif i == 9: # NEW YORK TIMES - POLITICS

        print('Scraping New York Times Politics ...')

        list_links = get_links_nyt('https://www.nytimes.com/politics')

        for n in np.arange(0, len(list_links)):

            article = requests.get(list_links[n])
            article_content = article.content
            soup_article = BeautifulSoup(article_content, 'html5lib')

            # get title
            for c in np.arange(0, len(headlines_nyt)):
                title = str(soup_article.find_all('h1', class_=headlines_nyt[c]))
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

            news_contents = create_article()

        nyt_politics = make_data('NYTimes')




    elif i == 10: # NBC

        print('Scraping NBC ...')

        list_links = get_links_nbc('https://www.nbcnews.com/')

        for n in np.arange(0, len(list_links)):

            article = requests.get(list_links[n])
            article_content = article.content
            soup_article = BeautifulSoup(article_content, 'html5lib')

            for c in np.arange(0, len(headlines_nbc)):
                current_class = headlines_nbc[c]
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

        nbc = make_data('NBC')




    elif i == 11: # NBC - POLITICS

        print('Scraping NBC Politics ...')

        list_links = get_links_nbc('https://www.nbcnews.com/politics')

        for n in np.arange(0, len(list_links)):

            article = requests.get(list_links[n])
            article_content = article.content
            soup_article = BeautifulSoup(article_content, 'html5lib')

            for c in np.arange(0, len(headlines_nbc)):
                current_class = headlines_nbc[c]
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

        nbc_politics = make_data('NBC')



    elif i == 12: # WALL STREET JOURNAL

        print('Scraping Wall Street Journal ...')

        url_list = get_links_wsj('https://www.wsj.com')
        signInPage = 'https://sso.accounts.dowjones.com/login?state=g6Fo2SBxM2VMZ0hJNnhwWUFmR056N0NmMlBPX3hydl9YQmR3WqN0aWTZIEt6WG1Hd3lzRXJwTWM0U2dzUExCVjRuV05QM0N1c1h1o2NpZNkgNWhzc0VBZE15MG1KVElDbkpOdkM5VFhFdzNWYTdqZk8&client=5hssEAdMy0mJTICnJNvC9TXEw3Va7jfO&protocol=oauth2&scope=openid%20idp_id%20roles%20email%20given_name%20family_name%20djid%20djUsername%20djStatus%20trackid%20tags%20prts&response_type=code&redirect_uri=https%3A%2F%2Faccounts.wsj.com%2Fauth%2Fsso%2Flogin&nonce=a3b676cb-4bdf-483d-ada6-3700a992b5f4&ui_locales=en-us-x-wsj-83-2&ns=prod%2Faccounts-wsj&savelogin=on#!/signin'

        options = webdriver.ChromeOptions()
        options.add_argument("headless")

        driver = webdriver.Chrome(executable_path='/Users/hojer/Desktop/projects/chromedriver', options=options)
        driver.get(signInPage)

        loginPageEmail = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'//input[@name="username"]')))
        loginPageEmail.send_keys(email)
        loginPagepassword = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'//input[@name="password"]')))
        loginPagepassword.send_keys(password)
        submitButton = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'//button[@type="submit"]')))
        submitButton.click()

        for n in np.arange(0, len(url_list)):
            url = url_list[n]
            if '/newsletter' in url:
                continue
            else:
                driver.get(url)

                try:
                    title = driver.find_element_by_class_name("wsj-article-headline").text
                    list_titles.append(title)

                    body = driver.find_elements_by_xpath('//div//p')

                    list_paragraphs = []

                    for i in body:
                        paragraph = i.text
                        list_paragraphs.append(paragraph)
                        final_article = " ".join(list_paragraphs)

                    news_contents.append(final_article)

                    list_links.append(url)

                except:
                    continue

        wsj = make_data('WSJ')


    elif i == 13: # WALL STREET JOURNAL POLITICS

        print('Scraping Wall Street Journal Politics')

        url_list = get_links_wsj('https://www.wsj.com/news/politics')
        signInPage = 'https://sso.accounts.dowjones.com/login?state=g6Fo2SBxM2VMZ0hJNnhwWUFmR056N0NmMlBPX3hydl9YQmR3WqN0aWTZIEt6WG1Hd3lzRXJwTWM0U2dzUExCVjRuV05QM0N1c1h1o2NpZNkgNWhzc0VBZE15MG1KVElDbkpOdkM5VFhFdzNWYTdqZk8&client=5hssEAdMy0mJTICnJNvC9TXEw3Va7jfO&protocol=oauth2&scope=openid%20idp_id%20roles%20email%20given_name%20family_name%20djid%20djUsername%20djStatus%20trackid%20tags%20prts&response_type=code&redirect_uri=https%3A%2F%2Faccounts.wsj.com%2Fauth%2Fsso%2Flogin&nonce=a3b676cb-4bdf-483d-ada6-3700a992b5f4&ui_locales=en-us-x-wsj-83-2&ns=prod%2Faccounts-wsj&savelogin=on#!/signin'

        options = webdriver.ChromeOptions()
        options.add_argument("headless")

        driver = webdriver.Chrome(executable_path='/Users/hojer/Desktop/projects/chromedriver', options=options)
        driver.get(signInPage)

        loginPageEmail = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'//input[@name="username"]')))
        loginPageEmail.send_keys(email)
        loginPagepassword = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'//input[@name="password"]')))
        loginPagepassword.send_keys(password)
        submitButton = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'//button[@type="submit"]')))
        submitButton.click()

        for n in np.arange(0, len(url_list)):
            url = url_list[n]
            if '/newsletter' in url:
                continue
            else:
                driver.get(url)

                try:
                    title = driver.find_element_by_class_name("wsj-article-headline").text
                    list_titles.append(title)

                    body = driver.find_elements_by_xpath('//div//p')

                    list_paragraphs = []

                    for i in body:
                        paragraph = i.text
                        list_paragraphs.append(paragraph)
                        final_article = " ".join(list_paragraphs)

                    news_contents.append(final_article)

                    list_links.append(url)

                except:
                    continue

        wsj_politics = make_data('WSJ')



main = [politico, cnn, fox, nyt, nbc, breitbart, wsj]
mainData = pd.concat(main)

politics = [politico_politics, cnn_politics, fox_politics,
            nyt_politics, nbc_politics, breitbart_politics,
            wsj_politics]
politicsData = pd.concat(politics)

mainData.to_excel(mainFilename)
politicsData.to_excel(politicsFilename)
