import os
import requests

STREAM_URL = " https://aliyun-flv-ipv6.yy.com/live/15013_xv_54880976_54880976_0_2_0-15013_xa_54880976_54880976_0_0_0-0-0-0-0-0-1761271203486347.flv?codec=orig&appid=15013&secret=ee998cf619a1b10c78e68d64ce8ac150&t=1761275384&stream_key=15013_xv_54880976_54880976_0_2_0&mtk=1&line_seq=2&cp_id=2&r=cli_switch&playeruid=2390116452&uuid=6027049d-6cc9-4ec7-8e71-a449ef62ce13  "
LOCAL_FILE = "e:/4.ts"
STREAM_URL=STREAM_URL.strip()

def download_stream(url, file_path, chunk_size=65536, timeout=30):
    """
    Download a streaming URL and save to file_path, keeping partial content if stream stops.
    Creates directories if needed and prints '.' for each chunk.

    Args:
        url (str): URL of the stream to download
        file_path (str): Local path where the stream should be saved
        chunk_size (int): Size of each chunk in bytes (default: 64KB = 65536 bytes)
        timeout (float): Timeout in seconds for initial connection

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
    with open(file_path, 'wb') as file:
        try:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:  # Filter out keep-alive chunks
                    file.write(chunk)
                    print(".", end="", flush=True)
            print("\ndownload completed")
        except Exception as e:
            # Stream ended or connection dropped, keep what was downloaded
            print(f"\nStream stopped, saving data downloaded so far")
            print(f"\nError: {e}")
        except KeyboardInterrupt:
            print("keyboarrd interrupt detected, saving data downloaded so far")
            pass

download_stream(STREAM_URL, LOCAL_FILE)
