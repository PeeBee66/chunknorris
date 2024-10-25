# File: dojo_handlers.py

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple

# Try to import xxhash, fall back to MD5 if not available
try:
    import xxhash
    HASH_TYPE = "xxhash64"
    def create_hasher():
        return xxhash.xxh64()
    def hash_data(data: bytes) -> str:
        return xxhash.xxh64(data).hexdigest()
except ImportError:
    HASH_TYPE = "md5"
    def create_hasher():
        return hashlib.md5()
    def hash_data(data: bytes) -> str:
        return hashlib.md5(data).hexdigest()

class FileValidator:
    """Handles all file validation and path operations."""
    
    @staticmethod
    def validate_input_file(file_path: str) -> Tuple[bool, str]:
        """Validate input file exists and is accessible.
        
        Args:
            file_path (str): Path to the file to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        if not os.path.exists(file_path):
            return False, f"Input file not found: {file_path}"
        if not os.path.isfile(file_path):
            return False, f"Path is not a file: {file_path}"
        if not os.access(file_path, os.R_OK):
            return False, f"Input file is not readable: {file_path}"
        return True, "File validation successful"

    @staticmethod
    def validate_output_path(output_path: str) -> Tuple[bool, str]:
        """Validate output path is writable.
        
        Args:
            output_path (str): Path to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        try:
            os.makedirs(output_path, exist_ok=True)
            if not os.access(output_path, os.W_OK):
                return False, f"Output path is not writable: {output_path}"
            return True, "Output path validation successful"
        except Exception as e:
            return False, f"Failed to validate output path: {str(e)}"

