import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import time
import random
import requests 
import os 
import humanize 
import shutil 
import subprocess 


from hydown_item import DownloadItem
from hydown_dialogs import AddDownloadDialog, SettingsDialog
from hydown_config import load_settings, save_settings_to_file, ensure_download_dir_exists


APP_NAME = "HyDown Download Manager" 
APP_WIDTH = 980 
APP_HEIGHT = 780

class DownloadManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.minsize(800, 600) 

        self.item_frames_map = {} 
        self.downloads_data = []
        self.current_filter = "all"
        self.current_search_term = ""
        self.active_download_threads = {}
        self.download_queue_lock = threading.Lock()


        settings = load_settings()
        self.download_dir = settings["download_dir"]
        self.max_concurrent_downloads = settings["max_concurrent_downloads"]
        self.appearance_mode = settings["appearance_mode"]
        
        ensure_download_dir_exists(self.download_dir) 

        ctk.set_appearance_mode(self.appearance_mode) 
        ctk.set_default_color_theme("blue") 

        self._create_widgets()
        self._render_download_list() 
        
        self.queue_manager_thread = threading.Thread(target=self._manage_download_queue, daemon=True)
        self.queue_manager_thread.start()
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _apply_and_save_settings(self, new_settings_dict):
        """Applies new settings and saves them to file."""
        previous_appearance_mode = self.appearance_mode
        
        self.download_dir = new_settings_dict.get("download_dir", self.download_dir)
        self.max_concurrent_downloads = new_settings_dict.get("max_concurrent_downloads", self.max_concurrent_downloads)
        self.appearance_mode = new_settings_dict.get("appearance_mode", self.appearance_mode)

        ensure_download_dir_exists(self.download_dir) 

        settings_to_save = {
            "download_dir": self.download_dir,
            "max_concurrent_downloads": self.max_concurrent_downloads,
            "appearance_mode": self.appearance_mode
        }
        
        if save_settings_to_file(settings_to_save):
            self.status_label.configure(text=f"Download Path: {self.download_dir}")
            active_count = sum(1 for item_id in self.active_download_threads if self.active_download_threads[item_id].is_alive())
            self.active_downloads_label.configure(text=f"Active: {active_count}/{self.max_concurrent_downloads}")
            
            if previous_appearance_mode != self.appearance_mode:
                ctk.set_appearance_mode(self.appearance_mode)
                self.theme_menu.set(self.appearance_mode.capitalize())

                self._render_download_list() 
        else:
            messagebox.showerror("Error", "Could not save settings.", parent=self)


    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1) 

        main_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_content_frame.pack(fill="both", expand=True, padx=15, pady=10)


        main_content_frame.grid_columnconfigure(0, weight=1)
        main_content_frame.grid_rowconfigure(2, weight=1) 

        header_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, pady=(0,15), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header_frame, text=APP_NAME, font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, sticky="w")

        header_buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_buttons_frame.grid(row=0, column=1, sticky="e")
        
        self.add_button = ctk.CTkButton(header_buttons_frame, text="+ Add New", command=lambda: self._show_add_dialog(), height=30)
        self.add_button.pack(side="left", padx=(0,8))
        
        self.settings_button = ctk.CTkButton(header_buttons_frame, text="Settings", command=lambda: self._show_settings_dialog(), height=30)
        self.settings_button.pack(side="left", padx=(0,8))

        self.theme_menu = ctk.CTkOptionMenu(header_buttons_frame, values=["Light", "Dark", "System"], command=self._change_theme_from_menu, height=30, width=100)
        self.theme_menu.set(self.appearance_mode.capitalize()) 
        self.theme_menu.pack(side="left")
        
        search_filter_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        search_filter_frame.grid(row=1, column=0, pady=(0,15), sticky="ew")
        search_filter_frame.grid_columnconfigure(1, weight=1) 

        self.filter_values = ["All", "Downloading", "Paused", "Queued", "Completed", "Failed"]
        self.segmented_button_var = ctk.StringVar(value="All") 
        self.filter_segmented_button = ctk.CTkSegmentedButton(
            search_filter_frame, 
            values=self.filter_values,
            command=self._set_filter_from_segmented,
            variable=self.segmented_button_var,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        self.filter_segmented_button.grid(row=0, column=0, padx=(0,15))
        
        self.search_bar = ctk.CTkEntry(search_filter_frame, placeholder_text="Search downloads...", height=30)
        self.search_bar.grid(row=0, column=1, sticky="ew")
        self.search_bar.bind("<KeyRelease>", lambda e: self._on_search())
        
        self.download_list_frame = ctk.CTkScrollableFrame(main_content_frame, label_text="Downloads", label_font=ctk.CTkFont(size=15, weight="bold"))
        self.download_list_frame.grid(row=2, column=0, sticky="nsew")
        if hasattr(self.download_list_frame, '_scrollbar') and self.download_list_frame._scrollbar: 
            self.download_list_frame._scrollbar.configure(height=0) 

        footer_frame = ctk.CTkFrame(main_content_frame, corner_radius=0, fg_color="transparent")
        footer_frame.grid(row=3, column=0, pady=(10,0), sticky="ew")
        self.active_downloads_label = ctk.CTkLabel(footer_frame, text=f"Active: 0/{self.max_concurrent_downloads}", font=ctk.CTkFont(size=11))
        self.active_downloads_label.pack(side="left")
        self.status_label = ctk.CTkLabel(footer_frame, text=f"Download Path: {self.download_dir}", font=ctk.CTkFont(size=11), anchor="e")
        self.status_label.pack(side="right", fill="x", expand=True)


    def _show_settings_dialog(self):
        current_settings_for_dialog = {
            "download_dir": self.download_dir,
            "max_concurrent_downloads": self.max_concurrent_downloads,
            "appearance_mode": self.appearance_mode
        }
        dialog = SettingsDialog(self, current_settings_for_dialog, self._apply_and_save_settings)

    def _show_add_dialog(self): 
        dialog = AddDownloadDialog(self, self._add_new_download_item)

    def _change_theme_from_menu(self, new_theme_choice: str):
        new_theme_lower = new_theme_choice.lower()
        if self.appearance_mode != new_theme_lower:

            self._apply_and_save_settings({"appearance_mode": new_theme_lower})


    def _update_filter_button_styles(self): 
        pass


    def _add_new_download_item(self, url, name):
        file_type = self._get_file_type_from_name(name)
        sanitized_name = "".join(c if c.isalnum() or c in ('.', '-', '_') else '_' for c in name)
        if not sanitized_name: sanitized_name = f"download_{int(time.time())}"
        
        new_item = DownloadItem( 
            id=int(time.time() * 10000 + random.randint(0,9999)), 
            name=sanitized_name, 
            url=url, 
            file_type=file_type
        )
        with self.download_queue_lock:
            self.downloads_data.insert(0, new_item)
        self.after(0, self._render_download_list)


    def _get_file_type_from_name(self, file_name):
        if not file_name or '.' not in file_name: return 'unknown'
        ext = file_name.split('.')[-1].lower()
        if ext in ['pdf', 'doc', 'docx', 'txt', 'pages']: return 'document'
        if ext in ['zip', 'rar', 'tar', 'gz', '7z']: return 'archive'
        if ext in ['mp4', 'mov', 'avi', 'mkv', 'flv']: return 'video'
        if ext in ['mp3', 'wav', 'aac', 'flac', 'm4a']: return 'audio'
        if ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'heic']: return 'image'
        if ext in ['dmg', 'pkg', 'app', 'exe', 'msi', 'deb']: return 'package'
        return 'unknown'

    def _file_type_icon(self, file_type):
        icons = {'document': "📄", 'archive': "📦", 'video': "🎞️", 'audio': "🎵", 
                   'image': "🖼️", 'package': "⚙️", 'os': "💻", 'unknown': "❔"}
        return icons.get(file_type, "❔")

    def _populate_action_buttons(self, parent_actions_frame, item_data: DownloadItem):
        for widget in parent_actions_frame.winfo_children(): 
            widget.destroy()
        
        btn_width = 28 
        btn_height = 28
        font_size = 14 
        
        if item_data.status == 'downloading':
            ctk.CTkButton(parent_actions_frame, text="❚❚", width=btn_width, height=btn_height, font=ctk.CTkFont(size=font_size), command=lambda i=item_data: self._pause_download(i)).pack(side="left", padx=2)
            ctk.CTkButton(parent_actions_frame, text="✕", width=btn_width, height=btn_height, font=ctk.CTkFont(size=font_size), fg_color="transparent", hover_color=("gray70", "gray30"), text_color=("gray10", "gray90"), command=lambda i=item_data: self._cancel_download(i)).pack(side="left", padx=2)
        elif item_data.status == 'paused':
            ctk.CTkButton(parent_actions_frame, text="▶", width=btn_width, height=btn_height, font=ctk.CTkFont(size=font_size), command=lambda i=item_data: self._resume_download(i)).pack(side="left", padx=2)
            ctk.CTkButton(parent_actions_frame, text="✕", width=btn_width, height=btn_height, font=ctk.CTkFont(size=font_size), fg_color="transparent", hover_color=("gray70", "gray30"), text_color=("gray10", "gray90"), command=lambda i=item_data: self._cancel_download(i)).pack(side="left", padx=2)
        elif item_data.status == 'completed':
            ctk.CTkButton(parent_actions_frame, text="↗", width=btn_width, height=btn_height, font=ctk.CTkFont(size=font_size), fg_color="transparent", hover_color=("gray70", "gray30"), text_color=("gray10", "gray90"), command=lambda i=item_data: self._open_file_location(i)).pack(side="left", padx=2)
            ctk.CTkButton(parent_actions_frame, text="🗑", width=btn_width, height=btn_height, font=ctk.CTkFont(size=font_size), fg_color="transparent", hover_color=("gray70", "gray30"), text_color=("gray10", "gray90"), command=lambda i=item_data: self._remove_from_list(i)).pack(side="left", padx=2)
        elif item_data.status == 'failed':
            ctk.CTkButton(parent_actions_frame, text="↻", width=btn_width, height=btn_height, font=ctk.CTkFont(size=font_size), command=lambda i=item_data: self._retry_download(i)).pack(side="left", padx=2)
            ctk.CTkButton(parent_actions_frame, text="🗑", width=btn_width, height=btn_height, font=ctk.CTkFont(size=font_size), fg_color="transparent", hover_color=("gray70", "gray30"), text_color=("gray10", "gray90"), command=lambda i=item_data: self._remove_from_list(i)).pack(side="left", padx=2)
        elif item_data.status == 'queued':
            ctk.CTkButton(parent_actions_frame, text="✕", width=btn_width, height=btn_height, font=ctk.CTkFont(size=font_size), fg_color="transparent", hover_color=("gray70", "gray30"), text_color=("gray10", "gray90"), command=lambda i=item_data: self._cancel_download(i)).pack(side="left", padx=2)
        elif item_data.status == 'cancelling':
             ctk.CTkLabel(parent_actions_frame, text="...", font=ctk.CTkFont(size=11)).pack(side="left", padx=2)


    def _populate_single_item_frame_content(self, item_frame, item_data: DownloadItem):
        for widget in item_frame.winfo_children(): 
            widget.destroy()
        
        item_frame.grid_columnconfigure(0, weight=0) 
        item_frame.grid_columnconfigure(1, weight=1) 
        item_frame.grid_columnconfigure(2, weight=0) 

        icon_label = ctk.CTkLabel(item_frame, text=self._file_type_icon(item_data.file_type), font=ctk.CTkFont(size=30)) 
        icon_label.grid(row=0, column=0, rowspan=2, padx=(10,15), pady=10, sticky="ns") 

        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", pady=(8,8)) 
        info_frame.grid_columnconfigure(0, weight=1)

        name_label = ctk.CTkLabel(info_frame, text=item_data.name, font=ctk.CTkFont(size=14, weight="bold"), anchor="w") 
        name_label.grid(row=0, column=0, sticky="ew", pady=(0,2))
        name_label.bind("<Enter>", lambda e, text=item_data.url: self.status_label.configure(text=text))
        name_label.bind("<Leave>", lambda e: self.status_label.configure(text=f"Download Path: {self.download_dir}"))

        if item_data.status not in ['completed', 'failed', 'queued', 'cancelling']:
            progress_bar = ctk.CTkProgressBar(info_frame, orientation="horizontal", height=6) 
            progress_bar.set(item_data.progress / 100 if item_data.progress > 0 else 0)
            progress_bar.grid(row=1, column=0, sticky="ew", pady=(2,4)) 
            
            status_detail_text = item_data.get_display_status()
            status_label_row = 2
        else: 
            status_detail_text = item_data.get_display_status()
            status_label_row = 1 

        size_text = item_data.get_display_size()
        if item_data.status == 'downloading' or item_data.status == 'paused':
            status_text_line = f"{humanize.naturalsize(item_data.downloaded_bytes)} of {size_text}  •  {status_detail_text}"
        elif item_data.status == 'completed':
             status_text_line = f"{size_text}  •  {status_detail_text}"
        else:
            status_text_line = status_detail_text

        status_detail_label = ctk.CTkLabel(info_frame, text=status_text_line, font=ctk.CTkFont(size=11), text_color=("gray30", "gray70"), anchor="w")
        status_detail_label.grid(row=status_label_row, column=0, sticky="ew", pady=(0,0))
        
        actions_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=2, rowspan=2, padx=(10,10), pady=10, sticky="nse") 
        self._populate_action_buttons(actions_frame, item_data)


    def _render_download_list(self):
        if not self.winfo_exists(): return
        with self.download_queue_lock:
            current_downloads_copy = list(self.downloads_data)
        filtered_list = []
        search_term_lower = self.current_search_term.lower()
        for item_data_obj in current_downloads_copy:
            current_filter_text = self.segmented_button_var.get().lower()
            matches_filter = (current_filter_text == "all" or item_data_obj.status == current_filter_text)
            matches_search = (not search_term_lower or
                              search_term_lower in item_data_obj.name.lower() or
                              search_term_lower in item_data_obj.url.lower())
            if matches_filter and matches_search:
                filtered_list.append(item_data_obj)

        visible_ids = {item.id for item in filtered_list}
        current_frame_ids = set(self.item_frames_map.keys())
        ids_to_remove_from_map = current_frame_ids - visible_ids
        for item_id in ids_to_remove_from_map:
            if item_id in self.item_frames_map:
                self.item_frames_map[item_id].destroy()
                del self.item_frames_map[item_id]
        
        for widget in self.download_list_frame.winfo_children():
            if hasattr(widget, "_is_no_items_label") and widget._is_no_items_label:
                widget.destroy()
                break 
            is_known_frame = False
            for known_frame in self.item_frames_map.values():
                if widget == known_frame:
                    is_known_frame = True
                    break
            if not is_known_frame and isinstance(widget, ctk.CTkFrame) and not hasattr(widget, "_is_no_items_label"):
                 widget.destroy()

        for frame_widget in self.item_frames_map.values():
            frame_widget.pack_forget()

        if not filtered_list:
            no_items_label = ctk.CTkLabel(self.download_list_frame, text="No downloads to show.", text_color="gray", font=ctk.CTkFont(size=14)) 
            no_items_label._is_no_items_label = True 
            no_items_label.pack(pady=30, anchor="center") 
        else:
            for item_data in filtered_list:
                frame = None
                if item_data.id in self.item_frames_map:
                    frame = self.item_frames_map[item_data.id]
                    self._populate_single_item_frame_content(frame, item_data)
                else:
                    frame = ctk.CTkFrame(self.download_list_frame, border_width=0, corner_radius=10, fg_color=("gray90", "gray20")) 
                    self._populate_single_item_frame_content(frame, item_data)
                    self.item_frames_map[item_data.id] = frame
                if frame: 
                    frame.pack(fill="x", pady=(0,6), padx=5) 
        
        active_count = sum(1 for item_id in self.active_download_threads if self.active_download_threads[item_id].is_alive())
        self.active_downloads_label.configure(text=f"Active: {active_count}/{self.max_concurrent_downloads}")

    def _on_search(self, event=None):
        self.current_search_term = self.search_bar.get()
        self.after(0, self._render_download_list)

    def _set_filter_from_segmented(self, value): 
        self.current_filter = value.lower() 
        self.after(0, self._render_download_list)


    def _pause_download(self, item: DownloadItem):
        if item.status == 'downloading':
            item.pause_event.set()
            item.status = 'paused'
            self.after(0, self._render_download_list)

    def _resume_download(self, item: DownloadItem):
        if item.status == 'paused':
            item.pause_event.clear()
            item.status = 'queued'
            self.after(0, self._render_download_list)

    def _cancel_download(self, item: DownloadItem):
        if item.status in ['downloading', 'paused', 'queued', 'failed']:
            item.status = 'cancelling'
            item.cancel_event.set()
            item.pause_event.set() 
            self.after(0, self._render_download_list)
            if item.id not in self.active_download_threads or not self.active_download_threads[item.id].is_alive():
                self._finalize_cancel(item)

    def _finalize_cancel(self, item: DownloadItem):
        with self.download_queue_lock:
            self.downloads_data = [d for d in self.downloads_data if d.id != item.id]
        if item.id in self.active_download_threads:
            del self.active_download_threads[item.id]
        if item.file_path and os.path.exists(item.file_path):
            try:
                os.remove(item.file_path)
                print(f"Partially downloaded file {item.file_path} deleted.")
            except OSError as e:
                print(f"Error deleting partial file {item.file_path}: {e}")
        self.after(0, self._render_download_list)

    def _remove_from_list(self, item: DownloadItem):
        if item.status in ['completed', 'failed']:
             if messagebox.askyesno("Confirm Remove", f"Are you sure you want to remove '{item.name}' from the list?\n(The actual file will not be deleted.)", parent=self):
                with self.download_queue_lock:
                    self.downloads_data = [d for d in self.downloads_data if d.id != item.id]
                self.after(0, self._render_download_list)

    def _retry_download(self, item: DownloadItem):
        if item.status == 'failed':
            item.status = 'queued'
            item.progress = 0
            item.downloaded_bytes = 0
            item.speed_bps = 0
            item.eta_seconds = float('inf')
            item.error_message = ""
            item.cancel_event.clear()
            item.pause_event.clear()
            self.after(0, self._render_download_list)

    def _open_file_location(self, item: DownloadItem):
        if item.status == 'completed' and item.file_path:
            try:
                if os.path.exists(item.file_path):
                    folder = os.path.dirname(item.file_path)
                    if os.name == 'nt': # Windows
                        os.startfile(folder)
                    elif os.name == 'posix': # macOS, Linux
                        if shutil.which('xdg-open'): # Linux
                            subprocess.run(['xdg-open', folder], check=False)
                        elif shutil.which('open'): # macOS
                            subprocess.run(['open', folder], check=False)
                        else:
                            messagebox.showinfo("Open Folder", f"Could not automatically open folder.\nPath: {folder}", parent=self)
                    else:
                         messagebox.showinfo("Open Folder", f"Unsupported OS for opening folder.\nPath: {folder}", parent=self)
                else:
                    messagebox.showerror("Error", f"File not found: {item.file_path}", parent=self)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open folder: {e}", parent=self)
        elif item.status == 'completed':
             messagebox.showerror("Error", "File path not available.", parent=self)

    def _manage_download_queue(self):
        while True:
            if not self.winfo_exists(): break 
            with self.download_queue_lock:
                active_count = sum(1 for item_id in self.active_download_threads if self.active_download_threads[item_id].is_alive())
                if active_count < self.max_concurrent_downloads:
                    queued_item = None
                    for item_data in self.downloads_data:
                        if item_data.status == 'queued' and item_data.id not in self.active_download_threads:
                            queued_item = item_data
                            break
                    if queued_item:
                        queued_item.status = 'downloading'
                        thread = threading.Thread(target=self._execute_download, args=(queued_item,), daemon=True)
                        queued_item.thread = thread
                        self.active_download_threads[queued_item.id] = thread
                        thread.start()
                        self.after(0, self._render_download_list) 
            

            finished_ids = [item_id for item_id, th in list(self.active_download_threads.items()) if not th.is_alive()] 
            for item_id in finished_ids:
                if item_id in self.active_download_threads: 
                    del self.active_download_threads[item_id]
            
            current_active_count = sum(1 for item_id in self.active_download_threads if self.active_download_threads[item_id].is_alive())
            self.after(0, lambda: self.active_downloads_label.configure(text=f"Active: {current_active_count}/{self.max_concurrent_downloads}"))
            time.sleep(0.8) 

    def _execute_download(self, item: DownloadItem):
        try:
            item.status = 'downloading'
            item.error_message = ""
            self.after(0, self._render_download_list) 
            
            base, ext = os.path.splitext(item.name)
            counter = 1
            prospective_file_name = item.name 
            item.file_path = os.path.join(self.download_dir, prospective_file_name) 
            
            while os.path.exists(item.file_path):
                if item.cancel_event.is_set(): raise SystemExit("Download cancelled during file check")
                prospective_file_name = f"{base}({counter}){ext}"
                item.file_path = os.path.join(self.download_dir, prospective_file_name) 
                counter += 1
            item.actual_file_name = prospective_file_name 

            start_time = time.time()
            last_update_time = start_time
            bytes_since_last_update = 0

            with requests.get(item.url, stream=True, timeout=30) as r: 
                r.raise_for_status() 
                
                total_size_str = r.headers.get('content-length')
                if total_size_str:
                    item.size_bytes = int(total_size_str)
                else:
                    item.size_bytes = 0 

                with open(item.file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=16384): 
                        if item.cancel_event.is_set():
                            item.status = 'cancelling'
                            self.after(0, self._render_download_list)
                            raise SystemExit("Download cancelled by user") 

                        while item.pause_event.is_set():
                            if item.cancel_event.is_set(): 
                                item.status = 'cancelling'
                                self.after(0, self._render_download_list)
                                raise SystemExit("Download cancelled during pause")
                            item.speed_bps = 0 
                            item.eta_seconds = float('inf')
                            if item.status != 'paused': 
                                item.status = 'paused'
                                self.after(0, self._render_download_list)
                            time.sleep(0.1) 
                        

                        if item.status == 'paused': 
                             item.status = 'downloading'
                             last_update_time = time.time() 
                             bytes_since_last_update = 0


                        if chunk:
                            f.write(chunk)
                            item.downloaded_bytes += len(chunk)
                            bytes_since_last_update += len(chunk)

                            if item.size_bytes > 0:
                                item.progress = int((item.downloaded_bytes / item.size_bytes) * 100)
                            
                            current_time = time.time()
                            time_diff = current_time - last_update_time
                            if time_diff >= 0.3: 
                                item.speed_bps = (bytes_since_last_update * 8) / time_diff 
                                if item.speed_bps > 0 and item.size_bytes > 0:
                                    remaining_bytes = item.size_bytes - item.downloaded_bytes
                                    item.eta_seconds = remaining_bytes / (item.speed_bps / 8)
                                else:
                                    item.eta_seconds = float('inf')
                                
                                bytes_since_last_update = 0
                                last_update_time = current_time
                                self.after(0, self._render_download_list)
            
            if not item.cancel_event.is_set(): 
                item.progress = 100
                item.status = 'completed'
                item.speed_bps = 0
                item.eta_seconds = 0

        except requests.exceptions.RequestException as e:
            if not item.cancel_event.is_set():
                item.status = 'failed'
                item.error_message = str(e).splitlines()[0][:100] # First line, max 100 chars
        except SystemExit as e: # For our explicit cancellations
            print(f"Thread for {item.name} exited: {e}")

        except Exception as e: # Catch other unexpected errors
            if not item.cancel_event.is_set():
                item.status = 'failed'
                item.error_message = f"Unexpected error: {str(e)[:100]}"
        finally:
            if item.status == 'cancelling':
                self.after(0, lambda: self._finalize_cancel(item))
            else: 
                self.after(0, self._render_download_list)
            


    def _on_closing(self):
        items_to_cancel = []
        with self.download_queue_lock: 
            for item in self.downloads_data:
                if item.status in ['downloading', 'paused']:
                    items_to_cancel.append(item)
        
        if items_to_cancel:
            if messagebox.askyesnocancel("Confirm Exit", f"{len(items_to_cancel)} download(s) are active. Cancel them and exit?"):
                for item in items_to_cancel:
                    item.cancel_event.set()
                    item.pause_event.set() 
            else:
                return # Don't close
        
        self.destroy()

if __name__ == "__main__":
    if os.name == 'nt': 
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception as e:
            print(f"Could not set DPI awareness: {e}")
    app = DownloadManagerApp()
    app.mainloop()
