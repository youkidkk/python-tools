import argparse
import os
import re
from ykdpyutil import files, texts


def same_text(texts):
    first = texts[0]
    first_len = len(first)
    for i in range(first_len + 1):
        current = first[0:i]
        if not allstartswith(texts, current):
            return current[0:i-1]
    return first


def allstartswith(texts, text):
    for item in texts:
        if not item.startswith(text):
            return False
    return True


def max_len(text_list):
    return max(list(map(lambda text: len(text), text_list)))


def rename(target_dir):
    path_list = files.get_files(target_dir, recursive=False)
    file_list = list(map(lambda p: os.path.basename(p), path_list))
    if not file_list:
        print("Error: 対象ファイルなし")
        return
    starts = same_text(file_list)
    reversed_list = list(map(lambda i: texts.reverse(i), file_list))
    ends = texts.reverse(same_text(reversed_list))

    print(starts, ends)

    df_list = list(
        map(lambda p: p[len(starts): len(p) - len(ends)], file_list))
    if all(list(map(lambda d: re.match("[0-9]+", d), df_list))):
        if starts == "0":
            print("Error: リネーム不要のため中断")
            return
        num_len = max_len(df_list) + 1
        for idx, src in enumerate(file_list):
            dst = df_list[idx].zfill(num_len) + ends
            print(src, "->", dst)
            src_path = os.path.join(target_dir, src)
            dst_path = os.path.join(target_dir, dst)
            files.move(src_path, dst_path)
    else:
        print("Error: 不一致部分に数値以外が含まれている")
        return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target_dir")
    args = parser.parse_args()
    target_dir = args.target_dir
    rename(target_dir)


if __name__ == '__main__':
    main()