class FileOperations:
    """Handles file operations including hashing."""
    
    @staticmethod
    def calculate_hash(file_path: str, buffer_size: int = 16777216) -> Tuple[str, int]:
        """Calculate file hash and return file size.
        
        Args:
            file_path (str): Path to the file
            buffer_size (int): Read buffer size (default 16MB for optimal performance)
            
        Returns:
            Tuple[str, int]: (hash_hex_string, file_size)
            
        Raises:
            Exception: If hash calculation fails
        """
        hasher = create_hasher()
        file_size = 0
        
        try:
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(buffer_size)
                    if not data:
                        break
                    hasher.update(data)
                    file_size += len(data)
            return hasher.hexdigest(), file_size
        except Exception as e:
            raise Exception(f"Error calculating file hash: {str(e)}")

    @staticmethod
    def calculate_chunk_hash(data: bytes) -> str:
        """Calculate hash of chunk data.
        
        Args:
            data (bytes): Chunk data
            
        Returns:
            str: Hash hex string
        """
        return hash_data(data)

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            int: File size in bytes
        """
        return os.path.getsize(file_path)

    @staticmethod
    def get_hash_type() -> str:
        """Get the type of hash being used.
        
        Returns:
            str: Hash type identifier
        """
        return HASH_TYPE

class InventoryManager:
    """Utilities for managing chunk inventory."""
    
    @staticmethod
    def get_inventory_summary(inventory_path: str) -> Dict:
        """Get a summary of the inventory status.
        
        Args:
            inventory_path (str): Path to inventory file
            
        Returns:
            Dict: Summary of inventory status
        """
        with open(inventory_path, 'r') as f:
            inventory = json.load(f)
        
        completed_chunks = []
        pending_chunks = []
        for chunk_num, chunk_info in inventory['chunks'].items():
            if chunk_info['status'] == 'completed':
                completed_chunks.append(chunk_num)
            else:
                pending_chunks.append(chunk_num)
        
        return {
            'filename': inventory['original_filename'],
            'total_chunks': inventory['total_chunks'],
            'completed': len(completed_chunks),
            'pending': len(pending_chunks),
            'completed_chunks': sorted(completed_chunks, key=int),
            'pending_chunks': sorted(pending_chunks, key=int),
            'creation_time': inventory['creation_time'],
            'last_updated': inventory['last_updated']
        }
    
    @staticmethod
    def print_inventory_status(inventory_path: str):
        """Print a human-readable inventory status.
        
        Args:
            inventory_path (str): Path to inventory file
        """
        summary = InventoryManager.get_inventory_summary(inventory_path)
        
        print("\nInventory Status")
        print("================")
        print(f"File: {summary['filename']}")
        print(f"Total Chunks: {summary['total_chunks']}")
        print(f"Completed: {summary['completed']}")
        print(f"Pending: {summary['pending']}")
        print(f"\nCreated: {summary['creation_time']}")
        print(f"Last Updated: {summary['last_updated']}")
        
        if summary['completed'] > 0:
            print("\nCompleted Chunks:")
            for chunk in summary['completed_chunks']:
                print(f"  - Chunk {chunk}")
        
        if summary['pending'] > 0:
            print("\nPending Chunks:")
            for chunk in summary['pending_chunks']:
                print(f"  - Chunk {chunk}")
    
    @staticmethod
    def verify_inventory_integrity(inventory_path: str) -> Tuple[bool, List[str]]:
        """Verify the integrity of the inventory file.
        
        Args:
            inventory_path (str): Path to inventory file
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_issues)
        """
        try:
            with open(inventory_path, 'r') as f:
                inventory = json.load(f)
            
            issues = []
            
            # Check required fields
            required_fields = ['original_filename', 'original_size', 'original_hash',
                             'total_chunks', 'chunks', 'chunk_status']
            
            for field in required_fields:
                if field not in inventory:
                    issues.append(f"Missing required field: {field}")
            
            # Verify chunk numbers are sequential
            chunk_numbers = sorted([int(k) for k in inventory['chunks'].keys()])
            expected_numbers = list(range(1, inventory['total_chunks'] + 1))
            
            if chunk_numbers != expected_numbers:
                issues.append("Chunk numbers are not sequential")
            
            # Verify chunk status counts
            completed = sum(1 for c in inventory['chunks'].values() 
                          if c['status'] == 'completed')
            if completed != inventory['chunk_status']['total_processed']:
                issues.append("Chunk status counter mismatch")
            
            # Verify each chunk entry
            for chunk_num, chunk_info in inventory['chunks'].items():
                if chunk_info['status'] == 'completed':
                    required_chunk_fields = ['chunk_id', 'size', 'hash', 'offset']
                    missing_fields = [field for field in required_chunk_fields 
                                    if field not in chunk_info]
                    if missing_fields:
                        issues.append(f"Chunk {chunk_num} missing fields: {missing_fields}")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"Failed to verify inventory: {str(e)}"]

    @staticmethod
    def create_inventory_backup(inventory_path: str) -> str:
        """Create a backup of the inventory file.
        
        Args:
            inventory_path (str): Path to inventory file
            
        Returns:
            str: Path to backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{inventory_path}.{timestamp}.backup"
        try:
            with open(inventory_path, 'r') as source:
                with open(backup_path, 'w') as target:
                    target.write(source.read())
            return backup_path
        except Exception as e:
            raise Exception(f"Failed to create inventory backup: {str(e)}")

    @staticmethod
    def merge_inventory_files(inventory_paths: List[str], output_path: str) -> bool:
        """Merge multiple inventory files into one.
        
        Args:
            inventory_paths (List[str]): List of inventory file paths
            output_path (str): Path for merged inventory
            
        Returns:
            bool: True if merge successful
        """
        try:
            base_inventory = None
            chunks_info = {}
            
            # Load and validate all inventories
            for inv_path in inventory_paths:
                with open(inv_path, 'r') as f:
                    inventory = json.load(f)
                
                if base_inventory is None:
                    base_inventory = inventory.copy()
                    base_inventory['chunks'] = {}
                else:
                    # Verify inventories are compatible
                    if (inventory['original_hash'] != base_inventory['original_hash'] or
                        inventory['original_size'] != base_inventory['original_size']):
                        raise ValueError(f"Incompatible inventory found: {inv_path}")
                
                # Merge chunk information
                for chunk_num, chunk_info in inventory['chunks'].items():
                    if chunk_info['status'] == 'completed':
                        chunks_info[chunk_num] = chunk_info
            
            if not base_inventory:
                raise ValueError("No valid inventory files found")
            
            # Update merged inventory
            base_inventory['chunks'] = chunks_info
            base_inventory['chunk_status'] = {
                'total_processed': len(chunks_info),
                'chunks_remaining': base_inventory['total_chunks'] - len(chunks_info)
            }
            base_inventory['last_updated'] = datetime.now().isoformat()
            base_inventory['merged_from'] = inventory_paths
            
            # Write merged inventory
            with open(output_path, 'w') as f:
                json.dump(base_inventory, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error merging inventories: {str(e)}")
            return False