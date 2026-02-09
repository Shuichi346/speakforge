"""アプリケーション設定モジュール."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション設定."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LM Studio設定
    lm_studio_base_url: str = Field(
        default="http://localhost:1234/v1",
        description="LM StudioのベースURL",
    )
    lm_studio_model: str = Field(
        default="",
        description="使用するモデル名（空の場合はLM Studioでロード中のモデルを使用）",
    )

    # Whisper設定
    whisper_model: str = Field(
        default="base",
        description="Whisperモデル名（tiny, base, small, medium, large）",
    )
    whisper_language: str = Field(
        default="en",
        description="音声認識の言語",
    )

    # TTS設定（Pocket TTS）
    tts_enabled: bool = Field(
        default=True,
        description="テキスト読み上げ機能を有効にするか",
    )
    tts_voice: str = Field(
        default="alba",
        description="Pocket TTSのボイス名（alba, marius, javert, jean, fantine, cosette, eponine, azelma）",
    )
    tts_temperature: float = Field(
        default=0.7,
        description="TTS生成の温度パラメータ",
    )

    # パス設定
    data_dir: Path = Field(
        default=Path("data"),
        description="データディレクトリ",
    )
    models_dir: Path = Field(
        default=Path("models"),
        description="モデルディレクトリ",
    )

    # Gradio設定
    gradio_server_port: int = Field(
        default=7860,
        description="Gradioサーバーのポート番号",
    )
    gradio_share: bool = Field(
        default=False,
        description="Gradioの共有リンクを生成するか",
    )

    @property
    def sentences_dir(self) -> Path:
        """例文データディレクトリ."""
        return self.data_dir / "sentences"

    @property
    def topics_dir(self) -> Path:
        """トピックデータディレクトリ."""
        return self.data_dir / "monologue_topics"

    @property
    def user_data_dir(self) -> Path:
        """ユーザーデータディレクトリ."""
        return self.data_dir / "user_data"

    def get_model_display_name(self) -> str:
        """表示用のモデル名を取得."""
        if self.lm_studio_model:
            return self.lm_studio_model
        return "自動検出"


# シングルトンインスタンス
settings = Settings()
