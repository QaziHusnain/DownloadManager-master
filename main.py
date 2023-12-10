import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import requests
import os
import time
from tkinter import ttk  # Import ttk for Progressbar
import threading

class DownloadManagerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Download Manager")

        self.url_label = tk.Label(master, text="Enter URL:")
        self.url_label.pack()

        self.url_entry = tk.Entry(master, width=50)
        self.url_entry.pack()

        self.download_path_label = tk.Label(master, text="Enter Download Path:")
        self.download_path_label.pack()

        self.download_path_entry = tk.Entry(master, width=50)
        self.download_path_entry.pack()

        self.browse_button = tk.Button(master, text="Browse", command=self.browse_download_path)
        self.browse_button.pack()

        self.download_button = tk.Button(master, text="Download", command=self.download_file)
        self.download_button.pack()

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(master, variable=self.progress_var, length=300, mode='determinate')
        self.progress_bar.pack()

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(master, textvariable=self.status_var)
        self.status_label.pack()

        # Additional labels for speed, remaining, and total volume
        self.speed_var = tk.StringVar()
        self.speed_label = tk.Label(master, textvariable=self.speed_var)
        self.speed_label.pack()

        self.remaining_var = tk.StringVar()
        self.remaining_label = tk.Label(master, textvariable=self.remaining_var)
        self.remaining_label.pack()

        self.total_var = tk.StringVar()
        self.total_label = tk.Label(master, textvariable=self.total_var)
        self.total_label.pack()

    def browse_download_path(self):
        download_path = filedialog.askdirectory(title="Select Download Folder")
        if download_path:
            self.download_path_entry.delete(0, tk.END)
            self.download_path_entry.insert(0, download_path)

    def download_file(self):
        url = self.url_entry.get()
        download_folder = self.download_path_entry.get()

        try:
            os.makedirs(download_folder, exist_ok=True)

            # Create a separate thread for the download operation
            download_thread = threading.Thread(target=self.download, args=(url, download_folder))
            download_thread.start()

        except Exception as e:
            messagebox.showerror("Error", f"Download manager error: {e}")

    def download(self, url, destination_folder):
        try:
            file_name = os.path.join(destination_folder, url.split("/")[-1])

            # Check if the file already exists
            if os.path.exists(file_name):
                total_size = os.path.getsize(file_name)
            else:
                with requests.get(url, stream=True) as response:
                    response.raise_for_status()
                    total_size = int(response.headers.get('content-length', 0))

                    with open(file_name, "wb") as file:
                        downloaded_size = 0
                        for data in response.iter_content(chunk_size=1024):
                            size = file.write(data)
                            downloaded_size += size
                            progress = (downloaded_size / total_size) * 100 if total_size > 0 else 0
                            self.progress_var.set(progress)
                            self.master.update_idletasks()  # Force GUI update

            self.status_var.set(f"Downloaded: {file_name}")
            self.progress_var.set(0)  # Reset progress bar
            self.master.update()  # Force GUI update
        except Exception as e:
            self.status_var.set(f"Error downloading {url}: {e}")
            self.master.update()  # Force GUI update

    @staticmethod
    def format_size(size):
        # Format size to human-readable format
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                break
            size /= 1024.0
        return f"{size:.2f} {unit}"

if __name__ == "__main__":
    root = tk.Tk()
    gui = DownloadManagerGUI(root)
    root.mainloop()
