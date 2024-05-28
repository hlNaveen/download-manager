import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import datetime, timedelta
from ttkbootstrap import Style
from plyer import notification

from ai_assistant import AIAssistant
from utils import get_max_speed, prompt_save_location

class DownloadManager(tk.Tk):
    def __init__(self):
        super().__init__()

        self.style = Style(theme="cosmo")
        self.title("Download Manager")
        self.geometry("600x400")

        self.create_widgets()
        self.download_queue = []
        self.downloading = False
        self.download_thread = None
        self.current_download = None
        self.paused = False
        self.progress = 0
        self.bytes_downloaded = 0
        self.retry_count = 3

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(9, weight=1)

    def create_widgets(self):
        self.url_label = ttk.Label(self, text="Enter URLs:")
        self.url_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.url_entry = ttk.Entry(self, width=40)
        self.url_entry.grid(row=0, column=1, columnspan=4, padx=5, pady=5, sticky=tk.W+tk.E)

        self.add_to_queue_button = ttk.Button(self, text="Add to Queue", command=self.add_to_queue)
        self.add_to_queue_button.grid(row=0, column=5, padx=5, pady=5)

        self.start_download_button = ttk.Button(self, text="Start", command=self.start_download)
        self.start_download_button.grid(row=1, column=1, padx=5, pady=5)

        self.pause_download_button = ttk.Button(self, text="Pause", command=self.pause_download)
        self.pause_download_button.grid(row=1, column=2, padx=5, pady=5)

        self.resume_download_button = ttk.Button(self, text="Resume", command=self.resume_download)
        self.resume_download_button.grid(row=1, column=3, padx=5, pady=5)

        self.stop_download_button = ttk.Button(self, text="Stop", command=self.stop_download)
        self.stop_download_button.grid(row=1, column=4, padx=5, pady=5)

        self.clear_queue_button = ttk.Button(self, text="Clear Queue", command=self.clear_queue)
        self.clear_queue_button.grid(row=1, column=5, padx=5, pady=5)

        self.schedule_button = ttk.Button(self, text="Schedule", command=self.schedule_download)
        self.schedule_button.grid(row=1, column=0, padx=5, pady=5)

        self.bandwidth_label = ttk.Label(self, text="Max Speed (KB/s):")
        self.bandwidth_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        self.bandwidth_entry = ttk.Entry(self, width=10)
        self.bandwidth_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        self.dark_mode_button = ttk.Button(self, text="Toggle Dark Mode", command=self.toggle_dark_mode)
        self.dark_mode_button.grid(row=2, column=2, columnspan=2, padx=5, pady=5, sticky=tk.W)

        self.queue_label = ttk.Label(self, text="Download Queue:")
        self.queue_label.grid(row=3, column=0, columnspan=6, padx=5, pady=5, sticky=tk.W)

        self.queue_listbox = tk.Listbox(self, width=80, height=5)
        self.queue_listbox.grid(row=4, column=0, columnspan=6, padx=5, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)

        self.progress_label = ttk.Label(self, text="Progress:")
        self.progress_label.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)

        self.progress_bar = ttk.Progressbar(self, mode='determinate', length=200)
        self.progress_bar.grid(row=5, column=2, columnspan=4, pady=5, padx=5, sticky=tk.W+tk.E)

        self.status_label = ttk.Label(self, text="")
        self.status_label.grid(row=6, column=0, columnspan=6, sticky=tk.W+tk.E)

        self.details_label = ttk.Label(self, text="")
        self.details_label.grid(row=7, column=0, columnspan=6, sticky=tk.W+tk.E)

        self.history_label = ttk.Label(self, text="Download History:")
        self.history_label.grid(row=8, column=0, columnspan=6, padx=5, pady=5, sticky=tk.W)

        self.history_listbox = tk.Text(self, width=80, height=5, wrap=tk.WORD)
        self.history_listbox.grid(row=9, column=0, columnspan=6, padx=5, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)

    def add_to_queue(self):
        urls = self.url_entry.get()
        if not urls:
            messagebox.showerror("Error", "Please enter valid URLs.")
            return

        for url in urls.split(','):
            self.queue_listbox.insert(tk.END, url.strip())
        self.url_entry.delete(0, tk.END)

    def start_download(self):
        if self.downloading:
            messagebox.showinfo("Info", "Download already in progress.")
            return

        if self.queue_listbox.size() == 0:
            messagebox.showinfo("Info", "Queue is empty.")
            return

        self.downloading = True
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Progress: 0%")
        self.status_label.config(text="Starting download...")

        self.download_thread = threading.Thread(target=self.download_queue_files)
        self.download_thread.start()

    def download_queue_files(self):
        while self.queue_listbox.size() > 0 and self.downloading:
            url = self.queue_listbox.get(0)
            file_path = prompt_save_location(url)
            if not file_path:
                self.queue_listbox.delete(0)
                continue

            self.download_file(url, file_path)

            if not self.downloading:
                break

        self.status_label.config(text="All downloads complete.")
        self.downloading = False

    def download_file(self, url, file_path):
        start_time = time.time()
        bytes_downloaded = 0
        total_size = 0
        self.bytes_downloaded = 0
        max_speed = get_max_speed(self.bandwidth_entry)

        for _ in range(self.retry_count):
            try:
                with requests.get(url, stream=True) as response:
                    response.raise_for_status()
                    total_size = int(response.headers.get('content-length', 0))

                    chunk_size = 1024
                    with open(file_path, 'wb') as file:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if not self.downloading:
                                self.status_label.config(text="Download paused.")
                                self.current_download = {
                                    'url': url,
                                    'file_path': file_path,
                                    'bytes_downloaded': bytes_downloaded,
                                    'total_size': total_size,
                                    'start_time': start_time
                                }
                                return

                            if chunk:
                                file.write(chunk)
                                bytes_downloaded += len(chunk)
                                self.bytes_downloaded = bytes_downloaded
                                progress = (bytes_downloaded / total_size) * 100
                                elapsed_time = time.time() - start_time
                                download_speed = bytes_downloaded / elapsed_time / 1024
                                remaining_time = (total_size - bytes_downloaded) / (download_speed * 1024)
                                self.progress_bar['value'] = progress
                                self.progress_label.config(text=f"Progress: {int(progress)}%")
                                self.details_label.config(text=f"Downloaded: {bytes_downloaded // 1024} KB, Speed: {download_speed:.2f} KB/s, Remaining time: {remaining_time:.2f} s")
                                self.update_idletasks()

                                if max_speed and download_speed > max_speed:
                                    time.sleep((len(chunk) / 1024) / max_speed)

                    self.queue_listbox.delete(0)
                    self.history_listbox.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {file_path} downloaded successfully.\n")
                    self.status_label.config(text=f"Download {file_path} complete.")
                    notification.notify(
                        title="Download Complete",
                        message=f"{file_path} has been downloaded successfully.",
                        timeout=5
                    )
                    self.current_download = None
                    break

            except requests.exceptions.RequestException as err:
                self.history_listbox.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {file_path} download failed: {err}\n")
                self.status_label.config(text=f"Download {file_path} failed: {err}")

    def pause_download(self):
        if not self.downloading:
            messagebox.showinfo("Info", "No download in progress.")
            return

        self.downloading = False
        self.paused = True
        self.status_label.config(text="Download paused.")
        self.progress_label.config(text=f"Progress: {int(self.progress)}%")
        self.details_label.config(text="")

    def resume_download(self):
        if not self.paused:
            messagebox.showinfo("Info", "No download to resume.")
            return

        self.downloading = True
        self.paused = False
        self.progress_label.config(text=f"Progress: {int(self.progress)}%")
        self.status_label.config(text="Resuming download...")
        self.download_thread = threading.Thread(target=self.resume_file_download)
        self.download_thread.start()

    def resume_file_download(self):
        if self.current_download:
            url = self.current_download['url']
            file_path = self.current_download['file_path']
            bytes_downloaded = self.current_download['bytes_downloaded']
            total_size = self.current_download['total_size']
            start_time = self.current_download['start_time']
            max_speed = get_max_speed(self.bandwidth_entry)

            try:
                with requests.get(url, stream=True, headers={'Range': f'bytes={bytes_downloaded}-'}) as response:
                    response.raise_for_status()
                    chunk_size = 1024
                    with open(file_path, 'ab') as file:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if not self.downloading:
                                self.status_label.config(text="Download paused.")
                                self.current_download = {
                                    'url': url,
                                    'file_path': file_path,
                                    'bytes_downloaded': bytes_downloaded,
                                    'total_size': total_size,
                                    'start_time': start_time
                                }
                                return

                            if chunk:
                                file.write(chunk)
                                bytes_downloaded += len(chunk)
                                self.bytes_downloaded = bytes_downloaded
                                progress = (bytes_downloaded / total_size) * 100
                                elapsed_time = time.time() - start_time
                                download_speed = bytes_downloaded / elapsed_time / 1024
                                remaining_time = (total_size - bytes_downloaded) / (download_speed * 1024)
                                self.progress_bar['value'] = progress
                                self.progress_label.config(text=f"Progress: {int(progress)}%")
                                self.details_label.config(text=f"Downloaded: {bytes_downloaded // 1024} KB, Speed: {download_speed:.2f} KB/s, Remaining time: {remaining_time:.2f} s")
                                self.update_idletasks()

                                if max_speed and download_speed > max_speed:
                                    time.sleep((len(chunk) / 1024) / max_speed)

                    self.queue_listbox.delete(0)
                    self.history_listbox.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {file_path} downloaded successfully.\n")
                    self.status_label.config(text=f"Download {file_path} complete.")
                    notification.notify(
                        title="Download Complete",
                        message=f"{file_path} has been downloaded successfully.",
                        timeout=5
                    )
                    self.current_download = None

            except requests.exceptions.RequestException as err:
                self.history_listbox.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {file_path} download failed: {err}\n")
                self.status_label.config(text=f"Download {file_path} failed: {err}")

    def stop_download(self):
        self.downloading = False
        self.current_download = None
        self.status_label.config(text="Download stopped.")
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Progress: 0%")
        self.details_label.config(text="")

    def clear_queue(self):
        self.queue_listbox.delete(0, tk.END)

    def on_closing(self):
        if self.downloading:
            self.downloading = False
            if self.download_thread and self.download_thread.is_alive():
                self.download_thread.join()

        self.destroy()

    def schedule_download(self):
        schedule_time = tk.simpledialog.askstring("Schedule Download", "Enter time (HH:MM):")
        if not schedule_time:
            return

        try:
            schedule_time = datetime.strptime(schedule_time, '%H:%M').time()
            now = datetime.now()
            schedule_datetime = datetime.combine(now.date(), schedule_time)

            if schedule_datetime < now:
                schedule_datetime += timedelta(days=1)

            delay = (schedule_datetime - now).total_seconds()
            threading.Timer(delay, self.start_download).start()
            messagebox.showinfo("Info", f"Download scheduled for {schedule_time.strftime('%H:%M')}")
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Please use HH:MM.")

    def toggle_dark_mode(self):
        current_theme = self.style.theme_use()
        if current_theme == "cosmo":
            self.style.theme_use("darkly")
        else:
            self.style.theme_use("cosmo")

if __name__ == "__main__":
    app = DownloadManager()
    app.mainloop()
