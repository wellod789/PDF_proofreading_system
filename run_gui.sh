#!/bin/bash
echo "PDF校正システム - GUI版を起動しています..."
echo

# 仮想環境の確認
if [ ! -f "venv/bin/activate" ]; then
    echo "エラー: 仮想環境が見つかりません。"
    echo "まず以下のコマンドを実行してください:"
    echo "python -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

# 仮想環境をアクティベート
source venv/bin/activate

# GUI版を起動
python pdf_corrector_gui.py
