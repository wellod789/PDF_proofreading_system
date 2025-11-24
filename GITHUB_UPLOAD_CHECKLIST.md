# GitHubアップロード前チェックリスト

## ✅ セキュリティ確認

- [x] `.gitignore`に機密情報ファイルが含まれている
  - `config/credentials.local.env` ✓
  - `config/credentials.staging.env` ✓
  - `config/credentials.production.env` ✓
  - `.env`ファイル ✓

- [x] ビルド成果物が除外されている
  - `build/` ✓
  - `dist/` ✓
  - `__pycache__/` ✓
  - `*.pyc` ✓

- [x] 仮想環境が除外されている
  - `venv/` ✓
  - `env/` ✓

- [x] 出力ファイルが除外されている
  - `outputs/` ✓
  - `uploads/` ✓

## ✅ ファイル確認

- [x] `.gitignore`ファイルが存在する
- [x] `.gitattributes`ファイルが作成された（改行コードの統一）
- [x] `LICENSE`ファイルが作成された（MITライセンス）
- [x] `README.md`が存在し、内容が適切
- [x] `requirements.txt`が存在する

## ✅ 設定ファイル

- [x] テンプレートファイル（`.example`）が含まれている
  - `config/credentials.local.env.example` ✓
  - `config/credentials.staging.env.example` ✓
  - `config/credentials.production.env.example` ✓

## 📝 Gitリポジトリの初期化手順

以下のコマンドを実行してGitリポジトリを初期化し、GitHubにアップロードしてください：

```bash
# 1. Gitリポジトリを初期化
git init

# 2. すべてのファイルをステージング
git add .

# 3. 初回コミット
git commit -m "Initial commit: PDF校正システム"

# 4. GitHubでリポジトリを作成後、リモートを追加
# git remote add origin https://github.com/your-username/your-repo-name.git

# 5. メインブランチを設定（必要に応じて）
# git branch -M main

# 6. GitHubにプッシュ
# git push -u origin main
```

## ⚠️ 注意事項

1. **機密情報の確認**: `config/credentials.local.env`がGitに含まれていないことを確認
   ```bash
   git status
   git ls-files | grep credentials.local.env
   ```
   何も表示されなければOKです。

2. **大きなファイルの確認**: 大きなファイルが含まれていないか確認
   ```bash
   find . -type f -size +10M -not -path "./.git/*" -not -path "./venv/*" -not -path "./dist/*" -not -path "./build/*"
   ```

3. **不要なファイルの確認**: `.gitignore`で除外されているファイルが正しく除外されているか確認
   ```bash
   git status --ignored
   ```

## 📋 アップロード後の確認

- [ ] GitHubリポジトリで機密情報ファイルが表示されていない
- [ ] `README.md`が正しく表示されている
- [ ] ライセンス情報が表示されている
- [ ] `.gitignore`が正しく機能している

