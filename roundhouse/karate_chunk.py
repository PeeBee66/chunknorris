# File: karate_chunk.py

import os
import json
from datetime import datetime
from typing import Dict, Optional, Tuple, List
from roundhouse.dojo_handlers import FileOperations

class ChunkManager:
    """Manages the chunking process."""
    
    def __init__(self, logger):
        """Initialize ChunkManager with logger."""
        self.logger = logger
        self.file_ops = FileOperations()
    
    def _generate_chunk_id(self, base_filename: str, chunk_number: int) -> str:
        """Generate chunk ID using the original filename pattern.
        
        Args:
            base_filename (str): Original filename without extension
            chunk_number (int): Current chunk number
            
        Returns:
            str: Formatted chunk filename (e.g., filename.chunk001.bin)
        """
        return f"{base_filename}.chunk{chunk_number:03d}.bin"
    
    def _initialize_inventory(self, input_file: str, file_hash: str, file_size: int, 
                            chunk_size: int, inventory_path: str) -> Dict:
        """Initialize inventory with all chunks pre-populated.
        
        Args:
            input_file (str): Path to the original input file
            file_hash (str): Hash of the original file
            file_size (int): Size of the original file in bytes
            chunk_size (int): Size of each chunk in bytes
            inventory_path (str): Path where inventory will be saved
            
        Returns:
            Dict: Complete inventory structure with pending chunks
        """
        total_chunks = (file_size + chunk_size - 1) // chunk_size
        base_filename = os.path.splitext(os.path.basename(input_file))[0]
        
        inventory = {
            "original_filename": os.path.basename(input_file),
            "original_size": file_size,
            "original_hash": file_hash,
            "hash_type": self.file_ops.get_hash_type(),
            "chunk_size": chunk_size,
            "total_chunks": total_chunks,
            "inventory_type": "progressive",
            "creation_time": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "inventory_file": os.path.basename(inventory_path),
            "chunk_status": {
                "total_processed": 0,
                "chunks_remaining": total_chunks
            },
            "chunks": {}
        }
        
        # Pre-populate all chunks with pending status
        for chunk_num in range(1, total_chunks + 1):
            start_pos = (chunk_num - 1) * chunk_size
            expected_size = min(chunk_size, file_size - start_pos)
            
            inventory["chunks"][str(chunk_num)] = {
                "status": "pending",
                "chunk_id": self._generate_chunk_id(base_filename, chunk_num),
                "chunk_number": chunk_num,
                "offset": start_pos,
                "expected_size": expected_size
            }
        
        return inventory
    
    def _load_or_create_inventory(self, input_file: str, inventory_path: str, 
                                file_hash: str, file_size: int, chunk_size: int) -> Dict:
        """Load existing inventory or create new one if it doesn't exist.
        
        Args:
            input_file (str): Path to the original input file
            inventory_path (str): Path to inventory file
            file_hash (str): Hash of the original file
            file_size (int): Size of the original file in bytes
            chunk_size (int): Size of each chunk in bytes
            
        Returns:
            Dict: Loaded or newly created inventory
        """
        try:
            if os.path.exists(inventory_path):
                with open(inventory_path, 'r') as f:
                    inventory = json.load(f)
                self.logger.log_info(f"Loaded existing inventory: {inventory_path}")
                return inventory
        except Exception as e:
            self.logger.log_error(f"Error loading inventory: {str(e)}")
        
        self.logger.log_info(f"Creating new inventory: {inventory_path}")
        return self._initialize_inventory(input_file, file_hash, file_size, 
                                       chunk_size, inventory_path)
    
    def _update_inventory(self, inventory: Dict, chunk_num: int, chunk_info: Dict) -> Dict:
        """Update inventory with completed chunk information.
        
        Args:
            inventory (Dict): Current inventory
            chunk_num (int): Number of the chunk being updated
            chunk_info (Dict): New information for the chunk
            
        Returns:
            Dict: Updated inventory
        """
        chunk_key = str(chunk_num)
        
        # Update chunk information
        inventory["chunks"][chunk_key].update({
            "status": "completed",
            "size": chunk_info["size"],
            "hash": chunk_info["hash"],
            "processing_time": chunk_info["processing_time"],
            "completed_at": datetime.now().isoformat()
        })
        
        # Update status counters
        inventory["chunk_status"]["total_processed"] = sum(
            1 for chunk in inventory["chunks"].values() 
            if chunk["status"] == "completed"
        )
        inventory["chunk_status"]["chunks_remaining"] = (
            inventory["total_chunks"] - inventory["chunk_status"]["total_processed"]
        )
        inventory["last_updated"] = datetime.now().isoformat()
        
        return inventory
    
    def calculate_chunk_boundaries(self, file_size: int, chunk_size: int, chunk_number: int) -> Tuple[int, int]:
        """Calculate the start and end positions for a specific chunk.
        
        Args:
            file_size (int): Total size of the file in bytes
            chunk_size (int): Size of each chunk in bytes
            chunk_number (int): The chunk number to calculate boundaries for
            
        Returns:
            Tuple[int, int]: (start_position, end_position)
            
        Raises:
            ValueError: If chunk number is beyond file size
        """
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
        base_filename = os.path.splitext(os.path.basename(input_file))[0]
        
        # Calculate hash and get file size
        self.logger.log_sequence("HASH", "START", f"Calculating file {self.file_ops.get_hash_type()} hash...")
        file_hash, file_size = self.file_ops.calculate_hash(input_file)
        self.logger.log_sequence("HASH", "COMPLETE", f"Hash: {file_hash[:16]}...")
        
        # Load or create inventory
        inventory = self._load_or_create_inventory(
            input_file, inventory_path, file_hash, file_size, chunk_size
        )
        
        total_chunks = inventory["total_chunks"]
        
        # Determine which chunks to process
        if specific_chunk is not None:
            if specific_chunk < 1 or specific_chunk > total_chunks:
                raise ValueError(f"Chunk number must be between 1 and {total_chunks}")
            chunks_to_process = [specific_chunk]
            self.logger.log_info(f"Processing single chunk {specific_chunk}/{total_chunks}")
        else:
            chunks_to_process = [i for i in range(1, total_chunks + 1)
                               if inventory["chunks"][str(i)]["status"] == "pending"]
        
        self.logger.log_sequence("CHUNKING", "START", 
                               f"Processing {len(chunks_to_process)} chunks")
        
        input_file_handle = None
        try:
            # Open the input file once
            input_file_handle = open(input_file, 'rb')
            
            for chunk_num in chunks_to_process:
                chunk_start = datetime.now()
                chunk_id = self._generate_chunk_id(base_filename, chunk_num)
                output_path = os.path.join(output_dir, chunk_id)
                
                # Show progress
                progress = (chunk_num/total_chunks*100) if not specific_chunk else 100
                print(f"\rProcessing chunk {chunk_num}/{total_chunks} "
                      f"({progress:.1f}%) - {chunk_id}", end="", flush=True)
                
                # Calculate chunk boundaries
                start_pos, end_pos = self.calculate_chunk_boundaries(file_size, chunk_size, chunk_num)
                chunk_size_actual = end_pos - start_pos
                
                # Read chunk
                input_file_handle.seek(start_pos)
                chunk_data = input_file_handle.read(chunk_size_actual)
                
                # Write chunk
                os.makedirs(output_dir, exist_ok=True)
                with open(output_path, 'wb') as chunk_file:
                    chunk_file.write(chunk_data)
                
                # Calculate chunk hash
                chunk_hash = self.file_ops.calculate_chunk_hash(chunk_data)
                
                chunk_info = {
                    "size": chunk_size_actual,
                    "hash": chunk_hash,
                    "processing_time": (datetime.now() - chunk_start).total_seconds()
                }
                
                # Update inventory
                inventory = self._update_inventory(inventory, chunk_num, chunk_info)
                
                # Save inventory after each chunk
                with open(inventory_path, 'w') as f:
                    json.dump(inventory, f, indent=2)
                
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
        
        finally:
            # Ensure we always close the input file
            if input_file_handle:
                input_file_handle.close()
        
        print("\n")  # New line after progress
        
        # Print summary
        print(f"\nChunking Status:")
        print(f"Processed: {inventory['chunk_status']['total_processed']}/{total_chunks}")
        print(f"Remaining: {inventory['chunk_status']['chunks_remaining']}")
        
        return inventory