import rumps
import subprocess
import AppKit
from pynput import keyboard

# Constants
screen = AppKit.NSScreen.mainScreen().frame()
width, height = int(screen.size.width), int(screen.size.height)

MWM = "MacWinMan"

COMBO_center = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.Key.enter}
COMBO_left = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.Key.left}
COMBO_right = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.Key.right}
current_keys = set()

# Rumps Functions
def get_applescript(x_coor, y_coor):
    script = f'''
        tell application "System Events"
            tell (first process where frontmost is true)
                set frontWindow to front window
                set {{x, y}} to position of frontWindow
                set {{w, h}} to size of frontWindow

                set screenWidth to {width}
                set screenHeight to {height}

                set newX to {x_coor}
                set newY to {y_coor}

                set position of frontWindow to {{newX, newY}}
            end tell
        end tell
        '''
    return script

def center_window(_):
    rumps.notification(MWM, "", "Centered!")
    x, y = "(screenWidth - w) / 2", "-22"
    script = get_applescript(x, y)
    subprocess.run(["osascript", "-e", script])

def move_left(_):
    rumps.notification(MWM, "", "Moved left!")
    x, y = "0", "-22"
    script = get_applescript(x, y)
    subprocess.run(["osascript", "-e", script])

def move_right(_):
    rumps.notification(MWM, "", "Moved right!")
    x, y = "screenWidth - w", "-22"
    script = get_applescript(x, y)
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

def on_release(key):
    current_keys.discard(key)

# App
app = rumps.App(MWM)

app.menu["Center Window"] = rumps.MenuItem("Center Window", callback=center_window)
app.menu["Move Left"] = rumps.MenuItem("Move Left", callback=move_left)
app.menu["Move Right"] = rumps.MenuItem("Move Right", callback=move_right)

# Main
def main():
    listener.start()
    app.run()

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
if __name__ == "__main__":
    main()