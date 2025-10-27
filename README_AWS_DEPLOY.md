# PDF校正システム - AWSデプロイガイド

## 概要
AWS Elastic Beanstalkを使用してPDF校正システムをデプロイするためのガイドです。

## 前提条件
- AWSアカウント
- AWS CLIがインストール済み
- Python 3.11以上

## デプロイ手順

### 1. 環境変数の設定
`.env`ファイルを作成し、以下の内容を設定してください：

```bash
# AWS認証情報
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=ap-northeast-3

# Flask設定
SECRET_KEY=your_secret_key_here
FLASK_DEBUG=False

# 認証設定
LOGIN_ID=your_login_id
LOGIN_PASSWORD=your_password
```

### 2. デプロイ用ファイルの準備
以下のコマンドでデプロイ用ZIPファイルを作成：

**Windows (PowerShell):**
```powershell
.\deploy.ps1
```

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

### 3. AWS Elastic Beanstalkでのデプロイ

#### 方法1: AWSコンソールを使用
1. [AWS Elastic Beanstalk コンソール](https://ap-northeast-3.console.aws.amazon.com/elasticbeanstalk/)にアクセス
2. 「新しいアプリケーションを作成」をクリック
3. アプリケーション名: `pdf-kousei-system`
4. プラットフォーム: `Python 3.11`
5. アプリケーションコード: `pdf-kousei-deploy.zip`をアップロード
6. 「アプリケーションを作成」をクリック

#### 方法2: AWS CLIを使用
```bash
# アプリケーションを作成
aws elasticbeanstalk create-application \
    --application-name pdf-kousei-system \
    --description "PDF校正システム" \
    --region ap-northeast-3

# 環境を作成
aws elasticbeanstalk create-environment \
    --application-name pdf-kousei-system \
    --environment-name pdf-kousei-env \
    --solution-stack-name "64bit Amazon Linux 2023 v4.0.0 running Python 3.11" \
    --region ap-northeast-3
```

### 4. 環境変数の設定
AWS Elastic Beanstalkコンソールで以下の環境変数を設定：

- `AWS_ACCESS_KEY_ID`: あなたのAWSアクセスキー
- `AWS_SECRET_ACCESS_KEY`: あなたのAWSシークレットキー
- `AWS_DEFAULT_REGION`: `ap-northeast-3`
- `SECRET_KEY`: ランダムな文字列（セキュリティ用）
- `FLASK_DEBUG`: `False`

### 5. セキュリティ設定
- セキュリティグループでHTTP（ポート80）とHTTPS（ポート443）を許可
- 必要に応じて特定のIPアドレスからのアクセスのみに制限

## ファイル構成
```
aws_kousei/
├── application.py          # Elastic Beanstalk用エントリーポイント
├── app.py                  # メインアプリケーション
├── config.py               # 設定ファイル
├── requirements.txt        # Python依存関係
├── .ebextensions/          # Elastic Beanstalk設定
│   ├── 01_packages.config
│   ├── 02_python.config
│   └── 03_environment.config
├── templates/              # HTMLテンプレート
│   ├── index.html
│   └── login.html
├── static/                 # 静的ファイル
│   └── robots.txt
├── deploy.sh               # Linux/Mac用デプロイスクリプト
├── deploy.ps1              # Windows用デプロイスクリプト
└── config/                 # 環境別認証情報
    └── credentials.*.env.example
```

## トラブルシューティング

### よくある問題
1. **AWS認証エラー**: 環境変数が正しく設定されているか確認
2. **依存関係エラー**: `requirements.txt`に必要なパッケージが含まれているか確認
3. **権限エラー**: IAMユーザーにElastic Beanstalkの権限があるか確認

### ログの確認
```bash
aws elasticbeanstalk describe-events \
    --application-name pdf-kousei-system \
    --environment-name pdf-kousei-env \
    --region ap-northeast-3
```

## セキュリティ注意事項
- 本番環境では強力なパスワードを使用
- HTTPSの使用を推奨
- 定期的なセキュリティアップデート
- アクセスログの監視

## コスト最適化
- 不要な環境は停止
- 適切なインスタンスタイプを選択
- CloudWatchでリソース使用量を監視
