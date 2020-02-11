import argparse
from datetime import datetime
from pathlib import Path

from PIL import Image
from PIL.ExifTags import TAGS

from ykdpyutil import files, datetimes, console


TEXT_ERROR_DIST_NOT_EMPTY = "出力先ディレクトリが空ではないため終了します。{}"
TEXT_CANT_GET_EXIF = "{} : EXIF情報が取得できないため、作成日時にてファイル名を設定します。 "
TEXT_ADD_NUMBER = "{} : 出力先パスが存在するため、連番を付与しました。  "
TEXT_COMPLETE = "\r{}/{} 完了しました。 {}"
TEXT_END = "終了しました。"


def get_exif(file):
    im = Image.open(file)

    try:
        exif = im._getexif()
        exif_table = {}
        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            exif_table[tag] = value
        return exif_table
    except AttributeError:
        return None


def get_datetime_org_text(file):
    exif_table = get_exif(file)
    if exif_table is not None:
        dt = exif_table.get("DateTimeOriginal")
        ms = exif_table.get("SubsecTimeOriginal") or "000000"

        if datetime:
            return "{}.{}".format(dt, ms)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("src_root")
    parser.add_argument("dst_root")
    parser.add_argument("-p", "--pattern", type=str,
                        default="%Y-%m%d_%H%M%S-%f")
    args = parser.parse_args()

    return Path(args.src_root), Path(args.dst_root), args.pattern


def get_datetime(file):
    result = datetimes.get_from_str(
        get_datetime_org_text(file), "%Y:%m:%d %H:%M:%S.%f")
    if result is None:
        print("\n" + TEXT_CANT_GET_EXIF.format(file))
        result = files.get_created(file)
    return result


def get_dst_path(dst_parent, filename):
    dst_path = Path(dst_parent, filename + ".jpg")
    if dst_path.exists():
        idx = 1
        while dst_path.exists():
            dst_path = Path(
                dst_parent, filename + "-" + str(idx) + ".jpg")
            idx += 1
        print("\n" + TEXT_ADD_NUMBER.format(dst_path))
    return dst_path


def main():
    src_root, dst_root, pattern = get_args()

    try:
        # 出力先ディレクトリのチェック
        files.check_empty(dst_root)

        list = files.get_files(
            src_root,
            recursive=True,
            path_filter=lambda p: files.get_suffix(p).lower() == "jpg")
        count = 1
        total = len(list)

        lp = console.LinePrinter()
        for src_path in list:
            rel_path = src_path.relative_to(src_root)
            dst_parent = Path(dst_root, rel_path).parent

            dt = get_datetime(src_path)

            filename = dt.strftime(pattern)
            dst_path = get_dst_path(dst_parent, filename)

            files.copy(src_path, dst_path)
            files.modify_times(dst_path, dt)

            dst_rel = dst_path.relative_to(dst_root)
            result_text = TEXT_COMPLETE.format(
                str(count).rjust(len(str(total))), total, str(dst_rel))
            lp.print(result_text)

            count += 1
        print("\n" + TEXT_END)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
