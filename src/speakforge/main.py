"""アプリケーションエントリーポイント."""

from speakforge.config import settings
from speakforge.ui import create_app


def main() -> None:
    """アプリケーションを起動."""
    print("=" * 50)
    print("SpeakForge を起動中...")
    print("=" * 50)
    print(f"LM Studio URL: {settings.lm_studio_base_url}")
    print(f"LM Studio モデル: {settings.get_model_display_name()}")
    print(f"Whisper モデル: {settings.whisper_model}")
    print(f"サーバーポート: {settings.gradio_server_port}")
    print("=" * 50)

    app = create_app()

    app.launch(
        server_port=settings.gradio_server_port,
        share=settings.gradio_share,
        show_error=True,
    )


if __name__ == "__main__":
    main()
