"""
GUIモジュール - PySide6によるユーザーインターフェースを提供
"""

import os
import sys
import threading
from typing import List, Dict, Any, Optional, Tuple, Callable
from pathlib import Path

from PySide6.QtCore import Qt, QSize, Signal, Slot, QThread, QTimer, QMimeData
from PySide6.QtGui import QIcon, QPixmap, QDragEnterEvent, QDropEvent, QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QCheckBox, QComboBox, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit, QMessageBox,
    QDialog, QFormLayout, QGroupBox, QRadioButton, QSplitter, QListWidget,
    QListWidgetItem, QProgressBar, QMenu, QSystemTrayIcon, QToolBar, QStatusBar,
    QSpacerItem, QSizePolicy,QStyle
)

from src.config import Config, FileRule, get_config_path, OrganizeConfig
from src.file_operations import FileOperations, FileInfo
from src.utils import get_user_documents_dir, get_file_size_str, setup_logger

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
        "enter_destination": "保存先フォルダ名を入力",
        "drag_drop_hint": "ファイルやフォルダをドラッグ＆ドロップできます",
        "preview": "プレビュー",
        "file_info": "ファイル情報",
        "file_count": "ファイル数",
        "close": "閉じる",
        "minimize_to_tray": "トレイに最小化",
        "restore": "復元",
        "exit": "終了",
        "app_running": "アプリケーションはバックグラウンドで実行中です",
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
        "enter_destination": "Enter destination folder name",
        "drag_drop_hint": "Drag and drop files or folders here",
        "preview": "Preview",
        "file_info": "File Information",
        "file_count": "File Count",
        "close": "Close",
        "minimize_to_tray": "Minimize to Tray",
        "restore": "Restore",
        "exit": "Exit",
        "app_running": "Application is running in the background",
    }
}

# テーマとQSSマッピング
THEMES = {
    "System": "",  # システムデフォルト
    "Light": """
        QWidget {
            background-color: #f0f0f0;
            color: #333333;
        }
        QTabWidget::pane {
            border: 1px solid #c0c0c0;
            background-color: #f8f8f8;
        }
        QTabBar::tab {
            background-color: #e0e0e0;
            padding: 8px 12px;
            margin-right: 2px;
            border: 1px solid #c0c0c0;
            border-bottom: 0px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #f8f8f8;
        }
        QPushButton {
            background-color: #e0e0e0;
            border: 1px solid #c0c0c0;
            padding: 5px 10px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #d0d0d0;
        }
        QPushButton:pressed {
            background-color: #c0c0c0;
        }
        QLineEdit, QTextEdit, QComboBox {
            border: 1px solid #c0c0c0;
            background-color: white;
            padding: 3px;
            border-radius: 2px;
        }
    """,
    "Dark": """
        QWidget {
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        QTabWidget::pane {
            border: 1px solid #555555;
            background-color: #353535;
        }
        QTabBar::tab {
            background-color: #3d3d3d;
            padding: 8px 12px;
            margin-right: 2px;
            border: 1px solid #555555;
            border-bottom: 0px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #353535;
        }
        QPushButton {
            background-color: #4d4d4d;
            border: 1px solid #555555;
            padding: 5px 10px;
            border-radius: 3px;
            color: #e0e0e0;
        }
        QPushButton:hover {
            background-color: #5d5d5d;
        }
        QPushButton:pressed {
            background-color: #3d3d3d;
        }
        QLineEdit, QTextEdit, QComboBox {
            border: 1px solid #555555;
            background-color: #404040;
            color: #e0e0e0;
            padding: 3px;
            border-radius: 2px;
        }
        QTableWidget {
            background-color: #353535;
            color: #e0e0e0;
            gridline-color: #555555;
        }
        QTableWidget::item:selected {
            background-color: #4a6db5;
        }
        QHeaderView::section {
            background-color: #404040;
            color: #e0e0e0;
            padding: 5px;
            border: 1px solid #555555;
        }
    """,
    "Blue": """
        QWidget {
            background-color: #f0f8ff;
            color: #333333;
        }
        QTabWidget::pane {
            border: 1px solid #a0c0e0;
            background-color: #f8faff;
        }
        QTabBar::tab {
            background-color: #d0e0f0;
            padding: 8px 12px;
            margin-right: 2px;
            border: 1px solid #a0c0e0;
            border-bottom: 0px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #f8faff;
        }
        QPushButton {
            background-color: #d0e0f0;
            border: 1px solid #a0c0e0;
            padding: 5px 10px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #c0d0e0;
        }
        QPushButton:pressed {
            background-color: #b0c0d0;
        }
        QLineEdit, QTextEdit, QComboBox {
            border: 1px solid #a0c0e0;
            background-color: white;
            padding: 3px;
            border-radius: 2px;
        }
    """
}

