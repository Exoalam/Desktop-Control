import tkinter as tk
from PIL import Image, ImageTk
import socket
import threading
import struct
import io

class RemoteControlServer:
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.controlling = False

        self.root = tk.Tk()
        self.root.title("Remote Control Server")
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.root.bind('<Escape>', self.toggle_control)
        self.root.bind('<Motion>', self.send_mouse_move)
        self.root.bind('<Button-1>', self.send_mouse_click)
        self.root.bind('<KeyPress>', self.send_key_press)
        self.root.bind('<KeyRelease>', self.send_key_release)

        self.status_label = tk.Label(self.root, text="Status: Disconnected")
        self.status_label.pack()

        self.image_on_canvas = None

    def start(self):
        server_thread = threading.Thread(target=self.start_server)
        server_thread.daemon = True
        server_thread.start()
        self.root.mainloop()

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.status_label.config(text="Status: Waiting for connection...")
        
        while True:
            self.client_socket, addr = self.server_socket.accept()
            self.status_label.config(text=f"Status: Connected to {addr}")
            self.receive_screenshots()

    def receive_screenshots(self):
        try:
            while True:
                size_data = self.client_socket.recv(4)
                if not size_data:
                    break
                size = struct.unpack('>I', size_data)[0]
                data = b''
                while len(data) < size:
                    packet = self.client_socket.recv(size - len(data))
                    if not packet:
                        return None
                    data += packet
                image = Image.open(io.BytesIO(data))
                self.display_image(image)
        except Exception as e:
            print(f"Error receiving screenshots: {e}")
            self.status_label.config(text="Status: Disconnected")

    def display_image(self, image):
        photo = ImageTk.PhotoImage(image)
        if self.image_on_canvas:
            self.canvas.itemconfig(self.image_on_canvas, image=photo)
        else:
            self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.config(width=photo.width(), height=photo.height())
        self.canvas.image = photo  # Keep a reference to avoid garbage collection
        self.root.update_idletasks()  # Force update of the window

    def toggle_control(self, event):
        self.controlling = not self.controlling
        status = "Controlling" if self.controlling else "Viewing"
        self.status_label.config(text=f"Status: Connected - {status}")

    def send_mouse_move(self, event):
        if self.controlling and self.client_socket:
            x, y = event.x, event.y
            self.send_command(f"MOVE {x} {y}")

    def send_mouse_click(self, event):
        if self.controlling and self.client_socket:
            x, y = event.x, event.y
            self.send_command(f"CLICK {x} {y}")

    def send_key_press(self, event):
        if self.controlling and self.client_socket:
            key = event.keysym
            self.send_command(f"KEYDOWN {key}")

    def send_key_release(self, event):
        if self.controlling and self.client_socket:
            key = event.keysym
            self.send_command(f"KEYUP {key}")

    def send_command(self, command):
        if self.client_socket:
            try:
                self.client_socket.send(command.encode())
            except Exception as e:
                print(f"Error sending command: {e}")

if __name__ == "__main__":
    server = RemoteControlServer()
    server.start()
