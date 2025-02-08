import os
import requests
import pandas as pd
from newspaper import Article
from together import Together
from dotenv import load_dotenv

load_dotenv()

client = Together(api_key=os.getenv("PUBLIC_KEY_LLAMA"))

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
                           100. Your answer should ONLY consist of this number and no other text. The score should
                           take into account how many keywords are shared in between the summary and the articles.
                           But the context of the summary and the articles should take presence over shared keywords.
                           Every time you get an article it will start with the prefix string of "An article is given:"
                           """
    }]

    for url in urls:
        article = Article(url)

        article.download()
        article.parse()

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
