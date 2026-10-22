
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

endpoint = os.getenv("AOAI_CHAT_ENDPOINT")
key = os.getenv("AOAI_CHAT_KEY")
deployment = os.getenv("AOAI_CHAT_DEPLOYMENT")
api_version = os.getenv("AOAI_API_VERSION_GPT")

if not all([endpoint, key, deployment, api_version]):
    raise ValueError(
        "One or more AOAI settings are missing from .env"
    )

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=key,
    api_version=api_version,
)

try:
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "user",
                "content": "Reply with: Azure OpenAI is working!"
            }
        ],
        max_tokens=50,
    )
    print("SUCCESS: Azure OpenAI is responding.")
    print(response.choices[0].message.content)

except Exception as error:
    print("Azure OpenAI test failed.")
    print("Error type:", type(error).__name__)
    print("Details:", str(error))
