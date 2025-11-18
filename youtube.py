import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import threading
import os

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Variables
        self.download_path = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.url = tk.StringVar()
        self.quality = tk.StringVar(value="best")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="YouTube Video Downloader", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # URL input
        ttk.Label(main_frame, text="Video URL:").grid(row=1, column=0, sticky=tk.W, pady=5)
        url_entry = ttk.Entry(main_frame, textvariable=self.url, width=50)
        url_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Download path
        ttk.Label(main_frame, text="Save to:").grid(row=2, column=0, sticky=tk.W, pady=5)
        path_entry = ttk.Entry(main_frame, textvariable=self.download_path, width=40)
        path_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        browse_btn = ttk.Button(main_frame, text="Browse", command=self.browse_folder)
        browse_btn.grid(row=2, column=2, padx=(5, 0), pady=5)
        
        # Quality selection
        ttk.Label(main_frame, text="Quality:").grid(row=3, column=0, sticky=tk.W, pady=5)
        quality_frame = ttk.Frame(main_frame)
        quality_frame.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        qualities = [("Best Quality", "best"), ("720p", "720p"), ("480p", "480p"), 
                    ("360p", "360p"), ("Audio Only (MP3)", "audio")]
        
        for i, (text, value) in enumerate(qualities):
            ttk.Radiobutton(quality_frame, text=text, variable=self.quality, 
                          value=value).grid(row=0, column=i, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=500)
        self.progress.grid(row=4, column=0, columnspan=3, pady=20)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to download", 
                                     foreground="green")
        self.status_label.grid(row=5, column=0, columnspan=3, pady=5)
        
        # Download button
        self.download_btn = ttk.Button(main_frame, text="Download", 
                                      command=self.start_download, width=20)
        self.download_btn.grid(row=6, column=0, columnspan=3, pady=20)
        
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_path.set(folder)
    
    def update_status(self, message, color="black"):
        self.status_label.config(text=message, foreground=color)
    
    def download_video(self):
        try:
            url = self.url.get().strip()
            if not url:
                self.update_status("Please enter a URL", "red")
                return
            
            self.download_btn.config(state="disabled")
            self.progress.start()
            self.update_status("Downloading...", "blue")
            
            # yt-dlp options
            ydl_opts = {
                'outtmpl': os.path.join(self.download_path.get(), '%(title)s.%(ext)s'),
            }
            
            quality = self.quality.get()
            if quality == "audio":
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            elif quality == "best":
                ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            else:
                ydl_opts['format'] = f'bestvideo[height<={quality[:-1]}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality[:-1]}]'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.progress.stop()
            self.update_status("Download completed successfully!", "green")
            messagebox.showinfo("Success", "Video downloaded successfully!")
            
        except Exception as e:
            self.progress.stop()
            self.update_status(f"Error: {str(e)}", "red")
            messagebox.showerror("Error", f"Download failed: {str(e)}")
        
        finally:
            self.download_btn.config(state="normal")
    
    def start_download(self):
        # Run download in a separate thread to prevent GUI freezing
        thread = threading.Thread(target=self.download_video, daemon=True)
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()Lab 
