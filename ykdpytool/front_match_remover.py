import argparse
from pathlib import Path
from ykdpyutil import files


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
    # 対象ディレクトリ直下のファイルパスのリストを取得
    path_list = files.get_files(target_dir, recursive=False)

    # ファイル名のリストを取得
    file_list = list(map(lambda p: p.name, path_list))

    if not file_list:
        # 該当ファイルなしの場合は終了
        print("Error: 対象ファイルなし")
        return

    # 前方一致部分の取得
    starts = same_text(file_list)

    print("前方一致部分： {}".format(starts))

    # 不一致部分のリストを取得
    df_list = list(
        map(lambda p: p[len(starts): len(p)], file_list))

    # 前方一致部分がない場合は中断
    if len(starts) <= 0:
        print("Error: リネーム不要のため中断")
        return

    # リネーム処理
    for idx, src in enumerate(file_list):
        dst = df_list[idx]
        print(src, "->", dst)
        src_path = Path(target_dir, src)
        dst_path = Path(target_dir, dst)
        if src_path != dst_path:
            files.move(src_path, dst_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target_dir")
    args = parser.parse_args()
    target_dir = Path(args.target_dir)
    rename(target_dir)


if __name__ == '__main__':
    main()
