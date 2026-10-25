from google import genai
import os

# The client gets the API key from the environment variable `GEMINI_API_KEY`.

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_response(prompt):
  response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt+"(response should be in 2 sentence)"
  )
  return(response.text)

prompt=input("Enter the question:")
print(get_response(prompt))
