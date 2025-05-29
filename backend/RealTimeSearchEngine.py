from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

Username = os.getenv("Username")
Assistantname = os.getenv("Assistantname")
GroqAPIKey = os.getenv("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

System = "You are a helpful assistant."

# Ensure 'Data' directory exists
os.makedirs("Data", exist_ok=True)

chatlog_path = os.path.join("Data", "ChatLog.json")

# Load or create ChatLog.json
try:
    with open(chatlog_path, "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(chatlog_path, "w") as f:
        dump([], f)
    messages = []

def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for {query} are:\n[start]\n"
    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
    Answer += "[end]"
    return Answer

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "system", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

def Information():
    now = datetime.datetime.now()
    return (
        "Use This Real-time Information if needed:\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours, {now.strftime('%M')} minutes, {now.strftime('%S')} seconds.\n"
    )

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    if not prompt.strip():
        return "Please provide a valid input."

    # Load messages
    with open(chatlog_path, "r") as f:
        messages = load(f)

    messages.append({"role": "user", "content": prompt})

    search_result = GoogleSearch(prompt).strip()
    if search_result:
        SystemChatBot.append({"role": "system", "content": search_result})

    info = Information().strip()
    all_messages = [m for m in (SystemChatBot + [{"role": "system", "content": info}] + messages) if m["content"].strip()]

    # Call Groq API
    completion = client.chat.completions.create(
        model='compound-beta-mini',
        messages=all_messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
    )

    # Stream response
    Answer = ""
    for chunk in completion:
        Answer += chunk.choices[0].delta.content or ""

    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    with open(chatlog_path, "w") as f:
        dump(messages, f, indent=4)

    if SystemChatBot and SystemChatBot[-1]["role"] == "system":
        SystemChatBot.pop()

    return AnswerModifier(Answer)

if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
