from together import Together
import TwitterDataFetcher as tdf

debate_content = tdf.all_comments

client = Together(api_key="849b3d33939c82557e2e389ca405d7c6024021315639c4650c2e27e897110d10")

responses = []
total_likes_list = []

for debate in debate_content:
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=[{"role": "user", "content": "The following data is a list of dictionaries corresponding to crypto "
                                            "tweets, with the first item corresponding to the main tweet, and the "
                                            "subsequent items corresponding to the replies. The tweet together "
                                            "with the replies form a debate. Use the 'main_text' value of the "
                                            "first item to provide a suitable title for the crypto debate topic. "
                                            "Use the 'username' values and the 'follower_count' values to determine "
                                            "the two most influential users. Generate the key points of the two "
                                            "opposing arguments using the the main tweet and its replies. If there is "
                                            "no counter argument, a comment stating this will suffice. "
                                            "Structure your response in the following order: title (just the title "
                                            "itself, no preceding 'title:'), username and '- follower_count followers' "
                                            "of first major account (precede with 1.), and similarly username and "
                                            "follower count of second major account (precede with 2.), a few key "
                                            "points (indicated with bullet points with -) for each of the two opposing "
                                            "arguments. "
                                              + str(debate)}]
    )
    responses.append(response.choices[0].message.content)

    total_likes_list.append(debate[0]["main_like_count"] + sum(t["reply_like_count"] for t in debate[1:]))

for i in range(tdf.MAX_TWEET_COUNT):
    print(responses[i])
    print("Total like count: " + str(total_likes_list[i]))
    print("\n")



