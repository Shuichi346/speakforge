"""ユーザー履歴管理モジュール."""

import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from speakforge.config import settings


@dataclass
class PracticeResult:
    """練習結果."""

    sentence_id: str
    category: str
    japanese: str
    user_answer: str
    is_correct: bool
    score: int
    tags: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    reviewed: bool = False


class UserHistory:
    """ユーザー履歴管理."""

    _instance: Optional["UserHistory"] = None
    _history: list[PracticeResult]
    _loaded: bool = False

    def __new__(cls) -> "UserHistory":
        """シングルトンパターンの実装."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._history = []
            cls._instance._loaded = False
        return cls._instance

    def __init__(self) -> None:
        """初期化処理."""
        if not self._loaded:
            self._history_file = settings.user_data_dir / "history.json"
            self._load_history()
            self._loaded = True

    def _load_history(self) -> None:
        """履歴をロード."""
        if self._history_file.exists():
            try:
                with open(self._history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._history = [PracticeResult(**item) for item in data]
                print(f"履歴をロードしました: {len(self._history)}件")
            except (json.JSONDecodeError, TypeError) as e:
                print(f"履歴の読み込みエラー: {e}")
                self._history = []
        else:
            settings.user_data_dir.mkdir(parents=True, exist_ok=True)
            print("履歴ファイルが存在しません。新規作成します。")

    def _save_history(self) -> None:
        """履歴を保存."""
        settings.user_data_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self._history_file, "w", encoding="utf-8") as f:
                json.dump(
                    [asdict(r) for r in self._history],
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
            print(f"履歴を保存しました: {len(self._history)}件")
        except Exception as e:
            print(f"履歴の保存エラー: {e}")

    def add_result(self, result: PracticeResult) -> None:
        """結果を追加."""
        self._history.append(result)
        self._save_history()
        print(f"結果を追加しました: {result.sentence_id}, 正解: {result.is_correct}, スコア: {result.score}")

    def get_incorrect_sentence_ids(self, limit: int = 20) -> list[str]:
        """
        間違えた問題のIDを取得（復習用）.

        Args:
            limit: 取得する最大数

        Returns:
            問題IDのリスト
        """
        incorrect_counts: Counter = Counter()
        for result in self._history:
            if not result.is_correct and not result.reviewed:
                incorrect_counts[result.sentence_id] += 1

        sorted_ids = [
            sentence_id
            for sentence_id, _ in incorrect_counts.most_common(limit)
        ]
        return sorted_ids

    def get_weak_tags(self) -> list[tuple[str, int]]:
        """
        苦手なタグを取得.

        Returns:
            (タグ名, 間違えた回数)のリスト
        """
        tag_counts: Counter = Counter()
        for result in self._history:
            if not result.is_correct:
                for tag in result.tags:
                    tag_counts[tag] += 1

        return tag_counts.most_common(10)

    def mark_as_reviewed(self, sentence_id: str) -> None:
        """問題を復習済みとしてマーク."""
        for result in self._history:
            if result.sentence_id == sentence_id and not result.is_correct:
                result.reviewed = True
        self._save_history()

    def get_statistics(self) -> dict:
        """
        学習統計を取得.

        Returns:
            統計情報の辞書
        """
        if not self._history:
            return {
                "total_attempts": 0,
                "correct_count": 0,
                "incorrect_count": 0,
                "accuracy_rate": 0.0,
                "average_score": 0.0,
                "practice_days": 0,
            }

        total = len(self._history)
        correct = sum(1 for r in self._history if r.is_correct)
        scores = [r.score for r in self._history]

        practice_dates = set(
            datetime.fromisoformat(r.timestamp).date()
            for r in self._history
        )

        return {
            "total_attempts": total,
            "correct_count": correct,
            "incorrect_count": total - correct,
            "accuracy_rate": (correct / total * 100) if total > 0 else 0.0,
            "average_score": sum(scores) / len(scores) if scores else 0.0,
            "practice_days": len(practice_dates),
        }

    def get_recent_results(self, limit: int = 10) -> list[PracticeResult]:
        """
        最近の結果を取得.

        Args:
            limit: 取得する数

        Returns:
            結果のリスト
        """
        return self._history[-limit:][::-1]

    def get_history_count(self) -> int:
        """履歴の件数を取得."""
        return len(self._history)
