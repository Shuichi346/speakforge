#!/bin/bash
# cleanup_for_publish.sh

echo "=== 公開前クリーンアップ ==="

# ユーザー履歴を削除
if [ -f "data/user_data/history.json" ]; then
    rm data/user_data/history.json
    echo "✓ 学習履歴を削除しました"
fi

# カスタム問題を削除
if [ -f "data/sentences/custom.json" ]; then
    rm data/sentences/custom.json
    echo "✓ カスタム問題を削除しました"
fi

# .envを削除（.env.exampleは残す）
if [ -f ".env" ]; then
    rm .env
    echo "✓ .envを削除しました"
fi

# .venvを削除
if [ -d ".venv" ]; then
    rm -rf .venv
    echo "✓ .venvを削除しました"
fi

# Pythonキャッシュを削除
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo "✓ Pythonキャッシュを削除しました"

# .DS_Storeを削除（macOS）
find . -name ".DS_Store" -delete 2>/dev/null
echo "✓ .DS_Storeを削除しました"

echo "=== 完了 ==="
echo "git status で確認してからコミットしてください"
