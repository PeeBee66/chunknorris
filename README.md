# ChunkNorris File Chunking Tool

ChunkNorris is a robust Python tool designed to efficiently split large files into manageable chunks and reconstruct them while maintaining data integrity through hash verification. It's particularly useful for handling large files that need to be transferred or processed in smaller segments.

## Features

- **Flexible Chunking**: Split files into chunks of customizable size
- **Progressive Processing**: Process specific chunks or resume partial operations
- **Data Integrity**: XXHash (default) or MD5 hash verification for both original file and chunks
- **Detailed Logging**: Comprehensive logging of all operations with timestamps
- **Inventory Management**: JSON-based inventory tracking with chunk metadata
- **Real-time Progress**: Operation status and progress monitoring
- **File Reconstruction**: Ability to rebuild original file from chunks with hash verification
- **Error Recovery**: Resume operations and retry failed chunks
- **Disk Space Validation**: Pre-checks for sufficient storage space

## Project Structure
```
./
├── chunknorris.py          # Main script and CLI interface
├── roundhouse/            
│   ├── black_belt_logs.py  # Logging functionality
│   ├── dojo_handlers.py    # File operations and validation
│   ├── karate_chunk.py     # Chunk processing logic
│   └── total_reunion.py    # File reconstruction logic
└── test/
    └── hash_test.py        # Hash performance benchmarking
```

## Installation

### Prerequisites
- Python 3.6 or higher
- Operating System: Windows, Linux, or macOS

### Optional Dependencies
- xxhash: Faster hashing alternative to MD5 (`pip install xxhash`)

### Basic Installation
```bash
git clone https://github.com/PeeBee66/chunknorris.git
cd chunknorris
```

## Usage

### Chunking Mode
Split a file into chunks:
```bash
python chunknorris.py -f <input_file> [-s chunk_size] [-o output_dir] [-l log_dir] [-i inventory_dir]
```

### Reconstruction Mode
Rebuild the original file from chunks:
```bash
python chunknorris.py -n <any_chunk_file> [-o output_dir] [--no-validate]
```

### Command Line Arguments
| Argument | Long Form | Description | Default |
|----------|-----------|-------------|---------|
| `-f` | `--file` | Input file to chunk | Required (chunking mode) |
| `-n` | `--norris` | Path to any chunk file for reconstruction | Required (reconstruction mode) |
| `-s` | `--size` | Chunk size in MB | 1000 |
| `-c` | `--chunk` | Specific chunk to process | None |
| `-o` | `--output` | Output directory | Input file directory |
| `-l` | `--log` | Log directory | Input file directory |
| `-i` | `--inventory` | Inventory directory | Input file directory |
| `--no-validate` | | Skip hash validation during reconstruction | False |

### Examples

1. Split a file into 1GB chunks:
```bash
python chunknorris.py -f large_file.dat
```

2. Split with custom chunk size and output location:
```bash
python chunknorris.py -f large_file.dat -s 500 -o /path/to/chunks
```

3. Process only a specific chunk:
```bash
python chunknorris.py -f large_file.dat -c 5
```

4. Reconstruct file from chunks:
```bash
python chunknorris.py -n /path/to/chunks/filename.chunk001.bin -o /output/dir
```

## Output Structure

### Chunks
- Format: `filename.chunkXXX.bin` (e.g., `myfile.chunk001.bin`)
- Sequential numbering with zero-padding
- Stored in specified output directory or alongside source file

### Inventory File
The inventory JSON file contains:
```json
{
    "original_filename": "example.dat",
    "original_size": 1234567890,
    "original_hash": "xxh64_hash_value",
    "hash_type": "xxhash64",
    "chunk_size": 1073741824,
    "total_chunks": 10,
    "inventory_type": "progressive",
    "creation_time": "2024-10-24T15:30:45.123456",
    "last_updated": "2024-10-24T15:35:12.345678",
    "chunk_status": {
        "total_processed": 10,
        "chunks_remaining": 0
    },
    "chunks": {
        "1": {
            "chunk_id": "example.chunk001.bin",
            "status": "completed",
            "size": 1073741824,
            "hash": "chunk_hash_value",
            "offset": 0,
            "processing_time": 1.23
        }
    }
}
```

### Log File
Log entries include:
```
2024-10-24 15:30:45.123 | Session Start: 20241024_153045
2024-10-24 15:30:45.234 | INFO: Sufficient disk space available (500.00GB free, 1.50GB required)
2024-10-24 15:30:45.345 | Chunk: example.chunk001.bin | Status: completed | Size: 1000.00MB | Duration: 1.23s | Hash: abcdef123456
```

## Error Handling

The tool includes comprehensive error handling for:
- Invalid input files or paths
- Insufficient disk space
- Missing or corrupted chunks
- Hash verification failures
- Invalid chunk numbers
- File access issues

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Future Enhancements

- [ ] Parallel processing for faster chunking
- [ ] Compression support
- [ ] Network transfer capabilities
- [ ] Encryption support

