import os
from src.text_extractor.image_extractor import extract_text_from_image

# Get absolute path to project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Change this filename to one of your JPG resumes
image_file = "sample5.jpg"

image_path = os.path.join(BASE_DIR, "data", "raw", image_file)

print("Using image path:", image_path)

text = extract_text_from_image(image_path)

print("\n---- EXTRACTED IMAGE TEXT PREVIEW ----")
print(text[:2000])
