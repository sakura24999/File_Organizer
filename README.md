# ファイル管理自動化ツール (File Organizer)

ファイル管理自動化ツールは、日常的なファイル整理作業を自動化し、時間を節約するためのPythonアプリケーションです。

## 主な機能

- **拡張子ベースの自動分類**: ファイルをその拡張子に基づいて適切なフォルダに自動的に振り分けます
- **パターンベースの分類**: ファイル名のパターンに基づいて振り分けルールをカスタマイズできます
- **日付による整理**: ファイルの作成日・更新日に基づいた整理ができます
- **重複ファイルの検出**: 同一内容のファイルを検出し、整理を支援します
- **シンプルなGUI**: 直感的に操作できるインターフェースを提供します

## 使用方法

### Dockerを使用する場合

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/file_organizer.git
cd file_organizer

# Dockerコンテナをビルドして実行
docker-compose up file_organizer
```

### ローカルで実行する場合

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/file_organizer.git
cd file_organizer

# 仮想環境を作成して有効化
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt
pip install -e .

# アプリケーションを実行
python -m src.main
```

## 実行ファイル（.exe）のビルド方法

```bash
# PyInstallerを使用して実行ファイルをビルド
pyinstaller --onefile --windowed --name="FileOrganizer" --icon=src/assets/icon.ico src/main.py
```

ビルドが完了すると、`dist`ディレクトリに`FileOrganizer.exe`が生成されます。

## 開発者向け情報

### テストの実行

```bash
# Dockerを使用する場合
docker-compose up test

# ローカルで実行する場合
pytest -xvs tests/
```

### コントリビューション

1. このリポジトリをフォークします
2. 新しいブランチを作成します (`git checkout -b feature/amazing-feature`)
3. 変更をコミットします (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュします (`git push origin feature/amazing-feature`)
5. プルリクエストを作成します

