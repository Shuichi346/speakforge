"""メインアプリケーションUIモジュール."""

import json

import gradio as gr

from speakforge.config import settings
from speakforge.core.monologue_practice import MonologuePractice
from speakforge.core.sentence_practice import SentencePractice
from speakforge.core.smart_review import SmartReview
from speakforge.data.sentence_loader import SentenceLoader
from speakforge.services.llm_service import LLMService
from speakforge.services.problem_generator import ProblemGenerator
from speakforge.services.text_to_speech import TextToSpeechService
from speakforge.ui.components import (
    create_monologue_result_display,
    create_result_display,
    create_statistics_display,
)
from speakforge.ui.styles import CUSTOM_CSS


def create_app() -> gr.Blocks:
    """Gradioアプリケーションを作成."""
    # サービスのインスタンス化
    sentence_practice = SentencePractice()
    monologue_practice = MonologuePractice()
    smart_review = SmartReview()
    llm_service = LLMService()
    tts_service = TextToSpeechService()
    problem_generator = ProblemGenerator()

    # TTS機能の状態を確認
    tts_available = tts_service.is_available()
    tts_status = "有効" if tts_available else "無効"

    # カテゴリの取得とデフォルト値の設定
    sentence_categories = sentence_practice.get_categories()
    topic_categories = monologue_practice.get_categories()

    # デフォルトカテゴリを設定（リストが空でない場合）
    default_sentence_category = sentence_categories[0] if sentence_categories else None
    default_topic_category = topic_categories[0] if topic_categories else None

    # 初期カテゴリをサービスに設定
    if default_sentence_category:
        sentence_practice.set_category(default_sentence_category)
    if default_topic_category:
        monologue_practice.set_category(default_topic_category)

    # SentenceLoaderへの参照（問題追加後のリロード用）
    sentence_loader = SentenceLoader()

    with gr.Blocks(
        title="SpeakForge - 英語スピーキング練習",
        css=CUSTOM_CSS,
        theme=gr.themes.Soft(),
    ) as app:
        gr.Markdown(
            f"""
            # 🎯 SpeakForge - 英語スピーキング練習アプリ

            英語の瞬発力と表現力を鍛えるAIトレーニングアプリです。

            <small>🤖 LLM: **{llm_service.get_current_model()}** | 🎤 STT: **{settings.whisper_model}** | 🔊 TTS: **{tts_status}**</small>
            """
        )

        # 口頭英作文の現在の模範回答を保持するState
        current_model_answers = gr.State([])
        # 独り言英会話の模範回答を保持するState
        current_monologue_answer = gr.State("")
        # 生成された問題データを保持するState
        generated_sentences_data = gr.State(None)
        generated_topics_data = gr.State(None)

        with gr.Tabs():
            # === 口頭英作文タブ ===
            with gr.TabItem("📝 口頭英作文"):
                gr.Markdown(
                    """
                    ### 口頭英作文トレーニング
                    日本語の文章を見て、瞬時に英語で話してください。
                    """
                )

                with gr.Row():
                    sentence_category = gr.Dropdown(
                        choices=sentence_categories,
                        value=default_sentence_category,
                        label="カテゴリ",
                        interactive=True,
                    )
                    next_sentence_btn = gr.Button(
                        "次の問題",
                        variant="primary",
                    )

                sentence_display = gr.Markdown(
                    value="「次の問題」ボタンを押して開始してください。",
                    label="問題",
                )

                sentence_audio = gr.Audio(
                    sources=["microphone"],
                    type="numpy",
                    label="音声を録音",
                )

                submit_sentence_btn = gr.Button(
                    "回答を送信",
                    variant="primary",
                    elem_classes=["submit-btn-row"],
                )

                sentence_result = gr.HTML(label="結果")

                # TTS読み上げセクション（口頭英作文）
                if tts_available:
                    with gr.Group(elem_classes=["tts-section"]):
                        gr.Markdown("#### 🔊 発音確認")
                        speak_model_answer_btn = gr.Button(
                            "模範回答を読み上げ",
                            variant="secondary",
                            elem_classes=["tts-button"],
                        )
                        tts_audio_sentence = gr.Audio(
                            label="読み上げ音声",
                            type="numpy",
                            autoplay=True,
                            interactive=False,
                        )

                with gr.Accordion("質問する", open=False):
                    question_input = gr.Textbox(
                        label="質問内容",
                        placeholder="この問題について質問してください...",
                    )
                    ask_btn = gr.Button("質問する")
                    answer_display = gr.Markdown(label="回答")

                # 口頭英作文のイベント処理
                def on_category_change(category: str):
                    if category:
                        sentence_practice.set_category(category)
                        return (
                            f"カテゴリ「{category}」を選択しました。「次の問題」を押してください。",
                            [],
                        )
                    return "カテゴリを選択してください。", []

                def on_next_sentence():
                    sentence = sentence_practice.get_next_sentence()
                    if sentence:
                        display_html = f"""
                        <div class="question-box">
                            <h3>🇯🇵 日本語</h3>
                            <p style="font-size: 1.3em;">{sentence.japanese}</p>
                            <small>難易度: {'⭐' * sentence.difficulty} | タグ: {', '.join(sentence.tags)}</small>
                        </div>
                        """
                        return display_html, sentence.english_examples
                    return "問題を取得できませんでした。カテゴリを確認してください。", []

                def on_submit_sentence(audio, model_answers):
                    if audio is None:
                        return "<p>音声を録音してください。</p>", model_answers

                    result = sentence_practice.evaluate_answer(audio)
                    if result is None:
                        return (
                            "<p>評価中にエラーが発生しました。もう一度お試しください。</p>",
                            model_answers,
                        )

                    result_html = create_result_display(
                        is_correct=result.is_correct,
                        score=result.score,
                        user_answer=result.user_answer,
                        feedback=result.feedback,
                        grammar_issues=result.grammar_issues,
                        better_expressions=result.better_expressions,
                        model_answers=result.sentence.english_examples,
                    )
                    return result_html, result.sentence.english_examples

                def on_ask_question(question: str):
                    if not question:
                        return "質問を入力してください。"
                    return sentence_practice.ask_question(question)

                def on_speak_model_answer(model_answers: list[str]):
                    """模範回答を読み上げ."""
                    if not model_answers:
                        return None
                    text = model_answers[0]
                    return tts_service.synthesize(text)

                sentence_category.change(
                    on_category_change,
                    inputs=[sentence_category],
                    outputs=[sentence_display, current_model_answers],
                )

                next_sentence_btn.click(
                    on_next_sentence,
                    outputs=[sentence_display, current_model_answers],
                )

                submit_sentence_btn.click(
                    on_submit_sentence,
                    inputs=[sentence_audio, current_model_answers],
                    outputs=[sentence_result, current_model_answers],
                )

                ask_btn.click(
                    on_ask_question,
                    inputs=[question_input],
                    outputs=[answer_display],
                )

                if tts_available:
                    speak_model_answer_btn.click(
                        on_speak_model_answer,
                        inputs=[current_model_answers],
                        outputs=[tts_audio_sentence],
                    )

            # === 独り言英会話タブ ===
            with gr.TabItem("🎤 独り言英会話"):
                gr.Markdown(
                    """
                    ### 独り言英会話トレーニング
                    トピックについて約1分間、英語で話してください。
                    """
                )

                with gr.Row():
                    topic_category = gr.Dropdown(
                        choices=topic_categories,
                        value=default_topic_category,
                        label="カテゴリ",
                        interactive=True,
                    )
                    next_topic_btn = gr.Button(
                        "次のトピック",
                        variant="primary",
                    )

                topic_display = gr.Markdown(
                    value="「次のトピック」ボタンを押して開始してください。",
                    label="トピック",
                )

                with gr.Accordion("メモ欄（日本語で構成を考える）", open=False):
                    memo_input = gr.Textbox(
                        label="構成メモ",
                        placeholder="話す内容を日本語でメモしてください...",
                        lines=5,
                    )

                monologue_audio = gr.Audio(
                    sources=["microphone"],
                    type="numpy",
                    label="音声を録音（約1分）",
                )

                submit_monologue_btn = gr.Button(
                    "提出して添削を受ける",
                    variant="primary",
                    elem_classes=["submit-btn-row"],
                )

                monologue_result = gr.HTML(label="添削結果")

                # TTS読み上げセクション（独り言英会話）
                if tts_available:
                    with gr.Group(elem_classes=["tts-section"]):
                        gr.Markdown("#### 🔊 発音確認")
                        speak_monologue_answer_btn = gr.Button(
                            "模範回答を読み上げ",
                            variant="secondary",
                            elem_classes=["tts-button"],
                        )
                        tts_audio_monologue = gr.Audio(
                            label="読み上げ音声",
                            type="numpy",
                            autoplay=True,
                            interactive=False,
                        )

                # 独り言英会話のイベント処理
                def on_topic_category_change(category: str):
                    if category:
                        monologue_practice.set_category(category)
                        return (
                            f"カテゴリ「{category}」を選択しました。「次のトピック」を押してください。",
                            "",
                        )
                    return "カテゴリを選択してください。", ""

                def on_next_topic():
                    topic = monologue_practice.get_next_topic()
                    if topic:
                        hints_html = "".join(
                            f"<li>{hint}</li>" for hint in topic.hints
                        )
                        display_html = f"""
                        <div class="question-box">
                            <h3>🎯 トピック</h3>
                            <p style="font-size: 1.3em;">{topic.title}</p>
                            <p>{topic.description}</p>
                            <details>
                                <summary>💡 ヒント</summary>
                                <ul>{hints_html}</ul>
                            </details>
                            <small>難易度: {'⭐' * topic.difficulty}</small>
                        </div>
                        """
                        return display_html, ""
                    return "トピックを取得できませんでした。カテゴリを確認してください。", ""

                def on_submit_monologue(audio, current_answer):
                    if audio is None:
                        return "<p>音声を録音してください。</p>", current_answer

                    result = monologue_practice.evaluate_monologue(audio)
                    if result is None:
                        return (
                            "<p>添削中にエラーが発生しました。もう一度お試しください。</p>",
                            current_answer,
                        )

                    result_html = create_monologue_result_display(
                        transcribed_text=result.transcribed_text,
                        duration=result.duration_seconds,
                        word_count=result.word_count,
                        wpm=result.wpm,
                        overall_score=result.overall_score,
                        cefr_level=result.cefr_level,
                        grammar_corrections=result.grammar_corrections,
                        expression_suggestions=result.expression_suggestions,
                        structure_feedback=result.structure_feedback,
                        model_answer=result.model_answer,
                        strengths=result.strengths,
                        areas_to_improve=result.areas_to_improve,
                    )
                    return result_html, result.model_answer

                def on_speak_monologue_answer(model_answer: str):
                    """独り言英会話の模範回答を読み上げ."""
                    if not model_answer:
                        return None
                    return tts_service.synthesize(model_answer)

                topic_category.change(
                    on_topic_category_change,
                    inputs=[topic_category],
                    outputs=[topic_display, current_monologue_answer],
                )

                next_topic_btn.click(
                    on_next_topic,
                    outputs=[topic_display, current_monologue_answer],
                )

                submit_monologue_btn.click(
                    on_submit_monologue,
                    inputs=[monologue_audio, current_monologue_answer],
                    outputs=[monologue_result, current_monologue_answer],
                )

                if tts_available:
                    speak_monologue_answer_btn.click(
                        on_speak_monologue_answer,
                        inputs=[current_monologue_answer],
                        outputs=[tts_audio_monologue],
                    )

            # === 問題作成タブ ===
            with gr.TabItem("🎨 問題作成"):
                gr.Markdown(
                    """
                    ### AIで問題を作成
                    学習したいシーンや内容を入力すると、AIが問題を自動生成します。
                    """
                )

                with gr.Tabs():
                    # 口頭英作文の問題作成
                    with gr.TabItem("📝 口頭英作文"):
                        gr.Markdown(
                            """
                            #### 口頭英作文の問題を作成
                            どんなシーンや内容の問題が欲しいか、自由に入力してください。
                            """
                        )

                        with gr.Group():
                            sentence_request = gr.Textbox(
                                label="リクエスト内容",
                                placeholder="例：海外旅行でホテルにチェックインする場面、レストランで注文する場面、道を尋ねる場面など",
                                lines=3,
                            )

                            with gr.Row():
                                sentence_category_name = gr.Textbox(
                                    label="カテゴリ名",
                                    placeholder="例：travel, restaurant, shopping",
                                    value="custom",
                                    scale=2,
                                )
                                sentence_count = gr.Slider(
                                    minimum=1,
                                    maximum=10,
                                    value=5,
                                    step=1,
                                    label="問題数",
                                    scale=1,
                                )
                                sentence_difficulty = gr.Radio(
                                    choices=[
                                        ("初級", 1),
                                        ("中級", 2),
                                        ("上級", 3),
                                    ],
                                    value=2,
                                    label="難易度",
                                    scale=1,
                                )

                            generate_sentences_btn = gr.Button(
                                "🤖 問題を生成",
                                variant="primary",
                            )

                        # ステータス表示エリア
                        sentence_generation_status = gr.Markdown(
                            value="",
                            elem_classes=["generation-status"],
                        )

                        # プレビューエリア（独立したGroupとして配置）
                        with gr.Group(visible=True, elem_classes=["generation-preview"]):
                            sentence_preview = gr.JSON(
                                label="生成された問題（プレビュー）",
                                value=None,
                            )

                        # 保存ボタン
                        save_sentences_btn = gr.Button(
                            "💾 保存して追加",
                            variant="secondary",
                            interactive=False,
                            elem_classes=["save-button-row"],
                        )

                        sentence_save_status = gr.Markdown("")

                    # 独り言英会話のトピック作成
                    with gr.TabItem("🎤 独り言英会話"):
                        gr.Markdown(
                            """
                            #### 独り言英会話のトピックを作成
                            どんなテーマについて話す練習をしたいか、自由に入力してください。
                            """
                        )

                        with gr.Group():
                            topic_request = gr.Textbox(
                                label="リクエスト内容",
                                placeholder="例：仕事のプレゼンで使える話題、趣味について説明する、将来の目標を語る",
                                lines=3,
                            )

                            with gr.Row():
                                topic_category_name = gr.Textbox(
                                    label="カテゴリ名",
                                    placeholder="例：presentation, hobby, career",
                                    value="custom",
                                    scale=2,
                                )
                                topic_count = gr.Slider(
                                    minimum=1,
                                    maximum=5,
                                    value=3,
                                    step=1,
                                    label="トピック数",
                                    scale=1,
                                )
                                topic_difficulty = gr.Radio(
                                    choices=[
                                        ("初級", 1),
                                        ("中級", 2),
                                        ("上級", 3),
                                    ],
                                    value=2,
                                    label="難易度",
                                    scale=1,
                                )

                            generate_topics_btn = gr.Button(
                                "🤖 トピックを生成",
                                variant="primary",
                            )

                        # ステータス表示エリア
                        topic_generation_status = gr.Markdown(
                            value="",
                            elem_classes=["generation-status"],
                        )

                        # プレビューエリア（独立したGroupとして配置）
                        with gr.Group(visible=True, elem_classes=["generation-preview"]):
                            topic_preview = gr.JSON(
                                label="生成されたトピック（プレビュー）",
                                value=None,
                            )

                        # 保存ボタン
                        save_topics_btn = gr.Button(
                            "💾 保存して追加",
                            variant="secondary",
                            interactive=False,
                            elem_classes=["save-button-row"],
                        )

                        topic_save_status = gr.Markdown("")

                # 問題作成のイベント処理
                def on_generate_sentences(request, category, count, difficulty):
                    if not request.strip():
                        return (
                            "❌ リクエスト内容を入力してください。",
                            None,
                            gr.update(interactive=False),
                            None,
                        )

                    category = category.strip() or "custom"

                    data = problem_generator.generate_sentences(
                        user_request=request,
                        category_name=category,
                        count=int(count),
                        difficulty=int(difficulty),
                    )

                    if data and "sentences" in data:
                        count_generated = len(data["sentences"])
                        return (
                            f"✅ {count_generated}問の問題を生成しました。内容を確認して保存してください。",
                            data,
                            gr.update(interactive=True),
                            data,
                        )
                    else:
                        return (
                            "❌ 問題の生成に失敗しました。もう一度お試しください。",
                            None,
                            gr.update(interactive=False),
                            None,
                        )

                def on_save_sentences(data, category):
                    if not data:
                        return "❌ 保存する問題がありません。", gr.update(interactive=False)

                    category = category.strip() or "custom"
                    file_path = problem_generator.save_sentences(data, category)

                    # データをリロード
                    sentence_loader._load_all_data()

                    return (
                        f"✅ 問題を保存しました: `{file_path}`\n\n"
                        "**アプリを再起動すると、新しいカテゴリが選択できるようになります。**",
                        gr.update(interactive=False),
                    )

                def on_generate_topics(request, category, count, difficulty):
                    if not request.strip():
                        return (
                            "❌ リクエスト内容を入力してください。",
                            None,
                            gr.update(interactive=False),
                            None,
                        )

                    category = category.strip() or "custom"

                    data = problem_generator.generate_topics(
                        user_request=request,
                        category_name=category,
                        count=int(count),
                        difficulty=int(difficulty),
                    )

                    if data and "topics" in data:
                        count_generated = len(data["topics"])
                        return (
                            f"✅ {count_generated}個のトピックを生成しました。内容を確認して保存してください。",
                            data,
                            gr.update(interactive=True),
                            data,
                        )
                    else:
                        return (
                            "❌ トピックの生成に失敗しました。もう一度お試しください。",
                            None,
                            gr.update(interactive=False),
                            None,
                        )

                def on_save_topics(data, category):
                    if not data:
                        return "❌ 保存するトピックがありません。", gr.update(interactive=False)

                    category = category.strip() or "custom"
                    file_path = problem_generator.save_topics(data, category)

                    # データをリロード
                    sentence_loader._load_all_data()

                    return (
                        f"✅ トピックを保存しました: `{file_path}`\n\n"
                        "**アプリを再起動すると、新しいカテゴリが選択できるようになります。**",
                        gr.update(interactive=False),
                    )

                generate_sentences_btn.click(
                    on_generate_sentences,
                    inputs=[
                        sentence_request,
                        sentence_category_name,
                        sentence_count,
                        sentence_difficulty,
                    ],
                    outputs=[
                        sentence_generation_status,
                        sentence_preview,
                        save_sentences_btn,
                        generated_sentences_data,
                    ],
                )

                save_sentences_btn.click(
                    on_save_sentences,
                    inputs=[generated_sentences_data, sentence_category_name],
                    outputs=[sentence_save_status, save_sentences_btn],
                )

                generate_topics_btn.click(
                    on_generate_topics,
                    inputs=[
                        topic_request,
                        topic_category_name,
                        topic_count,
                        topic_difficulty,
                    ],
                    outputs=[
                        topic_generation_status,
                        topic_preview,
                        save_topics_btn,
                        generated_topics_data,
                    ],
                )

                save_topics_btn.click(
                    on_save_topics,
                    inputs=[generated_topics_data, topic_category_name],
                    outputs=[topic_save_status, save_topics_btn],
                )

            # === スマート復習タブ ===
            with gr.TabItem("📚 スマート復習"):
                gr.Markdown(
                    """
                    ### スマート復習
                    間違えた問題を重点的に復習しましょう。
                    """
                )

                refresh_review_btn = gr.Button(
                    "復習問題を更新",
                    variant="secondary",
                )

                review_sentences_display = gr.HTML(label="復習問題")

                review_audio = gr.Audio(
                    sources=["microphone"],
                    type="numpy",
                    label="音声を録音",
                )

                submit_review_btn = gr.Button(
                    "回答を送信",
                    variant="primary",
                    elem_classes=["submit-btn-row"],
                )

                review_result = gr.HTML(label="結果")

                # TTS読み上げセクション（復習）
                review_model_answers = gr.State([])
                if tts_available:
                    with gr.Group(elem_classes=["tts-section"]):
                        gr.Markdown("#### 🔊 発音確認")
                        speak_review_answer_btn = gr.Button(
                            "模範回答を読み上げ",
                            variant="secondary",
                            elem_classes=["tts-button"],
                        )
                        tts_audio_review = gr.Audio(
                            label="読み上げ音声",
                            type="numpy",
                            autoplay=True,
                            interactive=False,
                        )

                # 復習問題の状態管理
                current_review_index = gr.State(0)
                review_sentences_state = gr.State([])

                def on_refresh_review():
                    sentences = smart_review.get_review_sentences(limit=10)
                    if not sentences:
                        return (
                            "<p>復習が必要な問題はありません。素晴らしい！</p>",
                            [],
                            0,
                            [],
                        )

                    html = "<h4>復習問題リスト</h4><ol>"
                    for s in sentences:
                        html += f"<li>{s.japanese}</li>"
                    html += "</ol>"

                    first_sentence = sentences[0]
                    html += f"""
                    <div class="question-box">
                        <h3>現在の問題 (1/{len(sentences)})</h3>
                        <p style="font-size: 1.3em;">{first_sentence.japanese}</p>
                    </div>
                    """

                    return html, sentences, 0, first_sentence.english_examples

                def on_submit_review(audio, sentences, index, model_answers):
                    if not sentences or index >= len(sentences):
                        return (
                            "<p>復習問題がありません。</p>",
                            sentences,
                            index,
                            model_answers,
                        )

                    if audio is None:
                        return (
                            "<p>音声を録音してください。</p>",
                            sentences,
                            index,
                            model_answers,
                        )

                    # 現在の問題を設定して評価
                    sentence_practice._current_sentence = sentences[index]
                    sentence_practice._current_category = sentences[index].category

                    result = sentence_practice.evaluate_answer(audio)
                    if result is None:
                        return (
                            "<p>評価中にエラーが発生しました。</p>",
                            sentences,
                            index,
                            model_answers,
                        )

                    result_html = create_result_display(
                        is_correct=result.is_correct,
                        score=result.score,
                        user_answer=result.user_answer,
                        feedback=result.feedback,
                        grammar_issues=result.grammar_issues,
                        better_expressions=result.better_expressions,
                        model_answers=result.sentence.english_examples,
                    )

                    # 正解なら復習済みにマーク
                    if result.is_correct:
                        smart_review.mark_as_reviewed(sentences[index].id)

                    # 次の問題へ
                    next_index = index + 1
                    next_model_answers = result.sentence.english_examples

                    if next_index < len(sentences):
                        result_html += f"""
                        <div class="question-box" style="margin-top: 20px;">
                            <h3>次の問題 ({next_index + 1}/{len(sentences)})</h3>
                            <p style="font-size: 1.3em;">{sentences[next_index].japanese}</p>
                        </div>
                        """
                        next_model_answers = sentences[next_index].english_examples
                    else:
                        result_html += """
                        <p style="margin-top: 20px; font-weight: bold;">
                            🎉 すべての復習問題が完了しました！
                        </p>
                        """

                    return result_html, sentences, next_index, next_model_answers

                def on_speak_review_answer(model_answers: list[str]):
                    """復習の模範回答を読み上げ."""
                    if not model_answers:
                        return None
                    text = model_answers[0]
                    return tts_service.synthesize(text)

                refresh_review_btn.click(
                    on_refresh_review,
                    outputs=[
                        review_sentences_display,
                        review_sentences_state,
                        current_review_index,
                        review_model_answers,
                    ],
                )

                submit_review_btn.click(
                    on_submit_review,
                    inputs=[
                        review_audio,
                        review_sentences_state,
                        current_review_index,
                        review_model_answers,
                    ],
                    outputs=[
                        review_result,
                        review_sentences_state,
                        current_review_index,
                        review_model_answers,
                    ],
                )

                if tts_available:
                    speak_review_answer_btn.click(
                        on_speak_review_answer,
                        inputs=[review_model_answers],
                        outputs=[tts_audio_review],
                    )

            # === 統計タブ ===
            with gr.TabItem("📊 学習統計"):
                gr.Markdown(
                    """
                    ### 学習統計
                    これまでの学習の記録を確認しましょう。
                    """
                )

                refresh_stats_btn = gr.Button(
                    "統計を更新",
                    variant="secondary",
                )

                stats_display = gr.HTML(label="統計情報")

                weak_tags_display = gr.Markdown(label="苦手な項目")

                def on_refresh_stats():
                    stats = smart_review.get_statistics()
                    stats_html = create_statistics_display(stats)

                    weak_tags = smart_review.get_weak_tags()
                    if weak_tags:
                        tags_md = "### 苦手な項目（間違いが多い順）\n\n"
                        for tag, count in weak_tags:
                            tags_md += f"- **{tag}**: {count}回\n"
                    else:
                        tags_md = "苦手な項目はまだありません。"

                    return stats_html, tags_md

                refresh_stats_btn.click(
                    on_refresh_stats,
                    outputs=[stats_display, weak_tags_display],
                )

            # === 設定タブ ===
            with gr.TabItem("⚙️ 設定"):
                gr.Markdown(
                    """
                    ### 現在の設定

                    設定を変更するには、プロジェクトルートの `.env` ファイルを編集してください。
                    """
                )

                # TTS設定情報を追加
                tts_voice_info = (
                    settings.tts_voice if settings.tts_enabled else "無効"
                )

                gr.Markdown(
                    f"""
                    | 項目 | 値 |
                    |------|-----|
                    | LM Studio URL | `{settings.lm_studio_base_url}` |
                    | LM Studio モデル | `{settings.lm_studio_model or '自動検出'}` |
                    | Whisper モデル | `{settings.whisper_model}` |
                    | Whisper 言語 | `{settings.whisper_language}` |
                    | TTS 有効 | `{settings.tts_enabled}` |
                    | TTS ボイス | `{tts_voice_info}` |
                    | サーバーポート | `{settings.gradio_server_port}` |
                    """
                )

                # ボイス変更機能（TTS有効時のみ）
                if tts_available:
                    gr.Markdown("### 🔊 ボイス設定")
                    with gr.Row():
                        voice_selector = gr.Dropdown(
                            choices=tts_service.get_available_voices(),
                            value=settings.tts_voice,
                            label="ボイスを選択",
                            interactive=True,
                        )
                        test_voice_btn = gr.Button("ボイスをテスト")

                    voice_test_audio = gr.Audio(
                        label="テスト音声",
                        type="numpy",
                        autoplay=True,
                        interactive=False,
                    )
                    voice_status = gr.Markdown("")

                    def on_change_voice(voice_name: str):
                        success = tts_service.change_voice(voice_name)
                        if success:
                            return f"✅ ボイスを **{voice_name}** に変更しました"
                        return "❌ ボイスの変更に失敗しました"

                    def on_test_voice(voice_name: str):
                        test_text = (
                            "Hello! This is a test of the text to speech system. "
                            "How does this voice sound to you?"
                        )
                        return tts_service.synthesize(test_text)

                    voice_selector.change(
                        on_change_voice,
                        inputs=[voice_selector],
                        outputs=[voice_status],
                    )

                    test_voice_btn.click(
                        on_test_voice,
                        inputs=[voice_selector],
                        outputs=[voice_test_audio],
                    )

                gr.Markdown(
                    """
                    ### .env ファイルの例

                    ```
                    LM_STUDIO_BASE_URL=http://localhost:1234/v1
                    LM_STUDIO_MODEL=qwen3-vl-8b-instruct
                    WHISPER_MODEL=base
                    WHISPER_LANGUAGE=en
                    TTS_ENABLED=true
                    TTS_VOICE=alba
                    TTS_TEMPERATURE=0.7
                    GRADIO_SERVER_PORT=7860
                    ```

                    設定を変更した後は、アプリを再起動してください。
                    """
                )

        # フッター
        gr.Markdown(
            """
            ---
            **SpeakForge** v0.1.0 | 英語スピーキング練習アプリ

            💡 ヒント: 毎日少しずつ続けることが上達の秘訣です！
            🔊 模範回答の読み上げ機能で正しい発音を確認しましょう。
            🎨 「問題作成」タブでオリジナルの問題を作成できます。
            """
        )

    return app
