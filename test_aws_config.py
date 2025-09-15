#!/usr/bin/env python3
"""
AWS設定テストスクリプト
"""

import boto3
import os
import json
from dotenv import load_dotenv

def test_aws_config():
    """AWS設定をテストする"""
    print("=== AWS設定テスト ===")
    
    # 環境変数を読み込み
    load_dotenv()
    
    # 環境変数の確認
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    
    print(f"Region: {region}")
    print(f"Access Key ID: {access_key[:10]}..." if access_key else "Access Key ID: 未設定")
    print(f"Secret Access Key: {'設定済み' if secret_key else '未設定'}")
    
    if not access_key or not secret_key:
        print("❌ 環境変数が設定されていません")
        return False
    
    # 現在のリージョンでプロビジョンドスループットをテスト
    return test_provisioned_throughput(access_key, secret_key, region)

def test_provisioned_throughput(access_key, secret_key, region):
    """プロビジョンドスループットをテストする"""
    try:
        # Bedrockクライアントの作成
        bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        
        print("✅ Bedrockクライアントの作成に成功")
        
        # 推論プロファイルIDを使用
        model_id = "apac.anthropic.claude-3-5-sonnet-20241022-v2:0"
        print(f"使用するモデルID: {model_id}")
        
        # 正しいAPIリクエスト形式を使用
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200,
            "top_k": 250,
            "stop_sequences": [],
            "temperature": 1,
            "top_p": 0.999,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "hello world"
                        }
                    ]
                }
            ]
        }
        
        response = bedrock_client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )
        print("✅ Bedrock APIの呼び出しに成功")
        return True
        
    except Exception as e:
        print(f"❌ 詳細エラー: {e}")
        if "AccessDeniedException" in str(e):
            print("❌ アクセス権限がありません。IAMポリシーを確認してください。")
        elif "ValidationException" in str(e):
            print("❌ モデルアクセスが有効化されていません。Bedrockコンソールで確認してください。")
        else:
            print(f"❌ Bedrock APIエラー: {e}")
        return False


def test_pdf_processing():
    """PDF処理ライブラリをテストする"""
    print("\n=== PDF処理ライブラリテスト ===")
    
    try:
        import PyPDF2
        print("✅ PyPDF2: インストール済み")
    except ImportError:
        print("❌ PyPDF2: 未インストール")
    
    try:
        import pdfplumber
        print("✅ pdfplumber: インストール済み")
    except ImportError:
        print("❌ pdfplumber: 未インストール")
    
    try:
        from PIL import Image
        print("✅ Pillow: インストール済み")
    except ImportError:
        print("❌ Pillow: 未インストール")
    
    try:
        import openpyxl
        print("✅ openpyxl: インストール済み")
    except ImportError:
        print("❌ openpyxl: 未インストール")

if __name__ == "__main__":
    print("PDF校正システム - 設定テスト")
    print("=" * 50)
    
    # PDF処理ライブラリのテスト
    test_pdf_processing()
    
    # AWS設定のテスト
    aws_ok = test_aws_config()
    
    print("\n" + "=" * 50)
    if aws_ok:
        print("🎉 すべての設定が正常です！")
        print("python app.py でアプリケーションを起動できます。")
    else:
        print("⚠️  設定に問題があります。上記のエラーを確認してください。")
