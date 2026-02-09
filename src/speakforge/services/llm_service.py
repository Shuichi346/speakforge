"""LLMサービスモジュール."""

import json
from typing import Optional

from openai import OpenAI

from speakforge.config import settings


# JSON Schemaの定義
SENTENCE_JUDGMENT_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "sentence_judgment",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "is_correct": {
                    "type": "boolean",
                    "description": "ユーザーの回答が正解かどうか",
                },
                "score": {
                    "type": "integer",
                    "description": "0から100のスコア",
                },
                "feedback": {
                    "type": "string",
                    "description": "フィードバック（必ず日本語で記述）",
                },
                "grammar_issues": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "文法の問題点のリスト（必ず日本語で記述）",
                },
                "better_expressions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "より良い表現の提案リスト（英語の例文は可、説明は日本語）",
                },
                "explanation": {
                    "type": "string",
                    "description": "詳細な解説（必ず日本語で記述）",
                },
            },
            "required": [
                "is_correct",
                "score",
                "feedback",
                "grammar_issues",
                "better_expressions",
                "explanation",
            ],
            "additionalProperties": False,
        },
    },
}

MONOLOGUE_EVALUATION_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "monologue_evaluation",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "overall_score": {
                    "type": "integer",
                    "description": "0から100の総合スコア",
                },
                "cefr_level": {
                    "type": "string",
                    "description": "CEFRレベル（A1, A2, B1, B2, C1, C2のいずれか）",
                },
                "grammar_corrections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "original": {
                                "type": "string",
                                "description": "間違った部分",
                            },
                            "corrected": {
                                "type": "string",
                                "description": "修正後",
                            },
                            "explanation": {
                                "type": "string",
                                "description": "説明（日本語）",
                            },
                        },
                        "required": ["original", "corrected", "explanation"],
                        "additionalProperties": False,
                    },
                    "description": "文法修正のリスト",
                },
                "expression_suggestions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "original": {
                                "type": "string",
                                "description": "元の表現",
                            },
                            "suggested": {
                                "type": "string",
                                "description": "より良い表現",
                            },
                            "reason": {
                                "type": "string",
                                "description": "理由（日本語）",
                            },
                        },
                        "required": ["original", "suggested", "reason"],
                        "additionalProperties": False,
                    },
                    "description": "表現改善の提案リスト",
                },
                "structure_feedback": {
                    "type": "string",
                    "description": "全体構成へのフィードバック（日本語）",
                },
                "model_answer": {
                    "type": "string",
                    "description": "模範回答（英語で60-80語程度）",
                },
                "strengths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "良かった点のリスト（日本語）",
                },
                "areas_to_improve": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "改善点のリスト（日本語）",
                },
            },
            "required": [
                "overall_score",
                "cefr_level",
                "grammar_corrections",
                "expression_suggestions",
                "structure_feedback",
                "model_answer",
                "strengths",
                "areas_to_improve",
            ],
            "additionalProperties": False,
        },
    },
}


class LLMService:
    """LM Studioを使用したLLMサービス（構造化出力対応）."""

    _instance: Optional["LLMService"] = None
    _client: Optional[OpenAI] = None
    _model_name: Optional[str] = None

    def __new__(cls) -> "LLMService":
        """シングルトンパターンの実装."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """初期化処理."""
        if self._client is None:
            self._client = OpenAI(
                base_url=settings.lm_studio_base_url,
                api_key="lm-studio",
            )
            self._initialize_model()

    def _initialize_model(self) -> None:
        """モデル名を初期化."""
        if settings.lm_studio_model:
            self._model_name = settings.lm_studio_model
            print(f"LLMモデル（設定ファイル指定）: {self._model_name}")
            return

        try:
            models = self._client.models.list()
            if models.data:
                self._model_name = models.data[0].id
                print(f"LLMモデル（自動検出）: {self._model_name}")
                return
        except Exception as e:
            print(f"モデル一覧の取得に失敗: {e}")

        self._model_name = "local-model"
        print(f"LLMモデル（フォールバック）: {self._model_name}")

    def _get_model_name(self) -> str:
        """使用するモデル名を取得."""
        if self._model_name:
            return self._model_name
        return "local-model"

    def get_current_model(self) -> str:
        """現在使用中のモデル名を取得（UI表示用）."""
        return self._get_model_name()

    def judge_sentence(
        self,
        japanese: str,
        user_answer: str,
        model_answers: list[str],
    ) -> dict:
        """
        口頭英作文の回答を判定（構造化出力使用）.
        """
        prompt = f"""あなたは英語教師です。以下の日本語文に対するユーザーの英語回答を評価してください。

【日本語】
{japanese}

【模範回答例】
{chr(10).join(f"- {ans}" for ans in model_answers)}

【ユーザーの回答】
{user_answer}

【採点基準】
スコアは以下の基準で0〜100点で採点してください：

- 90〜100点: 模範回答と同等またはそれ以上。文法・語彙・自然さすべて完璧
- 80〜89点: 意味が正確に伝わり、文法も正しい。細かい表現の違いのみ
- 70〜79点: 意味は伝わるが、より自然な表現がある。軽微な文法ミス
- 60〜69点: 意味は概ね伝わるが、文法ミスや不自然な表現がある
- 50〜59点: 意味は何とか伝わるが、複数の文法ミスや不自然な表現
- 40〜49点: 意味が部分的にしか伝わらない。重大な文法ミス
- 30〜39点: 意味がほとんど伝わらない
- 0〜29点: 全く意味が伝わらない、または無回答

