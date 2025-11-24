@echo off
echo PDF校正システム - GUI版を起動しています...
echo.

REM 仮想環境の確認
if not exist "venv\Scripts\activate.bat" (
    echo エラー: 仮想環境が見つかりません。
    echo まず以下のコマンドを実行してください:
    echo python -m venv venv
    echo .\venv\Scripts\activate
    echo pip install -r requirements.txt
    pause
    exit /b 1
)

REM 仮想環境をアクティベート
call venv\Scripts\activate.bat

REM GUI版を起動
python pdf_corrector_gui.py

pause
