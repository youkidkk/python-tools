import argparse
import os
from datetime import datetime

from PIL import Image
from PIL.ExifTags import TAGS

from ykdpyutil import files
from ykdpyutil import datetimes


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

    return args.src_root, args.dst_root, args.pattern


def get_datetime(file):
    result = datetimes.get_from_str(
        get_datetime_org_text(file), "%Y:%m:%d %H:%M:%S.%f")
    if result is None:
        print("\n{} : EXIF情報が取得できないため、作成日時にてファイル名を設定します。 ".format(file))
        result = files.get_created(file)
    return result


def get_dst_path(dst_parent, filename):
    dst_path = os.path.join(dst_parent, filename + ".jpg")
    if os.path.exists(dst_path):
        idx = 1
        while os.path.exists(dst_path):
            dst_path = os.path.join(
                dst_parent, filename + "-" + str(idx) + ".jpg")
            idx += 1
        print("\n{} : 出力先パスが存在するため、連番を付与しました。  ".format(dst_path))
    return dst_path


def main():
    src_root, dst_root, pattern = get_args()

    files.clear_dir(dst_root)

    list = files.get_files(
        src_root, lambda p: files.get_suffix(p).lower() == "jpg")
    count = 1
    total = len(list)
    for src_path in list:
        rel_path = os.path.relpath(src_path, src_root)
        dst_parent = os.path.dirname(os.path.join(dst_root, rel_path))

        dt = get_datetime(src_path)

        filename = dt.strftime(pattern)
        dst_path = get_dst_path(dst_parent, filename)

        files.copy(src_path, dst_path)
        files.modify_times(dst_path, dt)

        print(("\r{:>" + str(len(str(total))) +
               "}/{} 完了しました。 {}").format(count, total, str(dst_path)), end="")
        count += 1
    print("\n終了しました。")


if __name__ == '__main__':
    main()
