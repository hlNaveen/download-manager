import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime, timedelta
import requests
from ttkbootstrap import Style
from plyer import notification

from ai_assistant import AIAssistant
from utils import get_max_speed, prompt_save_location
from styles import apply_cloud_style

class DownloadManager(tk.Tk):
    def __init__(self):
        super().__init__()

        self.style = Style(theme="superhero")  # Use a modern, cloud-inspired theme
        self.title("Cloud Download Manager")
        self.geometry("800x600")
        apply_cloud_style(self)

        self.create_widgets()
        self.configure_grid()
        
        self.download_queue = []
        self.downloading = False
        self.download_thread = None
        self.current_download = None
        self.paused = False
        self.progress = 0
        self.bytes_downloaded = 0
        self.retry_count = 3

        self.ai_assistant = AIAssistant()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        self.url_label = ttk.Label(self, text="Enter URLs (comma-separated):")
        self.url_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.url_entry = ttk.Entry(self, width=50)
        self.url_entry.grid(row=0, column=1, columnspan=4, padx=10, pady=10, sticky=tk.W+tk.E)

        self.add_to_queue_button = ttk.Button(self, text="Add to Queue", command=self.add_to_queue)
        self.add_to_queue_button.grid(row=0, column=5, padx=10, pady=10)

        self.start_download_button = ttk.Button(self, text="Start", command=self.start_download)
        self.start_download_button.grid(row=1, column=1, padx=10, pady=10)

        self.pause_download_button = ttk.Button(self, text="Pause", command=self.pause_download)
        self.pause_download_button.grid(row=1, column=2, padx=10, pady=10)

        self.resume_download_button = ttk.Button(self, text="Resume", command=self.resume_download)
        self.resume_download_button.grid(row=1, column=3, padx=10, pady=10)

        self.stop_download_button = ttk.Button(self, text="Stop", command=self.stop_download)
        self.stop_download_button.grid(row=1, column=4, padx=10, pady=10)

        self.clear_queue_button = ttk.Button(self, text="Clear Queue", command=self.clear_queue)
        self.clear_queue_button.grid(row=1, column=5, padx=10, pady=10)

        self.schedule_button = ttk.Button(self, text="Schedule", command=self.schedule_download)
        self.schedule_button.grid(row=1, column=0, padx=10, pady=10)

        self.bandwidth_label = ttk.Label(self, text="Max Speed (KB/s):")
        self.bandwidth_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        self.bandwidth_entry = ttk.Entry(self, width=10)
        self.bandwidth_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)

        self.dark_mode_button = ttk.Button(self, text="Toggle Dark Mode", command=self.toggle_dark_mode)
        self.dark_mode_button.grid(row=2, column=2, columnspan=2, padx=10, pady=10, sticky=tk.W)

        self.queue_label = ttk.Label(self, text="Download Queue:")
        self.queue_label.grid(row=3, column=0, columnspan=6, padx=10, pady=10, sticky=tk.W)

        self.queue_listbox = tk.Listbox(self, width=80, height=10)
        self.queue_listbox.grid(row=4, column=0, columnspan=6, padx=10, pady=10, sticky=tk.W+tk.E+tk.N+tk.S)

        self.progress_label = ttk.Label(self, text="Progress:")
        self.progress_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)

        self.progress_bar = ttk.Progressbar(self, mode='determinate', length=400)
        self.progress_bar.grid(row=5, column=2, columnspan=4, pady=10, padx=10, sticky=tk.W+tk.E)

        self.status_label = ttk.Label(self, text="")
        self.status_label.grid(row=6, column=0, columnspan=6, sticky=tk.W+tk.E)

        self.details_label = ttk.Label(self, text="")
        self.details_label.grid(row=7, column=0, columnspan=6, sticky=tk.W+tk.E)

        self.history_label = ttk.Label(self, text="Download History:")
        self.history_label.grid(row=8, column=0, columnspan=6, padx=10, pady=10, sticky=tk.W)

        self.history_listbox = tk.Text(self, width=80, height=10, wrap=tk.WORD)
        self.history_listbox.grid(row=9, column=0, columnspan=6, padx=10, pady=10, sticky=tk.W+tk.E+tk.N+tk.S)

        self.chat_label = ttk.Label(self, text="Chat with AI Assistant:")
        self.chat_label.grid(row=10, column=0, columnspan=6, padx=10, pady=10, sticky=tk.W)

        self.chat_entry = ttk.Entry(self, width=80)
        self.chat_entry.grid(row=11, column=0, columnspan=5, padx=10, pady=10, sticky=tk.W+tk.E)

        self.chat_button = ttk.Button(self, text="Send", command=self.send_chat)
        self.chat_button.grid(row=11, column=5, padx=10, pady=10)

        self.chat_history = tk.Text(self, width=80, height=10, wrap=tk.WORD)
        self.chat_history.grid(row=12, column=0, columnspan=6, padx=10, pady=10, sticky=tk.W+tk.E+tk.N+tk.S)

    def configure_grid(self):
        for i in range(13):
            self.grid_rowconfigure(i, weight=1)
        for i in range(6):
            self.grid_columnconfigure(i, weight=1)

    def send_chat(self):
        user_input = self.chat_entry.get()
        self.chat_entry.delete(0, tk.END)
        response = self.ai_assistant.chat(user_input)
        self.chat_history.insert(tk.END, f"You: {user_input}\n")
        self.chat_history.insert(tk.END, f"Assistant: {response}\n")
        self.chat_history.see(tk.END)

    def add_to_queue(self):
        urls = self.url_entry.get().split(',')
        for url in urls:
            self.queue_listbox.insert(tk.END, url.strip())
        self.url_entry.delete(0, tk.END)

    def start_download(self):
        if self.downloading:
            messagebox.showinfo("Info", "Download in progress. Please wait.")
            return

        if not self.queue_listbox.size():
            messagebox.showinfo("Info", "Queue is empty. Add URLs to queue first.")
            return

        self.downloading = True
        self.paused = False
        self.download_thread = threading.Thread(target=self.download_files)
        self.download_thread.start()

    def download_files(self):
        while self.queue_listbox.size() > 0 and self.downloading:
            url = self.queue_listbox.get(0)
            save_location = prompt_save_location(url)
            if not save_location:
                self.queue_listbox.delete(0)
                continue

            try:
                self.status_label.config(text=f"Downloading {save_location}...")
                self.progress_bar['value'] = 0
                self.progress_label.config(text="Progress: 0%")
                self.details_label.config(text="")
                response = requests.get(url, stream=True)
                total_size = int(response.headers.get('content-length', 0))
                chunk_size = 1024
                start_time = time.time()
                max_speed = get_max_speed(self.bandwidth_entry)

                with open(save_location, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if not self.downloading:
                            self.status_label.config(text="Download paused.")
                            self.current_download = {
                                'url': url,
                                'file_path': save_location,
                                'bytes_downloaded': file.tell(),
                                'total_size': total_size,
                                'start_time': start_time
                            }
                            return

                        if chunk:
                            file.write(chunk)
                            self.bytes_downloaded += len(chunk)
                            progress = (self.bytes_downloaded / total_size) * 100
                            elapsed_time = time.time() - start_time
                            download_speed = self.bytes_downloaded / elapsed_time / 1024
                            remaining_time = (total_size - self.bytes_downloaded) / (download_speed * 1024)
                            self.progress_bar['value'] = progress
                            self.progress_label.config(text=f"Progress: {progress:.2f}%")
                            self.details_label.config(text=f"Downloaded: {self.bytes_downloaded / (1024 * 1024):.2f} MB | "
                                                           f"Speed: {download_speed:.2f} KB/s | "
                                                           f"ETA: {timedelta(seconds=int(remaining_time))}")

                            if max_speed and download_speed > max_speed:
                                time.sleep(1)

                self.queue_listbox.delete(0)
                self.history_listbox.insert(tk.END, f"Downloaded {save_location}\n")
                self.status_label.config(text=f"Completed downloading {save_location}.")
                self.show_notification("Download Complete", f"{save_location} downloaded successfully.")
            except Exception as e:
                self.status_label.config(text=f"Error downloading {save_location}. Retrying...")
                self.retry_count -= 1
                if self.retry_count > 0:
                    self.queue_listbox.insert(tk.END, url)
                else:
                    self.history_listbox.insert(tk.END, f"Failed to download {save_location}. Error: {str(e)}\n")
                    self.status_label.config(text=f"Failed to download {save_location}. Error: {str(e)}")
                    self.retry_count = 3

        self.downloading = False
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Progress: 0%")
        self.details_label.config(text="")

    def pause_download(self):
        self.downloading = False
        self.paused = True

    def resume_download(self):
        if self.paused:
            self.downloading = True
            self.paused = False
            self.status_label.config(text=f"Resuming download: {self.current_download['file_path']}")
            self.download_thread = threading.Thread(target=self.download_files)
            self.download_thread.start()

    def stop_download(self):
        self.downloading = False
        self.paused = False
        self.status_label.config(text="Download stopped.")
        self.current_download = None

    def clear_queue(self):
        self.queue_listbox.delete(0, tk.END)
        self.status_label.config(text="Queue cleared.")

    def schedule_download(self):
        schedule_time_str = tk.simpledialog.askstring("Schedule Download", "Enter start time (HH:MM):")
        if schedule_time_str:
            try:
                schedule_time = datetime.strptime(schedule_time_str, "%H:%M").time()
                now = datetime.now()
                first_run = datetime.combine(now, schedule_time)
                if first_run < now:
                    first_run += timedelta(days=1)
                delay = (first_run - now).total_seconds()
                self.status_label.config(text=f"Scheduled download at {schedule_time_str}.")
                self.after(int(delay * 1000), self.start_download)
            except ValueError:
                messagebox.showerror("Error", "Invalid time format. Use HH:MM.")

    def toggle_dark_mode(self):
        current_theme = self.style.theme_use()
        new_theme = "darkly" if current_theme == "superhero" else "superhero"
        self.style.theme_use(new_theme)

    def show_notification(self, title, message):
        notification.notify(
            title=title,
            message=message,
            timeout=5
        )

    def on_closing(self):
        if self.downloading:
            if messagebox.askokcancel("Quit", "There is a download in progress. Do you want to quit?"):
                self.downloading = False
                self.destroy()
        else:
            self.destroy()

if __name__ == "__main__":
    app = DownloadManager()
    app.mainloop()
