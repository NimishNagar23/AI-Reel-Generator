import os
from gtts import gTTS

def generate_voiceover(script_lines):
    """
    Combines script lines into one text and generates MP3 using gTTS.
    Saves to static/output/voice.mp3.
    Returns path to the audio file.
    """
    output_dir = os.path.join("static", "output")
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "voice.mp3")

    full_text = " ".join(script_lines)
    print("Generating voiceover...")

    try:
        tts = gTTS(text=full_text, lang='en')
        tts.save(filepath)
        return filepath
    except Exception as e:
        print(f"Error generating voiceover: {e}")
        return None
