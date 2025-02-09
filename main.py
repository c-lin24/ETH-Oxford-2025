from TwitterDataFetcher import influence_scores
from extract_news import get_crypto_news, relation_score, summariseURL, extract_keywords, list_to_query
from SummariseDebateData import debate_content, responses, total_likes_list

# crypto_news = get_crypto_news("(#Bitcoin OR #Ethereum OR #Crypto OR #Web3 OR #DeFi OR #NFT OR #Blockchain) OR Bitcoin OR Ethereum OR Crypto OR Web3 OR DeFi OR NFT OR Blockchain")
# urls = crypto_news['url']

for i in range(len(debate_content)):
    keywords = list_to_query(responses[i])
    crypto_news = get_crypto_news(keywords)
    urls = crypto_news['url']

    print(responses[i])
    print("Total like count: " + str(total_likes_list[i]))
    print("Influence score: " + str(influence_scores[i]) + "\n")

    relation_res = relation_score(urls, responses[i])
    if relation_res[1] < 85: print("No relevant event found.")
    else: print(summariseURL(relation_res[0]))

    print("\n" + "*" * 25 + "\n\n")

