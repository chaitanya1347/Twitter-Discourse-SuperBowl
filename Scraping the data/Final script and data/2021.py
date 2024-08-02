import datetime as dt
import csv
import time
from unicodedata import name
import tweepy
import pandas
from csv import DictReader, DictWriter


######################################### GET QUERIES ###################################################
def generate_query(location):
    ## Change items of query_terms list wrt your events
    query_terms = ["Super Bowl", "\"superbowl\"", "\"superbowl2019\"", "\"superbowl2019\"", "\"#superbowlnaespn\"",
                   "\"#superbowlweekend\"", "\"SUPERBOWL\"", "\"SuperBowl\"", "\"#superBowl\""]
    query = ""
    for term in query_terms:
        query = query + " " + term + " -is:retweet place_country:{0}".format(location) + "   OR"
    return query[1:-3]


######################################### GET TWEETS #####################################################
def gather_tweets(country, filename, start_year, years_back):
    header = ["tweet_id", "text", "author_id", "created_at", "place_id", "like_count", "quote_count", "reply_count",
              "retweet_count", "conversation_id", "in_reply_to_user_id"]
    with open(filename + '.csv', 'a', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
    query = generate_query(country)
    client = tweepy.Client(
        "AAAAAAAAAAAAAAAAAAAAAFcMZAEAAAAALRP%2BfjSOiikXDHTI%2FG%2FJ6gPDfno%3DOOtIVKcPEXmTGdngCAaVy8qoZOlUbcqDSlp6m2LZJZTRHsZl09")
    current_year = start_year
    for i in range(years_back):
        current_year = start_year - i
        print("Starting year " + str(current_year))
        for j in range(4, 10):
            print("Starting year " + str(current_year) + " and day " + str(j))
            for k in range(0, 24):
                tweets = client.search_all_tweets(
                    query=query,
                    start_time=dt.datetime(current_year, 2, j, k, 0, 0),
                    end_time=dt.datetime(current_year, 2, j, k, 59, 59),
                    max_results=250,
                    expansions=['author_id', 'geo.place_id', 'in_reply_to_user_id'],
                    place_fields=['country'],
                    user_fields=['id', 'location', 'public_metrics'],
                    tweet_fields=['id', 'created_at', 'text', 'in_reply_to_user_id', 'public_metrics',
                                  'conversation_id']
                )

                with open(filename + '.csv', 'a', encoding="utf-8") as f:
                    writer = csv.writer(f)
                    if tweets.data:
                        for tweet in tweets.data:
                            place_id = tweet.data['geo']['place_id'] if 'geo' in tweet.data and 'place_id' in \
                                                                        tweet.data['geo'] else "N/A"
                            in_reply_to_user_id = tweet.data[
                                'in_reply_to_user_id'] if 'in_reply_to_user_id' in tweet.data else "N/A"

                            data = [
                                tweet.data['id'],
                                tweet.data['text'],
                                tweet.data['author_id'],
                                tweet.data['created_at'],
                                place_id,
                                tweet.data['public_metrics']['like_count'],
                                tweet.data['public_metrics']['quote_count'],
                                tweet.data['public_metrics']['reply_count'],
                                tweet.data['public_metrics']['retweet_count'],
                                tweet.data['conversation_id'],
                                in_reply_to_user_id,
                            ]

                            writer.writerow(data)
                    else:
                        print('no tweets in hour', k)
                time.sleep(5)


######################################################### GET REPLIES ##################################################
def get_replies(filename, year):
    filename_csv = filename + ".csv"
    filename_reply = filename + "_replies" + ".csv"
    data = pandas.read_csv(filename_csv, header=0)
    conv_ids = list(data.conversation_id)
    client = tweepy.Client(
        "AAAAAAAAAAAAAAAAAAAAAFcMZAEAAAAALRP%2BfjSOiikXDHTI%2FG%2FJ6gPDfno%3DOOtIVKcPEXmTGdngCAaVy8qoZOlUbcqDSlp6m2LZJZTRHsZl09")
    header = ["tweet_id", "text", "author_id", "created_at", "place_id", "like_count", "quote_count", "reply_count",
              "retweet_count", "conversation_id", "in_reply_to_user_id"]
    with open(filename_reply, 'a', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
    i = 0
    while i < len(conv_ids):
        subsection = conv_ids[i:i + 26]
        query = ""
        for cid in subsection:
            query += "conversation_id:" + str(cid) + " OR "
        query = query[:-4]
        tweets = client.search_all_tweets(
            query=query,
            start_time=dt.datetime(year, 2, 4, 0, 0, 0),
            end_time=dt.datetime(year, 2, 10, 23, 59, 59),
            max_results=250,
            expansions=['author_id', 'geo.place_id', 'in_reply_to_user_id'],
            place_fields=['country'],
            user_fields=['id', 'location', 'public_metrics'],
            tweet_fields=['id', 'created_at', 'text', 'in_reply_to_user_id', 'public_metrics', 'conversation_id']
        )
        if tweets is not None and tweets.data is not None:
            with open(filename_reply, 'a', encoding="utf-8") as f:
                writer = csv.writer(f)
                if tweets.data:
                    for tweet in tweets.data:
                        place_id = tweet.data['geo']['place_id'] if 'geo' in tweet.data and 'place_id' in tweet.data[
                            'geo'] else "N/A"
                        in_reply_to_user_id = tweet.data[
                            'in_reply_to_user_id'] if 'in_reply_to_user_id' in tweet.data else "N/A"

                        data = [
                            tweet.data['id'],
                            tweet.data['text'],
                            tweet.data['author_id'],
                            tweet.data['created_at'],
                            place_id,
                            tweet.data['public_metrics']['like_count'],
                            tweet.data['public_metrics']['quote_count'],
                            tweet.data['public_metrics']['reply_count'],
                            tweet.data['public_metrics']['retweet_count'],
                            tweet.data['conversation_id'],
                            in_reply_to_user_id,
                        ]
                        writer.writerow(data)
                else:
                    print('no reply today')
        time.sleep(5)
        i += 26
        print(i)


########################################### TO TEXT #################################################
def tweets_to_LIWC(filename):
    with open(filename + '.csv', 'r', encoding="utf8") as infile, open("text_" + filename + '.txt', 'w',
                                                                       encoding="utf8") as outfile:
        reader = DictReader(infile)
        for row in reader:
            outfile.write(row['text'] + '\n')


if __name__ == "__main__":
    gather_tweets("GB", "GB_2021", 2021, 1)  # <<<<<<<--------- Change here
    time.sleep(2)
    get_replies("GB_2021", 2021)  # <<<<<<<--------- Change here
    time.sleep(2)
    tweets_to_LIWC("GB_2021")