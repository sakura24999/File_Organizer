"""
設定管理モジュール - ユーザー設定の読み込みと保存を担当
"""

import os
import json
import shutil
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any

class ConfigError(Exception):
    """設定関連のエラー"""
    pass

@dataclass
class FileRule:
    """ファイル振り分けルール"""
    name: str
    extensions: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    destination: str = ""
    enabled: bool = True

@dataclass
class OrganizeConfig:
    """整理設定"""
    source_dir: str = ""
    process_subdirectories: bool = False
    create_date_folders: bool = False
    handle_duplicates: bool = True
    duplicate_action: str = "skip"  # "skip", "rename", "move_to_trash"
    
@dataclass
class Config:
    """アプリケーション設定"""
    organize_config: OrganizeConfig = field(default_factory=OrganizeConfig)
    file_rules: List[FileRule] = field(default_factory=list)
    theme: str = "SystemDefault"
    language: str = "ja"
    log_level: str = "INFO"
    
    @classmethod
    def load(cls, config_path: str) -> 'Config':
        """設定ファイルから設定を読み込む"""
        config_file = Path(config_path)
        
        # 設定ファイルが存在しない場合はデフォルト設定を作成して保存
        if not config_file.exists():
            config = cls()
            # デフォルトのファイルルールを追加
            config.file_rules = [
                FileRule(
                    name="画像", 
                    extensions=[".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
                    destination="画像"
                ),
                FileRule(
                    name="文書", 
                    extensions=[".doc", ".docx", ".pdf", ".txt", ".rtf"],
                    destination="文書"
                ),
                FileRule(
                    name="音楽", 
                    extensions=[".mp3", ".wav", ".flac", ".aac", ".ogg"],
                    destination="音楽"
                ),
                FileRule(
                    name="動画", 
                    extensions=[".mp4", ".avi", ".mov", ".mkv", ".wmv"],
                    destination="動画"
                ),
                FileRule(
                    name="アーカイブ", 
                    extensions=[".zip", ".rar", ".7z", ".tar", ".gz"],
                    destination="アーカイブ"
                ),
            ]
            config.save(config_path)
            return config
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # 設定を構築
            config = cls()
            
            # 基本設定の復元
            for key in ['theme', 'language', 'log_level']:
                if key in config_dict:
                    setattr(config, key, config_dict[key])
            
            # 整理設定の復元
            if 'organize_config' in config_dict:
                organize_config = OrganizeConfig()
                for key, value in config_dict['organize_config'].items():
                    if hasattr(organize_config, key):
                        setattr(organize_config, key, value)
                config.organize_config = organize_config
            
            # ファイルルールの復元
            if 'file_rules' in config_dict:
                file_rules = []
                for rule_dict in config_dict['file_rules']:
                    rule = FileRule(
                        name=rule_dict.get('name', 'Unknown'),
                        extensions=rule_dict.get('extensions', []),
                        patterns=rule_dict.get('patterns', []),
                        destination=rule_dict.get('destination', ''),
                        enabled=rule_dict.get('enabled', True)
                    )
                    file_rules.append(rule)
                config.file_rules = file_rules
            
            return config
            
        except Exception as e:
            raise ConfigError(f"設定ファイルの読み込みに失敗しました: {e}")
    
    def save(self, config_path: str) -> None:
        """設定をファイルに保存"""
        config_file = Path(config_path)
        
        # 親ディレクトリが存在しない場合は作成
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # 設定を辞書に変換
            config_dict = asdict(self)
            
            # 設定をファイルに保存
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            raise ConfigError(f"設定ファイルの保存に失敗しました: {e}")
    
    def backup(self, config_path: str) -> str:
        """設定ファイルのバックアップを作成"""
        source = Path(config_path)
        if not source.exists():
            raise ConfigError("バックアップ対象の設定ファイルが存在しません")
        
        # バックアップファイル名を生成
        backup_path = f"{config_path}.backup"
        i = 1
        while Path(backup_path).exists():
            backup_path = f"{config_path}.backup{i}"
            i += 1
        
        # バックアップを作成
        try:
            shutil.copy2(source, backup_path)
            return backup_path
        except Exception as e:
            raise ConfigError(f"設定ファイルのバックアップに失敗しました: {e}")

def get_config_path() -> str:
    """設定ファイルのパスを取得"""
    # Windowsの場合
    if os.name == 'nt':
        app_data = os.getenv('APPDATA', '')
        return os.path.join(app_data, 'FileOrganizer', 'config.json')
    # macOSの場合
    elif os.name == 'posix':
        home = os.path.expanduser('~')
        return os.path.join(home, 'Library', 'Application Support', 'FileOrganizer', 'config.json')
    # その他の場合
    else:
        home = os.path.expanduser('~')
        return os.path.join(home, '.fileorganizer', 'config.json')