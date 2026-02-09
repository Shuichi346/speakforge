"""問題生成サービスモジュール."""

import json
import re
from pathlib import Path
from typing import Optional

from speakforge.config import settings
from speakforge.services.llm_service import LLMService


def _create_sentences_schema(category_name: str, difficulty: int) -> dict:
    """口頭英作文の問題生成用スキーマを作成."""
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "sentences_generation",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "カテゴリ名",
                    },
                    "sentences": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "string",
                                    "description": "問題ID",
                                },
                                "japanese": {
                                    "type": "string",
                                    "description": "日本語の文章",
                                },
                                "english_examples": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "英語の模範回答（2つ以上）",
                                },
                                "difficulty": {
                                    "type": "integer",
                                    "description": "難易度（1-3）",
                                },
                                "tags": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "タグ（文法項目、場面など）",
                                },
                            },
                            "required": [
                                "id",
                                "japanese",
                                "english_examples",
                                "difficulty",
                                "tags",
                            ],
                            "additionalProperties": False,
                        },
                        "description": "問題のリスト",
                    },
                },
                "required": ["category", "sentences"],
                "additionalProperties": False,
            },
        },
    }


def _create_topics_schema(category_name: str) -> dict:
    """独り言英会話のトピック生成用スキーマを作成."""
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "topics_generation",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "カテゴリ名",
                    },
                    "topics": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "string",
                                    "description": "トピックID",
                                },
                                "title": {
                                    "type": "string",
                                    "description": "トピックのタイトル",
                                },
                                "description": {
                                    "type": "string",
                                    "description": "トピックの説明",
                                },
                                "hints": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "話すべきポイント（3-5個）",
                                },
                                "difficulty": {
                                    "type": "integer",
                                    "description": "難易度（1-3）",
                                },
                            },
                            "required": [
                                "id",
                                "title",
                                "description",
                                "hints",
                                "difficulty",
                            ],
                            "additionalProperties": False,
                        },
                        "description": "トピックのリスト",
                    },
                },
                "required": ["category", "topics"],
                "additionalProperties": False,
            },
        },
    }


