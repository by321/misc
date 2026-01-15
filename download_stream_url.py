import os
import requests

STREAM_URL = " https://example.com/abc  "
LOCAL_FILE = "e:/6.ts"
STREAM_URL=STREAM_URL.strip()

def download_stream(url, file_path, chunk_size=1024*1024, timeout=15, max_size_mb=0):
    """
    Download a streaming URL and save to file_path, keeping partial content if stream stops.
    Creates directories if needed and prints '.' for each chunk.

    Args:
        url (str): URL of the stream to download
        file_path (str): Local path where the stream should be saved
        chunk_size (int): Size of each chunk in bytes (default: 1 MB = 1024*1024 bytes)
        timeout (float): Timeout in seconds for initial connection
        max_size_mb (int): Maximum size to download in megabytes (0 for no limit)
    Exits program on critical errors with exception message.
    """

    if os.path.exists(file_path):
        print(f"skipping download, file already exists: {file_path}")
        return

    os.makedirs(os.path.dirname(file_path), exist_ok=True)


	# Send HTTP GET request with streaming enabled
    response = requests.get(url, stream=True, timeout=timeout)

	# Raise an error for bad status codes
    response.raise_for_status()

	# Download stream and write chunks to file
    print(f"downloading {os.path.basename(file_path)}: ", end="", flush=True)
    saved_bytes=0; max_bytes=max_size_mb*1024*1024
    with open(file_path, 'wb') as file:
        try:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:  # Filter out keep-alive chunks
                    file.write(chunk)
                    print(".", end="", flush=True)
                    saved_bytes += len(chunk)
                    if max_bytes>0 and saved_bytes>=max_bytes:
                        print(f"\nreached max size of {max_size_mb} MB, stopping download")
                        break
            print("\ndownload completed")
        except Exception as e:
            # Stream ended or connection dropped, keep what was downloaded
            print(f"\nStream stopped, saving data downloaded so far")
            print(f"\nError: {e}")
        except KeyboardInterrupt:
            print("keyboarrd interrupt detected, saving data downloaded so far")
            pass

download_stream(STREAM_URL.strip(), LOCAL_FILE,max_size_mb=256)
