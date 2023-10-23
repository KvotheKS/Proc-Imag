import cv2
import os
import argparse
import re

# Função personalizada para ordenar alfanumericamente
def alphanumeric_sort(file_name):
    parts = re.split('(\d+)', file_name)
    parts[1::2] = map(int, parts[1::2])
    return parts

# Função para criar uma imagem concatenando verticalmente as imagens em uma pasta
def concatenate_images_in_folder(folder_path):
    # Listar os arquivos de imagem na pasta e ordená-los alfanumericamente
    image_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))], key=alphanumeric_sort)

    # Verificar se há pelo menos duas imagens para concatenar
    if len(image_files) < 2:
        print(f"Pelo menos duas imagens são necessárias para concatenar na pasta: {folder_path}")
        return None

    # Inicializar a lista para armazenar imagens com borda vermelha
    images_with_border = []

    # Adicionar borda vermelha a cada imagem e armazená-las na lista
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        image = cv2.imread(image_path)
        print(image_path)
        
        # Verificar se a imagem foi carregada corretamente
        if image is not None:
            # Adicionar uma borda vermelha
            bordered_image = cv2.copyMakeBorder(image, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=(200, 0, 200))
            images_with_border.append(bordered_image)

    # Concatenar as imagens verticalmente
    concatenated_image = cv2.vconcat(images_with_border)

    return concatenated_image

# Argumentos da linha de comando
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", required=True, help="Caminho para a imagem de saída")
ap.add_argument("folders", nargs='+', help="Caminhos para as pastas contendo imagens")
args = vars(ap.parse_args())

# Inicializar uma lista para armazenar imagens resultantes de cada pasta
result_images = []

# Processar cada pasta e criar a imagem resultante
for folder in args["folders"]:
    concatenated_image = concatenate_images_in_folder(folder)
    if concatenated_image is not None:
        result_images.append(concatenated_image)

# Concatenar as imagens horizontalmente
final_image = cv2.hconcat(result_images)

# Salvar a imagem concatenada
cv2.imwrite(args["output"], final_image)

# Exibir a imagem concatenada (opcional)
# cv2.imshow("Imagem Concatenada", final_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
