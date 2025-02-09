# 📌 Crypto Twitter Debate Analyzer -  ETH Oxford 2025
We have built an analysis tool that locates debates between influential Crypto Twitter accounts, generates summaries, detects underlying real-world events that may have triggered/influenced the debate.

## 🔧 Project requirements:
- Use the provided API to fetch and analyze Twitter data to identify conflicts/debates in the crypto space (contact us on Discord for API access if you want to do this challenge, or come to our booth in the 
mezzanine)
- Measuring issue importance, influence of involved accounts, and stance of participants
- Generate detailed summaries of the debate and the opposing viewpoints
- It should run on Linux and WSL, you can use docker to make it easy to deploy
- Clear documentation of the analysis methodology and scoring algorithms, and a video demonstration of the system in action

## 🔀 Data Pipeline:
- High-engagement tweets are retrieved via the <a href="https://docs.datura.ai/capabilities/twitter-search">Datura Basic Twitter Search API</a>
- Tweets provide the conversation_ids needed to retrieve the tweeted replies
- Main tweet and tweeted replies comprise the debate information - text body, username, like count, etc.
- Debate information is then fed into the <a href="https://www.llama.com">LLama 3.3 70B</a> model alongside a prompt to generate the debate summary
- Debate summary is then processed to extract key words by a method from the <a href="https://pypi.org/project/rake-nltk/">rake-nltk</a> library
- Key words are then supplied into the <a href="https://www.llama.com">Llama model</a> to filter for only crypto-related keywords
- Filtered key words are then passed to the <a href="https://newsapi.org/">NewsAPI</a> and the 15 most relevant articles are fetched
- Articles, alongside the summary debate, are then supplied into the <a href="https://www.llama.com">Llama model</a> to generate an approximate relavance score
- Article with the greatest relevance score is supplied into the <a href="https://www.llama.com">Llama model</a> to summarise
- Debate summary, debate metrics and article summary are output

## 🔑 Environment Variables
`API_KEY_NEWSAPI` = NewsAPI API key<br>
`API_KEY_LLAMA` = Meta Llama API key<br>
`API_KEY` = Datura Twitter API key<br>
