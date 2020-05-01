import argparse
import threading
from pathlib import Path
from time import sleep

from ykdpyutil import files

target_dir = Path("")
dest_dir = Path("")
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
    target_dir = Path(args.target_dir)
    dest_dir = Path(args.dest or target_dir)
    interval = args.interval
    length = args.length


def check_dir(path: Path) -> bool:
    if not path.exists():
        print("'{}' is not exists. : ".format(path))
        return False
    if path.is_file():
        print("'{}' is not directory.".format(path))
        return False
    if len(files.get_paths(path, recursive=True)) > 0:
        print("'{}' is not empty.".format(path))
        return False
    return True


def wait_update(target: Path) -> None:
    cnt = 0
    size_last = 0
    while True:
        size = target.stat().st_size
        if size_last == size:
            cnt += 1
        else:
            size_last = size
            cnt = 0
        if cnt >= 5:
            return
        sleep(interval)


def move(target: Path) -> None:
    prefix, suffix = files.get_prefix_suffix(target)
    if prefix is None:
        return

    wait_update(target)

    max = int("9" * length)
    for idx in range(1, max):
        dst = Path(
            dest_dir,
            prefix,
            "{}-{}.{}".format(prefix, str(idx).zfill(length), suffix))
        if not dst.exists():
            while True:
                try:
                    files.move(target, dst)
                    break
                except PermissionError:
                    files.delete(dst)
                sleep(interval)
            msg = "\r'{}' -> '{}'".format(
                target.name,
                dst.name)
            print(msg)
            return None


def end_process() -> None:
    for file in files.get_files(target_dir, recursive=True):
        files.move(file, Path(target_dir, file.name))
    for dir in reversed(files.get_dirs(target_dir, recursive=True)):
        dir.rmdir()


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
            target_dir,
            recursive=True,
            path_filter=lambda p: p.parent.samefile(target_dir))
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
