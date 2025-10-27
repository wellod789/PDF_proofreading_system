# PDF校正システム - EC2デプロイガイド

## 概要
EC2インスタンスに直接デプロイしてPDF校正システムを運用するためのガイドです。

## 前提条件
- AWSアカウント
- AWS CLIがインストール済み（ローカル環境）
- SSHアクセス用のキーペア

## デプロイ手順

### 1. EC2インスタンスの起動

#### AWSコンソールから起動
1. [EC2コンソール](https://ap-northeast-3.console.aws.amazon.com/ec2/)にアクセス
2. 「インスタンスを起動」をクリック
3. 以下の設定を行います：

**基本設定:**
- 名前: `pdf-kousei-system`
- アプリケーションとOS: `Amazon Linux 2023`
- インスタンスタイプ: `t3.small` 以上（2 vCPU, 4GB RAM推奨）
- キーペア: 新規作成または既存のものを選択

**ネットワーク設定:**
- セキュリティグループ: 新しいセキュリティグループを作成
  - インバウンドルール:
    - SSH (22): 自分のIPからのみ許可
    - HTTP (80): 0.0.0.0/0
    - HTTPS (443): 0.0.0.0/0
- 自動割り当てパブリックIP: 有効にする

**ストレージ:**
- サイズ: 20GB（最小推奨）

4. 「インスタンスを起動」をクリック

### 2. EC2インスタンスへの接続

#### Windows (PowerShell/CMD)
```powershell
ssh -i "your-key.pem" ec2-user@your-ec2-public-ip
```

#### Linux/Mac
```bash
ssh -i "your-key.pem" ec2-user@your-ec2-public-ip
chmod 400 your-key.pem
```

### 3. EC2インスタンスのセットアップ

#### システムパッケージの更新
```bash
sudo yum update -y
```

#### 必要なソフトウェアのインストール
```bash
# Python 3.11のインストール
sudo amazon-linux-extras install python3.11 -y

# pipとvenvのインストール
sudo python3.11 -m pip install --upgrade pip
sudo python3.11 -m pip install virtualenv

# poppler-utils（PDF変換用）のインストール
sudo yum install poppler-utils -y

# Gitのインストール
sudo yum install git -y
```

#### アプリケーションの配置
```bash
# ホームディレクトリに移動
cd ~

# アプリケーション用ディレクトリを作成
mkdir pdf-kousei
cd pdf-kousei

# アプリケーションファイルを転送
# (ローカル環境から以下のコマンドで転送)
```

**ローカル環境からファイルを転送:**

Windows (PowerShell):
```powershell
scp -i "your-key.pem" -r * ec2-user@your-ec2-public-ip:~/pdf-kousei/
```

Linux/Mac:
```bash
scp -i "your-key.pem" -r * ec2-user@your-ec2-public-ip:~/pdf-kousei/
```

または、GitHubからクローン:
```bash
git clone https://github.com/your-username/pdf-kousei-system.git .
```

### 4. Python仮想環境のセットアップ

```bash
cd ~/pdf-kousei

# 仮想環境の作成
python3.11 -m venv venv

# 仮想環境のアクティベート
source venv/bin/activate

# 依存関係のインストール
pip install --upgrade pip
pip install -r requirements.txt

# 仮想環境を無効化
deactivate
```

### 5. 環境変数の設定

```bash
# .envファイルを作成
cd ~/pdf-kousei
nano .env
```

以下の内容を設定:
```bash
# AWS設定
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=ap-northeast-3

# Bedrock設定
BEDROCK_MODEL_ID=apac.anthropic.claude-3-5-sonnet-20241022-v2:0

# Flask設定
SECRET_KEY=your-secret-key-here-make-it-long-and-random
FLASK_DEBUG=False

# 認証設定
LOGIN_ID=your-login-id
LOGIN_PASSWORD=your-password

# その他設定
MAX_PDF_PAGES=3
```

保存して終了: `Ctrl + X`, `Y`, `Enter`

### 6. アプリケーションの起動（systemdサービス）

#### サービスファイルの作成
```bash
sudo nano /etc/systemd/system/pdf-kousei.service
```

以下の内容を記述:
```ini
[Unit]
Description=PDF Kousei System
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/pdf-kousei
Environment="PATH=/home/ec2-user/pdf-kousei/venv/bin"
Environment="ENV=production"
Environment="AWS_ACCESS_KEY_ID=your_access_key_id"
Environment="AWS_SECRET_ACCESS_KEY=your_secret_access_key"
Environment="AWS_DEFAULT_REGION=ap-northeast-3"
Environment="SECRET_KEY=your-secret-key-here-make-it-long-and-random"
Environment="FLASK_DEBUG=False"
Environment="LOGIN_ID=your-login-id"
Environment="LOGIN_PASSWORD=your-password"
Environment="BEDROCK_MODEL_ID=apac.anthropic.claude-3-5-sonnet-20241022-v2:0"
Environment="MAX_PDF_PAGES=3"
ExecStart=/home/ec2-user/pdf-kousei/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### サービスの有効化と起動
```bash
# systemdのリロード
sudo systemctl daemon-reload

# サービスの有効化
sudo systemctl enable pdf-kousei

# サービスの起動
sudo systemctl start pdf-kousei

# サービスの状態確認
sudo systemctl status pdf-kousei
```

#### ログの確認
```bash
# サービスのログを確認
sudo journalctl -u pdf-kousei -f

# アプリケーションのログを確認
tail -f ~/pdf-kousei/app.log
```

### 7. Nginxの設定（リバースプロキシ）

#### Nginxのインストール
```bash
sudo amazon-linux-extras install nginx1 -y
```

#### 設定ファイルの作成
```bash
sudo nano /etc/nginx/conf.d/pdf-kousei.conf
```

以下の内容を記述:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # またはEC2のIPアドレス

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 大きなファイルのアップロードに対応
    client_max_body_size 50M;
}
```

#### Nginxの起動
```bash
sudo systemctl enable nginx
sudo systemctl start nginx
sudo systemctl status nginx
```

### 8. セキュリティ設定

#### ファイアウォールの設定
```bash
# 現在の設定を確認
sudo firewall-cmd --list-all

# HTTPとHTTPSを許可（既に設定済みの場合は不要）
# SSHは既に許可されているはず
```

#### Let's EncryptでHTTPS化（オプション）
```bash
# Certbotのインストール
sudo amazon-linux-extras install certbot -y

# SSL証明書の取得（ドメインがある場合）
sudo certbot --nginx -d your-domain.com
```

### 9. ディレクトリとファイルの設定

```bash
# アップロードと出力ディレクトリの作成
cd ~/pdf-kousei
mkdir uploads outputs
chmod 755 uploads outputs

# ログファイルの作成
touch app.log
chmod 644 app.log
```

### 10. サービスの管理コマンド

```bash
# サービスの停止
sudo systemctl stop pdf-kousei

# サービスの起動
sudo systemctl start pdf-kousei

# サービスの再起動
sudo systemctl restart pdf-kousei

# サービスの状態確認
sudo systemctl status pdf-kousei

# ログの確認
sudo journalctl -u pdf-kousei -n 50
```

## トラブルシューティング

### よくある問題

#### 1. アプリケーションが起動しない
```bash
# サービスログを確認
sudo journalctl -u pdf-kousei -n 100

# 仮想環境の状態を確認
source venv/bin/activate
python -c "import flask; print(flask.__version__)"
```

#### 2. ポート5000にアクセスできない
```bash
# ポートが開いているか確認
sudo netstat -tulpn | grep 5000

# gunicornが正常に起動しているか確認
ps aux | grep gunicorn
```

#### 3. 環境変数が読み込まれない
```bash
# .envファイルの確認
cat ~/pdf-kousei/.env

# 環境変数のテスト
source venv/bin/activate
python -c "from config import Config; print(Config.AWS_DEFAULT_REGION)"
```

#### 4. PDF変換が失敗する
```bash
# poppler-utilsがインストールされているか確認
which pdftoppm

# テスト実行
pdftoppm -version
```

## パフォーマンス調整

### システムリソースの監視
```bash
# CPU使用率の確認
top

# メモリ使用率の確認
free -h

# ディスク使用率の確認
df -h
```

### Gunicornワーカーの調整
`/etc/systemd/system/pdf-kousei.service`の`ExecStart`を変更:
```bash
# CPUコア数の2倍 + 1
# 例: 2コアの場合 → 5ワーカー
ExecStart=/home/ec2-user/pdf-kousei/venv/bin/gunicorn -w 5 -b 0.0.0.0:5000 app:app
```

### サーバーの再起動後も自動起動
上記のsystemd設定により、サーバー再起動後も自動で起動します。

## セキュリティ注意事項

1. **SSH鍵の管理**: キーペアは安全に保管
2. **環境変数**: `.env`ファイルに機密情報を含めない
3. **ファイアウォール**: 必要なポートのみ開放
4. **定期更新**: システムパッケージを定期的に更新
5. **ログ監視**: 不正アクセスがないかログを監視

## コスト最適化

1. **インスタンスタイプ**: 使用量に応じて調整
2. **Auto Scaling**: 負荷に応じて自動スケール
3. **停止/起動**: 不要な時間帯は停止
4. **リザーブドインスタンス**: 長期利用はRI検討

## バックアップ

### アプリケーションのバックアップ
```bash
# 定期的なバックアップスクリプト
cd ~
tar -czf pdf-kousei-backup-$(date +%Y%m%d).tar.gz pdf-kousei/
```

### S3への自動バックアップ
```bash
# AWS CLIでS3にバックアップ
aws s3 cp ~/pdf-kousei/outputs/ s3://your-bucket/pdf-kousei-backup/ --recursive
```

## 更新手順

```bash
# アプリケーションの更新
cd ~/pdf-kousei
git pull origin main  # またはファイルを再転送

# 仮想環境をアクティベート
source venv/bin/activate

# 依存関係の更新
pip install -r requirements.txt

# サービスの再起動
sudo systemctl restart pdf-kousei
```

## 関連ドキュメント

- [メインREADME](README.md) - プロジェクト概要
- [GUI版ガイド](README_GUI.md) - GUIアプリケーションの使い方
- [プログラム仕様書](プログラム仕様書.md) - システムの詳細仕様
