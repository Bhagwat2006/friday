import pyautogui
import base64
import io
import os
import json
from PIL import Image
from groq import Groq
from config import settings

class VisionSkill:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def capture_screen(self):
        """Captures the current screen and returns (base64_string, (width, height))."""
        screenshot = pyautogui.screenshot()
        original_size = screenshot.size
        
        # Resize if too large to speed up processing but keep reasonable detail for text
        # For UI detection, we need good resolution. 1024 is a safe compromise.
        max_dimension = 1024
        if screenshot.width > max_dimension or screenshot.height > max_dimension:
            screenshot.thumbnail((max_dimension, max_dimension))
            
        buffer = io.BytesIO()
        screenshot.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode('utf-8'), original_size, screenshot.size

    def analyze_screen(self, query="What is on the screen?"):
        """Analyzes the current screen content using Llama 3.2 Vision."""
        try:
            base64_image, _, _ = self.capture_screen()
            
            completion = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": query},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.5,
                max_tokens=1024,
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Vision Error: {e}"

    def find_element(self, description):
        """
        Finds the coordinates of an element matching the description.
        Returns a dictionary {'x': int, 'y': int} or None.
        """
        try:
            base64_image, original_size, resized_size = self.capture_screen()
            orig_w, orig_h = original_size
            resized_w, resized_h = resized_size
            
            # Scale factors
            scale_x = orig_w / resized_w
            scale_y = orig_h / resized_h
            
            prompt = f"""
            I need to click on "{description}".
            Look at the UI screenshot.
            Identify the bounding box [ymin, xmin, ymax, xmax] for the element that best matches "{description}".
            The image size is {resized_w}x{resized_h}.
            
            Return ONLY a JSON object:
            {{
                "box_2d": [ymin, xmin, ymax, xmax],
                "label": "short description of what you found"
            }}
            
            If you cannot find it, return:
            {{
                "box_2d": null,
                "label": "not found"
            }}
            """
            
            completion = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct", # Updated to Llama 4 Scout
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1, # Low temperature for precision
                response_format={"type": "json_object"},
                max_tokens=500,
            )
            
            result = json.loads(completion.choices[0].message.content)
            
            if result.get("box_2d"):
                ymin, xmin, ymax, xmax = result["box_2d"]
                
                # Calculate center in resized coordinates
                center_x_resized = (xmin + xmax) / 2
                center_y_resized = (ymin + ymax) / 2
                
                # Scale back to original screen coordinates
                final_x = int(center_x_resized * scale_x)
                final_y = int(center_y_resized * scale_y)
                
                print(f"Vision found '{result.get('label')}' at ({final_x}, {final_y})")
                return {"x": final_x, "y": final_y}
                
            print(f"Vision could not find '{description}'")
            return None
            
        except Exception as e:
            print(f"Vision Find Error: {e}")
            return None

    def find_and_click(self, description):
        """Finds an element and clicks it."""
        coords = self.find_element(description)
        if coords:
            pyautogui.click(coords['x'], coords['y'])
            return f"Clicked on {description} at ({coords['x']}, {coords['y']})"
        return f"Could not find {description} to click."

vision_skill = VisionSkill()

def analyze(query="Describe what you see"):
    return vision_skill.analyze_screen(query)

def find_and_click(description):
    """Finds an element by description and clicks it."""
    coords = vision_skill.find_element(description)
    if coords:
        pyautogui.click(coords['x'], coords['y'])
        return f"Clicked on {description} at ({coords['x']}, {coords['y']})"
    else:
        return f"Could not find '{description}' on the screen."
