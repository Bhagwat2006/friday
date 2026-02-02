import psutil
import screen_brightness_control as sbc
import os
import subprocess
import shutil
import glob
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
except ImportError:
    pass

# Common application paths and commands
APP_PATHS = {
    "chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "chrome"
    ],
    "notepad": ["notepad"],
    "calculator": ["calc"],
    "paint": ["mspaint"],
    "explorer": ["explorer"],
    "cmd": ["cmd"],
    "powershell": ["powershell"],
    "vscode": ["code"],
    "spotify": [r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe"],
    "discord": [r"C:\Users\%USERNAME%\AppData\Local\Discord\Update.exe", "--processStart", "Discord.exe"]
}

def get_system_stats():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    battery = psutil.sensors_battery()
    battery_percent = battery.percent if battery else "N/A"
    return f"CPU: {cpu}%, Memory: {memory}%, Battery: {battery_percent}%"

def set_brightness(level):
    try:
        sbc.set_brightness(level)
        return f"Brightness set to {level}%"
    except Exception as e:
        return f"Failed to set brightness: {e}"

def set_volume(level):
    """Set system volume to a specific percentage (0-100)."""
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        # Volume range is usually -65.25 to 0.0 dB
        # Converting percentage to scalar (0.0 to 1.0)
        scalar_volume = max(0.0, min(1.0, level / 100.0))
        volume.SetMasterVolumeLevelScalar(scalar_volume, None)
        
        return f"Volume set to {level}%"
    except Exception as e:
        return f"Failed to set volume: {e}"

def _find_executable(app_name):
    """Try to find the executable for the given app name."""
    app_lower = app_name.lower()
    
    # 1. Check known dictionary
    if app_lower in APP_PATHS:
        paths = APP_PATHS[app_lower]
        for path in paths:
            # Expand environment variables like %USERNAME%
            expanded_path = os.path.expandvars(path)
            # If it's a direct command (no path separators) or exists
            if os.sep not in expanded_path:
                if shutil.which(expanded_path):
                    return expanded_path
            elif os.path.exists(expanded_path):
                return expanded_path
                
    # 2. Check if it's in PATH directly
    if shutil.which(app_name):
        return app_name
        
    return None

def open_app(app_name):
    try:
        # Clean up input
        app_name = app_name.strip().strip('"').strip("'")
        
        # Try to find specific path first
        executable = _find_executable(app_name)
        
        if executable:
            proc = subprocess.Popen(executable)
            # Verify process started
            if proc.poll() is None:
                return f"Successfully opened {app_name} (PID: {proc.pid})"
            return f"Failed to open {app_name} (Process exited immediately)"
            
        try:
            os.startfile(app_name)
            # Cannot easily verify startfile, but if no exception, likely success
            return f"Opening {app_name} via Windows"
        except Exception as e:
            return f"Failed to open {app_name}: {e}"
    except Exception as e:
        return f"System Error: {e}"

def get_running_processes():
    """Returns a list of names of running processes."""
    try:
        return [p.name() for p in psutil.process_iter(['name'])]
    except Exception as e:
        return f"Error listing processes: {e}"

def kill_process(process_name):
    """Kills a process by name."""
    try:
        killed_count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'].lower() == process_name.lower() or \
               proc.info['name'].lower() == f"{process_name.lower()}.exe":
                proc.kill()
                killed_count += 1
        
        if killed_count > 0:
            return f"Killed {killed_count} instance(s) of {process_name}"
        return f"Process {process_name} not found."
    except Exception as e:
        return f"Error killing process: {e}"

def find_file(filename, search_path=None):
    """Finds a file in the user's home directory or specified path."""
    if not search_path:
        search_path = os.environ['USERPROFILE']
    
    matches = []
    try:
        for root, dirnames, filenames in os.walk(search_path):
            if filename in filenames:
                matches.append(os.path.join(root, filename))
                if len(matches) >= 3: # Limit to first 3 matches for speed
                    break
        return matches if matches else "File not found."
    except Exception as e:
        return f"Error searching for file: {e}"

def read_file(file_path):
    """Reads content of a text file."""
    try:
        if not os.path.exists(file_path):
            return "File does not exist."
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(file_path, content, mode='w'):
    """Writes content to a file."""
    try:
        with open(file_path, mode, encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {e}"
