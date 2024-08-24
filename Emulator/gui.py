import tkinter as tk

def setup_gui(app):
    app.root.title("Action Recorder/Player")
    app.root.geometry("300x350")

    app.record_button = tk.Button(app.root, text="Start Recording", command=app.toggle_recording)
    app.record_button.pack(pady=10)

    app.play_button = tk.Button(app.root, text="Play Recording", command=app.start_play_recording)
    app.play_button.pack(pady=10)

    app.loop_play_button = tk.Button(app.root, text="Loop Playback", command=app.start_loop_playback)
    app.loop_play_button.pack(pady=10)

    app.save_button = tk.Button(app.root, text="Save Recording", command=app.save_recording)
    app.save_button.pack(pady=10)

    app.load_button = tk.Button(app.root, text="Load Recording", command=app.load_recording)
    app.load_button.pack(pady=10)

    app.select_location_button = tk.Button(app.root, text="Select Save Location", command=app.select_save_location)
    app.select_location_button.pack(pady=10)

    # New elements for incremental number feature
    app.incremental_frame = tk.Frame(app.root)
    app.incremental_frame.pack(pady=10)

    app.incremental_label = tk.Label(app.incremental_frame, text="Initial Incremental Number:")
    app.incremental_label.pack(side=tk.LEFT)

    app.incremental_entry = tk.Entry(app.incremental_frame, width=10)
    app.incremental_entry.insert(0, "1")  # Default value
    app.incremental_entry.pack(side=tk.LEFT)

    app.status_label = tk.Label(app.root, text="Status: Idle")
    app.status_label.pack(pady=10)