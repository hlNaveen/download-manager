import threading
import humanize 
class DownloadItem:
    """Represents a single download item's data and state."""
    def __init__(self, id, name, url, file_type):
        self.id = id
        self.name = name 
        self.url = url
        self.actual_file_name = "" 
        self.file_path = ""
        self.size_bytes = 0
        self.downloaded_bytes = 0
        self.progress = 0 
        self.speed_bps = 0 
        self.eta_seconds = float('inf')
        self.status = 'queued' 
        self.file_type = file_type
        self.error_message = ""
        

        self.thread = None
        self.cancel_event = threading.Event()
        self.pause_event = threading.Event() 

    def get_display_size(self):
        if self.size_bytes > 0:
            return humanize.naturalsize(self.size_bytes)
        return "N/A"

    def get_display_speed(self):
        if self.status == 'downloading' and self.speed_bps > 0:
            return f"{humanize.naturalsize(self.speed_bps / 8, binary=True)}/s" # Bytes/s
        return ""

    def get_display_eta(self):
        if self.status == 'downloading' and self.eta_seconds != float('inf') and self.eta_seconds > 0:
            return humanize.naturaldelta(self.eta_seconds)
        return ""

    def get_display_status(self):
        if self.status == 'downloading':
            speed_str = self.get_display_speed()
            eta_str = self.get_display_eta()
            parts = [f"{self.progress}%"]
            if speed_str: parts.append(speed_str)
            if eta_str: parts.append(eta_str)
            return " - ".join(parts)
        elif self.status == 'paused':
            return f"Paused - {self.progress}%"
        elif self.status == 'completed':
            return "Completed"
        elif self.status == 'failed':
            return f"Failed: {self.error_message or 'Unknown error'}"
        elif self.status == 'queued':
            return "Queued"
        elif self.status == 'cancelling':
            return "Cancelling..."
        return self.status.capitalize()
