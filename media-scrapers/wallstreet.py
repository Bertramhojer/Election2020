# Import modules
import requests
import re
from bs4 import BeautifulSoup
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
import time



def get_news_wsj():
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
            if domain_name not in href:
                continue
            if len(re.findall('/articles/', href)) > 0:
                urls.append(href)

        return urls

    list_links = get_all_website_links('https://www.wsj.com')

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

    list_titles = []
    news_contents = []
    url_list = []

    for n in np.arange(0, len(list_links)):
        url = list_links[n]
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

                url_list.append(url)

            except:
                continue

    # create dataframe
    data = pd.DataFrame(
        {'Title': list_titles,
        'Content': news_contents,
        'Link': url_list,
        'Date': datetime.date(datetime.now()),
        'Organization': 'WSJ'}
        )

    return data

data = get_news_wsj()
data.to_excel('wsjNews.xlsx')
