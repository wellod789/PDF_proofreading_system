# AWS Elastic Beanstalk デプロイスクリプト (PowerShell)

Write-Host "=== PDF校正システム AWSデプロイ ===" -ForegroundColor Green

# 環境変数の確認
if (-not $env:AWS_ACCESS_KEY_ID -or -not $env:AWS_SECRET_ACCESS_KEY) {
    Write-Host "エラー: AWS認証情報が設定されていません" -ForegroundColor Red
    Write-Host "以下の環境変数を設定してください:" -ForegroundColor Yellow
    Write-Host '$env:AWS_ACCESS_KEY_ID="your_access_key"' -ForegroundColor Cyan
    Write-Host '$env:AWS_SECRET_ACCESS_KEY="your_secret_key"' -ForegroundColor Cyan
    exit 1
}

# アプリケーション名
$APP_NAME = "pdf-kousei-system"
$ENVIRONMENT_NAME = "pdf-kousei-env"
$REGION = "ap-northeast-3"

Write-Host "アプリケーション名: $APP_NAME" -ForegroundColor Yellow
Write-Host "環境名: $ENVIRONMENT_NAME" -ForegroundColor Yellow
Write-Host "リージョン: $REGION" -ForegroundColor Yellow

# 必要なディレクトリを作成
if (-not (Test-Path "uploads")) { New-Item -ItemType Directory -Name "uploads" }
if (-not (Test-Path "outputs")) { New-Item -ItemType Directory -Name "outputs" }

# 一時ファイルを削除
Get-ChildItem -Path . -Recurse -Name "*.pyc" | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Name "__pycache__" -Directory | Remove-Item -Recurse -Force

# ZIPファイルを作成
Write-Host "デプロイ用ZIPファイルを作成中..." -ForegroundColor Yellow
Compress-Archive -Path "*.py", "*.txt", "*.config", "templates", "static", ".ebextensions" -DestinationPath "pdf-kousei-deploy.zip" -Force

Write-Host "デプロイ用ZIPファイルが作成されました: pdf-kousei-deploy.zip" -ForegroundColor Green

# AWS CLIがインストールされているか確認
try {
    aws --version | Out-Null
} catch {
    Write-Host "AWS CLIがインストールされていません。" -ForegroundColor Red
    Write-Host "以下のコマンドでインストールしてください:" -ForegroundColor Yellow
    Write-Host "pip install awscli" -ForegroundColor Cyan
    exit 1
}

# AWS認証情報を設定
aws configure set aws_access_key_id $env:AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $env:AWS_SECRET_ACCESS_KEY
aws configure set default.region $REGION

Write-Host "AWS認証情報を設定しました" -ForegroundColor Green

Write-Host "デプロイが完了しました！" -ForegroundColor Green
Write-Host "次の手順でAWS Elastic Beanstalkにデプロイしてください:" -ForegroundColor Yellow
Write-Host "1. AWS Elastic Beanstalk コンソールにアクセス" -ForegroundColor Cyan
Write-Host "2. 新しいアプリケーションを作成" -ForegroundColor Cyan
Write-Host "3. pdf-kousei-deploy.zip をアップロード" -ForegroundColor Cyan
Write-Host "4. プラットフォーム: Python 3.11" -ForegroundColor Cyan
Write-Host "5. リージョン: ap-northeast-3" -ForegroundColor Cyan
Write-Host "6. プラットフォーム: Python 3.11 (Amazon Linux 2023 v4.7.1)" -ForegroundColor Cyan
