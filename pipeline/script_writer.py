import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load env variables if not already loaded
load_dotenv()

def get_mock_script(topic):
    return [
        f"Here is a fascinating fact about {topic}.",
        "Did you know it changes everything we know?",
        "Experts believe this is just the beginning.",
        "Imagine what the future holds for this.",
        "Follow for more amazing insights!"
    ]

def write_script(topic):
    """
    Generates a 4-6 line script for a reel based on the topic using Google Gemini.
    Returns a list of strings.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: Missing GEMINI_API_KEY. Using mock script.")
        return get_mock_script(topic)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = (
            f"Write a detailed, informative Instagram Reel script about '{topic}'. "
            "Provide exactly 5 distinct sections. Each section must be a short paragraph (2-3 sentences) "
            "that provides deep insight or detail. "
            "Return only the text for each section, one per line. No numbering, no extra text."
        )

        response = model.generate_content(prompt)
        content = response.text.strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        return lines[:6] # Ensure max 6 lines

    except Exception as e:
        print(f"Error in script_writer (Gemini): {e}")
        print("Falling back to mock script due to API error.")
        return get_mock_script(topic)

def generate_background_prompt(topic):
    """
    Generates a descriptive background prompt based on the topic.
    Returns a single string.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    default_bg = f"cinematic background representing {topic}, high quality, 8k"
    
    if not api_key:
        return default_bg

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = (
            f"Write a short, vivid, visual description for a background image representing the topic '{topic}'. "
            "It should be suitable for a cinematic video background. "
            "Examples: 'futuristic city with neon lights', 'peaceful zen garden with cherry blossoms'. "
            "Return only the description, max 15 words."
        )

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print(f"Error in generate_background_prompt: {e}")
        return default_bg