【is_correctの基準】
- スコアが70点以上の場合: is_correct = true
- スコアが70点未満の場合: is_correct = false

【重要】
- feedback, grammar_issues, explanationは必ず日本語で記述してください
- better_expressionsは英語の例文を含めても構いませんが、説明部分は日本語にしてください
"""

        default_result = {
            "is_correct": False,
            "score": 0,
            "feedback": "判定中にエラーが発生しました。もう一度お試しください。",
            "grammar_issues": [],
            "better_expressions": [],
            "explanation": "",
        }

        try:
            response = self._client.chat.completions.create(
                model=self._get_model_name(),
                messages=[
                    {
                        "role": "system",
                        "content": "あなたは日本人向けの英語教師です。採点基準に従って厳密に採点し、フィードバックや解説は必ず日本語で回答してください。",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format=SENTENCE_JUDGMENT_SCHEMA,
                temperature=0.3,
            )

            result_text = response.choices[0].message.content.strip()
            return json.loads(result_text)

        except json.JSONDecodeError as e:
            print(f"JSONパースエラー: {e}")
            return default_result
        except Exception as e:
            print(f"LLM呼び出しエラー: {e}")
            return default_result

    def evaluate_monologue(
        self,
        topic: str,
        transcribed_text: str,
        duration_seconds: float,
    ) -> dict:
        """
        独り言英会話の添削（構造化出力使用）.

        Args:
            topic: トピック
            transcribed_text: 認識されたテキスト
            duration_seconds: 発話時間（秒）

        Returns:
            添削結果の辞書
        """
        word_count = len(transcribed_text.split())
        wpm = (word_count / duration_seconds) * 60 if duration_seconds > 0 else 0

        prompt = f"""あなたは英語教師です。以下のトピックについて話されたスピーチを添削してください。

【トピック】
{topic}

【スピーチ内容】
{transcribed_text}

【発話統計】
- 発話時間: {duration_seconds:.1f}秒
- 単語数: {word_count}語
- WPM: {wpm:.1f}

【採点基準】
overall_scoreは以下の基準で0〜100点で採点してください：

- 90〜100点: 文法・語彙・構成すべて優秀。トピックを深く掘り下げ、説得力がある
- 80〜89点: 文法ミスがほとんどなく、論理的な構成。自然な英語表現を使用
- 70〜79点: 意味は明確に伝わる。軽微な文法ミスや不自然な表現が少しある
- 60〜69点: 意味は伝わるが、複数の文法ミスや構成の問題がある
- 50〜59点: 意味が部分的に伝わる。文法ミスが多く、構成が不明確
- 40〜49点: トピックに沿っているが、理解しにくい部分が多い
- 30〜39点: トピックとの関連性が薄い、または理解困難
- 0〜29点: ほぼ理解不能、または発話がほとんどない

【CEFRレベル判定基準】
スコアとWPMを総合的に判断して決定してください：

- C2: スコア90点以上かつWPM 150以上。ネイティブに近い流暢さ
- C1: スコア80〜89点かつWPM 130以上。複雑な話題も自在に表現
- B2: スコア70〜79点かつWPM 110以上。明確で詳細な説明が可能
- B1: スコア60〜69点かつWPM 90以上。日常的な話題を説明可能
- A2: スコア50〜59点かつWPM 70以上。基本的な情報を伝達可能
- A1: スコア50点未満またはWPM 70未満。基礎的な表現のみ

【重要な注意事項】
- 該当がない項目は空配列[]にしてください
- grammar_corrections, expression_suggestionsの説明は必ず日本語で記述
- structure_feedback, strengths, areas_to_improveは必ず日本語で記述
- model_answerは英語で60-80語程度で作成してください
"""

        default_result = {
            "overall_score": 0,
            "cefr_level": "判定不可",
            "grammar_corrections": [],
            "expression_suggestions": [],
            "structure_feedback": "添削中にエラーが発生しました。",
            "model_answer": "",
            "strengths": [],
            "areas_to_improve": [],
        }

        try:
            response = self._client.chat.completions.create(
                model=self._get_model_name(),
                messages=[
                    {
                        "role": "system",
                        "content": "あなたは日本人向けの英語教師です。採点基準に従って厳密に採点し、フィードバックや解説は必ず日本語で回答してください。",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format=MONOLOGUE_EVALUATION_SCHEMA,
                temperature=0.3,
            )

            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)

            # 統計情報を追加
            result["word_count"] = word_count
            result["wpm"] = round(wpm, 1)
            result["duration_seconds"] = round(duration_seconds, 1)

            return result

        except json.JSONDecodeError as e:
            print(f"JSONパースエラー: {e}")
            return default_result
        except Exception as e:
            print(f"LLM呼び出しエラー: {e}")
            return default_result

    def answer_question(self, context: str, question: str) -> str:
        """
        ユーザーの質問に回答.

        Args:
            context: 文脈（問題文や回答など）
            question: ユーザーの質問

        Returns:
            回答テキスト
        """
        prompt = f"""以下の文脈に基づいて、ユーザーの質問に200文字以内で日本語で簡潔に回答してください。

【文脈】
{context}

【質問】
{question}
"""

        try:
            response = self._client.chat.completions.create(
                model=self._get_model_name(),
                messages=[
                    {
                        "role": "system",
                        "content": "あなたは英語教師です。日本語で回答してください。",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"LLM呼び出しエラー: {e}")
            return "回答の生成中にエラーが発生しました。"
