"""
ファイル管理自動化ツール - メインモジュール
アプリケーションのエントリーポイント
"""

import os
import sys
import argparse
from loguru import logger

from src.config import Config, get_config_path
from src.gui import FileOrganizerGUI
from src.file_operations import FileOperations
from src.utils import setup_logger, get_default_log_dir


def parse_args():
    """コマンドライン引数を解析"""
    parser = argparse.ArgumentParser(description="ファイル管理自動化ツール")
    
    parser.add_argument(
        "--config", "-c",
        help="設定ファイルのパス",
        default=get_config_path()
    )
    
    parser.add_argument(
        "--log-level", "-l",
        help="ログレベル (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        default="INFO"
    )
    
    parser.add_argument(
        "--source", "-s",
        help="整理元ディレクトリ",
        default=None
    )
    
    parser.add_argument(
        "--no-gui", "-n",
        help="GUIを使用せずにコマンドラインモードで実行",
        action="store_true"
    )
    
    parser.add_argument(
        "--organize", "-o",
        help="指定したディレクトリのファイルを整理",
        action="store_true"
    )
    
    parser.add_argument(
        "--scan", 
        help="指定したディレクトリのファイルをスキャンのみ",
        action="store_true"
    )
    
    return parser.parse_args()


def cli_mode(args):
    """コマンドラインモードでの実行"""
    # 設定ファイルの読み込み
    config = Config.load(args.config)
    
    # ログの設定
    log_level = args.log_level if args.log_level else config.log_level
    log_dir = get_default_log_dir()
    setup_logger(log_dir, log_level)
    
    # 整理元ディレクトリ
    source_dir = args.source if args.source else config.organize_config.source_dir
    if not source_dir or not os.path.isdir(source_dir):
        logger.error(f"有効なディレクトリを指定してください: {source_dir}")
        return 1
    
    # スキャンのみの場合
    if args.scan:
        logger.info(f"ディレクトリをスキャン中: {source_dir}")
        include_subdirs = config.organize_config.process_subdirectories
        files = FileOperations.scan_directory(source_dir, include_subdirs)
        logger.info(f"{len(files)}個のファイルが見つかりました")
        
        # 拡張子ごとの統計
        extensions = {}
        for file in files:
            ext = file.extension
            if ext in extensions:
                extensions[ext] += 1
            else:
                extensions[ext] = 1
        
        logger.info("拡張子の統計:")
        for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {ext}: {count}個")
        
        return 0
    
    # ファイル整理の場合
    if args.organize:
        logger.info(f"ファイル整理を開始します: {source_dir}")
        include_subdirs = config.organize_config.process_subdirectories
        create_date_folders = config.organize_config.create_date_folders
        handle_duplicates = config.organize_config.handle_duplicates
        duplicate_action = config.organize_config.duplicate_action
        
        # ファイルのスキャン
        files = FileOperations.scan_directory(source_dir, include_subdirs)
        logger.info(f"{len(files)}個のファイルが見つかりました")
        
        # ファイルの整理
        result = FileOperations.organize_files(
            files, 
            config.file_rules, 
            source_dir, 
            create_date_folders, 
            handle_duplicates, 
            duplicate_action
        )
        
        # 結果の表示
        success_count = len(result["success"])
        skipped_count = len(result["skipped"])
        error_count = len(result["error"])
        
        logger.info(f"成功: {success_count}個")
        logger.info(f"スキップ: {skipped_count}個")
        logger.info(f"エラー: {error_count}個")
        
        if error_count > 0:
            logger.warning("エラーが発生したファイル:")
            for msg in result["error"]:
                logger.warning(f"  {msg}")
        
        return 0
    
    # スキャンもファイル整理も指定されていない場合
    logger.warning("--scan または --organize のいずれかを指定してください")
    return 1


def main():
    """アプリケーションのメイン関数"""
    # コマンドライン引数の解析
    args = parse_args()
    
    # コマンドラインモード
    if args.no_gui or args.scan or args.organize:
        return cli_mode(args)
    
    # GUIモード
    try:
        app = FileOrganizerGUI()
        app.run()
        return 0
    except Exception as e:
        logger.error(f"アプリケーションの実行中にエラーが発生しました: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())