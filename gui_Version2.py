import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
from main import FaceSwapEngine

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎭 Face Swap Professional")
        self.root.geometry("900x700")
        self.root.configure(bg="#1a1f3a")
        
        self.engine = FaceSwapEngine()
        self.source = None
        self.target = None
        
        # Header
        tk.Label(self.root, text="🎭 Face Swap Professional", 
                font=("Arial", 20, "bold"), bg="#1a1f3a", fg="#00ff88").pack(pady=20)
        
        # Feature selection
        frame = tk.Frame(self.root, bg="#1a1f3a")
        frame.pack(fill="both", expand=True, padx=20)
        
        self.feature = tk.StringVar(value="image")
        
        tk.Radiobutton(frame, text="Image Swap", variable=self.feature, value="image",
                      bg="#1a1f3a", fg="white", font=("Arial", 12)).pack(anchor="w", pady=5)
        tk.Radiobutton(frame, text="Video Swap", variable=self.feature, value="video",
                      bg="#1a1f3a", fg="white", font=("Arial", 12)).pack(anchor="w", pady=5)
        tk.Radiobutton(frame, text="Image to Video", variable=self.feature, value="generate",
                      bg="#1a1f3a", fg="white", font=("Arial", 12)).pack(anchor="w", pady=5)
        
        # File selection
        tk.Button(frame, text="📸 Select Source", command=self.select_source,
                 bg="#ff6600", fg="white", font=("Arial", 11, "bold"), width=20).pack(pady=10)
        self.source_label = tk.Label(frame, text="No file", bg="#0a0e27", fg="gray")
        self.source_label.pack()
        
        tk.Button(frame, text="🎬 Select Target", command=self.select_target,
                 bg="#0066cc", fg="white", font=("Arial", 11, "bold"), width=20).pack(pady=10)
        self.target_label = tk.Label(frame, text="No file", bg="#0a0e27", fg="gray")
        self.target_label.pack()
        
        # Process button
        tk.Button(frame, text="🚀 START!", command=self.start,
                 bg="#00ff00", fg="#000", font=("Arial", 12, "bold"), width=20, height=2).pack(pady=20)
        
        # Progress
        self.progress = ttk.Progressbar(frame, maximum=100, length=300)
        self.progress.pack(pady=10)
        
        self.status = tk.Label(frame, text="Ready", bg="#1a1f3a", fg="#00ff00")
        self.status.pack()
    
    def select_source(self):
        f = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png")])
        if f:
            self.source = f
            self.source_label.config(text=f"✓ {os.path.basename(f)}", fg="#00ff88")
    
    def select_target(self):
        f = filedialog.askopenfilename()
        if f:
            self.target = f
            self.target_label.config(text=f"✓ {os.path.basename(f)}", fg="#00ff88")
    
    def start(self):
        if not self.source:
            messagebox.showerror("Error", "Select source!")
            return
        
        if self.feature.get() != "generate" and not self.target:
            messagebox.showerror("Error", "Select target!")
            return
        
        threading.Thread(target=self.process).start()
    
    def process(self):
        try:
            self.status.config(text="Processing...", fg="#ffff00")
            
            if self.feature.get() == "image":
                self.engine.swap_faces_image(self.source, self.target, "output.jpg")
                self.status.config(text="✅ Done! output.jpg", fg="#00ff00")
            elif self.feature.get() == "video":
                self.engine.swap_faces_video(self.source, self.target, "output.mp4", max_duration=5)
                self.status.config(text="✅ Done! output.mp4", fg="#00ff00")
            else:
                self.engine.generate_video_from_image(self.source, "output.mp4", duration=5)
                self.status.config(text="✅ Done! output.mp4", fg="#00ff00")
            
            messagebox.showinfo("Success", "Processing complete!")
        except Exception as e:
            self.status.config(text="❌ Error", fg="#ff0000")
            messagebox.showerror("Error", str(e)[:100])

if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()