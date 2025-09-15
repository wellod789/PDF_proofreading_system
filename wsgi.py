import os
import sys

# アプリケーションのルートディレクトリをPythonパスに追加
sys.path.insert(0, os.path.dirname(__file__))

from app import app

# WSGIアプリケーションとして設定
application = app

if __name__ == "__main__":
    application.run()
