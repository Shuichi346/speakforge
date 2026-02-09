"""音声ユーティリティモジュール."""

import numpy as np


class AudioUtils:
    """音声処理ユーティリティ."""

    @staticmethod
    def get_audio_duration(audio_data: tuple[int, np.ndarray]) -> float:
        """
        音声データの長さを秒単位で取得.

        Args:
            audio_data: (サンプルレート, numpy配列)のタプル

        Returns:
            音声の長さ（秒）
        """
        sample_rate, audio_array = audio_data

        # サンプル数を取得
        if len(audio_array.shape) > 1:
            # ステレオの場合
            if audio_array.shape[0] == 2:
                # (channels, samples) の形式
                num_samples = audio_array.shape[1]
            else:
                # (samples, channels) の形式
                num_samples = audio_array.shape[0]
        else:
            # モノラルの場合
            num_samples = len(audio_array)

        return num_samples / sample_rate

    @staticmethod
    def normalize_audio(audio_array: np.ndarray) -> np.ndarray:
        """
        音声データを正規化.

        Args:
            audio_array: numpy配列

        Returns:
            正規化された音声データ
        """
        max_val = np.max(np.abs(audio_array))
        if max_val > 0:
            return audio_array / max_val
        return audio_array

    @staticmethod
    def is_audio_valid(audio_data: tuple[int, np.ndarray] | None) -> bool:
        """
        音声データが有効かどうかを確認.

        Args:
            audio_data: (サンプルレート, numpy配列)のタプル

        Returns:
            有効な場合True
        """
        if audio_data is None:
            return False

        try:
            sample_rate, audio_array = audio_data
        except (TypeError, ValueError):
            return False

        if sample_rate is None or sample_rate <= 0:
            return False

        if audio_array is None:
            return False

        # numpy配列かどうか確認
        if not isinstance(audio_array, np.ndarray):
            return False

        if audio_array.size == 0:
            return False

        # 最低0.3秒以上の音声があるか確認（短い発話も許容）
        duration = AudioUtils.get_audio_duration(audio_data)
        if duration < 0.3:
            return False

        # 音声に実際の信号があるか確認（無音でないか）
        if np.max(np.abs(audio_array)) < 1e-6:
            return False

        return True

    @staticmethod
    def get_audio_info(audio_data: tuple[int, np.ndarray]) -> dict:
        """
        音声データの情報を取得（デバッグ用）.

        Args:
            audio_data: (サンプルレート, numpy配列)のタプル

        Returns:
            音声情報の辞書
        """
        sample_rate, audio_array = audio_data

        return {
            "sample_rate": sample_rate,
            "shape": audio_array.shape,
            "dtype": str(audio_array.dtype),
            "duration": AudioUtils.get_audio_duration(audio_data),
            "min_value": float(np.min(audio_array)),
            "max_value": float(np.max(audio_array)),
            "mean_value": float(np.mean(audio_array)),
        }
