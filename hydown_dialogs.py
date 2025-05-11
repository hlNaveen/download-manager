import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import os
from hydown_config import DEFAULT_DOWNLOAD_DIR, DEFAULT_MAX_CONCURRENT_DOWNLOADS 

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, master, current_settings, callback):
        super().__init__(master)
        self.master_app = master 
        self.current_settings = current_settings
        self.save_callback = callback 

        self.title("Settings")
        self.geometry("550x320")
        self.resizable(False, False)
        self.grab_set()
        self.transient(master)

        self.grid_columnconfigure(1, weight=1)

 
        ctk.CTkLabel(self, text="Download Directory:", font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=20, pady=(25,10), sticky="w")
        self.dir_entry_var = tk.StringVar(value=self.current_settings.get("download_dir", DEFAULT_DOWNLOAD_DIR))
        self.dir_entry = ctk.CTkEntry(self, textvariable=self.dir_entry_var, width=300)
        self.dir_entry.grid(row=0, column=1, padx=10, pady=(25,10), sticky="ew")
        self.browse_button = ctk.CTkButton(self, text="Browse...", width=90, command=self._browse_directory)
        self.browse_button.grid(row=0, column=2, padx=(0,20), pady=(25,10), sticky="w")


        ctk.CTkLabel(self, text="Max Concurrent Downloads:", font=ctk.CTkFont(size=13)).grid(row=1, column=0, padx=20, pady=10, sticky="w")

        self.max_downloads_var = tk.IntVar(value=self.current_settings.get("max_concurrent_downloads", DEFAULT_MAX_CONCURRENT_DOWNLOADS))
        
        self.max_downloads_options = [str(i) for i in range(1, 11)] 
        self.max_downloads_menu = ctk.CTkOptionMenu(self, variable=tk.StringVar(value=str(self.max_downloads_var.get())), values=self.max_downloads_options, command=self._update_max_downloads_var, width=100)
        self.max_downloads_menu.grid(row=1, column=1, padx=10, pady=10, sticky="w")


        ctk.CTkLabel(self, text="Appearance Mode:", font=ctk.CTkFont(size=13)).grid(row=2, column=0, padx=20, pady=10, sticky="w")

        self.appearance_mode_var = tk.StringVar(value=self.current_settings.get("appearance_mode", "system").capitalize())
        self.appearance_mode_menu = ctk.CTkOptionMenu(self, variable=self.appearance_mode_var, values=["Light", "Dark", "System"], width=100)
        self.appearance_mode_menu.grid(row=2, column=1, padx=10, pady=10, sticky="w")


        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=4, column=0, columnspan=3, pady=(40,20), sticky="se")

        self.cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.destroy, width=90)
        self.cancel_button.pack(side="right", padx=(10,20))

        self.save_button = ctk.CTkButton(button_frame, text="Save", command=self._save_settings, width=90)
        self.save_button.pack(side="right", padx=0)
        
        self.bind("<Escape>", lambda e: self.destroy())

    def _update_max_downloads_var(self, choice_str):
        self.max_downloads_var.set(int(choice_str))

    def _browse_directory(self):
        new_dir = filedialog.askdirectory(initialdir=self.dir_entry_var.get(), parent=self)
        if new_dir:
            self.dir_entry_var.set(new_dir)

    def _save_settings(self):
        new_download_dir = self.dir_entry_var.get()

        if not os.path.isdir(new_download_dir):
            try:
                os.makedirs(new_download_dir, exist_ok=True)
            except OSError as e:
                messagebox.showerror("Error", f"Could not create download directory:\n{new_download_dir}\n{e}", parent=self)
                return
        
        new_settings = {
            "download_dir": new_download_dir,
            "max_concurrent_downloads": self.max_downloads_var.get(),
            "appearance_mode": self.appearance_mode_var.get().lower() 
        }
        
        self.save_callback(new_settings) #
        

        if ctk.get_appearance_mode() != new_settings["appearance_mode"]:
            ctk.set_appearance_mode(new_settings["appearance_mode"])
            if hasattr(self.master_app, '_update_filter_button_styles'): 
                 self.master_app._update_filter_button_styles()

        self.destroy()

class AddDownloadDialog(ctk.CTkToplevel):
    def __init__(self, master, callback):
        super().__init__(master)
        self.callback = callback
        self.transient(master) 
        self.title("Add New Download")
        self.geometry("500x280")
        self.resizable(False, False)
        self.grab_set() 
        self.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self, text="Download URL:", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, padx=20, pady=(25,5), sticky="w")
        self.url_entry = ctk.CTkEntry(self, width=460, placeholder_text="https://example.com/file.zip")
        self.url_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        ctk.CTkLabel(self, text="File Name (Optional):", font=ctk.CTkFont(size=13, weight="bold")).grid(row=2, column=0, padx=20, pady=(15,5), sticky="w")
        self.name_entry = ctk.CTkEntry(self, width=460, placeholder_text="My Important File.zip")
        self.name_entry.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=4, column=0, padx=20, pady=(30,20), sticky="e")
        
        self.cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.destroy, width=90)
        self.cancel_button.pack(side="left", padx=(0,10))
        
        self.add_button = ctk.CTkButton(button_frame, text="Add Download", command=self._on_add, width=120)
        self.add_button.pack(side="left")
        
        self.url_entry.focus()
        self.bind("<Escape>", lambda e: self.destroy())

    def _on_add(self):
        url = self.url_entry.get()
        name = self.name_entry.get()
        if not url:
            messagebox.showerror("Error", "Download URL cannot be empty.", parent=self)
            return
        if not name:
            try:
                potential_name = url.split('/')[-1].split('?')[0]
                if not potential_name or len(potential_name) > 200 or potential_name.count('.') == 0:
                    name = "Untitled Download"
                else:
                    name = potential_name
            except Exception:
                name = "Untitled Download"
        self.callback(url, name) 
        self.destroy()
