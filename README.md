# ChunkNorris File Chunking Tool

ChunkNorris is a robust Python tool designed to efficiently split large files into manageable chunks while maintaining data integrity through hash verification. It's particularly useful for handling large files that need to be transferred or processed in smaller segments.

## Features

- **Flexible Chunking**: Split files into chunks of customizable size
- **Smart Chunk Selection**: Process specific chunks without re-processing the entire file
- **Data Integrity**: SHA-256 hash verification for both original file and chunks
- **Detailed Logging**: Comprehensive logging of all operations
- **Inventory Management**: JSON-based inventory of all chunks with metadata
- **Progress Tracking**: Real-time operation status and progress monitoring
- **Error Recovery**: Ability to resume operations and retry failed chunks

## Installation

### Prerequisites
- Python 3.6 or higher
- Operating System: Windows, Linux, or macOS

### Basic Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/chunknorris.git
cd chunknorris
```

2. [Optional] Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Linux/macOS
venv\Scripts\activate     # On Windows
```

## Project Structure
```
chunknorris/
├── chunknorris.py     # Main script
├── file_handlers.py   # File operations and validation
├── logger.py          # Logging functionality
└── chunk_manager.py   # Chunk processing logic
```

## Usage

### Basic Usage
```bash
python chunknorris.py -f <input_file> [-s chunk_size] [-o output_dir] [-l log_file] [-i inventory_file]
```

### Command Line Arguments
| Argument | Long Form | Description | Default |
|----------|-----------|-------------|---------|
| `-f` | `--file` | Input file to chunk | Required |
| `-s` | `--size` | Chunk size in MB | 1000 |
| `-c` | `--chunk` | Specific chunk to process | None |
| `-o` | `--output` | Output directory for chunks | `<filename>_chunks` |
| `-l` | `--log` | Log file location | `<output_dir>/process.log` |
| `-i` | `--inventory` | Inventory JSON file location | `<output_dir>/inventory.json` |

### Examples

1. Split a file into 1GB chunks (default):
```bash
python chunknorris.py -f large_file.dat
```

2. Split a file into 500MB chunks:
```bash
python chunknorris.py -f large_file.dat -s 500
```

3. Process only chunk #5:
```bash
python chunknorris.py -f large_file.dat -c 5
```

4. Specify custom output locations:
```bash
python chunknorris.py -f large_file.dat -o /path/to/chunks -l /path/to/logs/process.log -i /path/to/inventory.json
```

## Output Structure

### Chunks
- Chunks are named sequentially: `chunk001`, `chunk002`, etc.
- Each chunk is stored in the output directory
- Default chunk size is 1000MB (1GB)

### Inventory File
The inventory JSON file contains:
```json
{
    "original_filename": "example.dat",
    "original_size": 1234567890,
    "original_hash": "sha256_hash_value",
    "chunk_size": 1073741824,
    "total_chunks": 10,
    "chunks": [
        {
            "chunk_id": "chunk001",
            "offset": 0,
            "size": 1073741824,
            "hash": "chunk_sha256_hash"
        }
    ]
}
```

### Log File
Log entries include:
- Operation timestamps
- Chunk processing details
- Hash values
- Error messages
- Performance metrics

Example log entry:
```
2024-10-24 15:30:45.123 | CHUNK chunk001 | Status: completed | Size: 1000.00MB | Duration: 1.23s
```

## Error Handling

The script includes comprehensive error handling for:
- Invalid input files
- Insufficient disk space
- Invalid chunk numbers
- File access issues
- Hash verification failures

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Future Enhancements

- [ ] File reconstruction functionality
- [ ] Parallel processing for faster chunking
- [ ] Compression support
- [ ] Network transfer capabilities
- [ ] GUI interface
- [ ] Progress bars

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- Your Name (@yourusername)

## Acknowledgments

- Inspired by the need for efficient large file handling
- Chuck Norris, for being awesome