import argparse
import msvcrt
import re
from pathlib import Path

from ykdpyutil import files


def load_config(path):
    result = []
    with open(path) as f:
        for line in f.readlines():
            if line.startswith("#"):
                continue
            sp = line.rstrip('\r\n').split("\t")
            if len(sp) >= 2:
                result.append(sp)
    return result


def confirm():
    while True:
        inp = chr(ord(msvcrt.getch()))
        inpl = inp.lower()
        if inpl == "y":
            return True
        elif inpl == "n":
            return False


def rename(path, regex_list):
    parent = path.parent

    dst = path.name
    for regex in regex_list:
        pattern = regex[0]
        after = regex[1]

        if re.match(pattern, dst):
            dst = re.sub(pattern, after, dst)
        else:
            dst = path.name
            break
    if dst != path.name:
        print("{} -> {} (y/n)  ".format(path.name, dst))
        if confirm():
            dst_path = Path(parent, dst)
            files.move(path, dst_path)
            print("リネームしました。")
        else:
            print()
    else:
        print("Error: 正規表現アンマッチ {}".format(path.name))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target_dir")
    parser.add_argument("regex_setting")
    args = parser.parse_args()

    target_dir = Path(args.target_dir)
    regex_setting = Path(args.regex_setting)

    regex_list = load_config(regex_setting)

    for dir in files.get_dirs(target_dir):
        rename(dir, regex_list)


if __name__ == '__main__':
    main()
