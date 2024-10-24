import os
import hashlib
from typing import Dict, Tuple

class FileValidator:
    """Handles all file validation and path operations."""
    
    @staticmethod
    def validate_input_file(file_path: str) -> Tuple[bool, str]:
        """Validate input file exists and is accessible."""
        if not os.path.exists(file_path):
            return False, f"Input file not found: {file_path}"
        if not os.path.isfile(file_path):
            return False, f"Path is not a file: {file_path}"
        if not os.access(file_path, os.R_OK):
            return False, f"Input file is not readable: {file_path}"
        return True, "File validation successful"

    @staticmethod
    def setup_chunk_directory(input_file: str) -> Dict[str, str]:
        """Create chunk directory and return paths."""
        abs_input_path = os.path.abspath(input_file)
        input_dir = os.path.dirname(abs_input_path)
        file_name = os.path.splitext(os.path.basename(abs_input_path))[0]
        
        chunks_dir = os.path.join(input_dir, f"{file_name}_chunks")
        os.makedirs(chunks_dir, exist_ok=True)
        
        return {
            'chunks_dir': chunks_dir,
            'inventory': os.path.join(chunks_dir, "inventory.json"),
            'log': os.path.join(chunks_dir, "process.log"),
            'original_file': abs_input_path
        }

class FileOperations:
    """Handles file operations including hashing."""
    
    @staticmethod
    def calculate_hash(file_path: str, chunk_size: int = 8192) -> Tuple[str, int]:
        """Calculate SHA-256 hash of file and return file size."""
        sha256_hash = hashlib.sha256()
        file_size = 0
        
        try:
            with open(file_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(chunk_size), b''):
                    sha256_hash.update(byte_block)
                    file_size += len(byte_block)
            return sha256_hash.hexdigest(), file_size
        except Exception as e:
            raise Exception(f"Error calculating file hash: {str(e)}")

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes."""
        return os.path.getsize(file_path)