class ProblemGenerator:
    """LLMを使用した問題生成サービス（構造化出力対応）."""

    def __init__(self) -> None:
        """初期化."""
        self._llm = LLMService()

    def generate_sentences(
        self,
        user_request: str,
        category_name: str,
        count: int = 5,
        difficulty: int = 2,
    ) -> Optional[dict]:
        """
        口頭英作文の問題を生成（構造化出力使用）.

        Args:
            user_request: ユーザーのリクエスト（シーンや学習目的の説明）
            category_name: カテゴリ名
            count: 生成する問題数
            difficulty: 難易度（1-3）

        Returns:
            生成された問題データ（JSON形式の辞書）
        """
        prompt = f"""あなたは英語教育の専門家です。以下のユーザーリクエストに基づいて、口頭英作文の練習問題を作成してください。

【ユーザーリクエスト】
{user_request}

【生成条件】
- 問題数: {count}問
- 難易度: {difficulty}（1=初級、2=中級、3=上級）
- カテゴリ名: {category_name}

注意事項：
- idは「{category_name}_001」のように連番で付与
- english_examplesは最低2つ、異なる表現パターンを含める
- tagsは文法項目（現在形、過去形、仮定法など）と場面（ビジネス、日常など）を含める
- 日本語は自然な日本語で、英語は実際に使われる自然な表現にする
- ユーザーのリクエストに沿った実用的な文章を作成する
"""

        try:
            from openai import OpenAI

            client = OpenAI(
                base_url=settings.lm_studio_base_url,
                api_key="lm-studio",
            )

            response = client.chat.completions.create(
                model=self._llm._get_model_name(),
                messages=[
                    {
                        "role": "system",
                        "content": "あなたは英語教育の専門家です。口頭英作文の練習問題を作成してください。",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format=_create_sentences_schema(category_name, difficulty),
                temperature=0.8,
            )

            result_text = response.choices[0].message.content.strip()
            return json.loads(result_text)

        except json.JSONDecodeError as e:
            print(f"JSONパースエラー: {e}")
            return None
        except Exception as e:
            print(f"問題生成エラー: {e}")
            return None

    def generate_topics(
        self,
        user_request: str,
        category_name: str,
        count: int = 3,
        difficulty: int = 2,
    ) -> Optional[dict]:
        """
        独り言英会話のトピックを生成（構造化出力使用）.

        Args:
            user_request: ユーザーのリクエスト（シーンや学習目的の説明）
            category_name: カテゴリ名
            count: 生成するトピック数
            difficulty: 難易度（1-3）

        Returns:
            生成されたトピックデータ（JSON形式の辞書）
        """
        prompt = f"""あなたは英語教育の専門家です。以下のユーザーリクエストに基づいて、独り言英会話の練習トピックを作成してください。

【ユーザーリクエスト】
{user_request}

【生成条件】
- トピック数: {count}個
- 難易度: {difficulty}（1=初級、2=中級、3=上級）
- カテゴリ名: {category_name}

注意事項：
- idは「topic_{category_name}_001」のように連番で付与
- hintsは3-5個程度、話す内容の構成を助けるポイント
- descriptionは具体的に何について話せばよいかを説明
- ユーザーのリクエストに沿った実用的なトピックを作成する
- 約1分間話せる程度の内容量を想定する
"""

        try:
            from openai import OpenAI

            client = OpenAI(
                base_url=settings.lm_studio_base_url,
                api_key="lm-studio",
            )

            response = client.chat.completions.create(
                model=self._llm._get_model_name(),
                messages=[
                    {
                        "role": "system",
                        "content": "あなたは英語教育の専門家です。独り言英会話の練習トピックを作成してください。",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format=_create_topics_schema(category_name),
                temperature=0.8,
            )

            result_text = response.choices[0].message.content.strip()
            return json.loads(result_text)

        except json.JSONDecodeError as e:
            print(f"JSONパースエラー: {e}")
            return None
        except Exception as e:
            print(f"トピック生成エラー: {e}")
            return None

    def save_sentences(self, data: dict, category_name: str) -> Path:
        """
        口頭英作文の問題をファイルに保存.

        Args:
            data: 問題データ
            category_name: カテゴリ名

        Returns:
            保存したファイルのパス
        """
        safe_name = self._sanitize_filename(category_name)
        file_path = settings.sentences_dir / f"{safe_name}.json"

        if file_path.exists():
            data = self._merge_sentences(file_path, data)

        settings.sentences_dir.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return file_path

    def save_topics(self, data: dict, category_name: str) -> Path:
        """
        独り言英会話のトピックをファイルに保存.

        Args:
            data: トピックデータ
            category_name: カテゴリ名

        Returns:
            保存したファイルのパス
        """
        safe_name = self._sanitize_filename(category_name)
        file_path = settings.topics_dir / f"{safe_name}.json"

        if file_path.exists():
            data = self._merge_topics(file_path, data)

        settings.topics_dir.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return file_path

    def _sanitize_filename(self, name: str) -> str:
        """ファイル名として安全な文字列に変換."""
        safe = re.sub(r"[^\w\-]", "_", name.lower())
        safe = re.sub(r"_+", "_", safe)
        safe = safe.strip("_")
        return safe or "custom"

    def _merge_sentences(self, file_path: Path, new_data: dict) -> dict:
        """既存の口頭英作文ファイルに新しい問題をマージ."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)

            max_num = 0
            for s in existing_data.get("sentences", []):
                match = re.search(r"_(\d+)$", s["id"])
                if match:
                    max_num = max(max_num, int(match.group(1)))

            for sentence in new_data.get("sentences", []):
                max_num += 1
                sentence["id"] = f"{new_data['category']}_{max_num:03d}"
                existing_data["sentences"].append(sentence)

            return existing_data

        except (json.JSONDecodeError, KeyError):
            return new_data

    def _merge_topics(self, file_path: Path, new_data: dict) -> dict:
        """既存の独り言英会話ファイルに新しいトピックをマージ."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)

            max_num = 0
            for t in existing_data.get("topics", []):
                match = re.search(r"_(\d+)$", t["id"])
                if match:
                    max_num = max(max_num, int(match.group(1)))

            for topic in new_data.get("topics", []):
                max_num += 1
                topic["id"] = f"topic_{new_data['category']}_{max_num:03d}"
                existing_data["topics"].append(topic)

            return existing_data

        except (json.JSONDecodeError, KeyError):
            return new_data

    def get_existing_categories(self) -> tuple[list[str], list[str]]:
        """既存のカテゴリ一覧を取得."""
        sentence_categories = []
        topic_categories = []

        if settings.sentences_dir.exists():
            for f in settings.sentences_dir.glob("*.json"):
                sentence_categories.append(f.stem)

        if settings.topics_dir.exists():
            for f in settings.topics_dir.glob("*.json"):
                topic_categories.append(f.stem)

        return sorted(sentence_categories), sorted(topic_categories)
