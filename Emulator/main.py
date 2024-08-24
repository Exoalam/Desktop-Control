import tkinter as tk
from recorder import ActionRecorderPlayer

def main():
    root = tk.Tk()
    app = ActionRecorderPlayer(root)
    root.mainloop()

if __name__ == "__main__":
    main()