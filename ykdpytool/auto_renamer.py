import argparse
import os
import threading
from time import sleep

from ykdpyutil import files

target_dir = ""
dest_dir = ""
interval = 1
length = 3

running = True


def get_args() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("target_dir")
    parser.add_argument("-d", "--dest", type=str)
    parser.add_argument("-i", "--interval", type=int, default=1)
    parser.add_argument("-l", "--length", type=int, default=2)
    args = parser.parse_args()

    global target_dir, dest_dir, interval, length
    target_dir = args.target_dir
    dest_dir = args.dest or target_dir
    interval = args.interval
    length = args.length


def check_dir(path: str) -> bool:
    if not os.path.exists(path):
        print("'{}' is not exists. : ".format(path))
        return False
    if os.path.isfile(path):
        print("'{}' is not directory.".format(path))
        return False
    if len(files.get_paths(path)) > 1:
        print("'{}' is not empty.".format(path))
        return False
    return True


def wait_update(target: str) -> None:
    cnt = 0
    size_last = 0
    while True:
        size = os.path.getsize(target)
        if size_last == size:
            cnt += 1
        else:
            size_last = size
            cnt = 0
        if cnt >= 5:
            return
        sleep(interval)


def move(target: str) -> None:
    prefix, suffix = files.get_prefix_suffix(target)
    if prefix is None:
        return

    wait_update(target)

    max = int("9" * length)
    for idx in range(1, max):
        dst = os.path.join(dest_dir, prefix, "{}-{}.{}"
                           .format(prefix, str(idx).zfill(length), suffix))
        if not os.path.exists(dst):
            while True:
                try:
                    files.move(target, dst)
                    break
                except PermissionError:
                    files.delete(dst)
                sleep(interval)
            msg = "\r'{}' -> '{}'".format(
                os.path.basename(target),
                os.path.basename(dst))
            print(msg)
            return None


def end_process() -> None:
    for file in files.get_files(target_dir):
        files.move(file, os.path.join(target_dir, os.path.basename(file)))
    for dir in reversed(files.get_dirs(target_dir)):
        os.rmdir(dir)


def main_loop() -> None:
    cnt = 1
    max = 10
    while True:
        if not running:
            end_process()
            print("Finish!!!")
            break
        print("\rRunning" + ("." * cnt).ljust(max), end="")
        cnt += 1
        if cnt > max:
            cnt -= max
        targets = files.get_files(
            target_dir, lambda p: os.path.dirname(p) == target_dir)
        for target in targets:
            try:
                move(target)
            except FileNotFoundError:
                pass
        sleep(interval)


def main() -> None:
    get_args()
    if not check_dir(target_dir) or not check_dir(dest_dir):
        return
    print("Please press <Enter-key> to finish.")

    global running
    thread = threading.Thread(target=main_loop)
    thread.start()

    input()
    running = False
    thread.join()


if __name__ == '__main__':
    main()
