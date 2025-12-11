import os
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

def generate_images(script_lines, background_prompt="cinematic background, high quality"):
    """
    Generates meaningful images using the free Pollinations.ai API.
    Saves images to static/output/image_X.png.
    Returns a tuple: (list of file paths, path to UI background).
    """
    output_dir = os.path.join("static", "output")
    os.makedirs(output_dir, exist_ok=True)
    
    image_paths = []
    # Default return if things fail
    ui_bg_path = os.path.join(output_dir, "background_ui.png")

    print(f"Generating images for {len(script_lines)} scenes with background theme: '{background_prompt}'...")
    
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from PIL import Image, ImageDraw, ImageFont

    def fetch_merged_image(index, line):
        try:
            filename = f"image_{index}.png"
            filepath = os.path.join(output_dir, filename)
            
            # 1. Generate URLs
            # Background
            encoded_bg_prompt = urllib.parse.quote(f"{background_prompt}, cinematic, 8k, no text")
            bg_seed = random.randint(0, 100000)
            bg_url = f"https://image.pollinations.ai/prompt/{encoded_bg_prompt}?width=1024&height=1024&nologo=true&seed={bg_seed}"
            
            # Foreground (Scene)
            fg_prompt = f"cinematic shot, 8k, hyper-realistic, dramatic lighting, {line}, movie scene"
            encoded_fg_prompt = urllib.parse.quote(fg_prompt)
            fg_seed = random.randint(0, 100000)
            fg_url = f"https://image.pollinations.ai/prompt/{encoded_fg_prompt}?width=1024&height=1024&nologo=true&seed={fg_seed}"
            
            # 2. Download Images
            print(f"Fetching images for scene {index+1}...")
            bg_resp = requests.get(bg_url, timeout=30)
            fg_resp = requests.get(fg_url, timeout=30)
            
            if bg_resp.status_code == 200 and fg_resp.status_code == 200:
                # 3. Process & Merge
                from io import BytesIO
                bg_img = Image.open(BytesIO(bg_resp.content)).convert("RGBA")
                fg_img = Image.open(BytesIO(fg_resp.content)).convert("RGBA")
                
                # Save first background for UI
                if index == 0:
                    bg_img.save(ui_bg_path)
                
                # Resize to ensure exact dimensions
                bg_img = bg_img.resize((1024, 1024), Image.Resampling.LANCZOS)
                fg_img = fg_img.resize((1024, 1024), Image.Resampling.LANCZOS)

                # Blend: FG on top of BG
                # We want the background to be visible but the foreground (scene) to be the main focus
                # strategy: 
                # 1. Background image full opacity
                # 2. Foreground image with reduced opacity (e.g. 85%) overlaid?
                # OR better: 
                # 3. Use the foreground image as base, but blend it with the background?
                # The user requirement: "Background should fill full frame. Foreground image should blend on top with slight transparency or soft edges"
                
                # Let's try blending them 70/30 or 80/20 favor of foreground, 
                # but "foreground on top" suggests FG is the subject.
                
                # Approach: 
                # Base layer = Background
                # Top layer = Foreground with alpha 0.85
                
                fg_img.putalpha(210) # ~82% opacity (0-255)
                merged = Image.alpha_composite(bg_img, fg_img)
                
                # Optional: Add a slight vignette to focus center?
                # (Skipping for now to keep it simple but effective)

                merged.save(filepath)
                return (index, filepath)
            else:
                print(f"Failed to fetch images for scene {index}: BG={bg_resp.status_code}, FG={fg_resp.status_code}")
                return None
        except Exception as e:
            print(f"Error generating scene {index}: {e}")
            return None

    # Use ThreadPool
    import random
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(fetch_merged_image, i, line): i for i, line in enumerate(script_lines)}
        
        results = []
        for future in as_completed(futures):
            res = future.result()
            if res:
                results.append(res)
    
    results.sort(key=lambda x: x[0])
    
    image_paths_map = {r[0]: r[1] for r in results}
    final_paths = []
    
    # Fallback handling
    for i, line in enumerate(script_lines):
        if i in image_paths_map:
            final_paths.append(image_paths_map[i])
        else:
            print(f"Generating fallback image for scene {i+1}...")
            filename = f"image_{i}.png"
            filepath = os.path.join(output_dir, filename)
            try:
                # Basic colors fallback
                colors = [(73, 109, 137), (137, 73, 109), (109, 137, 73)]
                bg_color = colors[i % len(colors)]
                img = Image.new('RGB', (1024, 1024), color=bg_color)
                
                # If we need a fallback UI BG
                if i == 0 and not os.path.exists(ui_bg_path):
                    img.save(ui_bg_path)

                d = ImageDraw.Draw(img)
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
                except:
                    font = ImageFont.load_default()
                d.text((50, 400), f"Scene {i+1}\n{line[:30]}...", fill=(255,255,255), font=font)
                img.save(filepath)
                final_paths.append(filepath)
            except Exception as e:
                print(f"Fallback failed: {e}")

    # Ensure UI background exists if everything failed
    if not os.path.exists(ui_bg_path):
        # Create a dummy one
        Image.new('RGB', (1024, 1024), color=(30, 30, 30)).save(ui_bg_path)

    return final_paths, ui_bg_path
