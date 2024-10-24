import os
import hashlib
from datetime import datetime
from typing import Dict, Optional, Tuple
from .file_handlers import FileOperations

class ChunkManager:
    """Manages the chunking process."""
    
    def __init__(self, logger):
        self.logger = logger
        self.file_ops = FileOperations()
    
    def calculate_chunk_boundaries(self, file_size: int, chunk_size: int, chunk_number: int) -> Tuple[int, int]:
        """Calculate the start and end positions for a specific chunk."""
        # Adjust chunk_number to 0-based for calculation
        zero_based_chunk = chunk_number - 1
        start_position = zero_based_chunk * chunk_size
        end_position = min(start_position + chunk_size, file_size)
        
        if start_position >= file_size:
            raise ValueError(f"Chunk number {chunk_number} is beyond file size")
            
        return start_position, end_position
    
    def chunk_file(self, input_file: str, output_dir: str, inventory_path: str,
                   chunk_size_mb: int = 1000, specific_chunk: Optional[int] = None) -> Dict:
        """Chunk file according to specifications."""
        chunk_size = chunk_size_mb * 1024 * 1024  # Convert MB to bytes
        
        # Calculate hash and get file size
        self.logger.log_sequence("HASH", "START", "Calculating file hash...")
        file_hash, file_size = self.file_ops.calculate_hash(input_file)
        self.logger.log_sequence("HASH", "COMPLETE", f"Hash: {file_hash[:16]}...")
        
        total_chunks = (file_size + chunk_size - 1) // chunk_size
        
        # Adjust chunk processing to be 1-based
        if specific_chunk is not None:
            if specific_chunk < 1 or specific_chunk > total_chunks:
                raise ValueError(f"Chunk number must be between 1 and {total_chunks}")
            chunks_to_process = [specific_chunk]
        else:
            chunks_to_process = range(1, total_chunks + 1)
        
        self.logger.log_sequence("CHUNKING", "START", 
                               f"Processing {len(chunks_to_process)} chunks")
        
        inventory = {
            "original_filename": os.path.basename(input_file),
            "original_size": file_size,
            "original_hash": file_hash,
            "chunk_size": chunk_size,
            "total_chunks": total_chunks,
            "chunks": []
        }
        
        with open(input_file, 'rb') as f:
            for chunk_num in chunks_to_process:
                chunk_start = datetime.now()
                chunk_id = f"chunk{chunk_num:03d}"
                output_path = os.path.join(output_dir, chunk_id)
                
                # Calculate chunk boundaries
                start_pos, end_pos = self.calculate_chunk_boundaries(file_size, chunk_size, chunk_num)
                chunk_size_actual = end_pos - start_pos
                
                # Read and write chunk
                f.seek(start_pos)
                chunk_data = f.read(chunk_size_actual)
                
                # Write chunk
                os.makedirs(output_dir, exist_ok=True)
                with open(output_path, 'wb') as chunk_file:
                    chunk_file.write(chunk_data)
                
                # Calculate chunk hash
                chunk_hash = hashlib.sha256(chunk_data).hexdigest()
                
                chunk_info = {
                    "chunk_id": chunk_id,
                    "offset": start_pos,
                    "size": chunk_size_actual,
                    "hash": chunk_hash
                }
                
                inventory["chunks"].append(chunk_info)
                
                self.logger.log_chunk_operation(
                    chunk_id=chunk_id,
                    status="completed",
                    start_time=chunk_start,
                    end_time=datetime.now(),
                    size=chunk_size_actual,
                    chunk_hash=chunk_hash,
                    output_path=output_path,
                    offset=start_pos
                )
        
        self.logger.log_sequence("CHUNKING", "COMPLETE", "All chunks processed")
        return inventory