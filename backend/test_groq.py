
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: Groq works",
            }
        ],
        max_tokens=30,
        timeout=30,
    )

    print("SUCCESS:", response.choices[0].message.content)

except Exception as exc:
    print("ERROR TYPE:", type(exc).__name__)
    print("ERROR DETAILS:", str(exc))
