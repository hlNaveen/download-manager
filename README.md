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
