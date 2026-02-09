"""スマート復習モジュール."""

from speakforge.data.sentence_loader import Sentence, SentenceLoader
from speakforge.data.user_history import UserHistory


class SmartReview:
    """スマート復習クラス."""

    def __init__(self) -> None:
        """初期化."""
        self._history = UserHistory()
        self._loader = SentenceLoader()

    def get_review_sentences(self, limit: int = 10) -> list[Sentence]:
        """
        復習が必要な問題を取得.

        Args:
            limit: 取得する問題数

        Returns:
            復習用の問題リスト
        """
        # 間違えた問題のIDを取得
        incorrect_ids = self._history.get_incorrect_sentence_ids(limit=limit * 2)

        # 対応する問題を取得
        sentences = []
        for sentence_id in incorrect_ids:
            sentence = self._loader.get_sentence_by_id(sentence_id)
            if sentence:
                sentences.append(sentence)
            if len(sentences) >= limit:
                break

        return sentences

    def get_weak_tags(self) -> list[tuple[str, int]]:
        """
        苦手なタグ（文法項目など）を取得.

        Returns:
            (タグ名, 間違えた回数)のリスト
        """
        return self._history.get_weak_tags()

    def mark_as_reviewed(self, sentence_id: str) -> None:
        """
        問題を復習済みとしてマーク.

        Args:
            sentence_id: 問題ID
        """
        self._history.mark_as_reviewed(sentence_id)

    def get_statistics(self) -> dict:
        """
        学習統計を取得.

        Returns:
            統計情報の辞書
        """
        return self._history.get_statistics()
