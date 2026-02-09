"""UIスタイル定義モジュール."""

# カスタムCSS
CUSTOM_CSS = """
.container {
    max-width: 1200px;
    margin: 0 auto;
}

.result-correct {
    background-color: #d4edda !important;
    border-color: #c3e6cb !important;
}

.result-incorrect {
    background-color: #f8d7da !important;
    border-color: #f5c6cb !important;
}

.score-display {
    font-size: 2em;
    font-weight: bold;
    text-align: center;
    padding: 20px;
}

.cefr-level {
    font-size: 1.5em;
    font-weight: bold;
    color: #007bff;
}

.feedback-section {
    margin-top: 20px;
    padding: 15px;
    border-radius: 8px;
    background-color: #f8f9fa;
}

.grammar-issue {
    color: #dc3545;
    margin: 5px 0;
}

.suggestion {
    color: #28a745;
    margin: 5px 0;
}

.stats-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
}

.question-box {
    border: 2px solid #007bff;
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
    background-color: #f0f7ff;
}

.model-answer {
    background-color: #e8f5e9;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #4caf50;
}

/* TTS関連のスタイル */
.tts-button {
    background-color: #17a2b8 !important;
    border-color: #17a2b8 !important;
}

.tts-button:hover {
    background-color: #138496 !important;
    border-color: #117a8b !important;
}

.speakable-text {
    cursor: pointer;
    border-bottom: 1px dashed #17a2b8;
}

.speakable-text:hover {
    background-color: #e3f2fd;
}

.tts-audio-player {
    margin-top: 10px;
    width: 100%;
}

.tts-status {
    font-size: 0.9em;
    color: #666;
    margin-top: 5px;
}

/* TTSセクションのレイアウト修正 */
.tts-section {
    margin-top: 20px;
    padding-top: 15px;
    border-top: 1px solid #e0e0e0;
}

.tts-section .tts-button-row {
    margin-bottom: 10px;
}

/* ボタンの配置調整 */
.submit-btn-row {
    margin-top: 15px;
    margin-bottom: 20px;
}

/* 問題生成セクションのスタイル */
.generation-section {
    margin-top: 20px;
}

.generation-status {
    padding: 15px;
    margin: 15px 0;
    border-radius: 8px;
    background-color: #f8f9fa;
    min-height: 50px;
}

.generation-status.processing {
    background-color: #fff3cd;
    border: 1px solid #ffc107;
}

.generation-preview {
    margin-top: 20px;
    margin-bottom: 15px;
}

.generation-preview .json-holder {
    max-height: 400px;
    overflow-y: auto;
}

/* プレビューとボタンの間隔 */
.save-button-row {
    margin-top: 15px;
    margin-bottom: 10px;
}

/* 問題生成フォームのレイアウト */
.generation-form {
    margin-bottom: 20px;
}

.generation-form .gr-form {
    gap: 15px;
}

/* プログレス表示の調整 */
.gradio-container .wrap.default {
    position: relative;
}

.gradio-container .progress-bar {
    margin-bottom: 10px;
}

/* JSONプレビューの調整 */
.gradio-container .json {
    margin-top: 10px;
}
"""
