"""
ファイル操作モジュール - ファイルの検索、移動、整理などの機能を提供
"""

import os
import re
import shutil
import hashlib
import datetime
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional, Any
from dataclasses import dataclass
import send2trash
from loguru import logger

from src.config import FileRule

@dataclass
class FileInfo:
    """ファイル情報を格納するクラス"""
    path: Path
    name: str
    extension: str
    size: int
    created_time: datetime.datetime
    modified_time: datetime.datetime
    hash: Optional[str] = None
    
    @classmethod
    def from_path(cls, file_path: Path) -> 'FileInfo':
        """パスからFileInfoオブジェクトを生成"""
        stat = file_path.stat()
        return cls(
            path=file_path,
            name=file_path.name,
            extension=file_path.suffix.lower(),
            size=stat.st_size,
            created_time=datetime.datetime.fromtimestamp(stat.st_ctime),
            modified_time=datetime.datetime.fromtimestamp(stat.st_mtime)
        )
    
    def calculate_hash(self) -> str:
        """ファイルのハッシュ値を計算"""
        if self.hash:
            return self.hash
        
        # 大きなファイルの場合は最初の1MBだけを使用
        max_bytes = 1024 * 1024  # 1MB
        
        hasher = hashlib.md5()
        with open(self.path, 'rb') as f:
            buf = f.read(max_bytes)
            hasher.update(buf)
        
        self.hash = hasher.hexdigest()
        return self.hash


