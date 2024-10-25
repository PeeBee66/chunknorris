# File: total_reunion.py

import os
import json
import sys
from datetime import datetime
from typing import Optional, List, Tuple, Dict
from roundhouse.dojo_handlers import create_hasher, hash_data

class FileReconstructor:
    """Handles file reconstruction from chunks."""

    def __init__(self, inventory_path: str, output_dir: Optional[str] = None, validate: bool = True):
        """Initialize the FileReconstructor.
        
        Args:
            inventory_path (str): Path to the inventory JSON file
            output_dir (Optional[str], optional): Directory for reconstructed file. Defaults to None.
            validate (bool, optional): Whether to validate chunks during reconstruction. Defaults to True.
            
        Raises:
            ValueError: If output directory is invalid or inventory can't be loaded
        """
        self.inventory_path = inventory_path
        self.validate = validate
        self.inventory = self._load_inventory()
        self.chunks_dir = os.path.dirname(inventory_path)
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            if not os.path.isdir(output_dir):
                raise ValueError(f"Output path must be a directory: {output_dir}")
            self.output_file = os.path.join(output_dir, self.inventory['original_filename'])
        else:
            self.output_file = os.path.join(os.getcwd(), self.inventory['original_filename'])

    def _load_inventory(self) -> Dict:
        """Load and validate inventory file.
        
        Returns:
            Dict: Loaded inventory data
            
        Raises:
            ValueError: If inventory file can't be loaded or is invalid
        """
        try:
            with open(self.inventory_path, 'r') as f:
                inventory = json.load(f)
                
            # Validate required fields
            required_fields = ['original_filename', 'original_size', 'original_hash', 
                             'hash_type', 'chunks']
            missing_fields = [field for field in required_fields if field not in inventory]
            
            if missing_fields:
                raise ValueError(f"Missing required fields in inventory: {', '.join(missing_fields)}")
                
            return inventory
        except Exception as e:
            raise ValueError(f"Failed to load inventory: {str(e)}")

    def _validate_chunks_presence(self) -> Tuple[bool, List[str], List[str]]:
        """Validate that all required chunk files are present.
        
        Returns:
            Tuple[bool, List[str], List[str]]: (is_valid, missing_chunks, found_chunks)
        """
        required_chunks = {}
        for chunk_num, chunk_info in self.inventory['chunks'].items():
            # Skip chunks that aren't marked as completed
            if chunk_info['status'] != 'completed':
                continue
            required_chunks[chunk_info['chunk_id']] = chunk_info
            
        missing_chunks = []
        found_chunks = []
        
        # Check each required chunk
        for chunk_id, chunk_info in required_chunks.items():
            chunk_path = os.path.join(self.chunks_dir, chunk_id)
            if os.path.exists(chunk_path):
                # Verify file size if available
                if 'size' in chunk_info:
                    actual_size = os.path.getsize(chunk_path)
                    if actual_size != chunk_info['size']:
                        missing_chunks.append(f"{chunk_id} (size mismatch: expected {chunk_info['size']}, got {actual_size})")
                        continue
                found_chunks.append(chunk_id)
            else:
                missing_chunks.append(chunk_id)
        
        return len(missing_chunks) == 0, missing_chunks, found_chunks

    def _print_chunk_status(self, missing_chunks: List[str], found_chunks: List[str]):
        """Print detailed chunk status information."""
        total_expected = sum(1 for chunk in self.inventory['chunks'].values() 
                           if chunk['status'] == 'completed')
        
        print("\nChunk Files Status:")
        print(f"Total chunks required: {self.inventory['total_chunks']}")
        print(f"Completed chunks: {total_expected}")
        print(f"Chunks found: {len(found_chunks)}")
        print(f"Chunks missing: {len(missing_chunks)}")
        
        if missing_chunks:
            print("\nMissing chunks:")
            for chunk in sorted(missing_chunks):
                print(f"  - {chunk}")
        
        print("\nFound chunks:")
        for chunk in sorted(found_chunks):
            print(f"  - {chunk}")

    def _validate_chunk(self, chunk_data: bytes, chunk_info: Dict):
        """Validate chunk data against stored hash.
        
        Args:
            chunk_data (bytes): The chunk data to validate
            chunk_info (Dict): Chunk information from inventory
            
        Raises:
            ValueError: If chunk hash doesn't match expected hash
        """
        if not self.validate:
            return
        
        if 'hash' not in chunk_info:
            print(f"Warning: No hash found for chunk {chunk_info['chunk_id']}, skipping validation")
            return
            
        chunk_hash = hash_data(chunk_data)
        if chunk_hash != chunk_info['hash']:
            raise ValueError(
                f"Chunk hash mismatch for {chunk_info['chunk_id']}:\n"
                f"Expected: {chunk_info['hash']}\n"
                f"Got: {chunk_hash}"
            )

    def reconstruct(self) -> bool:
        """Reconstruct file from chunks.
        
        Returns:
            bool: True if reconstruction successful, False otherwise
        """
        try:
            # Initial setup and validation
            print(f"\nValidating chunk files...")
            chunks_valid, missing_chunks, found_chunks = self._validate_chunks_presence()
            self._print_chunk_status(missing_chunks, found_chunks)
            
            if not chunks_valid:
                raise ValueError(
                    f"Cannot proceed with reconstruction: {len(missing_chunks)} "
                    "chunks missing or incomplete"
                )
            
            # Setup for reconstruction
            hash_type = self.inventory.get('hash_type', 'md5')
            hasher = create_hasher() if self.validate else None
            reconstructed_size = 0
            
            # Print reconstruction info
            print(f"\nReconstructing file: {self.output_file}")
            print(f"Using inventory: {self.inventory_path}")
            print(f"Expected file size: {self.inventory['original_size']:,} bytes")
            print(f"Total chunks: {self.inventory['total_chunks']}")
            print(f"Hash type: {hash_type}")
            print(f"Validation: {'enabled' if self.validate else 'disabled'}")
            
            # Check if output file already exists
            if os.path.exists(self.output_file):
                raise ValueError(f"Output file already exists: {self.output_file}")
            
            # Sort chunks by number for ordered reconstruction
            sorted_chunks = sorted(
                [(int(k), v) for k, v in self.inventory['chunks'].items()
                 if v['status'] == 'completed'],
                key=lambda x: x[0]
            )
            
            # Create directory for output file if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(self.output_file)), exist_ok=True)
            
            # Reconstruct file
            with open(self.output_file, 'wb') as outfile:
                for chunk_num, chunk_info in sorted_chunks:
                    current_percentage = (chunk_num / self.inventory['total_chunks']) * 100
                    print(f"\rProcessing chunk {chunk_num}/{self.inventory['total_chunks']} "
                          f"({current_percentage:.1f}%) - {chunk_info['chunk_id']}", 
                          end="", flush=True)
                    
                    chunk_path = os.path.join(self.chunks_dir, chunk_info['chunk_id'])
                    
                    # Read and validate chunk
                    with open(chunk_path, 'rb') as chunk_file:
                        chunk_data = chunk_file.read()
                        self._validate_chunk(chunk_data, chunk_info)
                        
                        # Write chunk to output file
                        outfile.write(chunk_data)
                        reconstructed_size += len(chunk_data)
                        
                        # Update file hash if validating
                        if self.validate:
                            hasher.update(chunk_data)
            
            print("\n\nReconstruction complete!")
            print(f"Written to: {self.output_file}")
            print(f"Final size: {reconstructed_size:,} bytes")
            
            # Validate final size
            if reconstructed_size != self.inventory['original_size']:
                raise ValueError(
                    f"File size mismatch:\n"
                    f"Expected: {self.inventory['original_size']:,} bytes\n"
                    f"Got:      {reconstructed_size:,} bytes"
                )
            
            # Validate final hash
            if self.validate:
                final_hash = hasher.hexdigest()
                if final_hash != self.inventory['original_hash']:
                    raise ValueError(
                        f"File hash mismatch:\n"
                        f"Expected: {self.inventory['original_hash']}\n"
                        f"Got:      {final_hash}"
                    )
                print(f"Hash verification: PASSED")
            
            return True
            
        except Exception as e:
            print(f"\nError during reconstruction: {str(e)}", file=sys.stderr)
            if os.path.exists(self.output_file):
                os.remove(self.output_file)
                print(f"Removed incomplete file: {self.output_file}")
            return False

