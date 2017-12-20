# -*- coding: utf-8 -*-
import os
import math

URLS_PATH = '..\\emotioNet_URLs'
SAVE_PATH = 'emotioNet_URLs'
NUMBERS = 1000  # 每个文件分割的大小


def get_file_list(urls_path):
    file_list = os.listdir(urls_path)
    for f in file_list:
        _, fext = os.path.splitext(f)
        if fext != '.txt':
            file_list.remove(f)
    return sorted(file_list)


def split_file(file):
    name, _ = os.path.splitext(file)
    file_path = os.path.join(URLS_PATH, file)
    save_path = os.path.join(SAVE_PATH, name)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    print('{}-{}-{}'.format(name, file_path, save_path))
    
    with open(file_path) as f:
        lines = f.readlines()
    lines_num = len(lines)
    files_num = math.ceil(lines_num / NUMBERS)

    # print(lines_num, files_num)
    for i in range(files_num):
        with open(os.path.join(save_path, '{}_{:03d}.txt'.format(name, i)), 'a+') as f:
            for line in lines[i*NUMBERS:(i+1)*NUMBERS]:
                f.write(line)


if __name__ == '__main__':
    file_list = get_file_list(URLS_PATH)
    for file in file_list:
        split_file(file)
    # file = 'test_urls.txt'
    # split_file(file)