import os
import time

imgs = ['lion', 'candyr']
color_number = [[8,16, 256], [8, 16, 256]]

os.makedirs('./results', exist_ok=True)

for i in range(len(imgs)):
    for z in color_number[i]:
        p_test = time.time()
        colours = z
        for exts in ['png', 'jpg', 'jpeg', 'jfif']:
            if os.path.exists(f'./imgs/{imgs[i]}.{exts}'):
                file_ext = exts
        t = '{0}'
        os.system(f'python3 ./src/ev.py -i ./imgs/{imgs[i]}.{file_ext} -r ./results/{imgs[i]}_{t}/{z}.png -n {colours}')
        now_num = time.time()
        print(f'img {imgs[i]} c {colours} d+k {now_num-p_test} ')
        
    # exit()