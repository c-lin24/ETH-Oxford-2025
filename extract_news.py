import os
import requests
import pandas as pd
from newspaper import Article
from together import Together
from dotenv import load_dotenv
from rake_nltk import Rake

load_dotenv()

client = Together(api_key=os.getenv("PUBLIC_KEY_LLAMA"))

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

def get_crypto_news(query):
    API_KEY = os.getenv("PUBLIC_KEY_NEWSAPI")
    url = f"https://newsapi.org/v2/everything"

    params = {
        "apiKey": API_KEY,
        "q": query,
        "language": "en",
        "sortBy": "popularity",
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        news_data = response.json()
        return pd.DataFrame(news_data["articles"][:15])  # Convert to DataFrame

    return f"Error fetching news: {response.status_code}"


def relation_score(urls, summary):
    list_of_articles = []

    conversation_history = [{"role": "system",
                           "content": f"""Hello. The following prompts will be about crypto currencies. I want you to
                           take the following summary and find how closely it connects to each of the articles I give you.
                           The summary is: {summary}
                           You must compare all articles to this summary and give them a relatability score from 0 to
                           100. Your answer should ONLY consist of this number and no other text. The score should heavily
                           take into account how many keywords and keyphrases are shared in between the summary and the articles.
                           The context of the summary and the articles should also be given high priority equally as the keywords and keyphrases.
                           Other clues that connect the article to the summary should also be taken into account but given less priority than these two.
                           70 is the threshold for articles that may actually have a link with the summary.
                           Every time you get an article it will start with the prefix string of "An article is given:"
                           """
    }]

    for url in urls:
        article = Article(url, headers=headers)

        try:
            article.download()
            article.parse()
        except Exception as e:
            print(f"Skipping article: {url} (Error: {e})")
            continue

        conversation_history.append({"role": "user", "content": f"An article is given: {article.text[:1500]}"})

        relatability = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=conversation_history,
        )
        relatability_text = relatability.choices[0].message.content
        print(relatability_text)

        conversation_history.append({"role": "assistant", "content": relatability_text})

        list_of_articles.append((article.url, int(relatability_text)))

    return max(list_of_articles, key=lambda x: x[1])


def summariseURL(url):
    article = Article(url, headers=headers)

    try:
        article.download()
        article.parse()
    except Exception as e:
        print(f"Skipping article: {url} (Error: {e})")
        return None

    summary = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=[{"role": "user", "content": f"I am giving you an article as text. Summarise the information in the article.{article.text[:4000]}"}]
    )

    return summary.choices[0].message.content


def extract_keywords(text):
    rake = Rake()
    rake.extract_keywords_from_text(text)
    return rake.get_ranked_phrases()  # Returns ranked keywords


def list_to_query(raw_string_list):
    extracted = extract_keywords(raw_string_list)
    extracted1 = []
    for s in extracted:
        extracted1.append(s.replace(" ", ""))
    return " OR ".join(extracted1)





print(list_to_query("What has the decentralised blockchain model to our society with the president Donald Trump is quite atrocious to be frank"))