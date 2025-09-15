import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # AWS設定
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'ap-northeast-3')
    
    # Bedrock設定
    BEDROCK_MODEL_ID = "apac.anthropic.claude-3-5-sonnet-20241022-v2:0"
    BEDROCK_MODEL_ARN = "arn:aws:bedrock:ap-northeast-3:YOUR_ACCOUNT_ID:inference-profile/apac.anthropic.claude-3-5-sonnet-20241022-v2:0"
    
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
