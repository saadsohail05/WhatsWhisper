from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from string import Template

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Modify prompt to use $-style placeholders
prompt = Template('''Act as a JSON task parser. Convert the following text into scheduled tasks.
Output MUST be a valid JSON array using DOUBLE QUOTES only. Example:
[
    {
        "title": "Team Meeting",
        "date": "2024-03-20",
        "start_time": "14:00",
        "end_time": "15:00",
        "description": "Regular team sync"
    }
]

Input text: $user_input''')

def process_tasks(user_input):
    current_date = datetime.now().strftime("%Y-%m-%d")
    formatted_prompt = prompt.substitute(current_date=current_date, user_input=user_input)
    
    try:
        completion = client.chat.completions.create(
            model="microsoft/phi-3.5-mini-128k-instruct",
            messages=[
                {"role": "user", "content": formatted_prompt}
            ],
            temperature=0.1
        )
        
        response_text = completion.choices[0].message.content
        
        # Extract JSON from response
        try:
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            return []
        except json.JSONDecodeError:
            return []
    except Exception as e:
        raise