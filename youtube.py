import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import threading
import os
from PIL import Image, ImageTk
import requests
from io import BytesIO


class YouTubeDownloader:
    """
    A YouTube video downloader application using tkinter and yt-dlp.
    """

    def __init__(self, root):
        """
        Initializes the main application window.
        """
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("650x650")
        self.root.minsize(600, 600)

        # Variables
        self.download_path = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.url = tk.StringVar()
        self.quality = tk.StringVar(value="best")
        self.thumbnail_image = None

        self.setup_ui()

    def setup_ui(self):
        """
        Sets up the user interface of the application.
        """
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame, text="YouTube Video Downloader", font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # URL input with Fetch button
        ttk.Label(main_frame, text="Video URL:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        url_entry = ttk.Entry(main_frame, textvariable=self.url, width=40)
        url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        fetch_btn = ttk.Button(main_frame, text="Fetch Info", command=self.fetch_info)
        fetch_btn.grid(row=1, column=2, padx=(5, 0), pady=5)

        # Thumbnail display
        self.thumbnail_frame = ttk.LabelFrame(
            main_frame, text="Video Preview", padding="10"
        )
        self.thumbnail_frame.grid(
            row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10
        )

        self.thumbnail_label = ttk.Label(
            self.thumbnail_frame, text="No thumbnail loaded"
        )
        self.thumbnail_label.pack()

        self.video_title = ttk.Label(
            self.thumbnail_frame, text="", wraplength=550, font=("Arial", 10, "bold")
        )
        self.video_title.pack(pady=(5, 0))

        self.video_duration = ttk.Label(self.thumbnail_frame, text="")
        self.video_duration.pack()

        # Download path
        ttk.Label(main_frame, text="Save to:").grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        path_entry = ttk.Entry(main_frame, textvariable=self.download_path, width=40)
        path_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        browse_btn = ttk.Button(main_frame, text="Browse", command=self.browse_folder)
        browse_btn.grid(row=3, column=2, padx=(5, 0), pady=5)

        # Quality selection
        ttk.Label(main_frame, text="Quality:").grid(
            row=4, column=0, sticky=tk.W, pady=5
        )
        quality_frame = ttk.Frame(main_frame)
        quality_frame.grid(row=4, column=1, columnspan=2, sticky=tk.W, pady=5)

        qualities = [
            ("Best Quality", "best"),
            ("720p", "720p"),
            ("480p", "480p"),
            ("360p", "360p"),
            ("Audio Only (MP3)", "audio"),
        ]

        for i, (text, value) in enumerate(qualities):
            ttk.Radiobutton(
                quality_frame, text=text, variable=self.quality, value=value
            ).grid(row=0, column=i, padx=5)

        # Progress bar (determinate mode for actual progress)
        ttk.Label(main_frame, text="Progress:").grid(
            row=5, column=0, sticky=tk.W, pady=(10, 5)
        )
        self.progress = ttk.Progressbar(main_frame, mode="determinate", length=500)
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # Status label
        self.status_label = ttk.Label(
            main_frame, text="Ready to download", foreground="green"
        )
        self.status_label.grid(row=7, column=0, columnspan=3, pady=5)

        # Download button
        self.download_btn = ttk.Button(
            main_frame, text="Download", command=self.start_download, width=20
        )
        self.download_btn.grid(row=8, column=0, columnspan=3, pady=20)

    def fetch_info(self):
        """
        Fetches video information from the given URL.
        """
        url = self.url.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please enter a YouTube URL")
            return

        self.update_status("Fetching video information...", "blue")
        threading.Thread(
            target=self._fetch_info_thread, args=(url,), daemon=True
        ).start()

    def _fetch_info_thread(self, url):
        """
        Fetches video information in a separate thread to avoid blocking the GUI.
        """
        try:
            ydl_opts = {"quiet": True, "no_warnings": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.root.after(0, lambda: self.display_video_info(info))
        except Exception as e:
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Error", f"Failed to fetch info: {str(e)}"
                ),
            )
            self.root.after(0, lambda: self.update_status("Ready to download", "green"))

    def display_video_info(self, info):
        """
        Displays the video information on the GUI.
        """
        # Display title
        title = info.get("title", "Unknown Title")
        self.video_title.config(text=title)

        # Display duration
        duration = info.get("duration", 0)
        mins, secs = divmod(duration, 60)
        self.video_duration.config(text=f"Duration: {int(mins)}:{int(secs):02d}")

        # Load and display thumbnail
        thumbnail_url = info.get("thumbnail")
        if thumbnail_url:
            try:
                response = requests.get(thumbnail_url, timeout=5)
                img_data = Image.open(BytesIO(response.content))
                img_data = img_data.resize((320, 180), Image.LANCZOS)
                self.thumbnail_image = ImageTk.PhotoImage(img_data)
                self.thumbnail_label.config(image=self.thumbnail_image, text="")
            except:
                self.thumbnail_label.config(text="Thumbnail not available")

        self.update_status("Ready to download", "green")

    def browse_folder(self):
        """
        Opens a dialog to choose a download folder.
        """
        folder = filedialog.askdirectory()
        if folder:
            self.download_path.set(folder)

    def update_status(self, message, color="black"):
        """
        Updates the status label with the given message and color.
        """
        self.status_label.config(text=message, foreground=color)

    def download_video(self):
        """
        Downloads the video using yt-dlp.
        """
        try:
            url = self.url.get().strip()
            if not url:
                self.update_status("Please enter a URL", "red")
                return

            self.download_btn.config(state="disabled")
            self.progress["value"] = 0
            self.update_status("Downloading...", "blue")

            # yt-dlp options with progress hook
            ydl_opts = {
                "outtmpl": os.path.join(self.download_path.get(), "%(title)s.%(ext)s"),
                "progress_hooks": [self.progress_hook],
            }

            quality = self.quality.get()
            if quality == "audio":
                ydl_opts.update(
                    {
                        "format": "bestaudio/best",
                        "postprocessors": [
                            {
                                "key": "FFmpegExtractAudio",
                                "preferredcodec": "mp3",
                                "preferredquality": "192",
                            }
                        ],
                    }
                )
            elif quality == "best":
                ydl_opts["format"] = (
                    "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
                )
            else:
                ydl_opts["format"] = (
                    f"bestvideo[height<={quality[:-1]}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality[:-1]}]"
                )

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.progress["value"] = 100
            self.update_status("Download completed successfully!", "green")
            messagebox.showinfo("Success", "Video downloaded successfully!")

        except Exception as e:
            self.update_status(f"Error: {str(e)}", "red")
            messagebox.showerror("Error", f"Download failed: {str(e)}")

        finally:
            self.download_btn.config(state="normal")

    def progress_hook(self, d):
        """
        A hook for yt-dlp to update the progress bar.
        """
        if d["status"] == "downloading":
            try:
                # Extract percentage from the progress info
                percent_str = d.get("_percent_str", "0%").replace("%", "").strip()
                percent = float(percent_str)

                # Update progress bar
                self.root.after(0, lambda: self.progress.config(value=percent))

                # Update status with download speed
                speed = d.get("_speed_str", "N/A")
                self.root.after(
                    0,
                    lambda: self.update_status(
                        f"Downloading... {percent:.1f}% - Speed: {speed}", "blue"
                    ),
                )
            except:
                pass
        elif d["status"] == "finished":
            self.root.after(0, lambda: self.update_status("Processing...", "orange"))

    def start_download(self):
        """
        Starts the video download in a separate thread.
        """
        # Run download in a separate thread to prevent GUI freezing
        thread = threading.Thread(target=self.download_video, daemon=True)
        thread.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()