## License

This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html) - see the LICENSE file for details.

## Authors

- PeeBee (peebee_github@protonmail.com)

## Acknowledgments

- Inspired by the need for efficient large file handling
- Chuck Norris, for being awesome

---

# Appendix: Step-by-Step Guide

## Step 1: Run the Chunking Command

1. Navigate to the ChunkNorris folder:
```
PS C:\Users\YourUsername\Desktop\ChunkNorris>
```

2. Run the chunking command (replace paths as needed):
```bash
& YourPythonPath/python.exe chunknorris.py -f F:\Hauler\hauler_airgap_08_21_24.zst -l F:\Hauler\stagging -o F:\Hauler\stagging -i F:\Hauler\stagging
```

Example Output:
```
Creating directory if not exists: F:\Hauler\stagging
Sufficient disk space available (39.14GB free, 11.34GB required)
Processing chunk 12/12 (100.0%) - hauler_airgap_08_21_24.chunk012.bin

Processed: 12/12
Remaining: 0

Processing completed successfully!
Input file: F:\Hauler\hauler_airgap_08_21_24.zst
Output directory: F:\Hauler\stagging
Log file: F:\Hauler\stagging\hauler_airgap_08_21_24.log
Inventory file: F:\Hauler\stagging\hauler_airgap_08_21_24.json

Summary:
Total chunks: 12
Original file size: 12,180,089,987 bytes
Original file hash: 8e428c002fbfd7429a3698739c0cb81c
```

## Step 2: Run the File Reconstruction Command

Run the reconstruction command (I deleted chunk 3 and 8):
```bash
& YourPythonPath/python.exe chunknorris.py -n F:\Hauler\stagging\chunk006.bin -o F:\Hauler\stagging
```

Example Output:
```
Using inventory file: F:\Hauler\stagging\hauler_airgap_08_21_24.json
Validating chunk files...

Chunk Files Status:
Total chunks required: 12
Completed chunks: 12
Chunks found: 10
Chunks missing: 2

Missing chunks:
- hauler_airgap_08_21_24.chunk003.bin
- hauler_airgap_08_21_24.chunk008.bin

Error during reconstruction: Cannot proceed with reconstruction: 2 chunks missing or incomplete
```

## Step 3: Recover Missing Chunks

Regenerate missing chunks using the `-c` option:
```bash
& YourPythonPath/python.exe chunknorris.py -f F:\Hauler\hauler_airgap_08_21_24.zst -l F:\Hauler\stagging -o F:\Hauler\stagging -i F:\Hauler\stagging -c 3
& YourPythonPath/python.exe chunknorris.py -f F:\Hauler\hauler_airgap_08_21_24.zst -l F:\Hauler\stagging -o F:\Hauler\stagging -i F:\Hauler\stagging -c 8
```

Example Output:
```
Creating directory if not exists: F:\Hauler\stagging
Sufficient disk space available (18.59GB free, 11.34GB required)
Processing chunk 3/12 (100.0%) - hauler_airgap_08_21_24.chunk003.bin

Chunking Status:
Processed: 12/12
Remaining: 0

Processing completed successfully!
Input file: F:\Hauler\hauler_airgap_08_21_24.zst
Output directory: F:\Hauler\stagging
Log file: F:\Hauler\stagging\hauler_airgap_08_21_24.log
Inventory file: F:\Hauler\stagging\hauler_airgap_08_21_24.json

Summary:
Total chunks: 12
Original file size: 12,180,089,987 bytes
Original file hash: 8e428c002fbfd7429a3698739c0cb81c
```

## Step 4: Complete File Reconstruction

Run the reconstruction command again after recovering all chunks:
```bash
& YourPythonPath/python.exe chunknorris.py -n F:\Hauler\stagging\chunk006.bin -o F:\Hauler\stagging
```

Example Output:
```
Chunk Files Status:
Total chunks required: 12
Completed chunks: 12
Chunks found: 12
Chunks missing: 0

Reconstructing file: F:\Hauler\stagging\hauler_airgap_08_21_24.zst
Using inventory: F:\Hauler\stagging\hauler_airgap_08_21_24.json
Expected file size: 12,180,089,987 bytes
Total chunks: 12
Hash type: md5
Validation: enabled
Processing chunk 12/12 (100.0%) - hauler_airgap_08_21_24.chunk012.bin

Reconstruction complete!
Written to: F:\Hauler\stagging\hauler_airgap_08_21_24.zst
Final size: 12,180,089,987 bytes
Hash verification: PASSED
```

## Summary

### Key Commands:
- `chunknorris.py -f` for chunking
- `chunknorris.py -n` for reconstruction
- Use `-c` flag for regenerating specific chunks

### Validation:
- All chunks are validated for file integrity
- Final file hash is verified against original

### Output:
- Step-by-step logs confirm:
  - Directory creation
  - Chunk processing status
  - File reconstruction progress
  - Final hash verification

This workflow ensures reliable file handling, even when encountering issues or missing chunks during the process.
