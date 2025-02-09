import json
import re
import requests
import time
import os
import math
from datetime import datetime
from together import Together


from dotenv import load_dotenv
load_dotenv()

client = Together(api_key=os.getenv("PUBLIC_KEY_LLAMA"))

MAX_TWEET_COUNT = 3
MIN_REPLY_COUNT = 300
MIN_LIKES_COUNT = 1000
MAX_RUNTIME = 300
DEFAULT_QUERY = "(#Bitcoin OR #Ethereum OR #Crypto OR #Web3 OR #DeFi OR #NFT OR #Blockchain) OR Bitcoin OR Ethereum OR Crypto OR Web3 OR DeFi OR NFT OR Blockchain"
DEFAULT_START_DATE = "2023-01-01"
DEFAULT_END_DATE = "2025-02-09"

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

def find_tweet(pstart_date=DEFAULT_START_DATE, pend_date=DEFAULT_END_DATE, query=DEFAULT_QUERY):
    tweets_id = []
    main_posts = []
    comment_count = []

    payload = {
        "query": query,
        "sort": "Top",
        "start_date": pstart_date,
        "end_date": pend_date,
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


def parse_tweet(cid, pcomments, pstart_date=DEFAULT_START_DATE, pend_date=DEFAULT_END_DATE):
    payload2 = {
        "query": "conversation_id:" + cid,
        "sort": "Top",
        "start_date": pstart_date,
        "end_date": pend_date,
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


choice = 0
while choice != 1 and choice != 2:
    choice = int(input("1. General crypto information \n2. Customised search \nPlease enter an option (1 or 2): "))
    if choice == 1:
        while len(all_tweet_ids) < MAX_TWEET_COUNT:
            all_tweet_ids, comments, comment_counts = find_tweet()

            if time.time() - start_time > MAX_RUNTIME:
                raise Exception("Stopping program due to runtime limit")

        for i in range(MAX_TWEET_COUNT):
            all_comments.append(parse_tweet(all_tweet_ids[i], comments[i]))
            influence_scores.append(calculate_influence_score(all_comments[i][0]["main_followers_count"],
                                                              all_comments[i][0]["main_like_count"], comment_counts[i]))

    elif choice == 2:
        keyword_choice = input("Please enter a word(s) or phrase(s) to search: ")
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=[
                {"role": "user", "content": f"""Find a list of upto 10 related words to the following text:
                                                {keyword_choice}. The words must all be preceded by # and
                                                separated by OR, followed by OR, and then do the same disjunction of
                                                 words without the preceding #s. And your
                                                 output should be this entire disjunction of words only"""}]
        )
        query = response.choices[0].message.content

        print("Please enter a time range to filter the tweets.")
        while True:
            try:
                start_date_choice = input("Enter a start date (yyyy-mm-dd): ")
                end_date_choice = input("Enter an end date (yyyy-mm-dd): ")

                start_date = datetime.strptime(start_date_choice, "%Y-%m-%d")
                end_date = datetime.strptime(end_date_choice, "%Y-%m-%d")

                if start_date > end_date:
                    print("Error: Start date must be before the end date. Try again.")
                    continue
                break

            except ValueError:
                print("Invalid date format. Please enter dates in YYYY-MM-DD format.")


        while len(all_tweet_ids) < MAX_TWEET_COUNT:
            all_tweet_ids, comments, comment_counts = find_tweet(start_date_choice, end_date_choice, query)

            if time.time() - start_time > MAX_RUNTIME:
                raise Exception("Stopping program. Could not find tweet in reasonable time.")

        for i in range(MAX_TWEET_COUNT):
            all_comments.append(parse_tweet(all_tweet_ids[i], comments[i], start_date_choice, end_date_choice))
            influence_scores.append(calculate_influence_score(all_comments[i][0]["main_followers_count"],
                                                              all_comments[i][0]["main_like_count"], comment_counts[i]))


    else:
        print("\nPlease enter either 1 or 2")
        choice = int(input("1. General crypto information \n2. Customised search \nPlease enter an option (1 or 2): "))

#for i in range(MAX_TWEET_COUNT):
#    all_comments.append(parse_tweet(all_tweet_ids[i], comments[i]))
#    influence_scores.append(calculate_influence_score(all_comments[i][0]["main_followers_count"], all_comments[i][0]["main_like_count"], comment_counts[i]))
