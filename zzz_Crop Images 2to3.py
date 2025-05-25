import os
from PIL import Image

def crop_to_aspect(image, target_ratio=(2, 3)):
    width, height = image.size
    target_width = width
    target_height = int(width * (target_ratio[1] / target_ratio[0]))

    if target_height > height:
        target_height = height
        target_width = int(height * (target_ratio[0] / target_ratio[1]))

    left = (width - target_width) // 2
    top = (height - target_height) // 2
    right = left + target_width
    bottom = top + target_height

    return image.crop((left, top, right, bottom))

def process_images(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    supported_formats = (".jpg", ".jpeg", ".png", ".bmp")

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(supported_formats):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            with Image.open(input_path) as img:
                if img.width / img.height != 2/3:
                    cropped_img = crop_to_aspect(img)
                    cropped_img.save(output_path)
                    print(f"Cropped: {filename}")
                else:
                    img.save(output_path)
                    print(f"Already correct aspect: {filename}")

# Beispielaufruf
input_folder = '/Users/schnebbe/Library/Mobile Documents/com~apple~CloudDocs/01 Nymo/03_NymoArt/03 KeyFrames/Style 1 liquid quiet/1_1'
output_folder = '/Users/schnebbe/Library/Mobile Documents/com~apple~CloudDocs/01 Nymo/03_NymoArt/03 KeyFrames/Style 1 liquid quiet/2_3'
process_images(input_folder, output_folder)
