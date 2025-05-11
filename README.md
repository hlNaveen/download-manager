# HyDown Download Manager

HyDown is a modern, user-friendly desktop application for managing your file downloads. Built with Python and CustomTkinter, it offers a clean interface inspired by Apple's design principles, making it intuitive to use.

![HyDown Screenshot]()

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
* **Cross-Platform:** Runs on Windows, macOS, and Linux where Python and its dependencies are supported.

## Installation

### Option 1: Run from Source

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your_username/HyDown.git
   cd HyDown
   ```

2. **Install dependencies:**
   ```bash
   pip install customtkinter requests humanize Pillow
   ```

3. **Run the application:**
   ```bash
   python hydown.py
   ```

### Option 2: Standalone Executable (Windows)

1. Download the latest release from the [Releases](https://github.com/your_username/HyDown/releases) page.
2. Extract the ZIP file (if applicable).
3. Run `HyDown.exe`.

## Usage Guide

### Adding Downloads

1. Click the "Add Download" button.
2. Enter the URL of the file you want to download.
3. Optionally, customize the filename.
4. Click "Add" to add the download to the queue.

### Managing Downloads

- **Start/Pause:** Click the play/pause button next to a download.
- **Cancel:** Click the "X" button to cancel a download.
- **Retry:** For failed downloads, click the retry button.
- **Open Folder:** Click the folder icon to open the folder containing a completed download.

### Filtering and Searching

- Use the status dropdown to filter downloads by status.
- Use the search box to search for downloads by name or URL.

### Settings

Access the settings panel by clicking the gear icon:

- **Download Directory:** Choose where downloaded files will be saved.
- **Max Concurrent Downloads:** Set how many files can be downloaded simultaneously.
- **Appearance Mode:** Choose between Light, Dark, or System.

## Building from Source

### Creating an Executable

You can create a standalone executable using PyInstaller:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```bash
   pyinstaller --name HyDown --windowed --onefile --icon=path/to/your/icon.ico hydown.py
   ```

The executable will be created in the `dist` directory.

## Configuration

HyDown saves your settings in `hydown_config.json` in the application's directory. The following settings are stored:

- Download directory
- Maximum concurrent downloads
- Appearance mode (Light/Dark/System)

The default download location is a folder named `HyDown_Downloads` created in the same directory as the application.

## Requirements

- Python 3.7+
- Dependencies:
  - customtkinter
  - requests
  - humanize
  - Pillow

## Future Enhancements

- True resumable downloads (handling HTTP Range requests)
- Bandwidth limiting options
- Download scheduling
- More detailed error reporting and logging
- Drag and drop support for adding URLs
- System tray integration
- Customizable themes beyond light/dark/system

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the modern UI framework
- [Requests](https://docs.python-requests.org/) for the HTTP library
- [Humanize](https://github.com/jmoiron/humanize) for human-readable metrics

