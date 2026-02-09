"""口頭英作文練習モジュール."""

from dataclasses import dataclass
from typing import Optional

from speakforge.data.sentence_loader import Sentence, SentenceLoader
from speakforge.data.user_history import PracticeResult, UserHistory
from speakforge.services.audio_utils import AudioUtils
from speakforge.services.llm_service import LLMService
from speakforge.services.speech_to_text import SpeechToTextService


@dataclass
class SentenceResult:
    """口頭英作文の結果."""

    sentence: Sentence
    user_answer: str
    is_correct: bool
    score: int
    feedback: str
    grammar_issues: list[str]
    better_expressions: list[str]
    explanation: str


class SentencePractice:
    """口頭英作文練習クラス."""

    def __init__(self) -> None:
        """初期化."""
        self._loader = SentenceLoader()
        self._stt = SpeechToTextService()
        self._llm = LLMService()
        self._history = UserHistory()
        self._current_sentence: Optional[Sentence] = None
        self._current_category: str = ""

    def get_categories(self) -> list[str]:
        """利用可能なカテゴリ一覧を取得."""
        return self._loader.get_categories()

    def set_category(self, category: str) -> None:
        """カテゴリを設定."""
        self._current_category = category

    def get_next_sentence(self) -> Optional[Sentence]:
        """次の問題を順番に取得."""
        if not self._current_category:
            categories = self.get_categories()
            if categories:
                self._current_category = categories[0]

        # 順番に取得（ランダムではなく）
        self._current_sentence = self._loader.get_next_sentence(
            self._current_category
        )
        return self._current_sentence

    def get_current_sentence(self) -> Optional[Sentence]:
        """現在の問題を取得."""
        return self._current_sentence

    def get_progress(self) -> tuple[int, int]:
        """
        現在の進捗を取得.

        Returns:
            (現在の問題番号, 全問題数)のタプル
        """
        if not self._current_category:
            return (0, 0)
        return self._loader.get_current_position(self._current_category, "sentence")

    def reset_progress(self) -> None:
        """進捗をリセットして最初から."""
        if self._current_category:
            self._loader.reset_position(self._current_category)

    def evaluate_answer(
        self,
        audio_data: tuple[int, any],
    ) -> Optional[SentenceResult]:
        """
        音声回答を評価.

        Args:
            audio_data: 録音された音声データ

        Returns:
            評価結果
        """
        if self._current_sentence is None:
            return None

        if not AudioUtils.is_audio_valid(audio_data):
            return None

        # 音声認識
        user_answer = self._stt.transcribe(audio_data, language="en")

        if not user_answer:
            return None

        # LLMで判定
        result = self._llm.judge_sentence(
            japanese=self._current_sentence.japanese,
            user_answer=user_answer,
            model_answers=self._current_sentence.english_examples,
        )

        # 結果を作成
        sentence_result = SentenceResult(
            sentence=self._current_sentence,
            user_answer=user_answer,
            is_correct=result.get("is_correct", False),
            score=result.get("score", 0),
            feedback=result.get("feedback", ""),
            grammar_issues=result.get("grammar_issues", []),
            better_expressions=result.get("better_expressions", []),
            explanation=result.get("explanation", ""),
        )

        # 履歴に保存
        category = self._current_sentence.category or self._current_category
        practice_result = PracticeResult(
            sentence_id=self._current_sentence.id,
            category=category,
            japanese=self._current_sentence.japanese,
            user_answer=user_answer,
            is_correct=sentence_result.is_correct,
            score=sentence_result.score,
            tags=self._current_sentence.tags,
        )
        self._history.add_result(practice_result)

        return sentence_result

    def ask_question(self, question: str) -> str:
        """
        現在の問題について質問.

        Args:
            question: 質問内容

        Returns:
            回答
        """
        if self._current_sentence is None:
            return "問題を選択してから質問してください。"

        context = f"""
問題（日本語）: {self._current_sentence.japanese}
模範回答: {', '.join(self._current_sentence.english_examples)}
"""
        return self._llm.answer_question(context, question)
