import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY", "")  # Make sure to set your GROQ_API_KEY environment variable
)

# Validate API key
if not client.api_key:
    raise ValueError("Please set the GROQ_API_KEY environment variable")

print("🔑 Groq client initialized successfully")