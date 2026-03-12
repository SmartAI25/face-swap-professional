import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import Canvas
import threading
import os
from PIL import Image, ImageTk
from main_engine import FaceSwapEngine
import subprocess

class ProfessionalFaceSwapGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎭 Face Swap Professional - All Features")
        self.root.geometry("1400x900")
        self.root.configure(bg="#0a0e27")
        
        self.engine = FaceSwapEngine()
        
        self.source_path = None
        self.target_path = None
        self.output_path = None
        self.preview_images = {}
        
        self.create_ui()
    
    def create_ui(self):
        """Create professional UI"""
        
        # Header
        header = tk.Frame(self.root, bg="#1a1f3a", height=80)
        header.pack(fill="x")
        
        title = tk.Label(header, text="🎭 Face Swap Professional", 
                        font=("Arial", 24, "bold"), bg="#1a1f3a", fg="#00ff88")
        title.pack(pady=10)
        
        subtitle = tk.Label(header, text="100% Local • No Restrictions • Full Privacy", 
                           font=("Arial", 11), bg="#1a1f3a", fg="#00ffff")
        subtitle.pack()
        
        # Main content
        content = tk.Frame(self.root, bg="#0a0e27")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left Panel - Controls
        left_panel = tk.Frame(content, bg="#1a1f3a", width=350)
        left_panel.pack(side="left", fill="both", padx=(0, 10))
        
        self.create_control_panel(left_panel)
        
        # Right Panel - Preview
        right_panel = tk.Frame(content, bg="#1a1f3a")
        right_panel.pack(side="right", fill="both", expand=True)
        
        self.create_preview_panel(right_panel)
    
    def create_control_panel(self, parent):
        """Create control panel"""
        
        # Feature Selection
        feature_frame = tk.LabelFrame(parent, text="Select Feature", 
                                     bg="#1a1f3a", fg="#00ff88", font=("Arial", 10, "bold"))
        feature_frame.pack(fill="x", padx=10, pady=10)
        
        self.feature_var = tk.StringVar(value="image_swap")
        
        features = [
            ("Image Face Swap", "image_swap"),
            ("Video Face Swap", "video_swap"),
            ("Image to Video", "image_to_video")
        ]
        
        for text, value in features:
            tk.Radiobutton(feature_frame, text=text, variable=self.feature_var, 
                          value=value, bg="#1a1f3a", fg="#ffffff",
                          selectcolor="#00ff88", font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)
        
        # File Selection
        file_frame = tk.LabelFrame(parent, text="Select Files", 
                                  bg="#1a1f3a", fg="#00ff88", font=("Arial", 10, "bold"))
        file_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Button(file_frame, text="📸 Select Source Image", 
                 command=self.select_source, bg="#ff6600", fg="white",
                 font=("Arial", 10, "bold"), width=25).pack(pady=5)
        
        self.source_label = tk.Label(file_frame, text="No file selected", 
                                    bg="#0a0e27", fg="gray", font=("Arial", 9), wraplength=300)
        self.source_label.pack(pady=2)
        
        tk.Button(file_frame, text="🎬 Select Target (Image/Video)", 
                 command=self.select_target, bg="#0066cc", fg="white",
                 font=("Arial", 10, "bold"), width=25).pack(pady=5)
        
        self.target_label = tk.Label(file_frame, text="No file selected", 
                                    bg="#0a0e27", fg="gray", font=("Arial", 9), wraplength=300)
        self.target_label.pack(pady=2)
        
        # Options
        options_frame = tk.LabelFrame(parent, text="Options", 
                                     bg="#1a1f3a", fg="#00ff88", font=("Arial", 10, "bold"))
        options_frame.pack(fill="x", padx=10, pady=10)
        
        # Duration
        duration_inner = tk.Frame(options_frame, bg="#1a1f3a")
        duration_inner.pack(pady=5)
        
        tk.Label(duration_inner, text="Duration (min):", bg="#1a1f3a", 
                fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        
        self.duration_var = tk.StringVar(value="5")
        duration_combo = ttk.Combobox(duration_inner, textvariable=self.duration_var,
                                      values=["5", "10", "15", "20"], 
                                      width=8, state="readonly")
        duration_combo.pack(side="left", padx=5)
        
        # FPS
        fps_inner = tk.Frame(options_frame, bg="#1a1f3a")
        fps_inner.pack(pady=5)
        
        tk.Label(fps_inner, text="Video FPS:", bg="#1a1f3a", 
                fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        
        self.fps_var = tk.StringVar(value="24")
        fps_combo = ttk.Combobox(fps_inner, textvariable=self.fps_var,
                                values=["24", "30"], 
                                width=8, state="readonly")
        fps_combo.pack(side="left", padx=5)
        
        # Process Button
        tk.Button(parent, text="��� START PROCESSING!", 
                 command=self.start_processing, bg="#00ff00", fg="#000000",
                 font=("Arial", 12, "bold"), width=25, height=3).pack(pady=20)
        
        # Progress
        progress_frame = tk.LabelFrame(parent, text="Progress", 
                                      bg="#1a1f3a", fg="#00ff88", font=("Arial", 10, "bold"))
        progress_frame.pack(fill="x", padx=10, pady=10)
        
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           maximum=100, length=300)
        self.progress_bar.pack(fill="x", pady=5)
        
        self.progress_label = tk.Label(progress_frame, text="0%", 
                                      bg="#1a1f3a", fg="#00ff00", font=("Arial", 12, "bold"))
        self.progress_label.pack()
        
        self.status_label = tk.Label(progress_frame, text="Ready...", 
                                    bg="#1a1f3a", fg="#ffff00", font=("Arial", 9))
        self.status_label.pack()
    
    def create_preview_panel(self, parent):
        """Create preview panel"""
        
        preview_frame = tk.LabelFrame(parent, text="Preview & Output", 
                                     bg="#1a1f3a", fg="#00ff88", font=("Arial", 10, "bold"))
        preview_frame.pack(fill="both", expand=True)
        
        # Canvas for images
        self.canvas_frame = tk.Frame(preview_frame, bg="#0a0e27")
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Output buttons
        button_frame = tk.Frame(preview_frame, bg="#1a1f3a")
        button_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(button_frame, text="📁 Open Folder", 
                 command=self.open_folder, bg="#0099ff", fg="white",
                 font=("Arial", 10, "bold"), width=15).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="▶️ Play Output", 
                 command=self.play_output, bg="#00cc00", fg="white",
                 font=("Arial", 10, "bold"), width=15).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="⬇️ Download Output", 
                 command=self.download_output, bg="#ff6600", fg="white",
                 font=("Arial", 10, "bold"), width=15).pack(side="left", padx=5)
    
    def select_source(self):
        file = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.png *.bmp")],
            title="Select Source Image"
        )
        if file:
            self.source_path = file
            self.source_label.config(text=f"✓ {os.path.basename(file)}", fg="#00ff88")
    
    def select_target(self):
        file = filedialog.askopenfilename(
            filetypes=[("All files", "*.*")],
            title="Select Target File"
        )
        if file:
            self.target_path = file
            self.target_label.config(text=f"✓ {os.path.basename(file)}", fg="#00ff88")
    
    def update_progress(self, current, total):
        """Update progress"""
        if total > 0:
            percent = int((current / total) * 100)
            self.progress_var.set(percent)
            self.progress_label.config(text=f"{percent}%")
            self.root.update()
    
    def start_processing(self):
        feature = self.feature_var.get()
        
        if feature in ["image_swap", "video_swap"] and (not self.source_path or not self.target_path):
            messagebox.showerror("Error", "Please select both source and target!")
            return
        
        if feature == "image_to_video" and not self.source_path:
            messagebox.showerror("Error", "Please select source image!")
            return
        
        self.progress_bar.config(state="disabled")
        self.progress_var.set(0)
        self.progress_label.config(text="0%")
        self.status_label.config(text="Processing started...", fg="#ffff00")
        
        thread = threading.Thread(target=self.process_worker)
        thread.start()
    
    def process_worker(self):
        try:
            feature = self.feature_var.get()
            
            if feature == "image_swap":
                self.output_path = "output_image.jpg"
                self.status_label.config(text="Swapping faces...", fg="#ffff00")
                self.engine.swap_faces_image(self.source_path, self.target_path, self.output_path)
                self.progress_var.set(100)
                self.progress_label.config(text="100%")
            
            elif feature == "video_swap":
                self.output_path = "output_video.mp4"
                duration = int(self.duration_var.get())
                self.status_label.config(text="Processing video...", fg="#ffff00")
                self.engine.swap_faces_video(self.source_path, self.target_path, 
                                            self.output_path, max_duration=duration,
                                            progress_callback=self.update_progress)
            
            elif feature == "image_to_video":
                self.output_path = "output_generated.mp4"
                duration = int(self.duration_var.get())
                fps = int(self.fps_var.get())
                self.status_label.config(text="Generating video...", fg="#ffff00")
                self.engine.generate_video_from_image(self.source_path, self.output_path, 
                                                     duration=duration, fps=fps)
                self.progress_var.set(100)
                self.progress_label.config(text="100%")
            
            self.status_label.config(text=f"✅ Complete! Output: {os.path.basename(self.output_path)}", fg="#00ff00")
            messagebox.showinfo("Success", f"Processing Complete!\n\nOutput: {self.output_path}")
        
        except Exception as e:
            self.status_label.config(text=f"❌ Error", fg="#ff0000")
            messagebox.showerror("Error", f"Error: {str(e)[:200]}")
        
        finally:
            self.progress_bar.config(state="normal")
    
    def open_folder(self):
        try:
            os.startfile(os.getcwd())
        except:
            messagebox.showwarning("Error", "Could not open folder")
    
    def play_output(self):
        if self.output_path and os.path.exists(self.output_path):
            try:
                os.startfile(self.output_path)
            except:
                messagebox.showerror("Error", "Could not open file")
        else:
            messagebox.showwarning("Warning", "No output file found!")
    
    def download_output(self):
        if self.output_path and os.path.exists(self.output_path):
            save_path = filedialog.asksaveasfilename(
                defaultextension=os.path.splitext(self.output_path)[1],
                filetypes=[("All files", "*.*")]
            )
            if save_path:
                import shutil
                shutil.copy(self.output_path, save_path)
                messagebox.showinfo("Success", f"Downloaded to:\n{save_path}")
        else:
            messagebox.showwarning("Warning", "No output file found!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProfessionalFaceSwapGUI(root)
    root.mainloop()