class FileOperations:
    """ファイル操作クラス"""
    
    @staticmethod
    def scan_directory(source_dir: str, include_subdirs: bool = False) -> List[FileInfo]:
        """ディレクトリ内のファイルをスキャン"""
        if not source_dir or not os.path.isdir(source_dir):
            logger.error(f"無効なディレクトリ: {source_dir}")
            return []
        
        files = []
        source_path = Path(source_dir)
        
        try:
            # 再帰的またはトップレベルのみのスキャン
            if include_subdirs:
                # 再帰的にすべてのファイルをスキャン
                for file_path in source_path.glob('**/*'):
                    if file_path.is_file():
                        files.append(FileInfo.from_path(file_path))
            else:
                # 直下のファイルのみスキャン
                for file_path in source_path.glob('*'):
                    if file_path.is_file():
                        files.append(FileInfo.from_path(file_path))
            
            logger.info(f"{len(files)}個のファイルをスキャンしました")
            return files
            
        except Exception as e:
            logger.error(f"ディレクトリのスキャン中にエラーが発生しました: {e}")
            return []
    
    @staticmethod
    def match_file_with_rules(file_info: FileInfo, rules: List[FileRule]) -> Optional[FileRule]:
        """ファイルに一致するルールを検索"""
        for rule in rules:
            if not rule.enabled:
                continue
                
            # 拡張子マッチング
            if rule.extensions and file_info.extension in rule.extensions:
                return rule
            
            # パターンマッチング
            if rule.patterns:
                for pattern in rule.patterns:
                    try:
                        if re.search(pattern, file_info.name, re.IGNORECASE):
                            return rule
                    except re.error:
                        # 正規表現エラーは無視して次のパターンへ
                        continue
        
        return None
    
    @staticmethod
    def organize_files(files: List[FileInfo], rules: List[FileRule], 
                       base_dir: str, create_date_folders: bool = False,
                       handle_duplicates: bool = True, 
                       duplicate_action: str = "skip") -> Dict[str, List[str]]:
        """ファイルをルールに従って整理"""
        result = {
            "success": [],
            "skipped": [],
            "error": []
        }
        
        # 重複ファイルの検出用マップ（ハッシュ値 -> ファイルパス）
        hash_map = {}
        
        for file_info in files:
            try:
                # ルールに一致するかチェック
                rule = FileOperations.match_file_with_rules(file_info, rules)
                if not rule:
                    logger.debug(f"ルールに一致しないファイル: {file_info.name}")
                    result["skipped"].append(f"{file_info.name} - マッチするルールがありません")
                    continue
                
                # 宛先ディレクトリを作成
                dest_dir = Path(base_dir) / rule.destination
                
                # 日付フォルダを使用する場合
                if create_date_folders:
                    date_str = file_info.modified_time.strftime('%Y-%m-%d')
                    dest_dir = dest_dir / date_str
                
                # 宛先ディレクトリが存在しない場合は作成
                dest_dir.mkdir(parents=True, exist_ok=True)
                
                # 宛先ファイルパス
                dest_path = dest_dir / file_info.name
                
                # 重複ファイルのチェック
                if handle_duplicates:
                    # ハッシュ値を計算
                    file_hash = file_info.calculate_hash()
                    
                    # すでに同じハッシュのファイルが処理されている場合
                    if file_hash in hash_map:
                        prev_file = hash_map[file_hash]
                        
                        if duplicate_action == "skip":
                            result["skipped"].append(f"{file_info.name} - 重複ファイル（{prev_file}と同一）")
                            continue
                        elif duplicate_action == "rename":
                            # ファイル名にサフィックスを追加
                            name_parts = os.path.splitext(file_info.name)
                            new_name = f"{name_parts[0]}_duplicate{name_parts[1]}"
                            dest_path = dest_dir / new_name
                        elif duplicate_action == "move_to_trash":
                            # ファイルをゴミ箱に移動
                            send2trash.send2trash(str(file_info.path))
                            result["success"].append(f"{file_info.name} - 重複ファイルのためゴミ箱に移動")
                            continue
                    
                    # ハッシュマップに追加
                    hash_map[file_hash] = str(dest_path)
                
                # 移動先にすでに同名ファイルが存在する場合
                if dest_path.exists():
                    # ファイル名を変更（名前_数字.拡張子）
                    counter = 1
                    while True:
                        name_parts = os.path.splitext(file_info.name)
                        new_name = f"{name_parts[0]}_{counter}{name_parts[1]}"
                        new_dest_path = dest_dir / new_name
                        if not new_dest_path.exists():
                            dest_path = new_dest_path
                            break
                        counter += 1
                
                # ファイルを移動
                shutil.move(str(file_info.path), str(dest_path))
                result["success"].append(f"{file_info.name} -> {dest_path}")
                
            except Exception as e:
                logger.error(f"ファイル {file_info.name} の処理中にエラーが発生しました: {e}")
                result["error"].append(f"{file_info.name} - エラー: {str(e)}")
        
        return result
    
    @staticmethod
    def find_duplicates(files: List[FileInfo]) -> Dict[str, List[FileInfo]]:
        """重複ファイルを検出"""
        # ハッシュ値ごとにファイルをグループ化
        hash_groups = {}
        
        for file_info in files:
            file_hash = file_info.calculate_hash()
            if file_hash not in hash_groups:
                hash_groups[file_hash] = []
            hash_groups[file_hash].append(file_info)
        
        # 2つ以上のファイルがある（重複している）グループのみを返す
        duplicates = {h: files for h, files in hash_groups.items() if len(files) > 1}
        return duplicates
    
    @staticmethod
    def create_directory_if_not_exists(directory: str) -> bool:
        """ディレクトリが存在しない場合は作成"""
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"ディレクトリの作成に失敗しました: {e}")
            return False
    
    @staticmethod
    def get_file_extensions(directory: str, include_subdirs: bool = False) -> Dict[str, int]:
        """ディレクトリ内のファイル拡張子とその数を取得"""
        extensions = {}
        source_path = Path(directory)
        
        try:
            # 再帰的またはトップレベルのみのスキャン
            pattern = '**/*' if include_subdirs else '*'
            
            for file_path in source_path.glob(pattern):
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    if ext in extensions:
                        extensions[ext] += 1
                    else:
                        extensions[ext] = 1
            
            return extensions
            
        except Exception as e:
            logger.error(f"拡張子の検索中にエラーが発生しました: {e}")
            return {}