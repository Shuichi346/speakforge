"""例文・トピックローダーモジュール."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from speakforge.config import settings


@dataclass
class Sentence:
    """例文データ."""

    id: str
    japanese: str
    english_examples: list[str]
    difficulty: int = 1
    tags: list[str] = field(default_factory=list)
    category: str = ""


@dataclass
class Topic:
    """トピックデータ."""

    id: str
    title: str
    description: str
    hints: list[str] = field(default_factory=list)
    difficulty: int = 1
    category: str = ""


class SentenceLoader:
    """例文・トピックローダー."""

    _instance: Optional["SentenceLoader"] = None

    def __new__(cls) -> "SentenceLoader":
        """シングルトンパターンの実装."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """初期化."""
        if self._initialized:
            return

        self._sentences: dict[str, list[Sentence]] = {}
        self._topics: dict[str, list[Topic]] = {}
        self._sentence_index: dict[str, Sentence] = {}

        # カテゴリごとの現在位置を管理
        self._sentence_positions: dict[str, int] = {}
        self._topic_positions: dict[str, int] = {}

        self._load_all_data()
        self._initialized = True

    def _load_all_data(self) -> None:
        """全データをロード."""
        self._load_sentences()
        self._load_topics()

    def _load_sentences(self) -> None:
        """例文データをロード."""
        sentences_dir = settings.sentences_dir

        if not sentences_dir.exists():
            sentences_dir.mkdir(parents=True, exist_ok=True)
            self._create_sample_sentences()
            return

        for json_file in sentences_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                category = data.get("category", json_file.stem)
                sentences = []

                for item in data.get("sentences", []):
                    sentence = Sentence(
                        id=item.get("id", f"{category}_{len(sentences)}"),
                        japanese=item.get("japanese", ""),
                        english_examples=item.get("english_examples", []),
                        difficulty=item.get("difficulty", 1),
                        tags=item.get("tags", []),
                        category=category,
                    )
                    sentences.append(sentence)
                    self._sentence_index[sentence.id] = sentence

                self._sentences[category] = sentences
                # 位置を初期化
                self._sentence_positions[category] = 0

            except (json.JSONDecodeError, KeyError) as e:
                print(f"例文ファイルの読み込みエラー: {json_file} - {e}")

        if not self._sentences:
            self._create_sample_sentences()

    def _load_topics(self) -> None:
        """トピックデータをロード."""
        topics_dir = settings.topics_dir

        if not topics_dir.exists():
            topics_dir.mkdir(parents=True, exist_ok=True)
            self._create_sample_topics()
            return

        for json_file in topics_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                category = data.get("category", json_file.stem)
                topics = []

                for item in data.get("topics", []):
                    topic = Topic(
                        id=item.get("id", f"{category}_{len(topics)}"),
                        title=item.get("title", ""),
                        description=item.get("description", ""),
                        hints=item.get("hints", []),
                        difficulty=item.get("difficulty", 1),
                        category=category,
                    )
                    topics.append(topic)

                self._topics[category] = topics
                # 位置を初期化
                self._topic_positions[category] = 0

            except (json.JSONDecodeError, KeyError) as e:
                print(f"トピックファイルの読み込みエラー: {json_file} - {e}")

        if not self._topics:
            self._create_sample_topics()

    def _create_sample_sentences(self) -> None:
        """サンプル例文を作成."""
        sample_data = {
            "business": {
                "category": "business",
                "sentences": [
                    {
                        "id": "biz_001",
                        "japanese": "私は昨日オンラインで注文をしました。",
                        "english_examples": [
                            "I ordered something online yesterday.",
                            "I placed an order online yesterday.",
                        ],
                        "difficulty": 1,
                        "tags": ["過去形", "オンラインショッピング"],
                    },
                    {
                        "id": "biz_002",
                        "japanese": "CEOが予算を承認しました。",
                        "english_examples": [
                            "The CEO approved the budget.",
                            "The CEO has approved the budget.",
                        ],
                        "difficulty": 2,
                        "tags": ["過去形", "ビジネス用語"],
                    },
                    {
                        "id": "biz_003",
                        "japanese": "私たちは昨日クライアントに会いました。",
                        "english_examples": [
                            "We met with the client yesterday.",
                            "We met the client yesterday.",
                        ],
                        "difficulty": 1,
                        "tags": ["過去形", "クライアント対応"],
                    },
                    {
                        "id": "biz_004",
                        "japanese": "私たちの会社には15の部署があります。",
                        "english_examples": [
                            "Our company has 15 departments.",
                            "There are 15 departments in our company.",
                        ],
                        "difficulty": 1,
                        "tags": ["現在形", "会社組織"],
                    },
                    {
                        "id": "biz_005",
                        "japanese": "会議を来週に延期しましょう。",
                        "english_examples": [
                            "Let's postpone the meeting to next week.",
                            "Let's reschedule the meeting for next week.",
                        ],
                        "difficulty": 2,
                        "tags": ["提案", "スケジュール"],
                    },
                ],
            },
            "engineer": {
                "category": "engineer",
                "sentences": [
                    {
                        "id": "eng_001",
                        "japanese": "ウェブサイトがダウンしています。ログを確認しています。",
                        "english_examples": [
                            "The website is down. I'm checking the logs.",
                            "The website is down. Checking the logs.",
                        ],
                        "difficulty": 1,
                        "tags": ["障害対応", "現在進行形"],
                    },
                    {
                        "id": "eng_002",
                        "japanese": "サービス中断についてチームに連絡しましょう。",
                        "english_examples": [
                            "Let's notify the team about the service interruption.",
                            "Let's tell the team about the service outage.",
                        ],
                        "difficulty": 2,
                        "tags": ["提案", "障害対応"],
                    },
                    {
                        "id": "eng_003",
                        "japanese": "このAPIはレート制限があります。",
                        "english_examples": [
                            "This API has rate limiting.",
                            "This API is rate-limited.",
                        ],
                        "difficulty": 2,
                        "tags": ["API", "技術用語"],
                    },
                    {
                        "id": "eng_004",
                        "japanese": "コードレビューをお願いできますか？",
                        "english_examples": [
                            "Could you review my code?",
                            "Can you do a code review?",
                        ],
                        "difficulty": 1,
                        "tags": ["依頼", "コードレビュー"],
                    },
                    {
                        "id": "eng_005",
                        "japanese": "デプロイは明日の朝に予定されています。",
                        "english_examples": [
                            "The deployment is scheduled for tomorrow morning.",
                            "We're scheduled to deploy tomorrow morning.",
                        ],
                        "difficulty": 2,
                        "tags": ["受動態", "デプロイ"],
                    },
                ],
            },
            "daily": {
                "category": "daily",
                "sentences": [
                    {
                        "id": "daily_001",
                        "japanese": "今日の天気はどうですか？",
                        "english_examples": [
                            "How's the weather today?",
                            "What's the weather like today?",
                        ],
                        "difficulty": 1,
                        "tags": ["疑問文", "天気"],
                    },
                    {
                        "id": "daily_002",
                        "japanese": "週末は何をしましたか？",
                        "english_examples": [
                            "What did you do on the weekend?",
                            "What did you do over the weekend?",
                        ],
                        "difficulty": 1,
                        "tags": ["疑問文", "過去形"],
                    },
                    {
                        "id": "daily_003",
                        "japanese": "コーヒーをもう一杯いただけますか？",
                        "english_examples": [
                            "Could I have another cup of coffee?",
                            "Can I get another coffee?",
                        ],
                        "difficulty": 1,
                        "tags": ["依頼", "レストラン"],
                    },
                ],
            },
        }

        sentences_dir = settings.sentences_dir
        sentences_dir.mkdir(parents=True, exist_ok=True)

        for category, data in sample_data.items():
            file_path = sentences_dir / f"{category}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            sentences = []
            for item in data["sentences"]:
                sentence = Sentence(
                    id=item["id"],
                    japanese=item["japanese"],
                    english_examples=item["english_examples"],
                    difficulty=item["difficulty"],
                    tags=item["tags"],
                    category=category,
                )
                sentences.append(sentence)
                self._sentence_index[sentence.id] = sentence
            self._sentences[category] = sentences
            self._sentence_positions[category] = 0

    def _create_sample_topics(self) -> None:
        """サンプルトピックを作成."""
        sample_data = {
            "business": {
                "category": "business",
                "topics": [
                    {
                        "id": "topic_biz_001",
                        "title": "あなたの仕事について説明してください",
                        "description": "自分の仕事内容、役割、やりがいについて話してください。",
                        "hints": ["職種", "主な業務", "チーム構成", "やりがい"],
                        "difficulty": 1,
                    },
                    {
                        "id": "topic_biz_002",
                        "title": "最近取り組んだプロジェクトについて",
                        "description": "最近のプロジェクトの内容と自分の貢献について話してください。",
                        "hints": ["プロジェクトの目的", "自分の役割", "課題", "成果"],
                        "difficulty": 2,
                    },
                ],
            },
            "engineer": {
                "category": "engineer",
                "topics": [
                    {
                        "id": "topic_eng_001",
                        "title": "印象に残っている技術的な挑戦",
                        "description": "技術的に難しかった経験とその解決方法について話してください。",
                        "hints": ["どんな問題だったか", "どう解決したか", "学んだこと"],
                        "difficulty": 2,
                    },
                    {
                        "id": "topic_eng_002",
                        "title": "お気に入りの技術やツール",
                        "description": "普段使っている技術やツールで気に入っているものについて話してください。",
                        "hints": ["何を使っているか", "なぜ好きか", "どう活用しているか"],
                        "difficulty": 1,
                    },
                ],
            },
            "daily": {
                "category": "daily",
                "topics": [
                    {
                        "id": "topic_daily_001",
                        "title": "あなたの趣味について",
                        "description": "趣味とその魅力について話してください。",
                        "hints": ["何が趣味か", "いつ始めたか", "なぜ好きか"],
                        "difficulty": 1,
                    },
                    {
                        "id": "topic_daily_002",
                        "title": "最近見た映画やドラマについて",
                        "description": "最近見た作品の感想を話してください。",
                        "hints": ["タイトル", "あらすじ", "感想", "おすすめポイント"],
                        "difficulty": 1,
                    },
                ],
            },
        }

        topics_dir = settings.topics_dir
        topics_dir.mkdir(parents=True, exist_ok=True)

        for category, data in sample_data.items():
            file_path = topics_dir / f"{category}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            topics = []
            for item in data["topics"]:
                topic = Topic(
                    id=item["id"],
                    title=item["title"],
                    description=item["description"],
                    hints=item["hints"],
                    difficulty=item["difficulty"],
                    category=category,
                )
                topics.append(topic)
            self._topics[category] = topics
            self._topic_positions[category] = 0

    def get_categories(self) -> list[str]:
        """例文のカテゴリ一覧を取得."""
        return list(self._sentences.keys())

    def get_topic_categories(self) -> list[str]:
        """トピックのカテゴリ一覧を取得."""
        return list(self._topics.keys())

    def get_sentences(self, category: str) -> list[Sentence]:
        """指定カテゴリの例文を取得."""
        return self._sentences.get(category, [])

    def get_topics(self, category: str) -> list[Topic]:
        """指定カテゴリのトピックを取得."""
        return self._topics.get(category, [])

    def get_next_sentence(self, category: str) -> Optional[Sentence]:
        """
        次の例文を順番に取得.

        Args:
            category: カテゴリ名

        Returns:
            次の例文（最後まで行ったら最初に戻る）
        """
        sentences = self.get_sentences(category)
        if not sentences:
            return None

        # 現在位置を取得
        position = self._sentence_positions.get(category, 0)

        # 例文を取得
        sentence = sentences[position]

        # 次の位置に進める（最後まで行ったら最初に戻る）
        next_position = (position + 1) % len(sentences)
        self._sentence_positions[category] = next_position

        return sentence

    def get_next_topic(self, category: str) -> Optional[Topic]:
        """
        次のトピックを順番に取得.

        Args:
            category: カテゴリ名

        Returns:
            次のトピック（最後まで行ったら最初に戻る）
        """
        topics = self.get_topics(category)
        if not topics:
            return None

        # 現在位置を取得
        position = self._topic_positions.get(category, 0)

        # トピックを取得
        topic = topics[position]

        # 次の位置に進める（最後まで行ったら最初に戻る）
        next_position = (position + 1) % len(topics)
        self._topic_positions[category] = next_position

        return topic

    def get_random_sentence(self, category: str) -> Optional[Sentence]:
        """
        ランダムな例文を取得（後方互換性のため残す）.

        Note:
            get_next_sentence()の使用を推奨
        """
        return self.get_next_sentence(category)

    def get_random_topic(self, category: str) -> Optional[Topic]:
        """
        ランダムなトピックを取得（後方互換性のため残す）.

        Note:
            get_next_topic()の使用を推奨
        """
        return self.get_next_topic(category)

    def get_sentence_by_id(self, sentence_id: str) -> Optional[Sentence]:
        """IDから例文を取得."""
        return self._sentence_index.get(sentence_id)

    def reset_position(self, category: str) -> None:
        """
        指定カテゴリの位置をリセット.

        Args:
            category: カテゴリ名
        """
        if category in self._sentence_positions:
            self._sentence_positions[category] = 0
        if category in self._topic_positions:
            self._topic_positions[category] = 0

    def get_current_position(self, category: str, content_type: str = "sentence") -> tuple[int, int]:
        """
        現在の位置情報を取得.

        Args:
            category: カテゴリ名
            content_type: "sentence" または "topic"

        Returns:
            (現在位置, 全体数)のタプル
        """
        if content_type == "sentence":
            sentences = self.get_sentences(category)
            position = self._sentence_positions.get(category, 0)
            return (position, len(sentences))
        else:
            topics = self.get_topics(category)
            position = self._topic_positions.get(category, 0)
            return (position, len(topics))
