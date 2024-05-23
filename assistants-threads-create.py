from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import time
from IPython.display import clear_output
import requests

load_dotenv()
    
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version="2024-05-01-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )


assistant = client.beta.assistants.create(
  instructions="You are a products expert. Use the provided functions to answer questions. You are able to show JSON data in a nice tabular format to user",
  model="gpt-4",
  tools=[
      {
      "type": "function",
      "function": {
        "name": "get_products",
        "description": "Get the list of products available in the store",
        "parameters": {
          "type": "object",
          "properties": {
              "prodname": {
              "type": "string",
              "description": "product name"
            }
          },
          "required": ["prodname"]
        }
      }
    }
  ]
)

thread = client.beta.threads.create()

print(assistant.id)
print(thread.id)