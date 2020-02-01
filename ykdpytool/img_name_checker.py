import argparse
import re

from pathlib import Path

from ykdpyutil import files

PATTERN_DIR_NAME = re.compile(r"^\[[^\]]+\]\[[^\]]+\].+$")
EXCLUDE_DIR_NAMES = ["PxDownloader"]
EXCLUDE_FILE_NAMES = ["Thumbs.db"]


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    args = parser.parse_args()

    return Path(args.target)


def check_dir_name(dir):
    return PATTERN_DIR_NAME.match(dir_name)


def check_sub_dir(dir):
    return len(files.get_dirs(dir)) == 0


def check_files(dir):
    file_list = files.get_files(
        dir, path_filter=lambda p: not is_exclude_file(p))
    name_list = list(map(lambda p: p.name, file_list))
    cnt = len(name_list)
    for i in range(cnt):
        name = str(i + 1).zfill(3) + ".jpg"
        if name not in name_list:
            return False
    return True


def is_exclude_dir(dir):
    dir_name = dir.name
    if dir_name in EXCLUDE_DIR_NAMES:
        return True
    return False


def is_exclude_file(file):
    file_name = file.name
    if file_name in EXCLUDE_FILE_NAMES:
        return True
    return False


target = get_args()
dir_list = files.get_dirs(target)
for dir in dir_list:
    dir_name = dir.name
    if not check_dir_name(dir):
        print("Invalid directory name: {}".format(dir_name))
    if not check_sub_dir(dir):
        print("Exists sub dir: {}".format(dir_name))
    if not check_files(dir):
        print("Invalid file name: {}".format(dir_name))
