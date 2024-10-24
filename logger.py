import os
import sys
from datetime import datetime

class LogHandler:
    """Handles logging operations with simple text format."""
    
    def __init__(self, log_path: str, input_file: str):
        """Initialize the log handler."""
        self.log_path = log_path
        self.operation_start = datetime.now()
        self.session_id = self.operation_start.strftime("%Y%m%d_%H%M%S")
        self.input_file = input_file
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        # Initialize log file with header
        self._write_log(f"=== Session Start: {self.session_id} ===")
        self._write_log(f"Input File: {input_file}")
        self._write_log(f"Start Time: {self.operation_start}")
        self._write_log("="*50)
    
    def _write_log(self, message: str):
        """Write a message to the log file."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            log_line = f"{timestamp} | {message}\n"
            
            with open(self.log_path, 'a', encoding='utf-8', buffering=1) as log_file:
                log_file.write(log_line)
        except Exception as e:
            print(f"Warning: Failed to write to log file: {str(e)}", file=sys.stderr)
    
    def log_sequence(self, step: str, status: str, message: str):
        """Log a sequence step."""
        self._write_log(f"{step:15} | {status:10} | {message}")
    
    def log_chunk_operation(self, chunk_id: str, status: str, start_time: datetime, 
                          end_time: datetime, size: int, chunk_hash: str, 
                          output_path: str, offset: int):
        """Log a chunk operation."""
        duration = (end_time - start_time).total_seconds()
        size_mb = size / (1024 * 1024)
        
        msg = (f"Chunk: {chunk_id} | Status: {status} | "
               f"Size: {size_mb:.2f}MB | Offset: {offset} | "
               f"Duration: {duration:.2f}s | Hash: {chunk_hash}")
        
        self._write_log(msg)
    
    def log_error(self, message: str):
        """Log an error message."""
        self._write_log(f"ERROR: {message}")
    
    def log_info(self, message: str):
        """Log an informational message."""
        self._write_log(f"INFO: {message}")
    
    def close(self):
        """Log session end and cleanup."""
        end_time = datetime.now()
        duration = (end_time - self.operation_start).total_seconds()
        
        self._write_log("="*50)
        self._write_log(f"Session End: {end_time}")
        self._write_log(f"Total Duration: {duration:.2f} seconds")
        self._write_log("="*50)