from together import Together
import TwitterDataFetcher as tdf
import os
#from dotenv import load_dotenv
#
#load_dotenv()

debate_content = tdf.all_comments

#client = Together(api_key=os.getenv("PUBLIC_KEY_LLAMA"))

responses = []
total_likes_list = []

for debate in debate_content:
    response = tdf.client.chat.completions.create(
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
                                            "itself, no preceding 'title:'), username (follow with: (for) or (against) "
                                            "depending on whether the user is arguing for the subject or arguing "
                                            "in favour of counter argument) and '- follower_count followers' "
                                            "of first major account (precede with 1.), and similarly username and "
                                            "follower count of second major account (precede with 2.), a few key "
                                            "points (indicated with bullet points with -) for each of the two opposing "
                                            "arguments. "
                                              + str(debate)}]
    )
    responses.append(response.choices[0].message.content)

    total_likes_list.append(debate[0]["main_like_count"] + sum(t["reply_like_count"] for t in debate[1:]))
