import time
import json
import threading
from tkinter import messagebox, filedialog
import os
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
from gui import setup_gui
from input_handlers import on_move, on_click, on_scroll, on_press, on_release
from playback import play_recording

class ActionRecorderPlayer:
    def __init__(self, root):
        self.root = root
        self.actions = []
        self.is_recording = False
        self.is_playing = False
        self.start_time = 0
        self.mouse_listener = None
        self.keyboard_listener = None
        self.mouse_controller = MouseController()
        self.keyboard_controller = KeyboardController()
        self.save_location = ""
        self.last_key = None
        self.underscore_pressed = False

        setup_gui(self)

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.actions = []
        self.start_time = time.time()
        self.is_recording = True
        self.record_button.config(text="Stop Recording")
        self.status_label.config(text="Status: Recording")
        
        self.mouse_listener = mouse.Listener(
            on_move=lambda x, y: on_move(self, x, y),
            on_click=lambda x, y, button, pressed: on_click(self, x, y, button, pressed),
            on_scroll=lambda x, y, dx, dy: on_scroll(self, x, y, dx, dy))
        self.mouse_listener.start()
        
        self.keyboard_listener = keyboard.Listener(
            on_press=lambda key: on_press(self, key),
            on_release=lambda key: on_release(self, key))
        self.keyboard_listener.start()

    def stop_recording(self):
        self.is_recording = False
        self.record_button.config(text="Start Recording")
        self.status_label.config(text="Status: Idle")
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        messagebox.showinfo("Recording Stopped", f"Recorded {len(self.actions)} actions.")

    def start_play_recording(self):
        threading.Thread(target=play_recording, args=(self, False), daemon=True).start()

    def start_loop_playback(self):
        threading.Thread(target=play_recording, args=(self, True), daemon=True).start()

    def emergency_stop(self):
        self.is_playing = False
        self.status_label.config(text="Status: Stopped (Emergency)")

    def save_recording(self):
        if not self.actions:
            messagebox.showwarning("No Recording", "No actions to save.")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(self.actions, f)
            messagebox.showinfo("Save Successful", f"Recording saved to {file_path}")

    def load_recording(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.actions = json.load(f)
                messagebox.showinfo("Load Successful", f"Loaded {len(self.actions)} actions from {file_path}")
            except json.JSONDecodeError:
                messagebox.showerror("Invalid File", "The file is not a valid recording.")

    def select_save_location(self):
        self.save_location = filedialog.askdirectory()
        if self.save_location:
            messagebox.showinfo("Save Location", f"Save location set to: {self.save_location}")

    def get_initial_incremental_number(self):
        try:
            return int(self.incremental_entry.get())
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid number for the initial incremental value.")
            return 1 