"""独り言英会話練習モジュール."""

from dataclasses import dataclass
from typing import Optional

from speakforge.data.sentence_loader import SentenceLoader, Topic
from speakforge.services.audio_utils import AudioUtils
from speakforge.services.llm_service import LLMService
from speakforge.services.speech_to_text import SpeechToTextService


@dataclass
class MonologueResult:
    """独り言英会話の結果."""

    topic: Topic
    transcribed_text: str
    duration_seconds: float
    word_count: int
    wpm: float
    overall_score: int
    cefr_level: str
    grammar_corrections: list[dict]
    expression_suggestions: list[dict]
    structure_feedback: str
    model_answer: str
    strengths: list[str]
    areas_to_improve: list[str]


class MonologuePractice:
    """独り言英会話練習クラス."""

    def __init__(self) -> None:
        """初期化."""
        self._loader = SentenceLoader()
        self._stt = SpeechToTextService()
        self._llm = LLMService()
        self._current_topic: Optional[Topic] = None
        self._current_category: str = ""

    def get_categories(self) -> list[str]:
        """利用可能なカテゴリ一覧を取得."""
        return self._loader.get_topic_categories()

    def set_category(self, category: str) -> None:
        """カテゴリを設定."""
        self._current_category = category

    def get_next_topic(self) -> Optional[Topic]:
        """次のトピックを順番に取得."""
        if not self._current_category:
            categories = self.get_categories()
            if categories:
                self._current_category = categories[0]

        # 順番に取得（ランダムではなく）
        self._current_topic = self._loader.get_next_topic(self._current_category)
        return self._current_topic

    def get_current_topic(self) -> Optional[Topic]:
        """現在のトピックを取得."""
        return self._current_topic

    def get_progress(self) -> tuple[int, int]:
        """
        現在の進捗を取得.

        Returns:
            (現在のトピック番号, 全トピック数)のタプル
        """
        if not self._current_category:
            return (0, 0)
        return self._loader.get_current_position(self._current_category, "topic")

    def reset_progress(self) -> None:
        """進捗をリセットして最初から."""
        if self._current_category:
            self._loader.reset_position(self._current_category)

    def evaluate_monologue(
        self,
        audio_data: tuple[int, any],
    ) -> Optional[MonologueResult]:
        """
        独り言音声を評価.

        Args:
            audio_data: 録音された音声データ

        Returns:
            評価結果
        """
        if self._current_topic is None:
            return None

        if not AudioUtils.is_audio_valid(audio_data):
            return None

        # 音声の長さを取得
        duration = AudioUtils.get_audio_duration(audio_data)

        # 音声認識
        transcribed_text = self._stt.transcribe(audio_data, language="en")

        if not transcribed_text:
            return None

        # LLMで添削
        result = self._llm.evaluate_monologue(
            topic=self._current_topic.title,
            transcribed_text=transcribed_text,
            duration_seconds=duration,
        )

        # 結果を作成
        return MonologueResult(
            topic=self._current_topic,
            transcribed_text=transcribed_text,
            duration_seconds=result.get("duration_seconds", duration),
            word_count=result.get("word_count", 0),
            wpm=result.get("wpm", 0),
            overall_score=result.get("overall_score", 0),
            cefr_level=result.get("cefr_level", "判定不可"),
            grammar_corrections=result.get("grammar_corrections", []),
            expression_suggestions=result.get("expression_suggestions", []),
            structure_feedback=result.get("structure_feedback", ""),
            model_answer=result.get("model_answer", ""),
            strengths=result.get("strengths", []),
            areas_to_improve=result.get("areas_to_improve", []),
        )
