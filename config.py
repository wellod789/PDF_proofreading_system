import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 環境に応じた認証情報ファイルを読み込む
def _resolve_resource_path(relative_path: str) -> str:
    """
    PyInstaller の onefile 実行環境（sys._MEIPASS）や exe 配置ディレクトリ、
    通常のソース実行時のディレクトリを考慮して、最初に見つかった実体パスを返す。
    見つからない場合は relative_path をそのまま返す。
    """
    candidates = []

    # PyInstaller 実行時（frozen）
    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).resolve().parent
        candidates.append(exe_dir / relative_path)

        # _MEIPASS（onefile 展開先）
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass:
            candidates.append(Path(meipass) / relative_path)

    # 通常実行時（スクリプトパス、カレントディレクトリ）
    here = Path(__file__).resolve().parent
    candidates.append(here / relative_path)
    candidates.append(Path.cwd() / relative_path)

    for p in candidates:
        if p.exists():
            return str(p)

    return relative_path


def load_credentials():
    """
    環境変数ENVに応じて適切な認証情報ファイルを読み込む
    ENV=local → config/credentials.local.env
    ENV=staging → config/credentials.staging.env
    ENV=production → config/credentials.production.env
    未設定 → config/credentials.local.env（デフォルト）
    """
    env = os.getenv('ENV', 'local')
    
    if env == 'production':
        credential_file = 'config/credentials.production.env'
    elif env == 'staging':
        credential_file = 'config/credentials.staging.env'
    else:  # local or default
        credential_file = 'config/credentials.local.env'
    
    # 候補パス解決
    resolved_path = _resolve_resource_path(credential_file)
    if os.path.exists(resolved_path):
        load_dotenv(resolved_path)
    else:
        # フォールバック: ルート直下や実行場所の .env を試す
        fallback = _resolve_resource_path('.env')
        load_dotenv(fallback)
        print(f"Warning: {credential_file} not found (tried: {resolved_path}), using .env instead")

# 認証情報を読み込む
load_credentials()

class Config:
    # AWS設定
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'ap-northeast-3')
    
    # Bedrock設定
    BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'apac.anthropic.claude-3-5-sonnet-20241022-v2:0')
    BEDROCK_MODEL_ARN = os.getenv('BEDROCK_MODEL_ARN', '')
    
    # AI分析設定
    TEMPERATURE = 0.0  # 温度差設定 (0.0-1.0, 低いほど一貫性が高く、高いほど創造性が高い) デフォルト0.3
    TOP_P = 0.9       # Top-p設定 (0.0-1.0, 核サンプリング)
    TOP_K = 50        # Top-k設定 (1-100, 上位k個のトークンから選択)
    
    # Flask設定
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # ファイルアップロード設定
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER = 'uploads'
    OUTPUT_FOLDER = 'outputs'
    
    # PDF校正設定
    MAX_PDF_PAGES = 3  # 校正対象の最大ページ数
    
    # 認証設定
    LOGIN_ID = os.getenv('LOGIN_ID', 'your-login-id')
    LOGIN_PASSWORD = os.getenv('LOGIN_PASSWORD', 'your-password')
