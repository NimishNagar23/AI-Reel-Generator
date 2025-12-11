
import os
import sys
from pipeline.script_writer import write_script, generate_background_prompt
from pipeline.image_generator import generate_images

def test_pipeline():
    print("Testing Pipeline...")
    topic = "Future AI"
    
    print(f"1. Generating Script for '{topic}'...")
    script = write_script(topic)
    print(f"   Script Lines: {len(script)}")
    
    print(f"2. Generating Background Prompt...")
    bg_prompt = generate_background_prompt(topic)
    print(f"   Bg Prompt: {bg_prompt}")
    
    print(f"3. Generating Images (Mocking download for speed)...")
    # We won't actually mock, we'll try to run it. 
    # But to save time and API calls we might want to just check imports and signature.
    # However, let's run it for real to be sure.
    
    try:
        paths, ui_bg = generate_images(script[:1], bg_prompt) # Just 1 line to save time
        print(f"   Generated {len(paths)} images.")
        print(f"   UI BG Path: {ui_bg}")
        
        if os.path.exists(ui_bg):
            print("   SUCCESS: UI Background exists.")
        else:
            print("   FAILURE: UI Background missing.")
            
    except Exception as e:
        print(f"   FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pipeline()
