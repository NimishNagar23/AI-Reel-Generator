import os
import random
import numpy as np
from moviepy import *
from PIL import Image, ImageDraw, ImageFont

def create_text_clip_pil(text, size=(1024, 1024), fontsize=50, color='white', stroke_width=2):
    """
    Creates a transparent ImageClip with text using Pillow.
    Dynamically scales font size to ensure text fits within width.
    """
    # Create transparent image
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Load Font
    def load_font(size):
        try:
            # Try common macOS fonts
            font_path = "/System/Library/Fonts/Helvetica.ttc"
            if not os.path.exists(font_path):
                font_path = "/Library/Fonts/Arial.ttf"
            return ImageFont.truetype(font_path, size)
        except Exception:
            return ImageFont.load_default()

    # Target constraints
    max_width = size[0] * 0.9  # 90% of screen width (approx 920px)
    max_height = size[1] * 0.4 # Max 40% of screen height
    
    current_fontsize = fontsize
    font = load_font(current_fontsize)
    
    # Text wrapping (Smart)
    import textwrap
    
    # Iteratively reduce font size and adjust wrap width until it fits
    # Initial wrap estimate: 900px / (size/2) -> approx chars
    # We loop to find the best fit
    
    wrapped_text = ""
    
    while current_fontsize > 20: # Don't go below 20px
        font = load_font(current_fontsize)
        
        # Estimate chars per line based on current font size
        # increased safety factor from 0.6 to 0.8 to assume wider chars check
        avg_char_width = current_fontsize * 0.8 
        wrap_width = int(max_width / avg_char_width)
        
        wrapper = textwrap.TextWrapper(width=wrap_width, break_long_words=True)
        lines = wrapper.wrap(text)
        wrapped_text = "\n".join(lines)
        
        # Check size
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        print(f"DEBUG: Font:{current_fontsize}px | Wrap:{wrap_width} chars | Width:{text_width}px / {max_width}px")
        
        if text_width <= max_width and text_height <= max_height:
            break
            
        # Reduce font size and try again
        current_fontsize -= 4 # Decrease faster

        
    # Draw text at bottom center
    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size[0] - text_width) // 2
    y = size[1] - text_height - 100  # 100px from bottom
    
    # Draw stroke (simulated by drawing multiple times)
    if stroke_width > 0:
        stroke_color = 'black'
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                draw.multiline_text((x + dx, y + dy), wrapped_text, font=font, fill=stroke_color, align="center")

    # Draw main text
    draw.multiline_text((x, y), wrapped_text, font=font, fill=color, align="center")
    
    # Convert to numpy array for MoviePy
    return ImageClip(np.array(img))

def create_video(image_paths, audio_path, script_lines=None):
    """
    Combines images, audio, and text into a final video with reliable transitions.
    Returns path to static/output/final_video.mp4.
    """
    output_dir = os.path.join("static", "output")
    output_path = os.path.join(output_dir, "final_video.mp4")
    
    print("Creating cinematic video with text and music...")
    
    try:
        # Load voiceover
        voice_clip = AudioFileClip(audio_path)
        total_duration = voice_clip.duration
        
        # Calculate duration per image
        if not image_paths:
            raise ValueError("No images provided")
            
        duration_per_image = total_duration / len(image_paths)
        
        clips = []
        for i, img_path in enumerate(image_paths):
            # --- Motion Effect (Ken Burns) ---
            # Helper for zoom
            def zoom_effect(t):
                return 1 + 0.04 * t  # Zoom speed

            img_clip = ImageClip(img_path).with_duration(duration_per_image)
            
            # Apply Resize (Zoom) -> CrossFade
            img_clip = (
                img_clip
                .with_effects([
                    vfx.Resize(zoom_effect), 
                    vfx.CrossFadeIn(1.0)
                ])
            )
            
            # --- Text Overlay ---
            if script_lines and i < len(script_lines):
                text_content = script_lines[i]
                
                # Use robust PIL generator
                txt_clip = (create_text_clip_pil(text_content, size=(1024, 1024))
                            .with_duration(duration_per_image)
                            .with_start(0.5)
                            .with_effects([vfx.CrossFadeIn(0.5)]))
                
                # Composite
                video_segment = CompositeVideoClip([img_clip, txt_clip], size=(1024, 1024))
            else:
                video_segment = CompositeVideoClip([img_clip], size=(1024, 1024))
                
            video_segment = video_segment.with_duration(duration_per_image)
            clips.append(video_segment)
            
        # Concatenate all segments
        final_video = concatenate_videoclips(clips, method="compose")
        
        # --- Audio ---
        final_video = final_video.with_audio(voice_clip)
        
        # Write file
        final_video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
        
        return output_path
        
    except Exception as e:
        print(f"Error creating video: {e}")
        import traceback
        traceback.print_exc()
        return None
