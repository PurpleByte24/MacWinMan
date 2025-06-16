import rumps
import subprocess
import AppKit
from AppKit import NSScreen
from pynput import keyboard

# Constants
MWM = "MacWinMan"
COMBO_center = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.Key.enter}
COMBO_left = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.Key.left}
COMBO_right = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.Key.right}
COMBO_travel = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.Key.backspace}

menubar_Offset = 22

# Get Functions
def get_screenInfo(index):
    mainScreen = AppKit.NSScreen.mainScreen().frame()
    screens = NSScreen.screens()
    screen_info = [screen.frame() for screen in screens]
    screen_dim = (int(mainScreen.size.width), int(mainScreen.size.height))

    if index is not None:
        screen = screens[index].frame()
        screen_dim = (int(screen.size.width), int(screen.size.height))

    return_package = {
        "screens": screens,
        "screen_info": screen_info,
        "screen_dim": screen_dim
    }
    return return_package

def get_applescript(x_coor, y_coor, window_w, window_h, screen_w, screen_h):
    script = f'''
        tell application "System Events"
            tell (first process where frontmost is true)
                set frontWindow to front window
                set {{x, y}} to position of frontWindow
                set {{w, h}} to size of frontWindow

                set screenWidth to {screen_w}
                set screenHeight to {screen_h}

                set newX to {x_coor}
                set newY to {y_coor}
                set newW to {window_w}
                set newH to {window_h}

                set position of frontWindow to {{newX, newY}}
                set size of frontWindow to {{newW, newH}}
            end tell
        end tell
        '''
    return script

def get_frontWindowPos():
    script = '''
    tell application "System Events"
        tell (first process where frontmost is true)
            set pos to position of front window
            return (item 1 of pos as string) & "," & (item 2 of pos as string)
        end tell
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    x_coor, y_coor = result.stdout.strip().split(",")
    windowPos = (int(x_coor), int(y_coor))
    return windowPos

def get_frontWindowSize():
    script = '''
    tell application "System Events"
        tell (first process where frontmost is true)
            set sz to size of front window
            return (item 1 of sz as string) & "," & (item 2 of sz as string)
        end tell
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    window_w, window_h = result.stdout.strip().split(",")
    window_Dim = (int(window_w), int(window_h))
    return window_Dim

def get_currentScreenIndex():
    windowPos = get_frontWindowPos()
    screens = get_screenInfo(None)["screens"]
    for i, screen in enumerate(screens):
        frame = screen.frame()
        sx, sy = int(frame.origin.x), int(frame.origin.y)
        screenPos = (sx, sy)
        sw, sh = int(frame.size.width), int(frame.size.height)
        screenDim = (sw, sh)
        if screenPos[0] <= windowPos[0] < screenPos[0] + screenDim[0] and screenPos[1] <= windowPos[1] < screenPos[1] + screenDim[1]:
            return i
    return -1  # not found

# Rumps Functions
def center_window(_):
    screen_w, screen_h = get_screenInfo(None)["screen_dim"]
    x, y = 0, -1 * menubar_Offset
    w, h = screen_w, screen_h

    script = get_applescript(x, y, w, h, screen_w, screen_h)
    subprocess.run(["osascript", "-e", script])

def move_left(_):
    current_index = get_currentScreenIndex()
    screen_info = get_screenInfo(current_index)
    screen_w, screen_h = screen_info["screen_dim"]

    screen_frame = screen_info["screens"][current_index].frame()
    x_origin, y_origin = int(screen_frame.origin.x), int(screen_frame.origin.y) - menubar_Offset

    x, y = x_origin, y_origin
    w, h = screen_w // 2, screen_h

    script = get_applescript(x, y, w, h, screen_w, screen_h)
    subprocess.run(["osascript", "-e", script])

def move_right(_):
    current_index = get_currentScreenIndex()
    screen_info = get_screenInfo(current_index)
    screen_w, screen_h = screen_info["screen_dim"]

    screen_frame = screen_info["screens"][current_index].frame()
    x_origin, y_origin = int(screen_frame.origin.x), int(screen_frame.origin.y) - menubar_Offset

    x, y = x_origin + screen_w // 2, y_origin
    
    w, h = screen_w // 2, screen_h

    script = get_applescript(x, y, w, h, screen_w, screen_h)
    subprocess.run(["osascript", "-e", script])

def travel_screens(_):
    screens = get_screenInfo(None)["screens"]
    
    current_index = get_currentScreenIndex()
    if current_index == -1:
        return  # could not detect screen

    next_index = current_index + 1 if (current_index + 1) < len(screens) else 0

    # Get next screen frame
    next_screen = screens[next_index].frame()

    next_x, next_y = int(next_screen.origin.x), int(next_screen.origin.y) - menubar_Offset
    next_w, next_h = int(next_screen.size.width), int(next_screen.size.height)

    script = get_applescript(next_x, next_y, next_w, next_h, next_w, next_h)
    subprocess.run(["osascript", "-e", script])

# Pynput Functions
def on_press(key):
    current_keys.add(key)
    if COMBO_center.issubset(current_keys):
        center_window(None)

    elif COMBO_left.issubset(current_keys):
        move_left(None)

    elif COMBO_right.issubset(current_keys):
        move_right(None)

    elif COMBO_travel.issubset(current_keys):
        travel_screens(None)

def on_release(key):
    current_keys.discard(key)

# App
app = rumps.App("", icon="icon.icns")

app.menu["Center Window"] = rumps.MenuItem("⌃⌥↩    Center Window", callback=center_window)
app.menu["Move Left"] = rumps.MenuItem("⌃⌥←    Move Left", callback=move_left)
app.menu["Move Right"] = rumps.MenuItem("⌃⌥→    Move Right", callback=move_right)
app.menu["Travel Screens"] = rumps.MenuItem("⌃⌥⌫    Travel Screens", callback=travel_screens)

# Main
def main():
    listener.start()
    app.run()

current_keys = set()
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
if __name__ == "__main__":
    main()