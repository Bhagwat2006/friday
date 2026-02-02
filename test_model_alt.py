from groq import Groq
from config import settings
import json

client = Groq(api_key=settings.GROQ_API_KEY)

try:
    completion = client.chat.completions.create(
        messages=[{"role": "system", "content": "You are a helper. Respond in JSON."}, {"role": "user", "content": "Hello"}],
        model="meta-llama/llama-4-maverick-17b-128e-instruct",
        response_format={"type": "json_object"}, 
    )
    print(completion.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")
