# HyDown Download Manager

HyDown is a modern, user-friendly desktop application for managing your file downloads. Built with Python and CustomTkinter, it offers a clean interface inspired by Apple's design principles, making it intuitive to use.

## Features

* **Modern UI:** Clean and aesthetically pleasing interface using CustomTkinter.
* **Queue Management:** Add multiple downloads to a queue.
* **Concurrent Downloads:** Download multiple files simultaneously (configurable).
* **Progress Tracking:** Real-time display of download progress, speed, and ETA for each item.
* **Download Controls:** Pause, resume, cancel, and retry downloads.
* **Filtering & Searching:**
    * Filter downloads by status (All, Downloading, Paused, Queued, Completed, Failed).
    * Search downloads by name or URL.
* **File Management:**
    * Automatically saves files to a specified download directory.
    * Handles duplicate filenames by appending numbers (e.g., `file(1).zip`).
    * Option to open the containing folder for completed downloads.
* **Settings Panel:**
    * Customize the download directory.
    * Set the maximum number of concurrent downloads.
    * Choose between Light, Dark, and System appearance modes.
* **Persistent Configuration:** Settings are saved locally in a `hydown_config.json` file.
* **Cross-Platform (Source):** Runs on Windows, macOS, and Linux where Python and its dependencies are supported.

## Requirements

To run HyDown Download Manager from source, you'll need:

* Python 3.7+
* The following Python libraries:
    * `customtkinter`
    * `requests`
    * `humanize`
    * `Pillow` (often a dependency of `customtkinter` for image handling, good to have)

You can install these using pip:
```bash
pip install customtkinter requests humanize Pillow


**File Structure**
The project is organized into the following Python files:

hydown_main.py: The main application script. This is the file you run.
hydown_item.py: Defines the DownloadItem class, representing a single download.
hydown_dialogs.py: Contains the AddDownloadDialog and SettingsDialog classes for UI pop-ups.
hydown_config.py: Manages loading and saving application settings and default configurations.
hydown_config.json (auto-generated): Stores user settings.
HyDown_Downloads/ (auto-generated): Default directory where downloaded files are saved.
How to Run from Source
Clone the repository (or download the files):


# If you have it on GitHub
# git clone [https://github.com/your_username/HyDownManager.git](https://github.com/your_username/HyDownManager.git)
# cd HyDownManager
Ensure all .py files (hydown_main.py, hydown_item.py, hydown_dialogs.py, hydown_config.py) are in the same directory.

Install dependencies:


pip install customtkinter requests humanize Pillow
Run the application:


python hydown_main.py
Building an Executable (.exe)
You can create a standalone executable using PyInstaller.

Install PyInstaller:


pip install pyinstaller
Navigate to the project directory in your terminal.

Run PyInstaller (example command):


pyinstaller --name HyDownManager --windowed --onefile --icon=path/to/your/icon.ico hydown_main.py
--windowed: For GUI applications (no console window).
--onefile: To bundle everything into a single executable (optional, creates a larger file but is simpler to distribute).
--icon=path/to/your/icon.ico: To set a custom icon for the executable.
You might need to use the --add-data option if PyInstaller doesn't automatically pick up all necessary customtkinter assets, though it often does.
The executable will be found in the dist folder created by PyInstaller.

Settings and Configuration
Application settings (download directory, max concurrent downloads, appearance mode) are stored in hydown_config.json in the application's root directory.
You can change these settings via the "Settings" button within the application.
The default download location is a folder named HyDown_Downloads created in the same directory as the application.
Future Enhancements (Ideas)
True resumable downloads (handling HTTP Range requests).
Bandwidth limiting options.
Download scheduling.
More detailed error reporting and logging.
Drag and drop support for adding URLs.
System tray integration.
Customizable themes beyond light/dark/system.
.
