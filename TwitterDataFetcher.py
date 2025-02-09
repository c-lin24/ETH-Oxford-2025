import json
import re
import requests
import time
import os
import math
import numpy as np

from dotenv import load_dotenv
load_dotenv()

MAX_TWEET_COUNT = 3
MIN_REPLY_COUNT = 300
MIN_LIKES_COUNT = 1000
MAX_RUNTIME = 300

all_tweet_ids = []
url = "https://apis.datura.ai/twitter"
all_comments = []
comments = []
comment_counts = []
influence_scores = []

start_time = time.time()

headers = {
        "Authorization": os.getenv("API_KEY"),
        "Content-Type": "application/json"
}

def find_tweet():
    tweets_id = []
    main_posts = []
    comment_count = []

    payload = {
        "query": "(#Bitcoin OR #Ethereum OR #Crypto OR #Web3 OR #DeFi OR #NFT OR #Blockchain) OR Bitcoin OR Ethereum OR Crypto OR Web3 OR DeFi OR NFT OR Blockchain",
        "sort": "Top",
        "start_date": "2024-06-01",
        "end_date": "2025-02-01",
        "lang": "en",
        "verified": True,
        "blue_verified": True,
        "min_replies": 100,
        "min_followers": 100,
        "min_retweets": 100,
        "min_likes": 500
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    raw_data = response.__dict__['_content']
    parsed_data = json.loads(raw_data.decode("utf-8"))

    for data in parsed_data:
        if data["reply_count"] > MIN_REPLY_COUNT and data["like_count"] > MIN_LIKES_COUNT:
            original_post = [{"main_text" : data["text"],
             "main_username" : data["user"]["username"],
             "main_followers_count": data["user"]["followers_count"],
             "main_like_count": data["like_count"]}]

            tweets_id.append(data["id"])
            main_posts.append(original_post)
            comment_count.append(data["reply_count"])

        if len(tweets_id) >= MAX_TWEET_COUNT:
            break

    return tweets_id, main_posts, comment_count


def parse_tweet(cid, pcomments):
    payload2 = {
        "query": "conversation_id:" + cid,
        "sort": "Top",
        "start_date": "2024-06-01",
        "end_date": "2025-02-01",
        "lang": "en"
    }

    response2 = requests.request("POST", url, json=payload2, headers=headers)
    raw_data2 = response2.__dict__['_content']
    parsed_data2 = json.loads(raw_data2.decode("utf-8"))

    for p in parsed_data2:
        text = {"reply_text": re.sub(r"^(?:@\S+\s*)+", "", str(p["text"])),
                "reply_username": str(p["user"]["username"]),
                "reply_followers_count": int(p["user"]["followers_count"]),
                "reply_like_count": int(p["like_count"])}
        pcomments.append(text)

    pcomments[1:] = sorted(pcomments[1:], key=lambda x: x["reply_like_count"], reverse=True)
    return pcomments

def calculate_influence_score(followers, likes, comment):
    alpha = 2.0
    beta = 1.2

    log_followers = math.log2(1 + followers)
    influence_score = alpha * log_followers + beta * (likes + comment)
    return round(influence_score/100, 2)


while len(all_tweet_ids) < MAX_TWEET_COUNT:
    all_tweet_ids, comments, comment_counts = find_tweet()

    if time.time() - start_time > MAX_RUNTIME:
        raise Exception("Stopping program due to runtime limit")


for i in range(MAX_TWEET_COUNT):
    all_comments.append(parse_tweet(all_tweet_ids[i], comments[i]))
    influence_scores.append(calculate_influence_score(all_comments[i][0]["main_followers_count"], all_comments[i][0]["main_like_count"], comment_counts[i]))

print(influence_scores)
