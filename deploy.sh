#!/bin/bash

# AWS Elastic Beanstalk デプロイスクリプト

echo "=== PDF校正システム AWSデプロイ ==="

# 環境変数の確認
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "エラー: AWS認証情報が設定されていません"
    echo "以下の環境変数を設定してください:"
    echo "export AWS_ACCESS_KEY_ID=your_access_key"
    echo "export AWS_SECRET_ACCESS_KEY=your_secret_key"
    exit 1
fi

# アプリケーション名
APP_NAME="pdf-kousei-system"
ENVIRONMENT_NAME="pdf-kousei-env"
REGION="ap-northeast-3"

echo "アプリケーション名: $APP_NAME"
echo "環境名: $ENVIRONMENT_NAME"
echo "リージョン: $REGION"

# 必要なディレクトリを作成
mkdir -p uploads outputs

# 一時ファイルを削除
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# ZIPファイルを作成
echo "デプロイ用ZIPファイルを作成中..."
zip -r pdf-kousei-deploy.zip . -x "venv/*" "*.pyc" "__pycache__/*" ".git/*" "*.log" "uploads/*" "outputs/*"

echo "デプロイ用ZIPファイルが作成されました: pdf-kousei-deploy.zip"

# AWS CLIがインストールされているか確認
if ! command -v aws &> /dev/null; then
    echo "AWS CLIがインストールされていません。"
    echo "以下のコマンドでインストールしてください:"
    echo "pip install awscli"
    exit 1
fi

# AWS認証情報を設定
aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
aws configure set default.region $REGION

echo "AWS認証情報を設定しました"

# アプリケーションが存在するか確認
if aws elasticbeanstalk describe-applications --application-names $APP_NAME --region $REGION > /dev/null 2>&1; then
    echo "アプリケーション '$APP_NAME' は既に存在します"
else
    echo "アプリケーション '$APP_NAME' を作成中..."
    aws elasticbeanstalk create-application \
        --application-name $APP_NAME \
        --description "PDF校正システム" \
        --region $REGION
fi

# 環境が存在するか確認
if aws elasticbeanstalk describe-environments --application-name $APP_NAME --environment-names $ENVIRONMENT_NAME --region $REGION > /dev/null 2>&1; then
    echo "環境 '$ENVIRONMENT_NAME' は既に存在します"
    echo "アプリケーションバージョンをデプロイ中..."
    
    # 新しいアプリケーションバージョンを作成
    VERSION_LABEL="v$(date +%Y%m%d%H%M%S)"
    aws elasticbeanstalk create-application-version \
        --application-name $APP_NAME \
        --version-label $VERSION_LABEL \
        --source-bundle S3Bucket=elasticbeanstalk-$REGION-$(aws sts get-caller-identity --query Account --output text),S3Key=pdf-kousei-deploy.zip \
        --region $REGION
    
    # 環境を更新
    aws elasticbeanstalk update-environment \
        --application-name $APP_NAME \
        --environment-name $ENVIRONMENT_NAME \
        --version-label $VERSION_LABEL \
        --region $REGION
else
    echo "環境 '$ENVIRONMENT_NAME' を作成中..."
    aws elasticbeanstalk create-environment \
        --application-name $APP_NAME \
        --environment-name $ENVIRONMENT_NAME \
        --solution-stack-name "64bit Amazon Linux 2023 v4.7.1 running Python 3.11" \
        --region $REGION
fi

echo "デプロイが完了しました！"
echo "環境のURLを確認するには:"
echo "aws elasticbeanstalk describe-environments --application-name $APP_NAME --environment-names $ENVIRONMENT_NAME --region $REGION --query 'Environments[0].CNAME' --output text"
