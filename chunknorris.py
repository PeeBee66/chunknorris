# File: chunknorris.py

import argparse
import os
import json
import sys
import shutil
from roundhouse.dojo_handlers import FileValidator, FileOperations
from roundhouse.black_belt_logs import LogHandler
from roundhouse.karate_chunk import ChunkManager
from roundhouse.total_reunion import FileReconstructor

def get_base_filename(file_path: str) -> str:
    """Get the base filename without directory path."""
    return os.path.basename(file_path)

def check_disk_space(file_size: int, output_dir: str) -> tuple[bool, str]:
    """Check if there's enough disk space for chunks."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        free_space = shutil.disk_usage(output_dir).free
        free_space_gb = free_space / (1024**3)
        required_space = file_size
        required_space_gb = required_space / (1024**3)
        
        if free_space > required_space:
            return True, f"Sufficient disk space available ({free_space_gb:.2f}GB free, {required_space_gb:.2f}GB required)"
        else:
            return False, f"Insufficient disk space: {free_space_gb:.2f}GB free, {required_space_gb:.2f}GB required"
    except Exception as e:
        return False, f"Error checking disk space: {str(e)}"

def setup_paths(input_file: str, output_dir: str = None, log_dir: str = None, 
                inventory_dir: str = None, specific_chunk: int = None) -> dict:
    """Setup all paths for files and directories."""
    base_filename = get_base_filename(input_file)
    input_dir = os.path.dirname(os.path.abspath(input_file))
    name_without_ext = os.path.splitext(base_filename)[0]
    
    # Set default paths
    default_output_dir = input_dir
    default_log_path = os.path.join(input_dir, f"{name_without_ext}.log")
    default_inventory_path = os.path.join(input_dir, f"{name_without_ext}.json")
    
    # Set final paths
    final_output_dir = output_dir if output_dir else default_output_dir
    final_log_path = os.path.join(log_dir, f"{name_without_ext}.log") if log_dir else default_log_path
    final_inventory_path = os.path.join(inventory_dir, f"{name_without_ext}.json") if inventory_dir else default_inventory_path
    
    return {
        'output_dir': final_output_dir,
        'log_path': final_log_path,
        'inventory_path': final_inventory_path
    }

def main():
    parser = argparse.ArgumentParser(description='ChunkNorris File Chunking Tool')
    
    # Create a mutually exclusive group for -f and -n
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', help='Input file to chunk')
    group.add_argument('-n', '--norris', help='Reconstruction mode: path to any chunk file (chunk*.bin)')
    
    # Optional arguments
    parser.add_argument('-s', '--size', type=int, default=1000, help='Chunk size in MB (default: 1000)')
    parser.add_argument('-c', '--chunk', type=int, help='Specific chunk number to process')
    parser.add_argument('-o', '--output', help='Output directory for reconstructed file or chunks', metavar='DIR')
    parser.add_argument('-l', '--log', help='Directory for log file (default: input file directory)')
    parser.add_argument('-i', '--inventory', help='Directory for inventory file (default: input file directory)')
    parser.add_argument('--no-validate', action='store_true', help='Skip hash validation during reconstruction')
    
    args = parser.parse_args()
    
    try:
        # Reconstruction mode
        if args.norris:
            print("Starting file reconstruction...")
            input_path = os.path.abspath(args.norris)
            search_dir = os.path.dirname(input_path)
            
            # Find the inventory file
            inventory_files = [f for f in os.listdir(search_dir) if f.endswith('.json')]
            
            if not inventory_files:
                raise FileNotFoundError(f"No inventory file found in directory: {search_dir}")
            
            # If multiple inventory files, use the most recent
            if len(inventory_files) > 1:
                print("\nFound multiple inventory files:")
                for idx, inv_file in enumerate(inventory_files, 1):
                    print(f"{idx}. {inv_file}")
                print("\nUsing most recent inventory file...")
                inventory_files.sort(key=lambda x: os.path.getmtime(os.path.join(search_dir, x)), reverse=True)
            
            inventory_path = os.path.join(search_dir, inventory_files[0])
            print(f"Using inventory file: {inventory_path}")
            
            # Validate output directory
            if args.output:
                try:
                    os.makedirs(args.output, exist_ok=True)
                except Exception as e:
                    raise ValueError(f"Cannot create output directory: {str(e)}")
                
                if not os.access(args.output, os.W_OK):
                    raise ValueError(f"Output directory is not writable: {args.output}")
            
            # Start reconstruction
            reconstructor = FileReconstructor(
                inventory_path=inventory_path,
                output_dir=args.output,
                validate=not args.no_validate
            )
            success = reconstructor.reconstruct()
            sys.exit(0 if success else 1)
        
        # Chunking mode
        if args.file:
            # Validate input file
            validator = FileValidator()
            success, message = validator.validate_input_file(args.file)
            if not success:
                raise ValueError(message)
            
            # Setup paths
            paths = setup_paths(args.file, args.output, args.log, args.inventory)
            
            # Create directories
            for dir_path in [
                paths['output_dir'],
                os.path.dirname(paths['log_path']),
                os.path.dirname(paths['inventory_path'])
            ]:
                print(f"Creating directory if not exists: {dir_path}")
                os.makedirs(dir_path, exist_ok=True)
            
            # Check disk space
            file_size = os.path.getsize(args.file)
            space_ok, space_message = check_disk_space(file_size, paths['output_dir'])
            print(space_message)
            if not space_ok:
                raise ValueError(space_message)
            
            # Initialize logger and start chunking
            logger = LogHandler(paths['log_path'], args.file)
            logger.log_info(space_message)
            
            try:
                chunk_manager = ChunkManager(logger)
                inventory = chunk_manager.chunk_file(
                    input_file=args.file,
                    output_dir=paths['output_dir'],
                    inventory_path=paths['inventory_path'],
                    chunk_size_mb=args.size,
                    specific_chunk=args.chunk
                )
                
                # Write inventory file
                with open(paths['inventory_path'], 'w') as f:
                    json.dump(inventory, f, indent=2)
                
                print(f"\nProcessing completed successfully!")
                print(f"Input file: {args.file}")
                print(f"Output directory: {paths['output_dir']}")
                print(f"Log file: {paths['log_path']}")
                print(f"Inventory file: {paths['inventory_path']}")
                print(f"\nSummary:")
                print(f"Total chunks: {inventory['total_chunks']}")
                print(f"Original file size: {inventory['original_size']:,} bytes")
                print(f"Original file hash: {inventory['original_hash']}")
                
            finally:
                logger.close()
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()