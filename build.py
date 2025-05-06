#!/usr/bin/env python
"""
ファイル管理自動化ツールのビルドスクリプト
実行ファイル（.exe）を生成します
"""

import os
import sys
import shutil
import argparse
import platform
import subprocess
from pathlib import Path

def parse_args():
    """コマンドライン引数を解析する"""
    parser = argparse.ArgumentParser(description="ファイル管理自動化ツールのビルドスクリプト")
    
    parser.add_argument(
        "--clean", "-c",
        help="ビルド前にdistおよびbuildディレクトリをクリーンアップ",
        action="store_true"
    )
    
    parser.add_argument(
        "--onefile", "-f",
        help="単一ファイルの実行ファイルを生成",
        action="store_true"
    )
    
    parser.add_argument(
        "--icon", "-i",
        help="実行ファイルのアイコンファイル",
        default=None
    )
    
    parser.add_argument(
        "--name", "-n",
        help="出力ファイル名",
        default="FileOrganizer"
    )
    
    parser.add_argument(
        "--version", "-v",
        help="バージョン情報を指定",
        default="0.1.0"
    )
    
    return parser.parse_args()

def clean_build_directories():
    """ビルドディレクトリをクリーンアップ"""
    directories = ["dist", "build"]
    for directory in directories:
        if os.path.exists(directory):
            print(f"クリーンアップ: {directory}")
            shutil.rmtree(directory)
    
    spec_files = list(Path(".").glob("*.spec"))
    for spec_file in spec_files:
        print(f"クリーンアップ: {spec_file}")
        os.remove(spec_file)

def build_executable(args):
    """実行ファイルをビルド"""
    # ビルド前の準備
    if args.clean:
        clean_build_directories()
    
    # システムに応じたオプション
    system = platform.system()
    separator = ";" if system == "Windows" else ":"
    
    # PyInstallerコマンドの構築
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--windowed"
    ]
    
    # ワンファイルオプション
    if args.onefile:
        cmd.append("--onefile")
    
    # 出力ファイル名
    cmd.extend(["--name", args.name])
    
    # バージョン情報
    if system == "Windows":
        version_info = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({args.version.replace('.', ', ')}, 0),
    prodvers=({args.version.replace('.', ', ')}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u''),
           StringStruct(u'FileDescription', u'ファイル管理自動化ツール'),
           StringStruct(u'FileVersion', u'{args.version}'),
           StringStruct(u'InternalName', u'FileOrganizer'),
           StringStruct(u'LegalCopyright', u''),
           StringStruct(u'OriginalFilename', u'{args.name}.exe'),
           StringStruct(u'ProductName', u'ファイル管理自動化ツール'),
           StringStruct(u'ProductVersion', u'{args.version}')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
        version_file = "file_version_info.txt"
        with open(version_file, "w", encoding="utf-8") as f:
            f.write(version_info)
        cmd.extend(["--version-file", version_file])
    
    # アイコン
    if args.icon:
        cmd.extend(["--icon", args.icon])
    
    # データファイル
    data_option = f"src{separator}src"
    cmd.extend(["--add-data", data_option])
    
    # エントリーポイント
    cmd.append("src/main.py")
    
    # コマンド実行
    print(f"実行コマンド: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    # 後処理
    if system == "Windows" and os.path.exists("file_version_info.txt"):
        os.remove("file_version_info.txt")
    
    # 出力パス
    output_path = os.path.join("dist", f"{args.name}.exe" if system == "Windows" else args.name)
    
    print(f"ビルド成功: {output_path}")
    return output_path

def main():
    """メイン関数"""
    args = parse_args()
    
    try:
        output_path = build_executable(args)
        print(f"実行ファイルが正常に生成されました: {output_path}")
        return 0
    except Exception as e:
        print(f"ビルド中にエラーが発生しました: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())