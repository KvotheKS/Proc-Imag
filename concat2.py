import cv2
import os

def load_images_from_folder(folder_path):
    images = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
            img = cv2.imread(os.path.join(folder_path, filename))
            if img is not None:
                images.append((filename, img))
    return images

def display_images_in_columns(images, columns=2):
    if columns < 1:
        columns = 1
    row_count = len(images) // columns + (len(images) % columns > 0)
    max_height = max(img.shape[0] for _, img in images)
    result = None

    for i in range(row_count):
        row_images = images[i * columns:(i + 1) * columns]
        row_result = None

        for name, img in row_images:
            img = cv2.resize(img, (img.shape[1] * max_height // img.shape[0], max_height))
            if row_result is None:
                row_result = img
            else:
                row_result = cv2.hconcat([row_result, img])

        if result is None:
            result = row_result
        else:
            result = cv2.vconcat([result, row_result])

    cv2.imwrite('candy.png', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    folder_path = input("Enter the folder path: ")
    images = load_images_from_folder(folder_path)

    if not images:
        print("No valid images found in the specified folder.")
    else:
        display_images_in_columns(images, columns=2)