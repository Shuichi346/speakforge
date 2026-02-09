"""テキスト読み上げサービスモジュール（Pocket TTS使用）."""

import tempfile
from pathlib import Path
from typing import Optional

import numpy as np

from speakforge.config import settings


class TextToSpeechService:
    """Pocket TTSを使用したテキスト読み上げサービス."""

    _instance: Optional["TextToSpeechService"] = None
    _model = None
    _voice_state: Optional[dict] = None
    _initialized: bool = False

    def __new__(cls) -> "TextToSpeechService":
        """シングルトンパターンの実装."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """初期化処理."""
        # 既に初期化済みの場合はスキップ
        if self._initialized:
            return

        if not settings.tts_enabled:
            print("TTS機能は無効化されています")
            self._initialized = True
            return

        self._load_model()
        self._initialized = True

    def _load_model(self) -> None:
        """Pocket TTSモデルをロード."""
        try:
            from pocket_tts import TTSModel

            print("Pocket TTSモデルをロード中...")
            self._model = TTSModel.load_model(
                temp=settings.tts_temperature,
            )

            # ボイスの状態を事前ロード
            voice_name = settings.tts_voice
            print(f"ボイスをロード中: {voice_name}")
            self._voice_state = self._model.get_state_for_audio_prompt(voice_name)

            print(f"Pocket TTSのロード完了（ボイス: {voice_name}）")

        except ImportError as e:
            print(f"Pocket TTSのインポートエラー: {e}")
            print("pip install pocket-tts でインストールしてください")
            self._model = None
        except Exception as e:
            print(f"Pocket TTSのロードエラー: {e}")
            self._model = None

    def is_available(self) -> bool:
        """TTSサービスが利用可能かどうかを確認."""
        return (
            settings.tts_enabled
            and self._model is not None
            and self._voice_state is not None
        )

    def get_sample_rate(self) -> int:
        """サンプルレートを取得."""
        if self._model is not None:
            return self._model.sample_rate
        return 24000  # Pocket TTSのデフォルト

    def synthesize(self, text: str) -> Optional[tuple[int, np.ndarray]]:
        """
        テキストを音声に変換.

        Args:
            text: 読み上げるテキスト（英語）

        Returns:
            (サンプルレート, 音声データ)のタプル、またはNone
        """
        if not self.is_available():
            return None

        if not text or not text.strip():
            return None

        try:
            # 音声を生成
            audio_tensor = self._model.generate_audio(
                self._voice_state,
                text.strip(),
                copy_state=True,
            )

            # NumPy配列に変換
            audio_array = audio_tensor.numpy()

            # float32 -> int16に変換（Gradioの音声コンポーネント用）
            audio_int16 = (audio_array * 32767).astype(np.int16)

            return (self.get_sample_rate(), audio_int16)

        except Exception as e:
            print(f"音声合成エラー: {e}")
            return None

    def synthesize_to_file(self, text: str, output_path: Path) -> bool:
        """
        テキストを音声に変換してファイルに保存.

        Args:
            text: 読み上げるテキスト（英語）
            output_path: 出力ファイルパス

        Returns:
            成功した場合True
        """
        import scipy.io.wavfile

        audio_data = self.synthesize(text)
        if audio_data is None:
            return False

        sample_rate, audio_array = audio_data

        try:
            scipy.io.wavfile.write(str(output_path), sample_rate, audio_array)
            return True
        except Exception as e:
            print(f"音声ファイル保存エラー: {e}")
            return False

    def change_voice(self, voice_name: str) -> bool:
        """
        ボイスを変更.

        Args:
            voice_name: 新しいボイス名

        Returns:
            成功した場合True
        """
        if self._model is None:
            return False

        try:
            self._voice_state = self._model.get_state_for_audio_prompt(voice_name)
            print(f"ボイスを変更しました: {voice_name}")
            return True
        except Exception as e:
            print(f"ボイス変更エラー: {e}")
            return False

    @staticmethod
    def get_available_voices() -> list[str]:
        """利用可能なボイス一覧を取得."""
        return [
            "alba",
            "marius",
            "javert",
            "jean",
            "fantine",
            "cosette",
            "eponine",
            "azelma",
        ]
