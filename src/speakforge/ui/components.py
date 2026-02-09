"""UIコンポーネントモジュール."""


def create_result_display(
    is_correct: bool,
    score: int,
    user_answer: str,
    feedback: str,
    grammar_issues: list[str],
    better_expressions: list[str],
    model_answers: list[str],
) -> str:
    """
    結果表示用のHTMLを生成.

    Args:
        is_correct: 正解かどうか
        score: スコア
        user_answer: ユーザーの回答
        feedback: フィードバック
        grammar_issues: 文法の問題点
        better_expressions: より良い表現
        model_answers: 模範回答

    Returns:
        HTML文字列
    """
    status = "✅ 正解！" if is_correct else "❌ もう一度挑戦しましょう"
    status_class = "result-correct" if is_correct else "result-incorrect"

    grammar_html = ""
    if grammar_issues:
        issues = "".join(f"<li>{issue}</li>" for issue in grammar_issues)
        grammar_html = f"""
        <div class="grammar-issue">
            <strong>📝 文法の注意点:</strong>
            <ul>{issues}</ul>
        </div>
        """

    suggestion_html = ""
    if better_expressions:
        suggestions = "".join(f"<li>{exp}</li>" for exp in better_expressions)
        suggestion_html = f"""
        <div class="suggestion">
            <strong>💡 より良い表現:</strong>
            <ul>{suggestions}</ul>
        </div>
        """

    # 模範回答のHTMLを生成（読み上げ対象として data-speakable 属性を付与）
    model_items = "".join(
        f'<li><span class="speakable-text" data-text="{ans}">{ans}</span></li>'
        for ans in model_answers
    )

    return f"""
    <div class="{status_class}" style="padding: 20px; border-radius: 10px; margin: 10px 0;">
        <h3>{status}</h3>
        <div class="score-display">スコア: {score}/100</div>
        <hr>
        <p><strong>あなたの回答:</strong> {user_answer}</p>
        <p><strong>フィードバック:</strong> {feedback}</p>
        {grammar_html}
        {suggestion_html}
        <div class="model-answer">
            <strong>📖 模範回答:</strong>
            <ul>{model_items}</ul>
            <p style="font-size: 0.85em; color: #666; margin-top: 10px;">
                🔊 下の「模範回答を読み上げ」ボタンで発音を確認できます
            </p>
        </div>
    </div>
    """


def create_monologue_result_display(
    transcribed_text: str,
    duration: float,
    word_count: int,
    wpm: float,
    overall_score: int,
    cefr_level: str,
    grammar_corrections: list[dict],
    expression_suggestions: list[dict],
    structure_feedback: str,
    model_answer: str,
    strengths: list[str],
    areas_to_improve: list[str],
) -> str:
    """
    独り言英会話の結果表示用HTMLを生成.

    Args:
        各種結果データ

    Returns:
        HTML文字列
    """
    # 文法修正のHTML（読み上げ対象として corrected を含む）
    grammar_html = ""
    if grammar_corrections:
        corrections = ""
        for c in grammar_corrections:
            corrected = c.get("corrected", "")
            corrections += f"""
            <div style="margin: 10px 0; padding: 10px; background: #fff3cd; border-radius: 5px;">
                <span style="color: #dc3545; text-decoration: line-through;">{c.get('original', '')}</span>
                → <span style="color: #28a745;" class="speakable-text" data-text="{corrected}">{corrected}</span>
                <br><small>{c.get('explanation', '')}</small>
            </div>
            """
        grammar_html = f"""
        <h4>📝 文法の修正</h4>
        {corrections}
        """

    # 表現提案のHTML（読み上げ対象として suggested を含む）
    expression_html = ""
    if expression_suggestions:
        suggestions = ""
        for s in expression_suggestions:
            suggested = s.get("suggested", "")
            suggestions += f"""
            <div style="margin: 10px 0; padding: 10px; background: #d1ecf1; border-radius: 5px;">
                「{s.get('original', '')}」→「<span class="speakable-text" data-text="{suggested}">{suggested}</span>」
                <br><small>{s.get('reason', '')}</small>
            </div>
            """
        expression_html = f"""
        <h4>💡 表現の改善提案</h4>
        {suggestions}
        """

    # 良かった点
    strengths_html = ""
    if strengths:
        items = "".join(f"<li>{s}</li>" for s in strengths)
        strengths_html = f"""
        <h4>✨ 良かった点</h4>
        <ul style="color: #28a745;">{items}</ul>
        """

    # 改善点
    improve_html = ""
    if areas_to_improve:
        items = "".join(f"<li>{a}</li>" for a in areas_to_improve)
        improve_html = f"""
        <h4>📈 改善点</h4>
        <ul style="color: #fd7e14;">{items}</ul>
        """

    return f"""
    <div style="padding: 20px; border-radius: 10px; background: #f8f9fa;">
        <div style="display: flex; justify-content: space-around; margin-bottom: 20px;">
            <div class="stats-card" style="flex: 1; margin: 0 5px;">
                <h3>スコア</h3>
                <div style="font-size: 2em;">{overall_score}/100</div>
            </div>
            <div class="stats-card" style="flex: 1; margin: 0 5px;">
                <h3>CEFRレベル</h3>
                <div style="font-size: 2em;">{cefr_level}</div>
            </div>
            <div class="stats-card" style="flex: 1; margin: 0 5px;">
                <h3>WPM</h3>
                <div style="font-size: 2em;">{wpm:.1f}</div>
            </div>
        </div>

        <div style="display: flex; justify-content: space-around; margin-bottom: 20px;">
            <div style="text-align: center;">
                <strong>発話時間:</strong> {duration:.1f}秒
            </div>
            <div style="text-align: center;">
                <strong>単語数:</strong> {word_count}語
            </div>
        </div>

        <hr>

        <h4>🎤 あなたのスピーチ</h4>
        <div style="padding: 15px; background: white; border-radius: 5px; margin-bottom: 15px;">
            {transcribed_text}
        </div>

        {grammar_html}
        {expression_html}

        <h4>📋 構成へのフィードバック</h4>
        <p>{structure_feedback}</p>

        {strengths_html}
        {improve_html}

        <h4>📖 模範回答例</h4>
        <div class="model-answer">
            <span class="speakable-text" data-text="{model_answer}">{model_answer}</span>
        </div>
        <p style="font-size: 0.85em; color: #666; margin-top: 10px;">
            🔊 下の「模範回答を読み上げ」ボタンで発音を確認できます
        </p>
    </div>
    """


def create_statistics_display(stats: dict) -> str:
    """
    統計情報の表示用HTMLを生成.

    Args:
        stats: 統計情報の辞書

    Returns:
        HTML文字列
    """
    return f"""
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
        <div class="stats-card">
            <h4>総回答数</h4>
            <div style="font-size: 1.5em;">{stats['total_attempts']}</div>
        </div>
        <div class="stats-card">
            <h4>正答率</h4>
            <div style="font-size: 1.5em;">{stats['accuracy_rate']:.1f}%</div>
        </div>
        <div class="stats-card">
            <h4>平均スコア</h4>
            <div style="font-size: 1.5em;">{stats['average_score']:.1f}</div>
        </div>
        <div class="stats-card">
            <h4>正解数</h4>
            <div style="font-size: 1.5em;">{stats['correct_count']}</div>
        </div>
        <div class="stats-card">
            <h4>不正解数</h4>
            <div style="font-size: 1.5em;">{stats['incorrect_count']}</div>
        </div>
        <div class="stats-card">
            <h4>練習日数</h4>
            <div style="font-size: 1.5em;">{stats['practice_days']}日</div>
        </div>
    </div>
    """
