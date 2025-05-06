"""
GUIモジュール - ユーザーインターフェースを提供
"""

import os
import sys
import threading
import PySimpleGUI as sg
from typing import List, Dict, Any, Optional, Tuple, Callable
from pathlib import Path

from src.config import Config, FileRule, get_config_path
from src.file_operations import FileOperations, FileInfo
from src.utils import get_user_documents_dir, get_file_size_str, setup_logger

# テーマとカラーの設定
THEME_CONFIG = {
    "SystemDefault": {"text_color": None, "background_color": None},
    "DarkBlue": {"text_color": "#FFFFFF", "background_color": "#1B2838"},
    "LightGrey": {"text_color": "#333333", "background_color": "#F0F0F0"},
    "DarkGrey": {"text_color": "#FFFFFF", "background_color": "#333333"},
    "BlueMono": {"text_color": "#AADDFF", "background_color": "#222B33"}
}

# 多言語サポート
TRANSLATIONS = {
    "ja": {
        "app_title": "ファイル管理自動化ツール",
        "tab_organize": "ファイル整理",
        "tab_rules": "ルール設定",
        "tab_settings": "設定",
        "tab_about": "このアプリについて",
        "source_dir": "整理元ディレクトリ",
        "browse": "参照",
        "include_subdirs": "サブディレクトリも含める",
        "create_date_folders": "日付フォルダを作成",
        "handle_duplicates": "重複ファイルを処理",
        "duplicate_action": "重複ファイルの処理方法:",
        "skip": "スキップ",
        "rename": "名前変更",
        "move_to_trash": "ゴミ箱に移動",
        "start_organize": "整理開始",
        "scan_only": "スキャンのみ",
        "status": "状態: ",
        "ready": "準備完了",
        "scanning": "スキャン中...",
        "organizing": "整理中...",
        "complete": "完了",
        "error": "エラー",
        "rule_name": "ルール名",
        "rule_extensions": "拡張子",
        "rule_patterns": "パターン",
        "rule_destination": "保存先",
        "rule_enabled": "有効",
        "add_rule": "ルール追加",
        "edit_rule": "編集",
        "delete_rule": "削除",
        "settings_theme": "テーマ",
        "settings_language": "言語",
        "settings_log_level": "ログレベル",
        "settings_save": "設定保存",
        "settings_reset": "初期設定に戻す",
        "about_title": "ファイル管理自動化ツール",
        "about_version": "バージョン: 0.1.0",
        "about_description": "日常的なファイル整理作業を自動化し、時間を節約するためのツールです。",
        "about_features": "主な機能:\n- 拡張子ベースの自動分類\n- ファイル名パターンによる分類\n- 日付ベースの整理\n- 重複ファイルの検出と処理",
        "confirm": "確認",
        "cancel": "キャンセル",
        "save": "保存",
        "files_found": "ファイルが見つかりました: ",
        "success_count": "成功: ",
        "skipped_count": "スキップ: ",
        "error_count": "エラー: ",
        "log_title": "処理ログ",
        "select_directory": "ディレクトリを選択",
        "rule_dialog_title": "ルール設定",
        "enter_rule_name": "ルール名を入力",
        "enter_extensions": "拡張子を入力（コンマ区切り、例: .jpg,.png）",
        "enter_patterns": "パターンを入力（コンマ区切り、例: report_,invoice_）",
        "enter_destination": "保存先フォルダ名を入力"
    },
    "en": {
        "app_title": "File Management Automation Tool",
        "tab_organize": "Organize Files",
        "tab_rules": "Rules",
        "tab_settings": "Settings",
        "tab_about": "About",
        "source_dir": "Source Directory",
        "browse": "Browse",
        "include_subdirs": "Include Subdirectories",
        "create_date_folders": "Create Date Folders",
        "handle_duplicates": "Handle Duplicate Files",
        "duplicate_action": "Duplicate Action:",
        "skip": "Skip",
        "rename": "Rename",
        "move_to_trash": "Move to Trash",
        "start_organize": "Start Organizing",
        "scan_only": "Scan Only",
        "status": "Status: ",
        "ready": "Ready",
        "scanning": "Scanning...",
        "organizing": "Organizing...",
        "complete": "Complete",
        "error": "Error",
        "rule_name": "Rule Name",
        "rule_extensions": "Extensions",
        "rule_patterns": "Patterns",
        "rule_destination": "Destination",
        "rule_enabled": "Enabled",
        "add_rule": "Add Rule",
        "edit_rule": "Edit",
        "delete_rule": "Delete",
        "settings_theme": "Theme",
        "settings_language": "Language",
        "settings_log_level": "Log Level",
        "settings_save": "Save Settings",
        "settings_reset": "Reset to Default",
        "about_title": "File Management Automation Tool",
        "about_version": "Version: 0.1.0",
        "about_description": "A tool to automate routine file organization tasks and save time.",
        "about_features": "Key Features:\n- Automatic classification by extension\n- Pattern-based file sorting\n- Date-based organization\n- Duplicate file detection and handling",
        "confirm": "Confirm",
        "cancel": "Cancel",
        "save": "Save",
        "files_found": "Files found: ",
        "success_count": "Success: ",
        "skipped_count": "Skipped: ",
        "error_count": "Error: ",
        "log_title": "Processing Log",
        "select_directory": "Select Directory",
        "rule_dialog_title": "Rule Configuration",
        "enter_rule_name": "Enter rule name",
        "enter_extensions": "Enter extensions (comma-separated, e.g.: .jpg,.png)",
        "enter_patterns": "Enter patterns (comma-separated, e.g.: report_,invoice_)",
        "enter_destination": "Enter destination folder name"
    }
}

