"""
ユーティリティモジュール - 共通の補助関数を提供
"""

import os
import sys
import platform
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from loguru import logger

def setup_logger(log_dir: Optional[str] = None, level: str = "INFO") -> None:
    """ロガーの設定を行う"""
    # レベルマッピング
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    log_level = level_map.get(level.upper(), logging.INFO)
    
    # loguru ロガーの設定をクリア
    logger.remove()
    
    # 標準エラー出力へのハンドラを追加
    logger.add(sys.stderr, level=log_level)
    
    # ログファイルへの出力を設定
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        log_file = log_path / f"file_organizer_{datetime.datetime.now().strftime('%Y%m%d')}.log"
        logger.add(
            str(log_file),
            rotation="10 MB",
            retention="30 days",
            level=log_level
        )

def get_user_documents_dir() -> str:
    """ユーザーのドキュメントディレクトリを取得"""
    system = platform.system()
    
    if system == 'Windows':
        return os.path.join(os.path.expanduser('~'), 'Documents')
    elif system == 'Darwin':  # macOS
        return os.path.join(os.path.expanduser('~'), 'Documents')
    elif system == 'Linux':
        # Linuxでは一般的に~/Documentsが使われる
        docs_dir = os.path.join(os.path.expanduser('~'), 'Documents')
        if os.path.exists(docs_dir):
            return docs_dir
        else:
            return os.path.expanduser('~')  # ホームディレクトリをフォールバック
    else:
        return os.path.expanduser('~')

def get_app_data_dir() -> str:
    """アプリケーションデータディレクトリを取得"""
    system = platform.system()
    app_name = "FileOrganizer"
    
    if system == 'Windows':
        app_data = os.getenv('APPDATA')
        if app_data:
            return os.path.join(app_data, app_name)
        else:
            return os.path.join(os.path.expanduser('~'), f'.{app_name.lower()}')
    elif system == 'Darwin':  # macOS
        return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', app_name)
    else:  # Linux/UNIX
        # XDG Base Directory 仕様に従う
        xdg_config_home = os.getenv('XDG_CONFIG_HOME')
        if xdg_config_home:
            return os.path.join(xdg_config_home, app_name)
        else:
            return os.path.join(os.path.expanduser('~'), f'.{app_name.lower()}')

def get_file_size_str(size_in_bytes: int) -> str:
    """ファイルサイズを人間が読みやすい形式に変換"""
    # バイト
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    
    # キロバイト
    size_in_kb = size_in_bytes / 1024
    if size_in_kb < 1024:
        return f"{size_in_kb:.2f} KB"
    
    # メガバイト
    size_in_mb = size_in_kb / 1024
    if size_in_mb < 1024:
        return f"{size_in_mb:.2f} MB"
    
    # ギガバイト
    size_in_gb = size_in_mb / 1024
    return f"{size_in_gb:.2f} GB"

def get_relative_path(path: str, base_path: str) -> str:
    """ベースパスからの相対パスを取得"""
    try:
        return os.path.relpath(path, base_path)
    except ValueError:
        # 異なるドライブ間など、相対パスを取得できない場合
        return path

def is_valid_directory(path: str) -> bool:
    """指定されたパスが有効なディレクトリかどうか確認"""
    if not path:
        return False
    return os.path.isdir(path)

def get_default_log_dir() -> str:
    """デフォルトのログディレクトリを取得"""
    app_data_dir = get_app_data_dir()
    log_dir = os.path.join(app_data_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

def format_timestamp(timestamp: float) -> str:
    """タイムスタンプを読みやすい形式にフォーマット"""
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M:%S')