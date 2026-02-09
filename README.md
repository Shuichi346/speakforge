# SpeakForge - 英語スピーキング練習アプリ

英語の瞬発力と表現力を鍛えるためのAI活用型トレーニングアプリです。

## 機能

### AI英会話学習アプリのデモ（YouTube）
<a href="https://www.youtube.com/watch?v=vhdZB_ZYoWg">
  <img src="https://img.youtube.com/vi/vhdZB_ZYoWg/maxresdefault.jpg" width="600" alt="動画のタイトル">
</a>

### 口頭英作文（Sentence Practice）
- 日本語の文章を瞬時に英語に変換するトレーニング
- AIによる柔軟な正誤判定（複数の正解パターンを許容）
- 詳細なフィードバックと質問機能
- **🔊 模範回答の英語読み上げ機能**

### 独り言英会話（Monologue Practice）
- トピックに沿って約1分間英語で話すトレーニング
- 文法、表現、構成の3観点からのAI添削
- WPM（発話速度）とCEFRレベルの判定
- **🔊 模範回答の英語読み上げ機能**

### スマート復習
- 苦手な文法や間違えた問題を自動抽出
- 効率的な復習システム
- **🔊 模範回答の英語読み上げ機能**

### 🔊 英語読み上げ機能（TTS）
- [Pocket TTS](https://github.com/kyutai-labs/pocket-tts)による高品質な英語音声合成
- 模範回答の発音を確認可能
- 複数のボイスから選択可能
- CPUで高速に動作（GPUなしでも利用可能）

## 必要条件

- [Python 3.11](https://www.python.org/downloads/)以上
- [LM Studio](https://lmstudio.ai/)（ローカルLLMサーバー）
- [ffmpeg](https://www.ffmpeg.org/download.html)（音声ファイル変換用）

## 対応モデル

### 推奨モデル（Qwen3系）

本アプリは[Qwen3](https://huggingface.co/collections/Qwen/qwen3)系モデルに最適化されています。以下のモデルを推奨します：

| モデル名 | VRAM目安 | 特徴 |
|---------|---------|------|
| qwen3-8b | 8GB | 軽量で高速 |
| qwen3-vl-8b-instruct | 8GB | マルチモーダル対応 |
| qwen3-14b | 12GB | バランス型 |
| qwen3-30b-a3b | 16GB | 高精度（MoE） |

### 非推奨・未対応モデル

以下のモデルは応答形式の違いにより動作しない可能性があります：

- Gemini系モデル
- Claude系モデル（ローカル非対応）
- GPT系モデル（ローカル非対応）

### Qwen3のThinking Mode

Qwen3はデフォルトで「Thinking Mode」が有効になっており、応答前に`<think>...</think>`タグ内で思考プロセスを出力します。本アプリではプロンプトに`/no_think`を追加することで、この機能を無効化し、JSON応答を正しく取得できるようにしています。

## セットアップ

### 1. uvのインストール（未インストールの場合）

[uv](https://docs.astral.sh/uv/)は高速なPythonパッケージマネージャーです。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. プロジェクトのセットアップ

```bash
cd speakforge
uv sync
```

### 3. Whisperモデルのダウンロード

初回起動時に自動でダウンロードされますが、手動でダウンロードする場合：

```bash
# modelsディレクトリにggml形式のモデルを配置
# 推奨: base または small モデル
```

モデルは[whisper.cpp](https://github.com/ggml-org/whisper.cpp)のggml形式を使用します。

### 4. LM Studioの起動

1. [LM Studio](https://lmstudio.ai/)を起動
2. 任意のモデルをロード（日本語対応推奨）
3. Developer タブでサーバーを起動（デフォルト: localhost:1234）

### 5. アプリの起動

```bash
uv run speakforge
```

ブラウザで `http://localhost:7860` を開いてください。

## 🔊 TTS（英語読み上げ）機能について

### 概要

[Pocket TTS](https://github.com/kyutai-labs/pocket-tts)を使用した英語読み上げ機能により、模範回答の発音を確認できます。

### 読み上げ対象

- **口頭英作文**: 模範回答（英語）
- **独り言英会話**: AIが生成した模範回答（英語）
- **スマート復習**: 模範回答（英語）

### 利用可能なボイス

| ボイス名 | 特徴 |
|---------|------|
| alba | 女性、落ち着いた声（デフォルト） |
| marius | 男性 |
| javert | 男性 |
| jean | 男性 |
| fantine | 女性 |
| cosette | 女性 |
| eponine | 女性 |
| azelma | 女性 |

### 設定方法

`.env`ファイルで以下の設定が可能です：

```
TTS_ENABLED=true           # TTS機能の有効/無効
TTS_VOICE=alba            # 使用するボイス
TTS_TEMPERATURE=0.7       # 音声生成の温度
```

### 注意事項

- 初回起動時にPocket TTSモデルが自動ダウンロードされます（約100MB）
- CPUで動作するため、GPUは不要です
- Apple Silicon（M1/M2/M3/M4）で特に高速に動作します

## 例文・トピックのカスタマイズ

`data/sentences/` および `data/monologue_topics/` 内のJSONファイルを編集することで、
独自の例文やトピックを追加できます。

### 例文JSONの形式

```json
{
  "category": "カテゴリ名",
  "sentences": [
    {
      "id": "unique_id",
      "japanese": "日本語の文章",
      "english_examples": ["英語の模範回答1", "英語の模範回答2"],
      "difficulty": 1,
      "tags": ["文法タグ", "場面タグ"]
    }
  ]
}
```

### トピックJSONの形式

```json
{
  "category": "カテゴリ名",
  "topics": [
    {
      "id": "unique_id",
      "title": "トピックタイトル",
      "description": "説明",
      "hints": ["ヒント1", "ヒント2"],
      "difficulty": 1
    }
  ]
}
```

## 環境変数

`.env`ファイルで設定可能な項目：

```
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_MODEL=qwen3-vl-8b-instruct
WHISPER_MODEL=base
WHISPER_LANGUAGE=en
TTS_ENABLED=true
TTS_VOICE=alba
TTS_TEMPERATURE=0.7
GRADIO_SERVER_PORT=7860
GRADIO_SHARE=false
```

## 使用技術

- [Gradio](https://www.gradio.app/) - WebUIフレームワーク
- [Whisper](https://github.com/openai/whisper) / [whisper.cpp](https://github.com/ggml-org/whisper.cpp) - 音声認識
- [Pocket TTS](https://github.com/kyutai-labs/pocket-tts) - 英語音声合成
- [LM Studio](https://lmstudio.ai/) - ローカルLLMサーバー
- [Qwen3](https://huggingface.co/collections/Qwen/qwen3) - 推奨LLMモデル

## ライセンス

MIT License

## 実装のポイント説明

### 読み上げ箇所の選定

英語学習において発音確認が効果的な以下の箇所を読み上げ対象としました：

1. **口頭英作文の模範回答** - 正しい英文の発音を学ぶ
2. **独り言英会話の模範回答** - 自然な英語表現の発音を学ぶ
3. **復習問題の模範回答** - 間違えた問題の正しい発音を確認

### 技術的なポイント

1. **シングルトンパターン** - TTSモデルのロードは重い処理のため、一度だけロードして再利用
2. **遅延初期化** - アプリ起動時にTTSが不要な場合はロードをスキップ可能
3. **State管理** - [Gradio](https://www.gradio.app/)のgr.Stateを使用して、現在の模範回答を保持
4. **自動再生** - `autoplay=True`で生成された音声を即座に再生

### ユーザー体験

1. 結果表示後に「🔊 模範回答を読み上げ」ボタンをクリックするだけで発音を確認
2. 設定タブでボイスの変更とテストが可能
3. TTS機能は`.env`で無効化可能（軽量動作が必要な場合）
