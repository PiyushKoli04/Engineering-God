from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
from RealTimeSearchEngine import RealtimeSearchEngine,AnswerModifier,GoogleSearch
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = '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'

client=Groq(api_key=GroqAPIKey)

messages = []

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

EngineeringTips = """
You are expected to assist with subjects like:
- Applied Mathematics
- Engineering Physics and Chemistry
- Programming (Python, C++)
- Data structures and algorithms
- Electronics, Mechanical, and Civil basics
You may also help with college advice, project ideas, or learning resources.
"""
SystemChatBot.insert(1, {"role": "system", "content": EngineeringTips})


try:
    with open(r"Data\ChatLog.json","r") as f:
        messages = load(f)
    
except FileNotFoundError:
    with open(r"Data\ChatLog.json","w") as f:
        dump([],f)

def RealtimeInformation():
    currrent_date_time = datetime.datetime.now()
    day= currrent_date_time.strftime("%A")
    date= currrent_date_time.strftime("%d")
    month= currrent_date_time.strftime("%B")
    year= currrent_date_time.strftime("%Y")
    hour= currrent_date_time.strftime("%H")
    minute= currrent_date_time.strftime("%M")
    second= currrent_date_time.strftime("%S")

    data= f"Please use this real-time information if needed,\n"
    data+= f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data+= f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
    return data

def AnswerModifier(Answer):
    lines= Answer.split('\n')
    non_empty_lines =[ line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def estimate_tokens(text):
    # Approximate: 1 token ≈ 4 characters in English (safe side)
    return len(text) // 4

def count_total_tokens(messages):
    return sum(estimate_tokens(m["content"]) for m in messages)

def trim_messages_to_fit(messages, max_prompt_tokens=6500):
    trimmed = []
    total = 0
    for m in reversed(messages):  # Start trimming from the end
        tokens = estimate_tokens(m["content"])
        if total + tokens > max_prompt_tokens:
            break
        total += tokens
        trimmed.insert(0, m)
    return trimmed

def ChatBot(Query):
    try:
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)

        messages.append({"role": "user", "content": Query})

        # Combine full prompt
        full_prompt = SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages

        # Trim to fit under ~6500 tokens (prompt side)
        safe_prompt = trim_messages_to_fit(full_prompt, max_prompt_tokens=6500)

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=safe_prompt,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("<\s>", "")

        messages.append({"role": "assistant", "content": Answer})

        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query)




def is_web_query(query):
    search_keywords = [
        "latest", "current",
        "top", "recent", "define", "explain", "news", "trending"
    ]
    return any(keyword in query.lower() for keyword in search_keywords)




if __name__=="__main__":
    while True:
        prompt = input("Enter your query: ")

        try:
            if is_web_query(prompt):
                print(RealtimeSearchEngine(prompt))
            else:
                print(ChatBot(prompt))  # Your regular assistant logic
        except Exception as e:
            print(f"Error: {e}")
            
