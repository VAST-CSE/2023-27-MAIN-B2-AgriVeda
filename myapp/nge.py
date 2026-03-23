from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key="AIzaSyB-Y1bb5EvPBSElsmrGmymYQXYS59J4YVU")

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Explain how AI works in a few words"
)
print(response.text)
