#!/usr/bin/env python
# coding=utf-8
import re, os


def main():
    map = {}
    imgs = []
    # root 当前目录路径  # dirs 当前路径下所有子目录  # files 当前路径下所有非目录子文件
    for root, dirs, files in os.walk('./images/'):
        for file_item in files:
            img_path = root + '/' + str(file_item)
            size = os.path.getsize(img_path)

            name = re.sub(r'\.\w+$', '', file_item)
            imgs.append(name)

            if size in map:
                map[size] = map[size] + 1
            else:
                map[size] = 1

    max_size = 0
    max_count = 0
    for key in map:
        if map[key] > max_count:
            max_count = map[key]
            max_size = key   # 269422
    print(max_size, len(map))

if __name__ == "__main__":
    main()