class ReconstructionManager:
    """Manages the overall reconstruction process including inventory verification."""
    
    def __init__(self, inventory_path: str):
        """Initialize ReconstructionManager.
        
        Args:
            inventory_path (str): Path to the inventory file
        """
        self.inventory_path = inventory_path
        
    def verify_reconstruction_readiness(self) -> Tuple[bool, List[str]]:
        """Verify if all necessary components are ready for reconstruction.
        
        Returns:
            Tuple[bool, List[str]]: (is_ready, list_of_issues)
        """
        issues = []
        
        # Check inventory file
        if not os.path.exists(self.inventory_path):
            issues.append(f"Inventory file not found: {self.inventory_path}")
            return False, issues
            
        try:
            with open(self.inventory_path, 'r') as f:
                inventory = json.load(f)
        except Exception as e:
            issues.append(f"Failed to load inventory: {str(e)}")
            return False, issues
            
        # Check required fields
        required_fields = ['original_filename', 'original_size', 'original_hash', 
                          'chunks', 'total_chunks']
        for field in required_fields:
            if field not in inventory:
                issues.append(f"Missing required field in inventory: {field}")
        
        # Check chunks
        chunks_dir = os.path.dirname(self.inventory_path)
        incomplete_chunks = []
        missing_chunks = []
        
        for chunk_num, chunk_info in inventory.get('chunks', {}).items():
            if chunk_info['status'] != 'completed':
                incomplete_chunks.append(chunk_info['chunk_id'])
            else:
                chunk_path = os.path.join(chunks_dir, chunk_info['chunk_id'])
                if not os.path.exists(chunk_path):
                    missing_chunks.append(chunk_info['chunk_id'])
        
        if incomplete_chunks:
            issues.append(f"Found {len(incomplete_chunks)} incomplete chunks")
        if missing_chunks:
            issues.append(f"Found {len(missing_chunks)} missing chunk files")
            
        return len(issues) == 0, issues
    
    def print_reconstruction_status(self):
        """Print current status of reconstruction readiness."""
        print("\nChecking reconstruction readiness...")
        ready, issues = self.verify_reconstruction_readiness()
        
        if ready:
            print("✓ All checks passed - ready for reconstruction")
        else:
            print("✗ Issues found preventing reconstruction:")
            for issue in issues:
                print(f"  - {issue}")