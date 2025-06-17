import os, argparse
from PIL import Image
import exiftool

def get_exif_datetime(file_path, is_image):
    if is_image:
        try:
            with Image.open(file_path) as img:
                exif_data = img._getexif()
                if exif_data and 36867 in exif_data:  # 36867 is EXIF tag for DateTimeOriginal
                    date_str = exif_data[36867]  # format: YYYY:MM:DD HH:MM:SS
                    return date_str.replace(":", "").replace(" ", "_")
        except Exception as e:
            print(f"error extracting EXIF data from file: {file_path}\n{e}")
        return None
    else:
        try:
            with exiftool.ExifToolHelper() as et:
                metadata = et.get_metadata([file_path])[0]
                date_tags = [ 'QuickTime:CreateDate', 'QuickTime:MediaCreateDate',
                    'EXIF:DateTimeOriginal', 'EXIF:CreateDate' ]
                for tag in date_tags:
                    if tag in metadata:
                        date_str = metadata[tag]  # Format: YYYY:MM:DD HH:MM:SS
                        return date_str.replace(":", "").replace(" ", "_")
        except Exception as e:
            print(f"Error extracting EXIF data for {file_path}:\n{e}")
            print("Please ensure exiftool is installed and in your system PATH.")
            print("Download from https://exiftool.org/ and add to PATH.")
            quit()
        return None

def generate_new_filename(directory, datetime_str, original_ext, existing_files):
    base_name = datetime_str
    new_name = f"{base_name}{original_ext}"
    counter = 1
    while new_name in existing_files or os.path.exists(os.path.join(directory, new_name)):
        new_name = f"{base_name}_{counter}{original_ext}"
        counter += 1
    return new_name

def rename_files(directory):
    for root, _, files in os.walk(directory):
        # Track existing files in the current directory to avoid name collisions
        existing_files = set(os.listdir(root))

        for filename in files:
            file_path = os.path.join(root, filename)
            if not os.path.isfile(file_path):
                continue

            is_image = filename.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp'))
            is_video = filename.lower().endswith(('.mp4', '.mov'))
            if not (is_image or is_video):
                continue

            datetime_str = get_exif_datetime(file_path, is_image)
            if not datetime_str:
                print(f'no EXIF date/time found in file: "{file_path}", skipping')
                continue

            original_ext = os.path.splitext(filename)[1].lower()
            new_filename = generate_new_filename(root, datetime_str, original_ext, existing_files)
            if filename == new_filename:
                print(f"filename {filename} already matches metadata date/time, skipping")
                continue

            print(f"{file_path} -> {os.path.join(root, new_filename)}")
            try:
                old_path = os.path.join(root, filename)
                new_path = os.path.join(root, new_filename)
                os.rename(old_path, new_path)
                existing_files.remove(filename)
                existing_files.add(new_filename)
            except Exception as e:
                print(f"error renaming: {file_path}\n{e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="rename image and video files to EXIF date & time recursively")
    parser.add_argument("--input-dir", required=True, help="directory containing files to rename")
    args = parser.parse_args()
    if not os.path.isdir(args.input_dir):
        print(f"error: {args.input_dir} is not a valid directory")
        quit()

    rename_files(args.input_dir)
