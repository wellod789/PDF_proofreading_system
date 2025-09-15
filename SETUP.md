# GitHub セットアップ手順

## 1. リポジトリの初期化

```bash
git init
git add .
git commit -m "Initial commit: PDF校正システム"
```

## 2. GitHubリポジトリの作成

1. GitHubで新しいリポジトリを作成
2. リモートリポジトリを追加

```bash
git remote add origin https://github.com/your-username/pdf-kousei-system.git
git branch -M main
git push -u origin main
```

## 3. 環境変数の設定

本番環境では、以下の環境変数を設定してください：

- `AWS_ACCESS_KEY_ID`: AWSアクセスキー
- `AWS_SECRET_ACCESS_KEY`: AWSシークレットキー
- `AWS_DEFAULT_REGION`: AWSリージョン（ap-northeast-3）
- `SECRET_KEY`: Flask用のシークレットキー
- `LOGIN_ID`: ログイン用のユーザーID
- `LOGIN_PASSWORD`: ログイン用のパスワード

## 4. セキュリティ注意事項

- `.env`ファイルは絶対にコミットしないでください
- 本番環境では強力なパスワードを使用してください
- AWS認証情報は適切に管理してください
