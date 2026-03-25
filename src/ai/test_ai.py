import os
from openai import OpenAI

key = os.getenv("OPENAI_API_KEY")
print("KEY HEAD:", key[:12] if key else None)
print("KEY TAIL:", key[-6:] if key else None)

client = OpenAI(api_key=key)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Pythonエンジニアの仕事内容を一文で説明して"}
    ]
)

print(response.choices[0].message.content)