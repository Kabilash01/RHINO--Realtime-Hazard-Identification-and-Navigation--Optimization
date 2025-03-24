import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk, filedialog
import vehicle_crash_detection
import ctypes

ctypes.windll.shcore.SetProcessDpiAwareness(1)

class GradientFrame(tk.Canvas):
    def __init__(self, parent, color1, color2, **kwargs):
        super().__init__(parent, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.draw_gradient()

    def draw_gradient(self):
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        
        r1, g1, b1 = self.winfo_rgb(self.color1)
        r2, g2, b2 = self.winfo_rgb(self.color2)

        r_ratio = (r2 - r1) / height
        g_ratio = (g2 - g1) / height
        b_ratio = (b2 - b1) / height

        for i in range(height):
            nr = int(r1 + (r_ratio * i)) // 256
            ng = int(g1 + (g_ratio * i)) // 256
            nb = int(b1 + (b_ratio * i)) // 256
            color = f"#{nr:02x}{ng:02x}{nb:02x}"
            self.create_line(0, i, width, i, fill=color, tags="gradient")

        self.tag_lower("gradient")

class VcdUI:
    def __init__(self, root):
        self.root = root  # create root window
        self.root.state('zoomed')
        self.root.title("RHINO-Real-Time Hazard Identification and Navigation Optimization")

        # Create a full-screen gradient background
        self.bg_canvas = GradientFrame(root, "#c94b4b", "#4b134f")
        self.bg_canvas.pack(fill='both', expand=True)

        self.title_bar_icon = ImageTk.PhotoImage(file="resources/icon/vehicle_crash_black.png")
        self.root.iconphoto(False, self.title_bar_icon)

        # RHINO Title with Transparent Background
        self.title_label = tk.Label(self.bg_canvas, text="RHINO-Real-Time Hazard Identification and Navigation Optimization", 
                                    font=('times new roman', 20, 'bold'), fg="white", bg="#c94b4b", padx=20, pady=10)
        self.title_label.pack(side="top", fill="x")

        # Sidebar Frame with Gradient
        self.sidebar = GradientFrame(self.bg_canvas, "#c94b4b", "#4b134f", width=200)
        self.sidebar.place(relx=0, rely=0, relheight=1)

        self.icon_white = Image.open("resources/icon/vehicle_crash_white.png").resize((60, 60))
        self.icon_white = ImageTk.PhotoImage(self.icon_white)

        self.sidebar_icon_label = tk.Label(self.sidebar, image=self.icon_white, bg='#4b134f')
        self.sidebar_icon_label.pack(side='top', pady=10)

        self.sidebar_button1 = tk.Button(self.sidebar, text='Crash Detection', width=25, height=2, fg="white", bg="#4b134f", font=('Cascadia Code', 10))
        self.sidebar_button1.pack()
        self.sidebar_button2 = tk.Button(self.sidebar, text='Records', command=self.open_image_viewer, width=25, height=2, fg="white", bg="#4b134f", font=('Cascadia Code', 10))
        self.sidebar_button2.pack()

        self.detections_update_label = tk.Label(self.bg_canvas, text="", bg="#c94b4b", font=('times new roman', 20), fg="white")
        self.detections_update_label.pack(side="bottom", anchor="s", padx=10, pady=60)

        self.combo_label = tk.Label(self.bg_canvas, text="Select a Video Source:", fg="white", bg="#c94b4b", font=('Cascadia Code', 12))
        self.combo_label.pack(side="top", anchor="n", padx=10, pady=10)
        self.combo_box = ttk.Combobox(self.bg_canvas, values=["Video File", "Live-Camera"], text='Select an option')
        self.combo_box.pack(pady=10)

        self.combo_box.bind("<<ComboboxSelected>>", self.handle_combobox)
        self.combo_box.pack(side="top", anchor="n", padx=10, pady=10)

        self.var = tk.BooleanVar()
        self.button1 = tk.Button(self.bg_canvas, text="Detection \nOFF", width=18, height=3, fg="white", bg="#4b134f", command=self.toggle, font=('Cascadia Code', 9))
        self.button1.place(relx=0.2, rely=0.7, anchor="center")

        self.vc = vehicle_crash_detection.VehicleCrash(self.detections_update_label, self.bg_canvas, self.button1)
        self.vc.load_model()

    def open_file(self):
        file_path = filedialog.askopenfilename()
        self.vc.set_source(str(file_path))

    def open_camera(self):
        self.vc.set_source(0)

    def handle_combobox(self, event):
        value = event.widget.get()
        if value == "Video File":
            self.open_file()
        elif value == "Live-Camera":
            self.open_camera()

    def toggle(self):
        self.var.set(not self.var.get())
        if self.var.get():
            self.button1.config(text="Detection \nON")
            self.vc.run_detection()
        else:
            self.button1.config(text="Detection \nOFF")
            self.vc.stop_detection()

    def open_image_viewer(self):
        self.root.withdraw()
        image_viewer_window = tk.Toplevel(self.root)
        image_viewer_window.title("Image Viewer")
        from image_data_viewer import ImageViewer
        ImageViewer(image_viewer_window)

if __name__ == '__main__':
    root = tk.Tk()
    app = VcdUI(root)
    root.mainloop()
