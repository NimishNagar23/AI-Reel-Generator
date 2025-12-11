
import os
from pipeline.video_maker import create_video
from PIL import Image

def test_video_creation():
    # Setup dummy data
    os.makedirs("static/output", exist_ok=True)
    
    # Create dummy images
    img_paths = []
    for i in range(3):
        p = f"static/output/test_img_{i}.png"
        img = Image.new('RGB', (1024, 1024), color=(i*50, 100, 100))
        img.save(p)
        img_paths.append(p)
        
    # Create dummy audio (if needed, but create_video loads it)
    # We'll need a real audio file or mock it. 
    # easier to Mock the AudioFileClip but let's just make a silent mp3? 
    # or just use an existing one if available.
    # We'll assume one exists or create a text file mimicking it? 
    # Actually, let's just try-except inside create_video to see the real error.
    
    # Check if voice.mp3 exists from previous runs
    audio_path = "static/output/voice.mp3"
    if not os.path.exists(audio_path):
        # Create a tiny dummy mp3? excessive.
        # Let's just create a dummy file and mock AudioFileClip? No, moviepy needs ffmpeg.
        print("No voice.mp3 found, cannot fully test without audio.")
        return

    print("Testing create_video...")
    try:
        script_lines = ["Line 1 text", "Line 2 text", "Line 3 text"]
        path = create_video(img_paths, audio_path, script_lines)
        if path:
            print(f"Success! Video at {path}")
        else:
            print("Failed (returned None).")
    except Exception as e:
        print(f"Exception during test: {e}")

if __name__ == "__main__":
    test_video_creation()