# ワーカースレッドクラス
class Worker(QThread):
    """バックグラウンド処理を行うワーカースレッド"""
    # 汎用的なシグナル
    started = Signal()
    finished = Signal(object)
    progress = Signal(int)
    log = Signal(str, str)  # メッセージ, カラー
    error = Signal(str)

    def __init__(self, task_func, *args, **kwargs):
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        self.result = None

    def run(self):
        """スレッド実行"""
        self.started.emit()
        try:
            self.result = self.task_func(*self.args, **self.kwargs)
            self.finished.emit(self.result)
        except Exception as e:
            self.error.emit(str(e))

# ドラッグ＆ドロップ対応のウィジェット
class DropArea(QWidget):
    """ファイルのドラッグ＆ドロップを受け付けるエリア"""
    fileDropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        
        # レイアウト設定
        layout = QVBoxLayout(self)
        
        # ドロップ領域のラベル
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumHeight(100)
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaaaaa;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        layout.addWidget(self.label)
        self.setLayout(layout)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """ドラッグ進入イベント"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.label.setStyleSheet("""
                QLabel {
                    border: 2px dashed #3498db;
                    border-radius: 5px;
                    background-color: rgba(52, 152, 219, 0.1);
                    padding: 10px;
                }
            """)

    def dragLeaveEvent(self, event):
        """ドラッグ離脱イベント"""
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaaaaa;
                border-radius: 5px;
                padding: 10px;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        """ドロップイベント"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isdir(path):
                    self.fileDropped.emit(path)
                    break
            
            # スタイルをリセット
            self.label.setStyleSheet("""
                QLabel {
                    border: 2px dashed #aaaaaa;
                    border-radius: 5px;
                    padding: 10px;
                }
            """)

# ルール編集ダイアログ
class RuleDialog(QDialog):
    """ルール追加・編集用ダイアログ"""
    def __init__(self, parent=None, rule=None, lang="ja"):
        super().__init__(parent)
        self.rule = rule
        self.t = TRANSLATIONS[lang]
        
        self.setWindowTitle(self.t["rule_dialog_title"])
        self.resize(400, 300)
        
        self.setup_ui()
        
        if rule:
            # 既存ルールの編集モード
            self.fill_form_with_rule(rule)

    def setup_ui(self):
        """UIセットアップ"""
        layout = QVBoxLayout()
        
        # フォーム部分
        form_layout = QFormLayout()
        
        # ルール名
        self.name_edit = QLineEdit()
        form_layout.addRow(self.t["enter_rule_name"], self.name_edit)
        
        # 拡張子
        self.extensions_edit = QLineEdit()
        form_layout.addRow(self.t["enter_extensions"], self.extensions_edit)
        
        # パターン
        self.patterns_edit = QLineEdit()
        form_layout.addRow(self.t["enter_patterns"], self.patterns_edit)
        
        # 保存先
        self.destination_edit = QLineEdit()
        form_layout.addRow(self.t["enter_destination"], self.destination_edit)
        
        # 有効/無効
        self.enabled_check = QCheckBox(self.t["rule_enabled"])
        self.enabled_check.setChecked(True)
        
        # レイアウトに追加
        layout.addLayout(form_layout)
        layout.addWidget(self.enabled_check)
        
        # ボタン
        button_layout = QHBoxLayout()
        self.save_button = QPushButton(self.t["save"])
        self.cancel_button = QPushButton(self.t["cancel"])
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # シグナル接続
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        # 名前が入力されたら保存先も自動設定
        self.name_edit.textChanged.connect(self.auto_set_destination)

    def auto_set_destination(self, text):
        """ルール名から保存先を自動設定"""
        if not self.destination_edit.text() and text:
            self.destination_edit.setText(text)

    def fill_form_with_rule(self, rule):
        """既存ルールの情報をフォームに設定"""
        self.name_edit.setText(rule.name)
        self.extensions_edit.setText(','.join(rule.extensions))
        self.patterns_edit.setText(','.join(rule.patterns))
        self.destination_edit.setText(rule.destination)
        self.enabled_check.setChecked(rule.enabled)

    def get_rule_data(self):
        """フォームからルールデータを取得"""
        name = self.name_edit.text().strip()
        
        # 拡張子の処理
        extensions_text = self.extensions_edit.text().strip()
        extensions = []
        if extensions_text:
            extensions = [ext.strip() for ext in extensions_text.split(",")]
            # 拡張子の先頭にドットがない場合は追加
            extensions = [ext if ext.startswith(".") else "." + ext for ext in extensions]
        
        # パターンの処理
        patterns_text = self.patterns_edit.text().strip()
        patterns = []
        if patterns_text:
            patterns = [pat.strip() for pat in patterns_text.split(",")]
        
        # 保存先の処理
        destination = self.destination_edit.text().strip()
        if not destination:
            destination = name
        
        return {
            "name": name,
            "extensions": extensions,
            "patterns": patterns,
            "destination": destination,
            "enabled": self.enabled_check.isChecked()
        }
    
    def validate(self):
        """入力の検証"""
        rule_data = self.get_rule_data()
        
        if not rule_data["name"]:
            QMessageBox.warning(self, self.t["error"], "ルール名を入力してください")
            return False
        
        if not rule_data["extensions"] and not rule_data["patterns"]:
            QMessageBox.warning(self, self.t["error"], "拡張子またはパターンを少なくとも1つ指定してください")
            return False
        
        return True
    
    def accept(self):
        """OKボタン押下時の処理"""
        if self.validate():
            super().accept()
        
