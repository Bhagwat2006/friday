import pyautogui
import time

# Safety: Fail-safe feature (move mouse to corner to abort)
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

def click(x=None, y=None, clicks=1, button='left'):
    """Clicks at coordinates or current position."""
    try:
        # Verify coordinates if provided
        if x is not None and y is not None:
            screen_width, screen_height = pyautogui.size()
            if not (0 <= x <= screen_width and 0 <= y <= screen_height):
                return f"Click failed: Coordinates ({x}, {y}) are out of bounds ({screen_width}x{screen_height})"
        
        pyautogui.click(x=x, y=y, clicks=clicks, button=button)
        
        # Verification delay
        time.sleep(0.1)
        return f"Clicked at {x if x else 'current pos'}, {y if y else ''}"
    except Exception as e:
        return f"Click failed: {e}"

def get_cursor_position():
    """Returns the current mouse cursor position as a dict."""
    try:
        x, y = pyautogui.position()
        return {"x": x, "y": y}
    except Exception as e:
        return {"x": 0, "y": 0, "error": str(e)}

def type_text(text, interval=0.05):
    """Types text."""
    try:
        pyautogui.write(text, interval=interval)
        return f"Typed: {text}"
    except Exception as e:
        return f"Typing failed: {e}"

def press_key(keys):
    """Presses a key or combination (e.g., 'enter', 'ctrl+c')."""
    try:
        if '+' in keys:
            modifiers = keys.split('+')
            key = modifiers.pop()
            for mod in modifiers:
                pyautogui.keyDown(mod)
            pyautogui.press(key)
            for mod in reversed(modifiers):
                pyautogui.keyUp(mod)
        else:
            pyautogui.press(keys)
        return f"Pressed {keys}"
    except Exception as e:
        return f"Key press failed: {e}"

def scroll(amount):
    """Scrolls up (positive) or down (negative)."""
    try:
        pyautogui.scroll(amount)
        return f"Scrolled {amount}"
    except Exception as e:
        return f"Scroll failed: {e}"

def hotkey(*args):
    """Executes a hotkey combination."""
    try:
        pyautogui.hotkey(*args)
        return f"Executed hotkey: {args}"
    except Exception as e:
        return f"Hotkey failed: {e}"

def double_click(x=None, y=None):
    """Double clicks."""
    try:
        pyautogui.doubleClick(x=x, y=y)
        return "Double clicked."
    except Exception as e:
        return f"Double click failed: {e}"

def right_click(x=None, y=None):
    """Right clicks."""
    try:
        pyautogui.rightClick(x=x, y=y)
        return "Right clicked."
    except Exception as e:
        return f"Right click failed: {e}"

def drag_and_drop(start_x, start_y, end_x, end_y):
    """Drags from start to end."""
    try:
        pyautogui.moveTo(start_x, start_y)
        pyautogui.dragTo(end_x, end_y, duration=0.5)
        return "Drag and drop complete."
    except Exception as e:
        return f"Drag failed: {e}"

def get_clipboard():
    """Returns clipboard content."""
    try:
        return pyperclip.paste()
    except Exception as e:
        return f"Clipboard error: {e}"

def set_clipboard(text):
    """Sets clipboard content."""
    try:
        pyperclip.copy(text)
        return "Clipboard updated."
    except Exception as e:
        return f"Clipboard error: {e}"

