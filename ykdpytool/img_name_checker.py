import argparse
import configparser
import re

from pathlib import Path

from ykdpyutil import files

CONF_DIR = "./config/img_name_checker/"

pattern_dir_name = None
pattern_file_name = None
file_suffix_list = None
exclude_dir_names = None
exclude_file_names = None


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    args = parser.parse_args()

    return Path(args.target)


def get_configs():
    global pattern_dir_name, pattern_file_name, file_suffix_list, \
        exclude_dir_names, exclude_file_names
    conf = configparser.ConfigParser()
    conf.read(CONF_DIR + "img_name_checker.conf", "UTF-8")

    pattern_dir_name = re.compile(conf.get("dir", "name_pattern"))
    pattern_file_name = re.compile(conf.get("file", "name_pattern"))

    file_suffix_list = conf.get("file", "suffix_list").split(",")

    exclude_dir_names = load_text_file(CONF_DIR + "exclude_dir_names.txt")
    exclude_file_names = load_text_file(CONF_DIR + "exclude_file_names.txt")


def load_text_file(path):
    result = []
    with open(path) as f:
        for line in f.readlines():
            line_text = line.rstrip("\n")
            if line_text.startswith("#") or line_text == "":
                continue
            result.append(line_text)
    return result


def check_dir_name(dir):
    dir_name = dir.name
    return pattern_dir_name.match(dir_name)


def check_sub_dir(dir):
    return len(files.get_dirs(dir)) == 0


def get_file_list(dir):
    return files.get_files(
        dir, path_filter=lambda p: not is_exclude_file(p))


def check_file_prefix(file):
    file_name = files.get_prefix(file)
    return pattern_file_name.match(file_name)


def check_file_suffix(file):
    file_suffix = files.get_suffix(file)
    return file_suffix in file_suffix_list


def check_serial_name(file_list):
    name_list = list(map(lambda p: files.get_prefix(p), file_list))
    cnt = len(file_list)
    for i in range(cnt):
        name = str(i + 1).zfill(3)
        if name not in name_list:
            return False
    return True


def is_exclude_dir(dir):
    dir_name = dir.name
    if dir_name in exclude_dir_names:
        return True
    return False


def is_exclude_file(file):
    file_name = file.name
    if file_name in exclude_file_names:
        return True
    return False


error_list = []
target = get_args()
get_configs()
dir_list = files.get_dirs(target, path_filter=lambda p: not is_exclude_dir(p))
for dir in dir_list:
    dir_name = dir.name
    if not check_dir_name(dir):
        error_list.append("Invalid directory name: {}".format(dir_name))
    if not check_sub_dir(dir):
        error_list.append("Exists sub dir: {}".format(dir_name))
    file_list = get_file_list(dir)
    for file in file_list:
        if not check_file_prefix(file):
            error_list.append("Invalid file name: {}".format(
                file.relative_to(target)))
        if not check_file_suffix(file):
            error_list.append("Invalid file suffix: {}".format(
                file.relative_to(target)))
    if not check_serial_name(file_list):
        error_list.append("Not serial number: {}".format(dir_name))
if len(error_list) > 0:
    for error in error_list:
        print(error)
else:
    print("No error")
