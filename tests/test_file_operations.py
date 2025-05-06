"""
ファイル操作モジュールのテスト
"""

import os
import shutil
import tempfile
import pytest
from pathlib import Path

from src.config import FileRule
from src.file_operations import FileOperations, FileInfo

class TestFileOperations:
    """ファイル操作クラスのテスト"""
    
    @pytest.fixture
    def setup_test_dir(self):
        """テスト用ディレクトリのセットアップ"""
        # 一時ディレクトリの作成
        test_dir = tempfile.mkdtemp()
        
        # テストファイルの作成
        test_files = [
            "document1.txt",
            "document2.pdf",
            "image1.jpg",
            "image2.png",
            "archive1.zip",
            "test_report.pdf",
            "report_2023.docx"
        ]
        
        for filename in test_files:
            file_path = os.path.join(test_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f"This is a test file for {filename}")
        
        # サブディレクトリの作成
        subdir = os.path.join(test_dir, "subdir")
        os.mkdir(subdir)
        
        # サブディレクトリ内のテストファイル
        subdir_files = [
            "subdir_document.txt",
            "subdir_image.jpg"
        ]
        
        for filename in subdir_files:
            file_path = os.path.join(subdir, filename)
            with open(file_path, 'w') as f:
                f.write(f"This is a subdirectory test file for {filename}")
        
        yield test_dir
        
        # テスト後のクリーンアップ
        shutil.rmtree(test_dir)
    
    def test_scan_directory_basic(self, setup_test_dir):
        """ディレクトリスキャンの基本機能テスト"""
        test_dir = setup_test_dir
        
        # サブディレクトリを含まないスキャン
        files = FileOperations.scan_directory(test_dir, include_subdirs=False)
        
        # 直下の7ファイルがスキャンされるはず
        assert len(files) == 7
        
        # すべてFileInfoオブジェクトであるか確認
        for file_info in files:
            assert isinstance(file_info, FileInfo)
    
    def test_scan_directory_with_subdirs(self, setup_test_dir):
        """サブディレクトリを含むディレクトリスキャンのテスト"""
        test_dir = setup_test_dir
        
        # サブディレクトリを含むスキャン
        files = FileOperations.scan_directory(test_dir, include_subdirs=True)
        
        # 直下の7ファイル + サブディレクトリの2ファイル = 計9ファイル
        assert len(files) == 9
    
    def test_match_file_with_rules(self, setup_test_dir):
        """ファイルとルールのマッチングテスト"""
        test_dir = setup_test_dir
        
        # テスト用ルールの作成
        rules = [
            FileRule(
                name="テキスト文書",
                extensions=[".txt"],
                destination="テキスト"
            ),
            FileRule(
                name="PDF文書",
                extensions=[".pdf"],
                destination="PDF"
            ),
            FileRule(
                name="画像",
                extensions=[".jpg", ".png", ".gif"],
                destination="画像"
            ),
            FileRule(
                name="レポート",
                patterns=["report_"],
                destination="レポート"
            )
        ]
        
        # テストファイルのスキャン
        files = FileOperations.scan_directory(test_dir, include_subdirs=False)
        
        # マッチングテスト
        for file_info in files:
            if file_info.extension == ".txt":
                # テキストファイルのマッチング
                matched_rule = FileOperations.match_file_with_rules(file_info, rules)
                assert matched_rule.name == "テキスト文書"
            
            elif file_info.extension == ".pdf":
                # PDFファイルのマッチング
                matched_rule = FileOperations.match_file_with_rules(file_info, rules)
                assert matched_rule.name == "PDF文書"
            
            elif file_info.extension in [".jpg", ".png"]:
                # 画像ファイルのマッチング
                matched_rule = FileOperations.match_file_with_rules(file_info, rules)
                assert matched_rule.name == "画像"
            
            elif "report_" in file_info.name:
                # パターンによるマッチング
                matched_rule = FileOperations.match_file_with_rules(file_info, rules)
                assert matched_rule.name == "レポート"
    
    def test_organize_files(self, setup_test_dir):
        """ファイル整理機能のテスト"""
        test_dir = setup_test_dir
        
        # テスト用ルールの作成
        rules = [
            FileRule(
                name="テキスト文書",
                extensions=[".txt"],
                destination="テキスト"
            ),
            FileRule(
                name="PDF文書",
                extensions=[".pdf"],
                destination="PDF"
            ),
            FileRule(
                name="画像",
                extensions=[".jpg", ".png", ".gif"],
                destination="画像"
            )
        ]
        
        # テストファイルのスキャン
        files = FileOperations.scan_directory(test_dir, include_subdirs=False)
        
        # ファイル整理の実行
        result = FileOperations.organize_files(
            files,
            rules,
            test_dir,
            create_date_folders=False,
            handle_duplicates=True,
            duplicate_action="skip"
        )
        
        # 成功したファイルの数をチェック
        success_count = len(result["success"])
        assert success_count > 0
        
        # 整理後のディレクトリ構造をチェック
        text_dir = os.path.join(test_dir, "テキスト")
        pdf_dir = os.path.join(test_dir, "PDF")
        image_dir = os.path.join(test_dir, "画像")
        
        assert os.path.isdir(text_dir)
        assert os.path.isdir(pdf_dir)
        assert os.path.isdir(image_dir)
        
        # 各ディレクトリのファイル数をチェック
        text_files = os.listdir(text_dir)
        pdf_files = os.listdir(pdf_dir)
        image_files = os.listdir(image_dir)
        
        # テキストファイルは1つ
        assert len(text_files) == 1
        # PDFファイルは2つ
        assert len(pdf_files) == 2
        # 画像ファイルは2つ
        assert len(image_files) == 2
    
    def test_find_duplicates(self):
        """重複ファイル検出のテスト"""
        # 一時ディレクトリの作成
        test_dir = tempfile.mkdtemp()
        
        try:
            # 同じ内容の2つのファイルを作成
            file1_path = os.path.join(test_dir, "file1.txt")
            file2_path = os.path.join(test_dir, "file2.txt")
            
            with open(file1_path, 'w') as f:
                f.write("This is a test file with duplicate content")
            
            # 同じ内容のファイルをコピー
            shutil.copy(file1_path, file2_path)
            
            # 異なる内容のファイル
            file3_path = os.path.join(test_dir, "file3.txt")
            with open(file3_path, 'w') as f:
                f.write("This is a test file with different content")
            
            # FileInfoオブジェクトの作成
            files = [
                FileInfo.from_path(Path(file1_path)),
                FileInfo.from_path(Path(file2_path)),
                FileInfo.from_path(Path(file3_path))
            ]
            
            # 重複ファイルの検出
            duplicates = FileOperations.find_duplicates(files)
            
            # 重複グループは1つだけ
            assert len(duplicates) == 1
            
            # 各グループに含まれるファイルは2つ
            for hash_key, file_list in duplicates.items():
                assert len(file_list) == 2
                assert any(file.path.name == "file1.txt" for file in file_list)
                assert any(file.path.name == "file2.txt" for file in file_list)
        
        finally:
            # クリーンアップ
            shutil.rmtree(test_dir)