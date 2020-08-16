# import modules
import tweepy
import time
import pandas as pd
import numpy as np
import re
import openpyxl
import datetime
from candidateList import candidates
import keys

# specify input variables
count = int(input('specify item count: '))

date1 = input('Start date (YYYY-MM-DD): ')
year, month, day = map(int, date1.split('-'))
startDate = datetime.datetime(year, month, day)

date2 = input('End date (YYYY-MM-DD): ')
year, month, day = map(int, date2.split('-'))
endDate = datetime.datetime(year, month, day)

filename = str(f'{date1}_{date2}.xlsx')


# specify filename
timer = 0


# specify access keys
# API's
consumer_key = keys.consumer_key
consumer_secret = keys.consumer_secret
# Tokens
access_token = keys.access_token
access_token_secret = keys.access_token_secret

# Authentication process
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)


# specify empty  DataFrame
data = pd.DataFrame(columns = ['name', 'username', 'twitter_name', 'text', 'date', 'time',
                                'hashtags', 'likes', 'retweets', 'retweet',
                                'tweet_count', 'position', 'party', 'state',
                                'links', 'acc_created'])


# run loop
for candidate in candidates.items():


    twitter_handle = candidate[0]
    position = candidate[1][0]
    party = candidate[1][1]
    state = candidate[1][2]
    name = candidate[1][3]


    tweets = tweepy.Cursor(api.user_timeline,
                            id = twitter_handle,
                            tweet_mode='extended').items(count)

    tweet_list = [tweet for tweet in tweets]

    for tweet in tweet_list:

        if tweet.created_at < endDate and tweet.created_at > startDate:

            twitter_name = tweet.user.name
            username = tweet.user.screen_name
            timestamp = tweet.created_at
            user_created = tweet.user.created_at
            tweet_count = tweet.user.statuses_count
            try:
                text = tweet.retweeted_status.full_text
                likes = tweet.retweeted_status.favorite_count
                retweetcount = tweet.retweeted_status.retweet_count
                hashtags = tweet.retweeted_status.entities['hashtags']
                retweet = 'YES'
            except AttributeError:
                text = tweet.full_text
                likes = tweet.favorite_count
                retweetcount = tweet.retweet_count
                hashtags = tweet.entities['hashtags']
                retweet = 'NO'

            date, time = str(timestamp).split()

            # get links
            links = list(re.findall('(https?:\/\/)(\s)?(www\.)?(\s?)(\w+\.)*([\w\-\s]+\/)*([\w-]+)\/?',
                                text))
            if len(links) > 0:
                links = [''.join(link) for link in links]

            current_tweet = [name, username, twitter_name, text, date, time, hashtags, likes,
                                retweetcount, retweet, tweet_count, position,
                                party, state, links, user_created]

            data.loc[len(data)] = current_tweet

            timer += 1
            print(timer, ')', 'tweet from', twitter_handle, 'filed')


data.to_excel(filename)
