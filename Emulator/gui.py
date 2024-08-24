import tkinter as tk
import tkinter.font as tkfont
from PIL import Image, ImageTk
import os

def setup_gui(app):
    app.root.title("Action Recorder/Player")
    app.root.geometry("300x500")  # Increased height to accommodate new elements

    # Load and display the logo
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(script_dir, "logo.png")
    
    if os.path.exists(logo_path):
        # Open the image file
        image = Image.open(logo_path)
        
        # Resize the image to 100x100 pixels
        image = image.resize((100, 100), Image.Resampling.LANCZOS)
        
        # Convert the Image object to a PhotoImage object
        photo = ImageTk.PhotoImage(image)
        
        # Create a label to display the image
        logo_label = tk.Label(app.root, image=photo)
        logo_label.image = photo  # Keep a reference to avoid garbage collection
        logo_label.pack(pady=10)
    else:
        print(f"Warning: logo.png not found at {logo_path}")
        # Fallback to placeholder if image is not found
        icon_canvas = tk.Canvas(app.root, width=100, height=100)
        icon_canvas.pack(pady=10)
        icon_canvas.create_oval(25, 25, 75, 75, fill="blue", outline="")
        icon_canvas.create_rectangle(35, 35, 65, 65, fill="white", outline="")

    # Create a bold font
    bold_font = tkfont.Font(weight="bold")

    # Add text under the icon with bold font
    text_label = tk.Label(app.root, text="ATR Lab\nKent State University", justify=tk.CENTER, font=bold_font)
    text_label.pack(pady=5)

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

    app.incremental_frame = tk.Frame(app.root)
    app.incremental_frame.pack(pady=10)

    app.incremental_label = tk.Label(app.incremental_frame, text="Initial Incremental Number:")
    app.incremental_label.pack(side=tk.LEFT)

    app.incremental_entry = tk.Entry(app.incremental_frame, width=10)
    app.incremental_entry.insert(0, "1")  # Default value
    app.incremental_entry.pack(side=tk.LEFT)

    app.status_label = tk.Label(app.root, text="Status: Idle")
    app.status_label.pack(pady=10)