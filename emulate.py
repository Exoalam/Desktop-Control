import time
import json
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import os
import queue

class ActionRecorderPlayer:
    def __init__(self):
        self.actions = []
        self.is_recording = False
        self.is_playing = False
        self.start_time = 0
        self.mouse_listener = None
        self.keyboard_listener = None
        self.mouse_controller = MouseController()
        self.keyboard_controller = KeyboardController()
        self.save_location = ""
        self.event_queue = queue.Queue()
        self.last_esc_time = 0
        self.incremental_count = 1

        self.root = tk.Tk()
        self.root.title("Action Recorder/Player")
        self.root.geometry("300x400")

        self.record_button = tk.Button(self.root, text="Start Recording", command=self.toggle_recording)
        self.record_button.pack(pady=10)

        self.play_button = tk.Button(self.root, text="Play Recording", command=self.start_play_recording)
        self.play_button.pack(pady=10)

        self.loop_play_button = tk.Button(self.root, text="Loop Playback", command=self.start_loop_playback)
        self.loop_play_button.pack(pady=10)

        self.save_button = tk.Button(self.root, text="Save Recording", command=self.save_recording)
        self.save_button.pack(pady=10)

        self.load_button = tk.Button(self.root, text="Load Recording", command=self.load_recording)
        self.load_button.pack(pady=10)

        self.select_location_button = tk.Button(self.root, text="Select Save Location", command=self.select_save_location)
        self.select_location_button.pack(pady=10)

        self.incremental_format_label = tk.Label(self.root, text="Incremental Format:")
        self.incremental_format_label.pack(pady=(10, 0))

        self.incremental_format_entry = tk.Entry(self.root)
        self.incremental_format_entry.insert(0, "file_{:03d}.txt")
        self.incremental_format_entry.pack(pady=(0, 10))

        self.status_label = tk.Label(self.root, text="Status: Idle")
        self.status_label.pack(pady=10)

        self.root.after(100, self.process_event_queue)

    def on_move(self, x, y):
        self.event_queue.put(('move', x, y, time.time() - self.start_time))

    def on_click(self, x, y, button, pressed):
        self.event_queue.put(('click', x, y, button.name, pressed, time.time() - self.start_time))

    def on_scroll(self, x, y, dx, dy):
        self.event_queue.put(('scroll', x, y, dx, dy, time.time() - self.start_time))

    def on_press(self, key):
        self.event_queue.put(('keypress', str(key), time.time() - self.start_time))

    def on_release(self, key):
        current_time = time.time()
        self.event_queue.put(('keyrelease', str(key), current_time - self.start_time))

        if key == Key.esc:
            if self.is_recording:
                if current_time - self.last_esc_time < 0.5:  # Double tap within 0.5 seconds
                    self.event_queue.put(('stop_recording', current_time - self.start_time))
                else:
                    incremental_format = self.incremental_format_entry.get()
                    incremental_text = incremental_format.format(self.incremental_count)
                    self.event_queue.put(('incremental', incremental_text, current_time - self.start_time))
                    # Emulate typing the incremental text
                    self.keyboard_controller.type(incremental_text)
                    self.incremental_count += 1
                self.last_esc_time = current_time
            elif self.is_playing:
                self.is_playing = False

    def process_event_queue(self):
        try:
            while not self.event_queue.empty():
                event = self.event_queue.get_nowait()
                if event[0] == 'stop_recording':
                    self.root.after(0, self.toggle_recording)
                elif event[0] == 'incremental':
                    self.actions.append(event)
                elif self.is_recording:
                    self.actions.append(event)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_event_queue)

    def toggle_recording(self):
        if not self.is_recording:
            self.actions = []
            self.start_time = time.time()
            self.is_recording = True
            self.record_button.config(text="Stop Recording")
            self.status_label.config(text="Status: Recording")
            self.incremental_count = 1
            
            self.mouse_listener = mouse.Listener(
                on_move=self.on_move,
                on_click=self.on_click,
                on_scroll=self.on_scroll)
            self.mouse_listener.start()
            
            self.keyboard_listener = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release)
            self.keyboard_listener.start()
        else:
            self.is_recording = False
            self.record_button.config(text="Start Recording")
            self.status_label.config(text="Status: Idle")
            if self.mouse_listener:
                self.mouse_listener.stop()
            if self.keyboard_listener:
                self.keyboard_listener.stop()
            messagebox.showinfo("Recording Stopped", f"Recorded {len(self.actions)} actions.")

    def play_recording(self, loop=False):
        if not self.actions:
            messagebox.showwarning("No Recording", "No actions recorded or loaded.")
            return

        if not self.save_location:
            messagebox.showwarning("No Save Location", "Please select a save location first.")
            return

        self.is_playing = True
        self.status_label.config(text="Status: Playing")
        initial_file_count = len(os.listdir(self.save_location))

        escape_listener = keyboard.Listener(on_release=self.on_release)
        escape_listener.start()

        loop_count = 0

        try:
            while self.is_playing:
                last_time = 0
                for action in self.actions:
                    if not self.is_playing:
                        break
                    time.sleep(max(0, action[-1] - last_time))
                    last_time = action[-1]

                    if action[0] == 'move':
                        self.mouse_controller.position = (action[1], action[2])
                    elif action[0] == 'click':
                        self.mouse_controller.position = (action[1], action[2])
                        if action[4]:  # If pressed
                            self.mouse_controller.press(getattr(Button, action[3]))
                        else:
                            self.mouse_controller.release(getattr(Button, action[3]))
                    elif action[0] == 'scroll':
                        self.mouse_controller.scroll(action[3], action[4])
                    elif action[0] == 'keypress':
                        key = action[1]
                        if key.startswith("Key."):
                            key = getattr(Key, key[4:])
                        self.keyboard_controller.press(key)
                    elif action[0] == 'keyrelease':
                        key = action[1]
                        if key.startswith("Key."):
                            key = getattr(Key, key[4:])
                        self.keyboard_controller.release(key)
                    elif action[0] == 'incremental':
                        self.keyboard_controller.type(action[1])

                loop_count += 1
                current_file_count = len(os.listdir(self.save_location))
                
                if current_file_count > initial_file_count:
                    print(f"New file created successfully in loop {loop_count}.")
                    initial_file_count = current_file_count
                else:
                    print(f"No new file was created in loop {loop_count}. Stopping playback.")
                    self.is_playing = False
                    break

                if not loop:
                    break

        except Exception as e:
            print(f"An error occurred during playback: {e}")
        finally:
            escape_listener.stop()
            self.is_playing = False
            self.root.after(0, lambda: self.status_label.config(text="Status: Idle"))
            self.root.after(0, lambda: messagebox.showinfo("Playback Complete", f"Finished playing back the recording. Completed {loop_count} loops."))

    def start_play_recording(self):
        threading.Thread(target=self.play_recording, args=(False,), daemon=True).start()

    def start_loop_playback(self):
        threading.Thread(target=self.play_recording, args=(True,), daemon=True).start()

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

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ActionRecorderPlayer()
    app.run()
