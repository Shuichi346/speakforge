# SpeakForge - English Speaking Practice App

An AI-powered training app to develop English fluency and expression skills.

## Features

### AI English Conversation Learning App Demo（YouTube）
<a href="https://www.youtube.com/watch?v=vhdZB_ZYoWg">
  <img src="https://img.youtube.com/vi/vhdZB_ZYoWg/maxresdefault.jpg" width="600" alt="動画のタイトル">
</a>

### Sentence Practice
- Training to instantly convert Japanese sentences into English
- Flexible AI-based correctness judgment (accepts multiple correct answer patterns)
- Detailed feedback and question features
- **🔊 English text-to-speech for model answers**

### Monologue Practice
- Training to speak in English for about 1 minute on given topics
- AI feedback from 3 perspectives: grammar, expression, and structure
- WPM (speaking speed) and CEFR level assessment
- **🔊 English text-to-speech for model answers**

### Smart Review
- Automatically extracts weak grammar points and incorrect problems
- Efficient review system
- **🔊 English text-to-speech for model answers**

### 🔊 English Text-to-Speech (TTS) Feature
- High-quality English speech synthesis using [Pocket TTS](https://github.com/kyutai-labs/pocket-tts)
- Pronunciation verification for model answers
- Multiple voice options available
- Fast operation on CPU (available without GPU)

## Requirements

- [Python 3.11](https://www.python.org/downloads/) or higher
- [LM Studio](https://lmstudio.ai/) (local LLM server)
- [ffmpeg](https://www.ffmpeg.org/download.html) (for audio file conversion)

## Supported Models

### Recommended Models (Qwen3 series)

This app is optimized for [Qwen3](https://huggingface.co/collections/Qwen/qwen3) series models. The following models are recommended:

| Model Name | VRAM Requirement | Features |
|------------|------------------|----------|
| qwen3-8b | 8GB | Lightweight and fast |
| qwen3-vl-8b-instruct | 8GB | Multimodal support |
| qwen3-14b | 12GB | Balanced |
| qwen3-30b-a3b | 16GB | High accuracy (MoE) |

### Not Recommended/Unsupported Models

The following models may not work due to differences in response format:

- Gemini series models
- Claude series models (not available locally)
- GPT series models (not available locally)

### Qwen3 Thinking Mode

Qwen3 has "Thinking Mode" enabled by default, which outputs the thinking process within `<think>...</think>` tags before responding. This app adds `/no_think` to the prompt to disable this feature and correctly obtain JSON responses.

## Setup

### 1. Install uv (if not already installed)

[uv](https://docs.astral.sh/uv/) is a fast Python package manager.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Project Setup

```bash
cd speakforge
uv sync
```

### 3. Download Whisper Model

Models are automatically downloaded on first startup, but for manual download:

```bash
# Place ggml format models in the models directory
# Recommended: base or small model
```

Models use ggml format from [whisper.cpp](https://github.com/ggml-org/whisper.cpp).

### 4. Start LM Studio

1. Launch [LM Studio](https://lmstudio.ai/)
2. Load any model (Japanese support recommended)
3. Start server in Developer tab (default: localhost:1234)

### 5. Launch App

```bash
uv run speakforge
```

Open `http://localhost:7860` in your browser.

## 🔊 TTS (English Text-to-Speech) Feature

### Overview

English text-to-speech feature using [Pocket TTS](https://github.com/kyutai-labs/pocket-tts) allows pronunciation verification of model answers.

### TTS Targets

- **Sentence Practice**: Model answers (English)
- **Monologue Practice**: AI-generated model answers (English)
- **Smart Review**: Model answers (English)

### Available Voices

| Voice Name | Characteristics |
|------------|-----------------|
| alba | Female, calm voice (default) |
| marius | Male |
| javert | Male |
| jean | Male |
| fantine | Female |
| cosette | Female |
| eponine | Female |
| azelma | Female |

### Configuration

The following settings are available in the `.env` file:

```
TTS_ENABLED=true           # Enable/disable TTS feature
TTS_VOICE=alba            # Voice to use
TTS_TEMPERATURE=0.7       # Temperature for speech generation
```

### Notes

- Pocket TTS model is automatically downloaded on first startup (about 100MB)
- Runs on CPU, no GPU required
- Particularly fast on Apple Silicon (M1/M2/M3/M4)

## Customizing Sentences and Topics

You can add custom sentences and topics by editing JSON files in `data/sentences/` and `data/monologue_topics/`.

### Sentence JSON Format

```json
{
  "category": "Category Name",
  "sentences": [
    {
      "id": "unique_id",
      "japanese": "Japanese sentence",
      "english_examples": ["English model answer 1", "English model answer 2"],
      "difficulty": 1,
      "tags": ["grammar tag", "situation tag"]
    }
  ]
}
```

### Topic JSON Format

```json
{
  "category": "Category Name",
  "topics": [
    {
      "id": "unique_id",
      "title": "Topic Title",
      "description": "Description",
      "hints": ["Hint 1", "Hint 2"],
      "difficulty": 1
    }
  ]
}
```

## Environment Variables

Configurable items in `.env` file:

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

## Technologies Used

- [Gradio](https://www.gradio.app/) - Web UI framework
- [Whisper](https://github.com/openai/whisper) / [whisper.cpp](https://github.com/ggml-org/whisper.cpp) - Speech recognition
- [Pocket TTS](https://github.com/kyutai-labs/pocket-tts) - English speech synthesis
- [LM Studio](https://lmstudio.ai/) - Local LLM server
- [Qwen3](https://huggingface.co/collections/Qwen/qwen3) - Recommended LLM model

## License

MIT License

## Implementation Points Explanation

### Selection of TTS Areas

The following areas where pronunciation verification is effective for English learning were selected as TTS targets:

1. **Sentence Practice Model Answers** - Learn pronunciation of correct English sentences
2. **Monologue Practice Model Answers** - Learn pronunciation of natural English expressions
3. **Review Problem Model Answers** - Verify correct pronunciation of missed problems

### Technical Points

1. **Singleton Pattern** - TTS model loading is heavy processing, so load once and reuse
2. **Lazy Initialization** - Skip loading at app startup when TTS is unnecessary
3. **State Management** - Use [Gradio](https://www.gradio.app/)'s gr.State to maintain current model answers
4. **Auto-play** - Immediately play generated audio with `autoplay=True`

### User Experience

1. Simply click the "🔊 Read Model Answer" button after result display to verify pronunciation
2. Voice changes and testing available in settings tab
3. TTS feature can be disabled in `.env` (for lightweight operation when needed)
