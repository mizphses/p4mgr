# P4Mgr - LED Matrix Display Manager

P4Mgr は、Raspberry Pi で LED Matrix (P4 32x64 パネル 2 枚)を制御し、電光掲示板として動作させる Python ツールです。

## 概要

- USB テンキーからの入力に応じて、事前定義されたテンプレートを表示
- 電車の行き先表示、テキスト表示、スクロールテキストなど複数の表示モードをサポート
- JSON 形式の設定ファイルで表示内容を管理

## 必要要件

- Raspberry Pi (GPIO 接続可能なモデル)
- P4 32x64 LED Matrix パネル x 2 枚
- Python 3.12 以上
- rpi-rgb-led-matrix ライブラリ
- USB テンキー

## インストール

```bash
# uvを使用したインストール
uv pip install -e .
```

## 使用方法

1. 設定ファイル(config.json)を作成
2. P4Mgr を起動
3. USB テンキーで表示したい番号を入力して Enter

### 設定ファイル例

```json
{
  "01": {
    "type": "dest",
    "destination": {
      "text": "大阪",
      "color": "#fff"
    },
    "dstBgColor": "#f00",
    "scroll": {
      "text": "途中、名古屋、京都に止まります",
      "color": "#fff"
    }
  },
  "02": {
    "type": "textNsc",
    "txt": {
      "text": "この車は回送です",
      "color": "#000",
      "size": 15
    }
  }
}
```

## 表示テンプレート

### 1. 行き先表示 (type: "dest")

電車の行き先表示風のテンプレート。種別欄、行き先、スクロール文字を表示。

### 2. テキスト表示 (type: "textNsc")

中央揃えで固定テキストを表示。

### 3. スクロールテキスト (type: "textScr")

テキストを無限ループでスクロール表示。

## 開発

```bash
# 開発依存関係のインストール
uv pip install -e ".[dev]"

# コードフォーマット
ruff format .

# リント
ruff check .
```
