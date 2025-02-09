import json
import re
import requests
import time
import os

from dotenv import load_dotenv
load_dotenv()

MAX_TWEET_COUNT = 3
MIN_REPLY_COUNT = 300
MIN_LIKES_COUNT = 1000
MAX_RUNTIME = 20

all_tweet_ids = []
url = "https://apis.datura.ai/twitter"
all_comments = []
comments = []

start_time = time.time()

headers = {
        "Authorization": os.getenv("API_KEY"),
        "Content-Type": "application/json"
}

def find_tweet():
    tweets_id = []
    main_posts = []
    payload = {
        "query": "(#Bitcoin OR #Ethereum OR #Crypto OR #Web3 OR #DeFi OR #NFT OR #Blockchain) OR Bitcoin OR Ethereum OR Crypto OR Web3 OR DeFi OR NFT OR Blockchain",
        "sort": "Top",
        "start_date": "2024-06-01",
        "end_date": "2025-02-01",
        "lang": "en",
        "verified": True,
        "blue_verified": True,
        "min_replies": 100,
        "min_followers": 100,  # Adjust as needed
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

        if len(tweets_id) >= MAX_TWEET_COUNT:
            break

    return tweets_id, main_posts


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


########################
#MAIN#
########################

while len(all_tweet_ids) < MAX_TWEET_COUNT:
    all_tweet_ids, comments = find_tweet()
    if time.time() - start_time > MAX_RUNTIME:
        raise Exception("Stopping program due to runtime limit")

for i in range(MAX_TWEET_COUNT):
    all_comments.append(parse_tweet(all_tweet_ids[i], comments[i]))