# メインウィンドウクラス
class FileOrganizerApp(QMainWindow):
    """ファイル管理自動化ツールのメインウィンドウ"""
    
    def __init__(self):
        super().__init__()
        
        # 設定ファイルの読み込み
        self.config_path = get_config_path()
        self.config = Config.load(self.config_path)
        
        # ロガーの設定
        setup_logger(level=self.config.log_level)
        
        # 言語設定
        self.lang = self.config.language
        if self.lang not in TRANSLATIONS:
            self.lang = "ja"  # デフォルト言語
        
        # 翻訳辞書へのショートカット
        self.t = TRANSLATIONS[self.lang]
        
        # 作業用変数の初期化
        self.files = []
        self.workers = {}
        self.is_running = False
        
        # UIの構築
        self.setup_ui()
        
        # テーマの適用
        self.apply_theme(self.config.theme)
        
        # システムトレイの設定
        self.setup_tray_icon()

    def setup_ui(self):
        """UIの初期化と構築"""
        # ウィンドウの設定
        self.setWindowTitle(self.t["app_title"])
        self.resize(900, 700)
        
        # メインウィジェットとレイアウト
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # 各タブの作成
        self.create_organize_tab()
        self.create_rules_tab()
        self.create_settings_tab()
        self.create_about_tab()
        
        # ステータスバーの設定
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel(self.t["status"] + self.t["ready"])
        self.status_bar.addWidget(self.status_label)

    def create_organize_tab(self):
        """ファイル整理タブの作成"""
        organize_widget = QWidget()
        organize_layout = QVBoxLayout(organize_widget)
        
        # 上部の入力エリア
        input_layout = QVBoxLayout()
        
        # ソースディレクトリの選択
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel(self.t["source_dir"]))
        self.source_dir_edit = QLineEdit(self.config.organize_config.source_dir)
        source_layout.addWidget(self.source_dir_edit, 1)
        
        self.browse_button = QPushButton(self.t["browse"])
        self.browse_button.clicked.connect(self.browse_source_dir)
        source_layout.addWidget(self.browse_button)
        
        input_layout.addLayout(source_layout)
        
        # ドラッグ＆ドロップエリア
        self.drop_area = DropArea()
        self.drop_area.label.setText(self.t["drag_drop_hint"])
        self.drop_area.fileDropped.connect(self.set_source_dir)
        input_layout.addWidget(self.drop_area)
        
        # オプション設定
        options_layout = QHBoxLayout()
        
        self.include_subdirs_check = QCheckBox(self.t["include_subdirs"])
        self.include_subdirs_check.setChecked(self.config.organize_config.process_subdirectories)
        options_layout.addWidget(self.include_subdirs_check)
        
        self.create_date_folders_check = QCheckBox(self.t["create_date_folders"])
        self.create_date_folders_check.setChecked(self.config.organize_config.create_date_folders)
        options_layout.addWidget(self.create_date_folders_check)
        
        self.handle_duplicates_check = QCheckBox(self.t["handle_duplicates"])
        self.handle_duplicates_check.setChecked(self.config.organize_config.handle_duplicates)
        options_layout.addWidget(self.handle_duplicates_check)
        
        input_layout.addLayout(options_layout)
        
        # 重複処理オプション
        duplicate_layout = QHBoxLayout()
        duplicate_layout.addWidget(QLabel(self.t["duplicate_action"]))
        
        self.duplicate_combo = QComboBox()
        self.duplicate_combo.addItems([self.t["skip"], self.t["rename"], self.t["move_to_trash"]])
        
        # 現在の設定値を選択
        current_action = self.config.organize_config.duplicate_action
        if current_action == "skip":
            self.duplicate_combo.setCurrentText(self.t["skip"])
        elif current_action == "rename":
            self.duplicate_combo.setCurrentText(self.t["rename"])
        elif current_action == "move_to_trash":
            self.duplicate_combo.setCurrentText(self.t["move_to_trash"])
        
        duplicate_layout.addWidget(self.duplicate_combo)
        duplicate_layout.addStretch(1)
        
        input_layout.addLayout(duplicate_layout)
        
        # ボタン
        buttons_layout = QHBoxLayout()
        
        self.start_button = QPushButton(self.t["start_organize"])
        self.start_button.clicked.connect(self.start_organizing)
        buttons_layout.addWidget(self.start_button)
        
        self.scan_button = QPushButton(self.t["scan_only"])
        self.scan_button.clicked.connect(self.start_scanning)
        buttons_layout.addWidget(self.scan_button)
        
        buttons_layout.addStretch(1)
        
        input_layout.addLayout(buttons_layout)
        
        # 情報表示エリア
        info_layout = QHBoxLayout()
        
        self.files_found_label = QLabel(self.t["files_found"] + "0")
        info_layout.addWidget(self.files_found_label)
        
        info_layout.addStretch(1)
        
        self.success_label = QLabel(self.t["success_count"] + "0")
        info_layout.addWidget(self.success_label)
        
        self.skipped_label = QLabel(self.t["skipped_count"] + "0")
        info_layout.addWidget(self.skipped_label)
        
        self.error_label = QLabel(self.t["error_count"] + "0")
        info_layout.addWidget(self.error_label)
        
        input_layout.addLayout(info_layout)
        
        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        input_layout.addWidget(self.progress_bar)
        
        organize_layout.addLayout(input_layout)
        
        # ログとプレビューのスプリッター
        splitter = QSplitter(Qt.Vertical)
        
        # ログエリア
        log_group = QGroupBox(self.t["log_title"])
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        splitter.addWidget(log_group)
        
        # プレビューエリア
        preview_group = QGroupBox(self.t["preview"])
        preview_layout = QHBoxLayout(preview_group)
        
        # ファイルリスト
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.show_file_preview)
        preview_layout.addWidget(self.file_list, 2)
        
        # プレビュー/情報
        preview_info_layout = QVBoxLayout()
        
        # ファイル情報
        self.file_info_label = QLabel(self.t["file_info"])
        preview_info_layout.addWidget(self.file_info_label)
        
        # ファイルプレビュー
        self.preview_area = QLabel()
        self.preview_area.setAlignment(Qt.AlignCenter)
        self.preview_area.setMinimumSize(QSize(200, 200))
        self.preview_area.setStyleSheet("background-color: #f0f0f0; border: 1px solid #d0d0d0;")
        preview_info_layout.addWidget(self.preview_area)
        
        preview_layout.addLayout(preview_info_layout, 3)
        
        splitter.addWidget(preview_group)
        
        # スプリッターの設定
        splitter.setSizes([200, 200])
        
        organize_layout.addWidget(splitter)
        
        self.tab_widget.addTab(organize_widget, self.t["tab_organize"])

    def create_rules_tab(self):
        """ルール設定タブの作成"""
        rules_widget = QWidget()
        rules_layout = QVBoxLayout(rules_widget)
        
        # ルールテーブル
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(5)
        self.rules_table.setHorizontalHeaderLabels([
            self.t["rule_name"],
            self.t["rule_extensions"],
            self.t["rule_patterns"],
            self.t["rule_destination"],
            self.t["rule_enabled"]
        ])
        
        # テーブルの設定
        self.rules_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.rules_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.rules_table.setSelectionMode(QTableWidget.SingleSelection)
        self.rules_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.rules_table.setAlternatingRowColors(True)
        
        # ルールデータの設定
        self.update_rules_table()
        
        rules_layout.addWidget(self.rules_table)
        
        # ボタン
        buttons_layout = QHBoxLayout()
        
        self.add_rule_button = QPushButton(self.t["add_rule"])
        self.add_rule_button.clicked.connect(self.add_rule)
        buttons_layout.addWidget(self.add_rule_button)
        
        self.edit_rule_button = QPushButton(self.t["edit_rule"])
        self.edit_rule_button.clicked.connect(self.edit_rule)
        self.edit_rule_button.setEnabled(False)
        buttons_layout.addWidget(self.edit_rule_button)
        
        self.delete_rule_button = QPushButton(self.t["delete_rule"])
        self.delete_rule_button.clicked.connect(self.delete_rule)
        self.delete_rule_button.setEnabled(False)
        buttons_layout.addWidget(self.delete_rule_button)
        
        buttons_layout.addStretch(1)
        
        rules_layout.addLayout(buttons_layout)
        
        # シグナル接続
        self.rules_table.itemSelectionChanged.connect(self.on_rule_selection_changed)
        
        self.tab_widget.addTab(rules_widget, self.t["tab_rules"])

    def create_settings_tab(self):
        """設定タブの作成"""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        form_layout = QFormLayout()
        
        # テーマ設定
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(THEMES.keys()))
        self.theme_combo.setCurrentText(self.config.theme if self.config.theme in THEMES else "System")
        form_layout.addRow(self.t["settings_theme"], self.theme_combo)
        
        # 言語設定
        self.language_combo = QComboBox()
        self.language_combo.addItems(list(TRANSLATIONS.keys()))
        self.language_combo.setCurrentText(self.lang)
        form_layout.addRow(self.t["settings_language"], self.language_combo)
        
        # ログレベル設定
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.setCurrentText(self.config.log_level)
        form_layout.addRow(self.t["settings_log_level"], self.log_level_combo)
        
        settings_layout.addLayout(form_layout)
        
        # ボタン
        buttons_layout = QHBoxLayout()
        
        self.save_settings_button = QPushButton(self.t["settings_save"])
        self.save_settings_button.clicked.connect(self.save_settings)
        buttons_layout.addWidget(self.save_settings_button)
        
        self.reset_settings_button = QPushButton(self.t["settings_reset"])
        self.reset_settings_button.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(self.reset_settings_button)
        
        buttons_layout.addStretch(1)
        
        settings_layout.addLayout(buttons_layout)
        settings_layout.addStretch(1)
        
        self.tab_widget.addTab(settings_widget, self.t["tab_settings"])

    def create_about_tab(self):
        """このアプリについてタブの作成"""
        about_widget = QWidget()
        about_layout = QVBoxLayout(about_widget)
        
        # タイトル
        title_label = QLabel(self.t["about_title"])
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        about_layout.addWidget(title_label)
        
        # バージョン
        version_label = QLabel(self.t["about_version"])
        version_label.setAlignment(Qt.AlignCenter)
        about_layout.addWidget(version_label)
        
        # 説明
        description_label = QLabel(self.t["about_description"])
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)
        about_layout.addWidget(description_label)
        
        # 機能
        features_text = QTextEdit()
        features_text.setReadOnly(True)
        features_text.setPlainText(self.t["about_features"])
        about_layout.addWidget(features_text)
        
        about_layout.addStretch(1)
        
        self.tab_widget.addTab(about_widget, self.t["tab_about"])

    def setup_tray_icon(self):
        """システムトレイアイコンの設定"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # アイコンの設定（実際のアプリではリソースからアイコンを読み込む）
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        # トレイメニューの作成
        tray_menu = QMenu()
        
        restore_action = QAction(self.t["restore"], self)
        restore_action.triggered.connect(self.showNormal)
        tray_menu.addAction(restore_action)
        
        tray_menu.addSeparator()
        
        exit_action = QAction(self.t["exit"], self)
        exit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        
        # ダブルクリックでウィンドウを表示
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        
        # トレイアイコンを表示
        self.tray_icon.show()

    def on_tray_icon_activated(self, reason):
        """トレイアイコンがアクティブ化された時の処理"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isHidden():
                self.showNormal()
            else:
                self.hide()

    def closeEvent(self, event):
        """ウィンドウを閉じる時の処理"""
        # トレイに最小化するか終了するか選択
        if self.tray_icon.isVisible():
            QMessageBox.information(self, self.t["app_title"],
                              self.t["app_running"])
            self.hide()
            event.ignore()
        else:
            event.accept()

    def apply_theme(self, theme_name):
        """テーマの適用"""
        if theme_name in THEMES:
            self.setStyleSheet(THEMES[theme_name])
        else:
            self.setStyleSheet(THEMES["System"])  # デフォルトテーマ

    def browse_source_dir(self):
        """ソースディレクトリを参照"""
        dir_path = QFileDialog.getExistingDirectory(
            self, 
            self.t["select_directory"],
            self.source_dir_edit.text() or get_user_documents_dir()
        )
        
        if dir_path:
            self.set_source_dir(dir_path)

    def set_source_dir(self, dir_path):
        """ソースディレクトリを設定"""
        self.source_dir_edit.setText(dir_path)
        
        # ドロップエリアのテキスト更新
        self.drop_area.label.setText(f"{self.t['drag_drop_hint']}\n{os.path.basename(dir_path)}")

    def update_rules_table(self):
        """ルールテーブルの更新"""
        self.rules_table.setRowCount(0)
        
        for i, rule in enumerate(self.config.file_rules):
            self.rules_table.insertRow(i)
            
            # ルール名
            self.rules_table.setItem(i, 0, QTableWidgetItem(rule.name))
            
            # 拡張子
            self.rules_table.setItem(i, 1, QTableWidgetItem(','.join(rule.extensions)))
            
            # パターン
            self.rules_table.setItem(i, 2, QTableWidgetItem(','.join(rule.patterns)))
            
            # 保存先
            self.rules_table.setItem(i, 3, QTableWidgetItem(rule.destination))
            
            # 有効/無効
            enabled_item = QTableWidgetItem("✓" if rule.enabled else "")
            enabled_item.setTextAlignment(Qt.AlignCenter)
            self.rules_table.setItem(i, 4, enabled_item)

    def on_rule_selection_changed(self):
        """ルール選択時の処理"""
        selected_rows = self.rules_table.selectionModel().selectedRows()
        
        if selected_rows:
            self.edit_rule_button.setEnabled(True)
            self.delete_rule_button.setEnabled(True)
        else:
            self.edit_rule_button.setEnabled(False)
            self.delete_rule_button.setEnabled(False)

    def add_rule(self):
        """新しいルールを追加"""
        dialog = RuleDialog(self, lang=self.lang)
        
        if dialog.exec_():
            rule_data = dialog.get_rule_data()
            
            # 新しいルールの作成
            new_rule = FileRule(
                name=rule_data["name"],
                extensions=rule_data["extensions"],
                patterns=rule_data["patterns"],
                destination=rule_data["destination"],
                enabled=rule_data["enabled"]
            )
            # ルールリストに追加
            self.config.file_rules.append(new_rule)
            self.config.save(self.config_path)
            # テーブルの更新
            self.update_rules_table()

    def edit_rule(self):
        """既存のルールを編集"""
        selected_rows = self.rules_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        row_index = selected_rows[0].row()
        rule = self.config.file_rules[row_index]
        dialog = RuleDialog(self, rule=rule, lang=self.lang)
        if dialog.exec_():
            rule_data = dialog.get_rule_data()
            # ルールの更新
            rule.name = rule_data["name"]
            rule.extensions = rule_data["extensions"]
            rule.patterns = rule_data["patterns"]
            rule.destination = rule_data["destination"]
            rule.enabled = rule_data["enabled"]
            
            # 設定の保存
            self.config.save(self.config_path)
            
            # テーブルの更新
            self.update_rules_table()

    def delete_rule(self):
        """ルールを削除"""
        selected_rows = self.rules_table.selectionModel().selectedRows()
        
        if not selected_rows:
            return
        
        row_index = selected_rows[0].row()
        rule = self.config.file_rules[row_index]
        
        # 削除確認
        reply = QMessageBox.question(
            self, 
            self.t["confirm"],
            f"ルール「{rule.name}」を削除しますか？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.config.file_rules[row_index]
            self.config.save(self.config_path)
            self.update_rules_table()
            
            # 選択解除のためボタンを無効化
            self.edit_rule_button.setEnabled(False)
            self.delete_rule_button.setEnabled(False)

    def start_scanning(self):
        """スキャン処理を開始"""
        if self.is_running:
            return
        
        source_dir = self.source_dir_edit.text()
        if not source_dir or not os.path.isdir(source_dir):
            QMessageBox.warning(self, self.t["error"], "有効なディレクトリを選択してください")
            return
        
        include_subdirs = self.include_subdirs_check.isChecked()
        
        # UI更新
        self.status_label.setText(self.t["status"] + self.t["scanning"])
        self.log_text.clear()
        self.file_list.clear()
        self.preview_area.clear()
        self.file_info_label.setText(self.t["file_info"])
        self.files_found_label.setText(self.t["files_found"] + "0")
        
        # プログレスバー表示
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不定のプログレス
        
        # フラグ設定
        self.is_running = True
        
        # スキャン処理をワーカースレッドで実行
        worker = Worker(FileOperations.scan_directory, source_dir, include_subdirs)
        worker.started.connect(self.on_scanning_started)
        worker.finished.connect(self.on_scanning_finished)
        worker.error.connect(self.on_worker_error)
        
        self.workers["scan"] = worker
        worker.start()

    def on_scanning_started(self):
        """スキャン開始時の処理"""
        self.log_text.append("ファイルをスキャンしています...")
        self.start_button.setEnabled(False)
        self.scan_button.setEnabled(False)

    def on_scanning_finished(self, files):
        """スキャン完了時の処理"""
        self.files = files
        self.is_running = False
        
        # UI更新
        self.status_label.setText(self.t["status"] + self.t["complete"])
        self.files_found_label.setText(self.t["files_found"] + str(len(files)))
        self.progress_bar.setVisible(False)
        
        self.log_text.append(f"{len(files)}個のファイルが見つかりました")
        
        # ボタンの有効化
        self.start_button.setEnabled(True)
        self.scan_button.setEnabled(True)
        
        # ファイルリストの更新
        self.update_file_list()

    def update_file_list(self):
        """ファイルリストの更新"""
        self.file_list.clear()
        
        for file_info in self.files:
            item = QListWidgetItem(file_info.name)
            item.setData(Qt.UserRole, file_info)
            self.file_list.addItem(item)

    def show_file_preview(self, item):
        """ファイルプレビューの表示"""
        file_info = item.data(Qt.UserRole)
        
        if not file_info:
            return
        
        # ファイル情報の表示
        info_text = f"ファイル名: {file_info.name}\n"
        info_text += f"パス: {file_info.path}\n"
        info_text += f"サイズ: {get_file_size_str(file_info.size)}\n"
        info_text += f"作成日時: {file_info.created_time}\n"
        info_text += f"更新日時: {file_info.modified_time}\n"
        
        self.file_info_label.setText(info_text)
        
        # プレビュー表示
        self.show_preview(file_info)

    def show_preview(self, file_info):
        """ファイルの種類に応じたプレビュー表示"""
        self.preview_area.clear()
        
        # 画像ファイルの場合
        image_exts = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
        if file_info.extension.lower() in image_exts:
            pixmap = QPixmap(str(file_info.path))
            if not pixmap.isNull():
                # サイズ調整
                pixmap = pixmap.scaled(
                    self.preview_area.width(), 
                    self.preview_area.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.preview_area.setPixmap(pixmap)
                return
        
        # テキストファイルの場合
        text_exts = [".txt", ".md", ".csv", ".json", ".xml", ".html", ".py", ".js", ".css"]
        if file_info.extension.lower() in text_exts:
            try:
                with open(file_info.path, 'r', encoding='utf-8') as f:
                    preview_text = f.read(1000)  # 先頭1000文字だけ読み込む
                    if len(preview_text) == 1000:
                        preview_text += "...\n(プレビューは一部のみ表示しています)"
                
                self.preview_area.setText(preview_text)
                self.preview_area.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                return
            except:
                pass
        
        # その他のファイル
        self.preview_area.setText(f"プレビューは利用できません: {file_info.extension}")
        self.preview_area.setAlignment(Qt.AlignCenter)

    def start_organizing(self):
        """ファイル整理処理を開始"""
        if self.is_running:
            return
        
        source_dir = self.source_dir_edit.text()
        if not source_dir or not os.path.isdir(source_dir):
            QMessageBox.warning(self, self.t["error"], "有効なディレクトリを選択してください")
            return
        
        include_subdirs = self.include_subdirs_check.isChecked()
        create_date_folders = self.create_date_folders_check.isChecked()
        handle_duplicates = self.handle_duplicates_check.isChecked()
        
        # 重複処理の設定
        duplicate_action_text = self.duplicate_combo.currentText()
        duplicate_action = "skip"
        if duplicate_action_text == self.t["rename"]:
            duplicate_action = "rename"
        elif duplicate_action_text == self.t["move_to_trash"]:
            duplicate_action = "move_to_trash"
        
        # 設定の更新
        self.config.organize_config.source_dir = source_dir
        self.config.organize_config.process_subdirectories = include_subdirs
        self.config.organize_config.create_date_folders = create_date_folders
        self.config.organize_config.handle_duplicates = handle_duplicates
        self.config.organize_config.duplicate_action = duplicate_action
        self.config.save(self.config_path)
        
        # ログのクリア
        self.log_text.clear()
        self.success_label.setText(self.t["success_count"] + "0")
        self.skipped_label.setText(self.t["skipped_count"] + "0")
        self.error_label.setText(self.t["error_count"] + "0")
        
        # ステータス更新
        self.status_label.setText(self.t["status"] + self.t["organizing"])
        
        # プログレスバー表示
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不定のプログレス
        
        # フラグ設定
        self.is_running = True
        
        # ファイルのスキャンが必要な場合
        if not self.files:
            self.log_text.append("ファイルをスキャンしています...")
            
            # スキャン処理をワーカースレッドで実行
            scan_worker = Worker(FileOperations.scan_directory, source_dir, include_subdirs)
            scan_worker.finished.connect(lambda files: self.organize_files(files, source_dir, create_date_folders, handle_duplicates, duplicate_action))
            scan_worker.error.connect(self.on_worker_error)
            
            self.workers["scan"] = scan_worker
            scan_worker.start()
        else:
            # すでにスキャン済みの場合は直接整理処理を開始
            self.organize_files(self.files, source_dir, create_date_folders, handle_duplicates, duplicate_action)

    def organize_files(self, files, source_dir, create_date_folders, handle_duplicates, duplicate_action):
        """ファイル整理処理の実行"""
        if not files:
            self.is_running = False
            self.status_label.setText(self.t["status"] + self.t["error"])
            self.log_text.append("エラー: ファイルが見つかりませんでした")
            self.progress_bar.setVisible(False)
            self.start_button.setEnabled(True)
            self.scan_button.setEnabled(True)
            return
        
        self.files = files
        self.files_found_label.setText(self.t["files_found"] + str(len(files)))
        self.log_text.append(f"{len(files)}個のファイルを整理します...")
        
        # 整理処理をワーカースレッドで実行
        worker = Worker(
            FileOperations.organize_files,
            files,
            self.config.file_rules,
            source_dir,
            create_date_folders,
            handle_duplicates,
            duplicate_action
        )
        worker.started.connect(self.on_organizing_started)
        worker.finished.connect(self.on_organizing_finished)
        worker.error.connect(self.on_worker_error)
        
        self.workers["organize"] = worker
        worker.start()

    def on_organizing_started(self):
        """整理開始時の処理"""
        self.start_button.setEnabled(False)
        self.scan_button.setEnabled(False)

    def on_organizing_finished(self, result):
        """整理完了時の処理"""
        self.is_running = False
        
        # UI更新
        self.status_label.setText(self.t["status"] + self.t["complete"])
        self.progress_bar.setVisible(False)
        
        # ボタンの有効化
        self.start_button.setEnabled(True)
        self.scan_button.setEnabled(True)
        
        # 結果の表示
        success_count = len(result["success"])
        skipped_count = len(result["skipped"])
        error_count = len(result["error"])
        
        self.success_label.setText(self.t["success_count"] + str(success_count))
        self.skipped_label.setText(self.t["skipped_count"] + str(skipped_count))
        self.error_label.setText(self.t["error_count"] + str(error_count))
        
        # ログ出力
        for msg in result["success"]:
            self.log_text.append(f"✓ {msg}")
        
        for msg in result["skipped"]:
            self.log_text.append(f"- {msg}")
        
        for msg in result["error"]:
            self.log_text.append(f"✗ {msg}")
        
        # ファイルリストをクリア（処理済み）
        self.files = []
        self.file_list.clear()

    def on_worker_error(self, error_msg):
        """ワーカーエラー時の処理"""
        self.is_running = False
        
        # UI更新
        self.status_label.setText(self.t["status"] + self.t["error"])
        self.progress_bar.setVisible(False)
        
        # ボタンの有効化
        self.start_button.setEnabled(True)
        self.scan_button.setEnabled(True)
        
        # エラーログ
        self.log_text.append(f"エラー: {error_msg}")

    def save_settings(self):
        """設定を保存"""
        # 現在の設定を保存
        old_lang = self.lang
        old_theme = self.config.theme
        
        # 新しい設定を適用
        theme = self.theme_combo.currentText()
        language = self.language_combo.currentText()
        log_level = self.log_level_combo.currentText()
        
        self.config.theme = theme
        self.config.language = language
        self.config.log_level = log_level
        
        # 設定を保存
        self.config.save(self.config_path)
        
        # 言語または外観が変更された場合、再起動が必要
        if old_lang != language or old_theme != theme:
            QMessageBox.information(
                self, 
                self.t["confirm"],
                "設定を適用するには、アプリケーションを再起動してください。"
            )
        else:
            # ロガーの設定を更新
            setup_logger(level=log_level)
            
            QMessageBox.information(
                self, 
                self.t["confirm"],
                "設定を保存しました。"
            )

    def reset_settings(self):
        """設定をデフォルトに戻す"""
        reply = QMessageBox.question(
            self, 
            self.t["confirm"],
            "設定をデフォルトに戻しますか？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # バックアップを作成
            try:
                backup_path = self.config.backup(self.config_path)
                QMessageBox.information(
                    self, 
                    self.t["confirm"],
                    f"現在の設定のバックアップを作成しました: {backup_path}"
                )
            except Exception as e:
                QMessageBox.warning(
                    self, 
                    self.t["error"],
                    f"バックアップの作成に失敗しました: {str(e)}"
                )
            
            # 新しい設定を作成
            self.config = Config()
            self.config.save(self.config_path)
            
            # UIを更新
            QMessageBox.information(
                self, 
                self.t["confirm"],
                "設定をデフォルトに戻しました。アプリケーションを再起動してください。"
            )
class FileOrganizerGUI:
    def __init__(self):
        # PySide6のアプリケーションを初期化
        self.app = QApplication(sys.argv)
        self.main_window = FileOrganizerApp()

    def run(self):
        """アプリケーションを実行"""
        self.main_window.show()
        return self.app.exec()