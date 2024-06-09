from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import time
from IPython.display import clear_output
import requests
import json

load_dotenv()

def get_products(prodname):
  headers= { 'Accept': 'application/json' }    
  r = requests.get('https://services.odata.org/V2/Northwind/Northwind.svc/Products?$top=2&$select=ProductID,ProductName,UnitPrice', headers=headers)
  results = r.json()
  return json.dumps(results)

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version="2024-05-01-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

#update thread_id and assistant_id with actual values
assistant_id = ""
thread_id = ""

message = client.beta.threads.messages.create(
  thread_id=thread_id,
  role="user",
  content="Show me products available for product name Ch in a tabular formmat. Table header, columns and rows should have consistent spacing.",
)

run = client.beta.threads.runs.create_and_poll(
  thread_id=thread_id,
  assistant_id=assistant_id,
)
 
#print(run)
 
# Define the list to store tool outputs
tool_outputs = []

if(run.required_action != None):
  # Loop through each tool in the required action section
  print(run.required_action.submit_tool_outputs.tool_calls)
  for tool in run.required_action.submit_tool_outputs.tool_calls:
    if tool.function.name == "get_products":

      tool_outputs.append({
        "tool_call_id": tool.id,
        "output": get_products("test")
      })

 
# Submit all tool outputs at once after collecting them in a list
if tool_outputs:
  try:
    run = client.beta.threads.runs.submit_tool_outputs_and_poll(
      thread_id=thread_id,
      run_id=run.id,
      tool_outputs=tool_outputs
    )
    print("Tool outputs submitted successfully.")
  except Exception as e:
    print("Failed to submit tool outputs:", e)
else:
  print("No tool outputs to submit.")
 
while run.status not in ["completed", "cancelled", "expired", "failed"]:
    time.sleep(5)
    run = client.beta.threads.runs.retrieve(thread_id=thread_id,run_id=run.id)
    status = run.status
    print(f'Status: {status}')
    print(run.last_error)

messages = client.beta.threads.messages.list(
  thread_id=thread_id
)

json_response = json.loads(messages.model_dump_json(indent=2))
print(json_response["data"][0]["content"][0]['text']['value'])



