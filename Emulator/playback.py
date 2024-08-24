import time
from tkinter import messagebox
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController, Listener as KeyboardListener
import os
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def on_press(key, app):
    if key == Key.esc:
        app.emergency_stop()
        return False  # Stop listener

def play_recording(app, loop=False):
    if not app.actions:
        messagebox.showwarning("No Recording", "No actions recorded or loaded.")
        return

    if not app.save_location:
        messagebox.showwarning("No Save Location", "Please select a save location first.")
        return

    app.is_playing = True
    app.status_label.config(text="Status: Playing")
    initial_file_count = len(os.listdir(app.save_location))

    incremental_number = app.get_initial_incremental_number()
    loop_count = 0

    mouse_controller = MouseController()
    keyboard_controller = KeyboardController()

    button_states = {Button.left: False, Button.right: False, Button.middle: False}

    # Start a keyboard listener for Esc key
    keyboard_listener = KeyboardListener(on_press=lambda key: on_press(key, app))
    keyboard_listener.start()

    try:
        while app.is_playing:
            logging.info(f"Starting loop iteration {loop_count + 1}")
            last_time = 0
            for action in app.actions:
                if not app.is_playing:
                    break
                time.sleep(max(0, action[-1] - last_time))
                last_time = action[-1]

                if action[0] == 'move':
                    mouse_controller.position = (action[1], action[2])
                    logging.debug(f"Mouse moved to {action[1]}, {action[2]}")
                elif action[0] == 'click':
                    mouse_controller.position = (action[1], action[2])
                    button = getattr(Button, action[3])
                    if action[4]:  # If pressed
                        if not button_states[button]:
                            mouse_controller.press(button)
                            button_states[button] = True
                            logging.debug(f"Mouse button {button} pressed at {action[1]}, {action[2]}")
                    else:
                        if button_states[button]:
                            mouse_controller.release(button)
                            button_states[button] = False
                            logging.debug(f"Mouse button {button} released at {action[1]}, {action[2]}")
                elif action[0] == 'scroll':
                    mouse_controller.scroll(action[3], action[4])
                    logging.debug(f"Mouse scrolled {action[3]}, {action[4]}")
                elif action[0] == 'keypress':
                    key = action[1]
                    if key.startswith("Key."):
                        key = getattr(Key, key[4:])
                    keyboard_controller.press(key)
                    logging.debug(f"Key pressed: {key}")
                elif action[0] == 'keyrelease':
                    key = action[1]
                    if key.startswith("Key."):
                        key = getattr(Key, key[4:])
                    keyboard_controller.release(key)
                    logging.debug(f"Key released: {key}")
                elif action[0] == 'underscore_trigger':
                    keyboard_controller.type(f"_{incremental_number}")
                    logging.debug(f"Underscore trigger: _{incremental_number}")

            loop_count += 1
            current_file_count = len(os.listdir(app.save_location))
            
            if current_file_count > initial_file_count:
                logging.info(f"New file created successfully in loop {loop_count}.")
                initial_file_count = current_file_count
                if loop:
                    incremental_number += 1
                    logging.info(f"Incremental number increased to {incremental_number}")
            else:
                logging.info(f"No new file was created in loop {loop_count}. Stopping playback.")
                break

            # Reset button states at the end of each loop
            for button in button_states:
                if button_states[button]:
                    mouse_controller.release(button)
                    button_states[button] = False
                    logging.debug(f"Reset: Mouse button {button} released")

            if not loop:
                break

    finally:
        keyboard_listener.stop()
        
        if not app.is_playing:
            app.status_label.config(text="Status: Stopped (Emergency)")
            logging.info("Playback stopped due to emergency stop")
        elif loop_count > 0 and current_file_count <= initial_file_count:
            app.status_label.config(text="Status: Stopped (No new file created)")
            logging.info("Playback stopped because no new file was created")
        else:
            app.status_label.config(text="Status: Idle")
            logging.info("Playback completed normally")
        
        app.is_playing = False
        messagebox.showinfo("Playback Complete", f"Finished playing back the recording. Completed {loop_count} loops.")
        logging.info(f"Playback finished. Completed {loop_count} loops.")