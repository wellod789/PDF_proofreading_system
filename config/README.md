# 認証情報管理

このディレクトリには環境別の認証情報を管理します。

## ファイル構成

```
config/
├── credentials.local.env          # ローカル開発用（実際の認証情報）
├── credentials.local.env.example  # ローカル用テンプレート
├── credentials.staging.env.example # ステージング用テンプレート
├── credentials.production.env.example # 本番用テンプレート
└── README.md                     # このファイル
```

## セットアップ方法

### 1. ローカル開発環境

```bash
# credentials.local.env ファイルを作成
cp credentials.local.env.example credentials.local.env

# .env ファイルを作成（ルートディレクトリ）
cp credentials.local.env .env
```

または既存の `.env` ファイルを `config/credentials.local.env` にコピーします。

### 2. ステージング環境（EC2/Elastic Beanstalk）

```bash
# config/credentials.staging.env.example を参考に
# サーバーに環境変数を設定
```

環境変数の設定方法：
- **EC2**: `/etc/systemd/system/pdf-kousei.service` で設定
- **Elastic Beanstalk**: `.ebextensions/03_environment.config` で設定

### 3. 本番環境（EC2）

本番環境では以下のいずれかの方法で環境変数を設定します。

#### 方法1: ルートディレクトリの `.env` ファイルを使用（推奨）

```bash
# EC2サーバー上で実行
cd ~/pdf-kousei
nano .env
```

`credentials.production.env.example` の内容を参考に、実際の認証情報を設定します。

#### 方法2: systemdサービスで直接環境変数を設定

`/etc/systemd/system/pdf-kousei.service` ファイルを編集して `Environment` ディレクティブを追加：

```ini
[Service]
Environment="ENV=production"
Environment="AWS_ACCESS_KEY_ID=your_access_key_id"
Environment="AWS_SECRET_ACCESS_KEY=your_secret_access_key"
Environment="AWS_DEFAULT_REGION=ap-northeast-3"
Environment="SECRET_KEY=your-secret-key-here"
Environment="FLASK_DEBUG=False"
Environment="LOGIN_ID=your-login-id"
Environment="LOGIN_PASSWORD=your-password"
# ... その他の環境変数
```

## Git管理について

- `*.example` ファイル → **Gitに含める**（テンプレートとして共有）
- `credentials.local.env` → **Gitから除外する**（`.gitignore`に追加）
- `.env`（ルート） → **Gitから除外する**（既存の`.gitignore`で管理）

## 認証情報の更新

### ローカル環境
1. `config/credentials.local.env` を編集
2. ルートディレクトリの `.env` を更新
3. アプリケーションを再起動

### 本番環境
1. AWSコンソールまたはコマンドラインで環境変数を更新
2. サーバーを再起動

## セキュリティ注意事項

⚠️ **重要**:
- 実際の認証情報を含むファイルはGitにコミットしない
- 本番環境では強力なパスワードを使用
- AWS認証情報は定期的にローテーション
- `.env` ファイルは共有しない
- サーバーへのアクセスは限定的に

### 本番環境の `.env` ファイルのセキュリティ設定

```bash
# ファイルの所有権を適切に設定
sudo chown ec2-user:ec2-user ~/pdf-kousei/.env

# ファイル権限を設定（所有者のみ読み取り可能）
chmod 600 ~/pdf-kousei/.env

# 確認
ls -la ~/pdf-kousei/.env
# 出力例: -rw------- 1 ec2-user ec2-user ... .env
```

## 環境ごとの使い分け

### ローカル開発環境（credentials.local.env）
- 開発・テスト用のAWS認証情報
- デバッグモード有効
- シンプルなパスワード（開発専用）

### ステージング環境
- 本番に近い環境
- デバッグモード無効
- 中間的なセキュリティ設定

### 本番環境
- 実際の運用環境
- 最高レベルのセキュリティ
- 強力なパスワードとシークレットキー

## 本番環境での環境変数設定方法の比較

### 方法1: `.env` ファイル（推奨）✅
**メリット:**
- 設定が簡単で管理しやすい
- コードと同じ場所で管理できる
- 環境変数の追加・変更が容易

**デメリット:**
- ファイルとして物理的に存在するため、アクセス制御が必要

**使用例:**
```bash
cd ~/pdf-kousei
nano .env  # 実際の認証情報を記述
```

### 方法2: systemd環境変数
**メリット:**
- 環境変数がシステムレベルで管理される
- ファイル分離が可能

**デメリット:**
- 設定が複雑
- 変更時にサービスファイルの再読み込みが必要

**使用例:**
```bash
sudo nano /etc/systemd/system/pdf-kousei.service
# Environment ディレクティブを追加
sudo systemctl daemon-reload
sudo systemctl restart pdf-kousei
```

## 推奨事項

本番環境では**方法1（`.env` ファイル）を推奨**します：
1. 設定と更新が簡単
2. アプリケーションコードと同一ディレクトリで管理
3. `.gitignore` で Git から除外済み
4. 必要に応じてファイル権限で保護可能
