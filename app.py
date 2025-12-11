import os
from flask import Flask, render_template, request
from dotenv import load_dotenv

# Pipeline imports
from pipeline.script_writer import write_script, generate_background_prompt
from pipeline.image_generator import generate_images
from pipeline.voiceover import generate_voiceover
from pipeline.video_maker import create_video

load_dotenv()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        prompt = request.form.get('prompt')
        if not prompt:
            return render_template('index.html', error="Please enter a prompt.")
        
        try:
            # 1. Script
            print(f"Generating script for: {prompt}")
            script_lines = write_script(prompt)
            if not script_lines:
                return render_template('index.html', error="Failed to generate script.")
            
            # 2. Images
            print("Generating images...")
            bg_prompt = generate_background_prompt(prompt)
            print(f"Background Style: {bg_prompt}")
            image_paths, ui_bg_path = generate_images(script_lines, bg_prompt)
            
            if not image_paths:
                return render_template('index.html', error="Failed to generate images.")
                
            # 3. Voiceover
            print("Generating voiceover...")
            voiceover_path = generate_voiceover(script_lines)
            if not voiceover_path:
                return render_template('index.html', error="Failed to generate voiceover.")
                
            # 4. Video
            print("Creating final video...")
            video_path = create_video(image_paths, voiceover_path, script_lines)
            if not video_path:
                return render_template('index.html', error="Failed to create video.")
                
            # Make path relative for generic static serving
            # video_path is absolute or relative like 'static/output/final_video.mp4'
            # We want to pass just the web path.
            web_path = "static/output/final_video.mp4" 
            # Note: browsers might cache, so maybe add a query param?
            import time
            web_path += f"?t={int(time.time())}"
            
            return render_template('index.html', video_url=web_path, script_lines=script_lines, ui_bg=ui_bg_path)
            
        except Exception as e:
            print(f"Error: {e}")
            return render_template('index.html', error=str(e))

    return render_template('index.html')

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, port=5001)
