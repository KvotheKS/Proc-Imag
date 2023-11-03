import os
import time

imgs = [ 'lion', 'candyr', 'catedral']
# types = ['kmeans', 'dither']
color_number = [[4,8,16, 256], [2, 4, 8, 16]]

os.makedirs('./results', exist_ok=True)

for i in range(len(imgs)):
    # for z in color_number[i]:
    p_test = time.time()
    # colours = z
    file_ext = 'png' if os.path.exists(f'./imgs/{imgs[i]}.png') else 'jpg'
    t = '{0}'
    os.system(f'python3 ./src/ev.py -i ./imgs/{imgs[i]}.{file_ext} -r ./results/{imgs[i]}tr/{t}.png')
    now_num = time.time()
    print(f'img {imgs[i]} d+k {now_num-p_test} ')
        
    # exit()