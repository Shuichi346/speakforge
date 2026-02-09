"""音声認識サービスモジュール."""

import tempfile
import wave
from pathlib import Path
from typing import Optional

import numpy as np
from pywhispercpp.model import Model

from speakforge.config import settings


class SpeechToTextService:
    """Whisper.cppを使用した音声認識サービス."""

    _instance: Optional["SpeechToTextService"] = None
    _model: Optional[Model] = None

    # Whisper.cppが要求するサンプルレート
    WHISPER_SAMPLE_RATE = 16000

    def __new__(cls) -> "SpeechToTextService":
        """シングルトンパターンの実装."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """初期化処理."""
        if self._model is None:
            self._load_model()

    def _load_model(self) -> None:
        """Whisperモデルをロード."""
        model_name = settings.whisper_model
        print(f"Whisperモデルをロード中: {model_name}")

        # モデルをロード（自動ダウンロード対応）
        self._model = Model(
            model_name,
            print_realtime=False,
            print_progress=False,
        )
        print(f"Whisperモデルのロード完了: {model_name}")

    def _resample_audio(
        self,
        audio_array: np.ndarray,
        original_sample_rate: int,
        target_sample_rate: int,
    ) -> np.ndarray:
        """
        音声データをリサンプリング.

        Args:
            audio_array: 元の音声データ
            original_sample_rate: 元のサンプルレート
            target_sample_rate: 目標サンプルレート

        Returns:
            リサンプリングされた音声データ
        """
        if original_sample_rate == target_sample_rate:
            return audio_array

        # リサンプリング比率を計算
        ratio = target_sample_rate / original_sample_rate
        new_length = int(len(audio_array) * ratio)

        # 線形補間でリサンプリング
        original_indices = np.arange(len(audio_array))
        new_indices = np.linspace(0, len(audio_array) - 1, new_length)
        resampled = np.interp(new_indices, original_indices, audio_array)

        return resampled.astype(audio_array.dtype)

    def _prepare_audio(
        self,
        audio_data: tuple[int, np.ndarray],
    ) -> tuple[str, Path]:
        """
        音声データをWhisper用に準備.

        Args:
            audio_data: (サンプルレート, numpy配列)のタプル

        Returns:
            一時ファイルのパス
        """
        sample_rate, audio_array = audio_data

        # float32に変換
        if audio_array.dtype == np.int16:
            audio_float = audio_array.astype(np.float32) / 32768.0
        elif audio_array.dtype == np.int32:
            audio_float = audio_array.astype(np.float32) / 2147483648.0
        elif audio_array.dtype == np.float64:
            audio_float = audio_array.astype(np.float32)
        elif audio_array.dtype == np.float32:
            audio_float = audio_array
        else:
            # その他の型はfloat32に変換を試みる
            audio_float = audio_array.astype(np.float32)
            # 値の範囲を確認して正規化
            max_val = np.max(np.abs(audio_float))
            if max_val > 1.0:
                audio_float = audio_float / max_val

        # ステレオをモノラルに変換
        if len(audio_float.shape) > 1:
            if audio_float.shape[1] == 2:
                # (samples, channels) の形式
                audio_float = np.mean(audio_float, axis=1)
            elif audio_float.shape[0] == 2:
                # (channels, samples) の形式
                audio_float = np.mean(audio_float, axis=0)

        # 16000Hzにリサンプリング
        if sample_rate != self.WHISPER_SAMPLE_RATE:
            print(f"リサンプリング: {sample_rate}Hz -> {self.WHISPER_SAMPLE_RATE}Hz")
            audio_float = self._resample_audio(
                audio_float,
                sample_rate,
                self.WHISPER_SAMPLE_RATE,
            )

        # クリッピングを防ぐ
        audio_float = np.clip(audio_float, -1.0, 1.0)

        # 一時ファイルとして保存
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = Path(f.name)

        # WAVファイルとして書き込み（16bit PCM）
        with wave.open(str(temp_path), "wb") as wf:
            wf.setnchannels(1)  # モノラル
            wf.setsampwidth(2)  # 16bit
            wf.setframerate(self.WHISPER_SAMPLE_RATE)  # 16000Hz

            # float32をint16に変換して書き込み
            int_data = (audio_float * 32767).astype(np.int16)
            wf.writeframes(int_data.tobytes())

        return str(temp_path), temp_path

    def transcribe(
        self,
        audio_data: tuple[int, np.ndarray] | str | Path,
        language: str = "en",
    ) -> str:
        """
        音声をテキストに変換.

        Args:
            audio_data: (サンプルレート, numpy配列)のタプル、または音声ファイルパス
            language: 認識言語（デフォルト: 英語）

        Returns:
            認識されたテキスト
        """
        if self._model is None:
            self._load_model()

        temp_path = None

        try:
            # numpy配列の場合は一時ファイルに保存
            if isinstance(audio_data, tuple):
                audio_path, temp_path = self._prepare_audio(audio_data)
            else:
                audio_path = str(audio_data)

            # 音声認識を実行
            segments = self._model.transcribe(
                audio_path,
                language=language,
            )

            # セグメントを結合
            text = " ".join(segment.text.strip() for segment in segments)

            return text.strip()

        finally:
            # 一時ファイルを削除
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)

    def calculate_wpm(self, text: str, duration_seconds: float) -> float:
        """
        WPM（Words Per Minute）を計算.

        Args:
            text: 認識されたテキスト
            duration_seconds: 音声の長さ（秒）

        Returns:
            WPM値
        """
        if duration_seconds <= 0:
            return 0.0

        word_count = len(text.split())
        minutes = duration_seconds / 60.0
        return word_count / minutes if minutes > 0 else 0.0