class FileOrganizerGUI:
    """ファイル管理自動化ツールのGUIクラス"""
    
    def __init__(self):
        """初期化"""
        # 設定ファイルの読み込み
        self.config_path = get_config_path()
        self.config = Config.load(self.config_path)
        
        # ロガーの設定
        setup_logger(level=self.config.log_level)
        
        # 言語設定
        self.lang = self.config.language
        if self.lang not in TRANSLATIONS:
            self.lang = "ja"  # デフォルト言語
        
        # テーマの設定
        if self.config.theme in THEME_CONFIG:
            sg.theme(self.config.theme)
        else:
            sg.theme('SystemDefault')
        
        # 作業用変数の初期化
        self.files = []
        self.scanning_thread = None
        self.organizing_thread = None
        self.is_running = False
        
        # GUIの構築
        self.window = self.create_window()
    
    def create_window(self) -> sg.Window:
        """メインウィンドウを作成"""
        # 翻訳辞書へのショートカット
        t = TRANSLATIONS[self.lang]
        
        # ファイル整理タブ
        organize_layout = [
            [sg.Text(t["source_dir"]), 
             sg.Input(self.config.organize_config.source_dir, key="-SOURCE_DIR-", size=(50, 1)), 
             sg.FolderBrowse(t["browse"])],
            [sg.Checkbox(t["include_subdirs"], default=self.config.organize_config.process_subdirectories, key="-INCLUDE_SUBDIRS-"),
             sg.Checkbox(t["create_date_folders"], default=self.config.organize_config.create_date_folders, key="-CREATE_DATE_FOLDERS-")],
            [sg.Checkbox(t["handle_duplicates"], default=self.config.organize_config.handle_duplicates, key="-HANDLE_DUPLICATES-"),
             sg.Text(t["duplicate_action"]), 
             sg.Combo([t["skip"], t["rename"], t["move_to_trash"]], 
                     default_value=t["skip"] if self.config.organize_config.duplicate_action == "skip" else 
                               t["rename"] if self.config.organize_config.duplicate_action == "rename" else 
                               t["move_to_trash"],
                     key="-DUPLICATE_ACTION-", size=(15, 1))],
            [sg.Button(t["start_organize"], key="-START-"), 
             sg.Button(t["scan_only"], key="-SCAN-")],
            [sg.Text(t["status"] + t["ready"], key="-STATUS-")],
            [sg.Text(t["files_found"] + "0", key="-FILES_FOUND-")],
            [sg.Multiline(size=(80, 15), key="-LOG-", autoscroll=True, disabled=True)],
            [sg.Text(t["success_count"] + "0", key="-SUCCESS-"), 
             sg.Text(t["skipped_count"] + "0", key="-SKIPPED-"), 
             sg.Text(t["error_count"] + "0", key="-ERROR-")]
        ]
        
        # ルール設定タブ
        rules_columns = [
            [sg.Table(
                values=[[rule.name, 
                         ','.join(rule.extensions), 
                         ','.join(rule.patterns), 
                         rule.destination, 
                         "✓" if rule.enabled else ""] 
                        for rule in self.config.file_rules],
                headings=[t["rule_name"], t["rule_extensions"], t["rule_patterns"], 
                          t["rule_destination"], t["rule_enabled"]],
                auto_size_columns=True,
                justification='left',
                key="-RULES_TABLE-",
                enable_events=True,
                select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                num_rows=min(10, len(self.config.file_rules) + 1)
            )]
        ]
        
        rules_layout = [
            [sg.Column(rules_columns, scrollable=True, size=(800, 200))],
            [sg.Button(t["add_rule"], key="-ADD_RULE-"), 
             sg.Button(t["edit_rule"], key="-EDIT_RULE-", disabled=True),
             sg.Button(t["delete_rule"], key="-DELETE_RULE-", disabled=True)]
        ]
        
        # 設定タブ
        settings_layout = [
            [sg.Text(t["settings_theme"]), 
             sg.Combo(list(THEME_CONFIG.keys()), default_value=self.config.theme, key="-THEME-")],
            [sg.Text(t["settings_language"]), 
             sg.Combo(list(TRANSLATIONS.keys()), default_value=self.lang, key="-LANGUAGE-")],
            [sg.Text(t["settings_log_level"]), 
             sg.Combo(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], 
                     default_value=self.config.log_level, key="-LOG_LEVEL-")],
            [sg.Button(t["settings_save"], key="-SAVE_SETTINGS-"), 
             sg.Button(t["settings_reset"], key="-RESET_SETTINGS-")]
        ]
        
        # このアプリについてタブ
        about_layout = [
            [sg.Text(t["about_title"], font=("Helvetica", 16))],
            [sg.Text(t["about_version"])],
            [sg.Text(t["about_description"])],
            [sg.Multiline(t["about_features"], size=(80, 5), disabled=True)]
        ]
        
        # タブレイアウト
        layout = [
            [sg.TabGroup([
                [sg.Tab(t["tab_organize"], organize_layout, key="-TAB_ORGANIZE-"),
                 sg.Tab(t["tab_rules"], rules_layout, key="-TAB_RULES-"),
                 sg.Tab(t["tab_settings"], settings_layout, key="-TAB_SETTINGS-"),
                 sg.Tab(t["tab_about"], about_layout, key="-TAB_ABOUT-")]
            ], key="-TABGROUP-", enable_events=True)]
        ]
        
        # ウィンドウの作成
        return sg.Window(t["app_title"], layout, finalize=True, resizable=True, size=(850, 600))
    
    def run(self) -> None:
        """GUIのイベントループを実行"""
        t = TRANSLATIONS[self.lang]
        
        while True:
            event, values = self.window.read(timeout=100)
            
            if event == sg.WIN_CLOSED:
                break
            
            # ファイル整理タブのイベント
            if event == "-SCAN-":
                self.start_scanning(values)
            
            elif event == "-START-":
                self.start_organizing(values)
            
            # ルール設定タブのイベント
            elif event == "-RULES_TABLE-":
                # テーブル選択時にボタンを有効化
                if len(values["-RULES_TABLE-"]) > 0:
                    self.window["-EDIT_RULE-"].update(disabled=False)
                    self.window["-DELETE_RULE-"].update(disabled=False)
            
            elif event == "-ADD_RULE-":
                self.add_rule()
            
            elif event == "-EDIT_RULE-":
                if len(values["-RULES_TABLE-"]) > 0:
                    selected_index = values["-RULES_TABLE-"][0]
                    self.edit_rule(selected_index)
            
            elif event == "-DELETE_RULE-":
                if len(values["-RULES_TABLE-"]) > 0:
                    selected_index = values["-RULES_TABLE-"][0]
                    self.delete_rule(selected_index)
            
            # 設定タブのイベント
            elif event == "-SAVE_SETTINGS-":
                self.save_settings(values)
            
            elif event == "-RESET_SETTINGS-":
                self.reset_settings()
            
            # タブ切り替えのイベント
            elif event == "-TABGROUP-":
                # タブ切り替え時のイベント処理
                pass
            
            # 進行中の処理を確認
            self.check_running_tasks()
        
        # ウィンドウを閉じる
        self.window.close()
    
    def start_scanning(self, values: Dict[str, Any]) -> None:
        """スキャン処理を開始"""
        if self.is_running:
            return
        
        source_dir = values["-SOURCE_DIR-"]
        if not source_dir or not os.path.isdir(source_dir):
            sg.popup_error("有効なディレクトリを選択してください")
            return
        
        include_subdirs = values["-INCLUDE_SUBDIRS-"]
        
        # ステータス更新
        t = TRANSLATIONS[self.lang]
        self.window["-STATUS-"].update(t["status"] + t["scanning"])
        self.window["-LOG-"].update("")
        self.window["-FILES_FOUND-"].update(t["files_found"] + "0")
        
        # フラグ設定
        self.is_running = True
        
        # スキャン処理をスレッドで実行
        self.scanning_thread = threading.Thread(
            target=self.scan_task,
            args=(source_dir, include_subdirs)
        )
        self.scanning_thread.daemon = True
        self.scanning_thread.start()
    
    def scan_task(self, source_dir: str, include_subdirs: bool) -> None:
        """スキャン処理を実行するタスク"""
        try:
            self.files = FileOperations.scan_directory(source_dir, include_subdirs)
            
            # UIの更新はメインスレッドで行う
            sg.cprint(f"{len(self.files)}個のファイルが見つかりました", key="-LOG-")
            
        except Exception as e:
            sg.cprint(f"エラー: {str(e)}", key="-LOG-")
        finally:
            self.is_running = False
    
    def start_organizing(self, values: Dict[str, Any]) -> None:
        """ファイル整理処理を開始"""
        if self.is_running:
            return
        
        source_dir = values["-SOURCE_DIR-"]
        if not source_dir or not os.path.isdir(source_dir):
            sg.popup_error("有効なディレクトリを選択してください")
            return
        
        include_subdirs = values["-INCLUDE_SUBDIRS-"]
        create_date_folders = values["-CREATE_DATE_FOLDERS-"]
        handle_duplicates = values["-HANDLE_DUPLICATES-"]
        
        t = TRANSLATIONS[self.lang]
        duplicate_action_text = values["-DUPLICATE_ACTION-"]
        duplicate_action = "skip"
        if duplicate_action_text == t["rename"]:
            duplicate_action = "rename"
        elif duplicate_action_text == t["move_to_trash"]:
            duplicate_action = "move_to_trash"
        
        # 設定の更新
        self.config.organize_config.source_dir = source_dir
        self.config.organize_config.process_subdirectories = include_subdirs
        self.config.organize_config.create_date_folders = create_date_folders
        self.config.organize_config.handle_duplicates = handle_duplicates
        self.config.organize_config.duplicate_action = duplicate_action
        self.config.save(self.config_path)
        
        # ログのクリア
        self.window["-LOG-"].update("")
        self.window["-SUCCESS-"].update(t["success_count"] + "0")
        self.window["-SKIPPED-"].update(t["skipped_count"] + "0")
        self.window["-ERROR-"].update(t["error_count"] + "0")
        
        # ステータス更新
        self.window["-STATUS-"].update(t["status"] + t["organizing"])
        
        # フラグ設定
        self.is_running = True
        
        # スキャンが必要な場合
        if not self.files:
            sg.cprint("ファイルをスキャンしています...", key="-LOG-")
            self.files = FileOperations.scan_directory(source_dir, include_subdirs)
        
        # 整理処理をスレッドで実行
        self.organizing_thread = threading.Thread(
            target=self.organize_task,
            args=(source_dir, create_date_folders, handle_duplicates, duplicate_action)
        )
        self.organizing_thread.daemon = True
        self.organizing_thread.start()
    
    def organize_task(self, base_dir: str, create_date_folders: bool, 
                      handle_duplicates: bool, duplicate_action: str) -> None:
        """整理処理を実行するタスク"""
        try:
            result = FileOperations.organize_files(
                self.files, 
                self.config.file_rules, 
                base_dir, 
                create_date_folders, 
                handle_duplicates, 
                duplicate_action
            )
            
            # UIの更新
            t = TRANSLATIONS[self.lang]
            success_count = len(result["success"])
            skipped_count = len(result["skipped"])
            error_count = len(result["error"])
            
            # 個別のログ出力
            for msg in result["success"]:
                sg.cprint("✓ " + msg, key="-LOG-", text_color="green")
            
            for msg in result["skipped"]:
                sg.cprint("- " + msg, key="-LOG-", text_color="blue")
            
            for msg in result["error"]:
                sg.cprint("✗ " + msg, key="-LOG-", text_color="red")
            
            # カウンター更新
            self.window["-SUCCESS-"].update(t["success_count"] + str(success_count))
            self.window["-SKIPPED-"].update(t["skipped_count"] + str(skipped_count))
            self.window["-ERROR-"].update(t["error_count"] + str(error_count))
            
            # ファイルリストをクリア（処理済み）
            self.files = []
            
        except Exception as e:
            sg.cprint(f"エラー: {str(e)}", key="-LOG-", text_color="red")
        finally:
            # 完了ステータスの更新
            t = TRANSLATIONS[self.lang]
            self.window["-STATUS-"].update(t["status"] + t["complete"])
            self.is_running = False
    
    def add_rule(self) -> None:
        """新しいルールを追加"""
        t = TRANSLATIONS[self.lang]
        
        layout = [
            [sg.Text(t["enter_rule_name"])],
            [sg.Input(key="-RULE_NAME-")],
            [sg.Text(t["enter_extensions"])],
            [sg.Input(key="-RULE_EXTENSIONS-")],
            [sg.Text(t["enter_patterns"])],
            [sg.Input(key="-RULE_PATTERNS-")],
            [sg.Text(t["enter_destination"])],
            [sg.Input(key="-RULE_DESTINATION-")],
            [sg.Checkbox(t["rule_enabled"], default=True, key="-RULE_ENABLED-")],
            [sg.Button(t["save"], key="-SAVE_RULE-"), sg.Button(t["cancel"], key="-CANCEL_RULE-")]
        ]
        
        window = sg.Window(t["rule_dialog_title"], layout, modal=True)
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, "-CANCEL_RULE-"):
                break
            
            if event == "-SAVE_RULE-":
                # 入力値の検証
                rule_name = values["-RULE_NAME-"].strip()
                if not rule_name:
                    sg.popup_error("ルール名を入力してください")
                    continue
                
                # 拡張子の処理
                extensions_text = values["-RULE_EXTENSIONS-"].strip()
                extensions = []
                if extensions_text:
                    extensions = [ext.strip() for ext in extensions_text.split(",")]
                    # 拡張子の先頭にドットがない場合は追加
                    extensions = [ext if ext.startswith(".") else "." + ext for ext in extensions]
                
                # パターンの処理
                patterns_text = values["-RULE_PATTERNS-"].strip()
                patterns = []
                if patterns_text:
                    patterns = [pat.strip() for pat in patterns_text.split(",")]
                
                # 保存先の処理
                destination = values["-RULE_DESTINATION-"].strip()
                if not destination:
                    destination = rule_name
                
                # 新しいルールの作成
                new_rule = FileRule(
                    name=rule_name,
                    extensions=extensions,
                    patterns=patterns,
                    destination=destination,
                    enabled=values["-RULE_ENABLED-"]
                )
                
                # ルールリストに追加
                self.config.file_rules.append(new_rule)
                self.config.save(self.config_path)
                
                # テーブルの更新
                self.update_rules_table()
                break
        
        window.close()
    
    def edit_rule(self, rule_index: int) -> None:
        """既存のルールを編集"""
        if rule_index < 0 or rule_index >= len(self.config.file_rules):
            return
        
        rule = self.config.file_rules[rule_index]
        t = TRANSLATIONS[self.lang]
        
        layout = [
            [sg.Text(t["enter_rule_name"])],
            [sg.Input(rule.name, key="-RULE_NAME-")],
            [sg.Text(t["enter_extensions"])],
            [sg.Input(','.join(rule.extensions), key="-RULE_EXTENSIONS-")],
            [sg.Text(t["enter_patterns"])],
            [sg.Input(','.join(rule.patterns), key="-RULE_PATTERNS-")],
            [sg.Text(t["enter_destination"])],
            [sg.Input(rule.destination, key="-RULE_DESTINATION-")],
            [sg.Checkbox(t["rule_enabled"], default=rule.enabled, key="-RULE_ENABLED-")],
            [sg.Button(t["save"], key="-SAVE_RULE-"), sg.Button(t["cancel"], key="-CANCEL_RULE-")]
        ]
        
        window = sg.Window(t["rule_dialog_title"], layout, modal=True)
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, "-CANCEL_RULE-"):
                break
            
            if event == "-SAVE_RULE-":
                # 入力値の検証
                rule_name = values["-RULE_NAME-"].strip()
                if not rule_name:
                    sg.popup_error("ルール名を入力してください")
                    continue
                
                # 拡張子の処理
                extensions_text = values["-RULE_EXTENSIONS-"].strip()
                extensions = []
                if extensions_text:
                    extensions = [ext.strip() for ext in extensions_text.split(",")]
                    # 拡張子の先頭にドットがない場合は追加
                    extensions = [ext if ext.startswith(".") else "." + ext for ext in extensions]
                
                # パターンの処理
                patterns_text = values["-RULE_PATTERNS-"].strip()
                patterns = []
                if patterns_text:
                    patterns = [pat.strip() for pat in patterns_text.split(",")]
                
                # 保存先の処理
                destination = values["-RULE_DESTINATION-"].strip()
                if not destination:
                    destination = rule_name
                
                # ルールの更新
                rule.name = rule_name
                rule.extensions = extensions
                rule.patterns = patterns
                rule.destination = destination
                rule.enabled = values["-RULE_ENABLED-"]
                
                # 設定の保存
                self.config.save(self.config_path)
                
                # テーブルの更新
                self.update_rules_table()
                break
        
        window.close()
    
    def delete_rule(self, rule_index: int) -> None:
        """ルールを削除"""
        if rule_index < 0 or rule_index >= len(self.config.file_rules):
            return
        
        rule = self.config.file_rules[rule_index]
        t = TRANSLATIONS[self.lang]
        
        # 削除確認
        if sg.popup_yes_no(f"ルール「{rule.name}」を削除しますか？", title=t["confirm"]) == "Yes":
            del self.config.file_rules[rule_index]
            self.config.save(self.config_path)
            self.update_rules_table()
            
            # 選択解除のためボタンを無効化
            self.window["-EDIT_RULE-"].update(disabled=True)
            self.window["-DELETE_RULE-"].update(disabled=True)
    
    def update_rules_table(self) -> None:
        """ルールテーブルを更新"""
        t = TRANSLATIONS[self.lang]
        
        self.window["-RULES_TABLE-"].update(
            values=[[rule.name, 
                     ','.join(rule.extensions), 
                     ','.join(rule.patterns), 
                     rule.destination, 
                     "✓" if rule.enabled else ""] 
                    for rule in self.config.file_rules]
        )
    
    def save_settings(self, values: Dict[str, Any]) -> None:
        """設定を保存"""
        # 現在の設定を保存
        old_lang = self.lang
        old_theme = self.config.theme
        
        # 新しい設定を適用
        self.config.theme = values["-THEME-"]
        self.config.language = values["-LANGUAGE-"]
        self.config.log_level = values["-LOG_LEVEL-"]
        
        # 設定を保存
        self.config.save(self.config_path)
        
        # 言語または外観が変更された場合、再起動が必要
        if old_lang != self.config.language or old_theme != self.config.theme:
            t = TRANSLATIONS[self.lang]
            sg.popup("設定を適用するには、アプリケーションを再起動してください。", title=t["confirm"])
        else:
            # ロガーの設定を更新
            setup_logger(level=self.config.log_level)
            
            t = TRANSLATIONS[self.lang]
            sg.popup("設定を保存しました。", title=t["confirm"])
    
    def reset_settings(self) -> None:
        """設定をデフォルトに戻す"""
        t = TRANSLATIONS[self.lang]
        
        if sg.popup_yes_no("設定をデフォルトに戻しますか？", title=t["confirm"]) == "Yes":
            # バックアップを作成
            try:
                backup_path = self.config.backup(self.config_path)
                sg.popup(f"現在の設定のバックアップを作成しました: {backup_path}", title=t["confirm"])
            except Exception as e:
                sg.popup_error(f"バックアップの作成に失敗しました: {e}")
            
            # 新しい設定を作成
            self.config = Config()
            self.config.save(self.config_path)
            
            # UIを更新
            sg.popup("設定をデフォルトに戻しました。アプリケーションを再起動してください。", title=t["confirm"])
    
    def check_running_tasks(self) -> None:
        """実行中のタスクをチェック"""
        t = TRANSLATIONS[self.lang]
        
        # スキャンタスクのチェック
        if self.scanning_thread and not self.scanning_thread.is_alive() and self.is_running:
            self.is_running = False
            self.window["-STATUS-"].update(t["status"] + t["complete"])
            self.window["-FILES_FOUND-"].update(t["files_found"] + str(len(self.files)))
            self.scanning_thread = None
        
        # 整理タスクのチェック
        if self.organizing_thread and not self.organizing_thread.is_alive() and self.is_running:
            self.is_running = False
            self.window["-STATUS-"].update(t["status"] + t["complete"])
            self.organizing_thread = None