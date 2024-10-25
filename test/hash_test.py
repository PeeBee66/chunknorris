import hashlib
import xxhash
import time

def hash_file(file_path, hasher, block_size=65536):
    """Hash a large file in chunks using the provided hasher."""
    with open(file_path, 'rb') as f:
        while chunk := f.read(block_size):
            hasher.update(chunk)

    return hasher.hexdigest()

def benchmark(file_path, algorithm='sha256', is_native=True):
    """Benchmark the time taken to hash a file."""
    print(f"\nBenchmarking {algorithm.upper()}...")
    start_time = time.time()

    if is_native:
        hasher = hashlib.new(algorithm)
    else:
        hasher = xxhash.xxh64() if algorithm == 'xxh64' else xxhash.xxh3_128()

    hash_value = hash_file(file_path, hasher)

    elapsed_time = time.time() - start_time
    print(f"{algorithm.upper()} Hash: {hash_value}")
    print(f"Time Taken: {elapsed_time:.2f} seconds")

# Path to your file
file_path = r'F:\Hauler\hauler_airgap_08_21_24.zst'

# Benchmark native algorithms
for algo in ['md5', 'sha1', 'sha256', 'sha3_256', 'blake2b']:
    benchmark(file_path, algo)

# Benchmark XXHash algorithms
for algo in ['xxh64', 'xxh3_128']:
    benchmark(file_path, algo, is_native=False)
