import os
import cv2
import sys

def crop_center_200x200(image):
    height, width, _ = image.shape
    if height < 200 or width < 200:
        return None  # Image is too small to crop
    center_x, center_y = width // 2, height // 2
    half_width, half_height = 50, 50
    cropped_image = image[center_y - half_height:center_y + half_height,
                          center_x - half_width:center_x + half_width]
    return cv2.resize(cropped_image, (200,200), interpolation=cv2.INTER_NEAREST)

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <folder_path>")
        return

    folder_path = sys.argv[1]

    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' does not exist.")
        return

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            try:
                image = cv2.imread(file_path)
                if image is not None:
                    cropped_image = crop_center_200x200(image)
                    if cropped_image is not None:
                        os.makedirs(folder_path + '_',exist_ok=True)
                        cv2.imwrite(os.path.join(folder_path+'_', filename), cropped_image)
                        print(f"Saved {filename}.png")
                    else:
                        print(f"Skipped {filename} (too small to crop)")
                else:
                    print(f"Could not open {filename} as an image")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    main()