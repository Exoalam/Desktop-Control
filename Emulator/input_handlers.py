import time
from pynput.keyboard import Key

def on_move(app, x, y):
    if app.is_recording:
        app.actions.append(('move', x, y, time.time() - app.start_time))

def on_click(app, x, y, button, pressed):
    if app.is_recording:
        app.actions.append(('click', x, y, button.name, pressed, time.time() - app.start_time))

def on_scroll(app, x, y, dx, dy):
    if app.is_recording:
        app.actions.append(('scroll', x, y, dx, dy, time.time() - app.start_time))

def on_press(app, key):
    if key == Key.esc:
        if app.is_recording:
            app.toggle_recording()
        elif app.is_playing:
            app.emergency_stop()
        return False
    
    if app.is_recording:
        current_time = time.time() - app.start_time
        if key == Key.shift:
            app.underscore_pressed = True
        elif hasattr(key, 'char') and key.char == '_' and app.underscore_pressed:
            app.actions.append(('underscore_trigger', current_time))
        else:
            try:
                char = key.char
            except AttributeError:
                char = str(key)
            app.actions.append(('keypress', char, current_time))

def on_release(app, key):
    if app.is_recording:
        current_time = time.time() - app.start_time
        if key == Key.shift:
            app.underscore_pressed = False
        else:
            try:
                char = key.char
            except AttributeError:
                char = str(key)
            app.actions.append(('keyrelease', char, current_time))

    app.last_key = key