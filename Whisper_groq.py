import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variable
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set")

# Initialize the Groq client with API key
client = Groq(api_key=api_key)

# Specify the path to the audio file
filename = os.path.dirname(__file__) + "/audio.mpga" # Replace with your audio file!

# Open the audio file
with open(filename, "rb") as file:
    # Create a transcription of the audio file
    transcription = client.audio.transcriptions.create(
      file=(filename, file.read()), # Required audio file
      model="whisper-large-v3-turbo", # Required model to use for transcription
      prompt="Specify context or spelling",  # Optional
      response_format="json",  # Optional
      language="en",  # Optional
      temperature=0.0  # Optional
    )
    # Print the transcription text
    print(transcription.text)