''' Recursively scan a directory and classify image files found, and save results to a text file.

Classification is done using pre-trained EfficientNetV2-B2 model.
info on EfficientNetV2 models: https://github.com/leondgarse/keras_efficientnet_v2

Furthermore, there's a group of interested labels, and the probabilities of these labels
are summed are written to output file too.

Output file format:

file: "D:\dir1\dir2\filename.jpg"
   {'label1': 568, 'label2': 181, 'label3': 38, 'label4': 26, 'label5': 24, 'label6': 11}
   interested labels: 123

Probabilities are scaled by 1000 and rounded to nearest integer before written to file.
'''
import os, pathlib, argparse

#ImageNet labels URL: https://storage.googleapis.com/download.tensorflow.org/data/ImageNetLabels.txt
IMAGENET_LABELS_FILE = r"C:\code\ImageNetLabels.txt"


interested_labels = { #fruits, vegetables, flowers, trees, etc
    'acorn_squash','artichoke', 'banana', 'bamboo', 'bell pepper', 'broccoli', 'Brussels sprout',
    'cabbage', 'carnation', 'cauliflower', 'common dandelion', 'corn', 'cucumber',
    'daisy', 'fig', 'Granny Smith', 'head cabbage', 'hippeastrum', 'iris', 'lemon',
    'lime', 'lotus', 'mango', 'marigold', 'mushroom', 'oak grove', 'orange', 'palm',
    'petunia', 'pineapple', 'pomegranate', 'pot', 'rapeseed','rose', 'snapdragon', 'strawberry',
    'sunflower', 'tulip', 'vase', 'water lily', 'willow', 'zucchini'
}

def build_interested_mask(imagenet_labels):
    mask = np.zeros(len(imagenet_labels))
    for i, label in enumerate(imagenet_labels):
        if label in interested_labels:
            mask[i] = 1
    return mask

def sum_probabilities_by_category(predictions, mappings, category_to_index):
    """sum probabilities for each unique category index in mappings."""
    predictions = np.array(predictions)
    mappings = np.array(mappings)
    category_probs = np.bincount(mappings, weights=predictions, minlength=len(category_to_index))
    return (category_probs*1000+0.5).astype(np.int32)

def process_image(outfh,image_path, model, interestd_mask):
    try: #classify one image
        img = image.load_img(image_path, target_size=(260, 260))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return

    print("file:",image_path)
    outfh.write(f'file: "{image_path}"\n')

    # Get predictions
    predictions = model.predict(img_array)[0]  # Shape: (1000,)
    decoded_preds = decode_predictions(predictions[np.newaxis, :], top=6)[0]
    pred_dict = {class_name: int(prob*1000+0.5) for _, class_name, prob in decoded_preds}
    print('  ',pred_dict)
    outfh.write(f"   {pred_dict}\n")

    # sum probabilities of interested labels
    x=int(1000*np.dot(predictions, interestd_mask)+0.5)
    print('  interested labels:',x)
    outfh.write(f"   interested labels: {x}\n")

def walk_and_process_images(dir_path, output_file, interestd_mask):
    """
    Recursively walk a directory and classify image files.

    dir_path (str): Path to the directory to start walking from
    model: Preloaded EfficientNetV2-B0 model
    index_mapping: Mapping from ImageNet indices to category indices
    cat_names: List of category names
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    model = EfficientNetV2B2(weights='imagenet')
    outfh = open(output_file, 'wt',encoding="utf-8")
    for root, _, files in os.walk(dir_path):
        files2=sorted(files)
        for file in files2:
            if pathlib.Path(file).suffix.lower() in image_extensions:
                full_path = pathlib.Path(root) / file
                try:
                    process_image(outfh,str(full_path), model, interestd_mask)
                except Exception as e:
                    print(f"error processing: {full_path}\n{str(e)}")
    outfh.close()


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="classify images using pre-trained EfficientNetV2-B2 model")
    parser.add_argument('--input-dir', required=True, help='directory to scan')
    parser.add_argument('--output-file', default='classification_results.txt', help='output text file for results')
    args = parser.parse_args()
    if not os.path.isdir(args.input_dir):
        print(f"directory does not exist: {args.input_dir}")
        quit()

    #delayed imports so we don't incur long start time if command line arguments are incorrect
    import numpy as np
    import tensorflow as tf
    from tensorflow.keras.applications import EfficientNetV2B2
    from tensorflow.keras.applications.efficientnet_v2 import preprocess_input,decode_predictions
    from tensorflow.keras.preprocessing import image

    with open(IMAGENET_LABELS_FILE, 'rt') as f: #load ImageNet labels
        imagenet_labels = f.read().strip().split("\n")[1:]  # skip 'background' class

    interested_mask=build_interested_mask(imagenet_labels)

    walk_and_process_images(args.input_dir, args.output_file, interested_mask)
    print(f"classification results saved to {args.output_file}")
