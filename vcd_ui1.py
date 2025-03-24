import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import ctypes
import vehicle_crash_detection1

# Optimize UI Scaling
ctypes.windll.shcore.SetProcessDpiAwareness(1)

# ---------------------------------------------------Vehicle Crash Detector User Interface------------------------------------------------------
class VcdUI:
    def __init__(self, root):
        self.root = root
        self.root.state('zoomed')
        self.root.title("AI-Powered Vehicle Crash Detection")
        self.root.config(bg="#1E1E1E")

        # Sidebar with Gradient Effect
        self.sidebar = tk.Frame(root, bg='#000000', width=250)
        self.sidebar.pack(side='left', fill='y')

        self.sidebar_icon_label = tk.Label(self.sidebar, text="🚗", font=('Arial', 40), bg='#000000', fg='white')
        self.sidebar_icon_label.pack(side='top', pady=10)

        self.sidebar_button1 = tk.Button(self.sidebar, text='🚘 Crash Detection', width=25, height=2, fg="white", bg="#FF5733",
                                         font=('Arial', 12, 'bold'), relief="ridge", bd=3, activebackground="#C70039")
        self.sidebar_button1.pack(pady=15, padx=10)

        self.sidebar_button2 = tk.Button(self.sidebar, text='📂 View Records', command=self.open_image_viewer, width=25, height=2, 
                                         fg="white", bg="#28A745", font=('Arial', 12, 'bold'), relief="ridge", bd=3, activebackground="#196F3D")
        self.sidebar_button2.pack(pady=15, padx=10)

        # Main Content Area with Gradient
        self.content = tk.Frame(root, bg="#2C3E50", width=800)
        self.content.pack(side='right', fill='both', expand=True)

        self.title_label = tk.Label(self.content, text="🚀 AI Vehicle Crash Detection", font=('Arial', 22, 'bold'), fg="white", bg="#007BFF", 
                                    padx=10, pady=10, relief="solid", bd=2)
        self.title_label.pack(side="top", pady=20, fill="x")

        # Video Selection Dropdown
        self.combo_label = tk.Label(self.content, text="📹 Select a Video Source:", fg="white", bg="#2C3E50", font=('Arial', 14))
        self.combo_label.pack(pady=5)

        self.combo_box = ttk.Combobox(self.content, values=["🎥 Video File", "📡 Live-Camera"], font=('Arial', 12))
        self.combo_box.pack(pady=10, padx=20)
        self.combo_box.bind("<<ComboboxSelected>>", self.handle_combobox)

        # Detection Button with Hover Effect
        self.button1 = tk.Button(self.content, text="🛑 Detection OFF", width=20, height=2, fg="white", bg="#FFC107", 
                                 font=('Arial', 14, 'bold'), relief="raised", bd=3, activebackground="#FFD700", command=self.toggle)
        self.button1.pack(pady=20)

        # Alert Label
        self.detections_update_label = tk.Label(self.content, text="🚨 No Detections Yet", font=('Arial', 16, 'bold'), fg="red", bg="#2C3E50")
        self.detections_update_label.pack(pady=15)

        self.source = "No Video Source Provided Yet!"
        self.var = tk.BooleanVar()
        self.vc = vehicle_crash_detection1.VehicleCrash(self.detections_update_label, self.content, self.button1)
        self.vc.load_model()

    def open_file(self):
        file_path = filedialog.askopenfilename()
        self.vc.set_source(str(file_path))

    def open_camera(self):
        self.vc.set_source(0)

    def handle_combobox(self, event):
        value = event.widget.get()
        if value == "🎥 Video File":
            self.open_file()
        elif value == "📡 Live-Camera":
            self.open_camera()

    def toggle(self):
        self.var.set(not self.var.get())
        if self.var.get():
            self.button1.config(text="✅ Detection ON", bg="red", activebackground="darkred")
            self.vc.run_detection()
        else:
            self.button1.config(text="🛑 Detection OFF", bg="#FFC107", activebackground="#FFD700")
            self.vc.stop_detection()
            self.detections_update_label.configure(text="🚨 No Detections Yet")

    def open_image_viewer(self):
        self.root.withdraw()
        image_viewer_window = tk.Toplevel(self.root)
        image_viewer_window.title("🖼️ Image Viewer")
        from image_data_viewer import ImageViewer
        ImageViewer(image_viewer_window)

if __name__ == '__main__':
    root = tk.Tk()
    app = VcdUI(root)
    root.mainloop()
