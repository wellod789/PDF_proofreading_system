import json
import os
from pathlib import Path
import string


class PromptManager:
    """
    プロンプトのデフォルトとユーザー上書きを管理するユーティリティ。
    保存場所はユーザーのホーム配下（Windows では %APPDATA% 相当）に作成する。
    """

    APP_DIR_NAME = ".aws_kousei_ds"
    FILE_NAME = "prompts.json"

    DEFAULTS = {
        # pdf_corrector_module: テキスト校正
        "text_check": (
            """
以下のテキストを校正してください。誤字脱字、文法ミス、表現の不自然さなどをチェックし、修正提案をしてください。

テキスト:
{content}

以下の形式で回答してください:
- 誤字脱字: [発見した誤字脱字とその修正案]
- 文法・表現: [文法ミスや不自然な表現とその修正案]
- その他: [その他の気になる点と修正提案]
""".strip()
        ),
        # pdf_corrector_module: 画像配置情報の校正
        "image_layout_check": (
            """
以下の画像配置情報をチェックしてください。画像の配置ミス、重複、不適切な配置などを確認し、修正提案をしてください。

画像情報:
{content}

以下の形式で回答してください:
- 配置問題: [発見した配置の問題点]
- 修正提案: [具体的な修正案]
- その他: [その他の気になる点]
""".strip()
        ),
        # pdf_corrector_gui: ページ画像の視覚的問題検出
        "image_visual_check": (
            """
以下のPDFページ（ページ {page_num}）の画像を校正の観点から分析してください。

画像の内容について以下の観点で分析し、詳細な報告をしてください：

1. 文書の種類・目的
2. レイアウト・構成の問題点
3. テキスト内容の概要と校正すべき点
4. 画像・図表の配置と内容
5. 誤字脱字、文法ミス、表現の不自然さ
6. 視覚的な問題の検出：
   - 不要な線、マーク、編集痕跡
   - 取り消し線、斜線、余分な図形
   - スキャン時の汚れ、ノイズ
   - 文字の重複、欠損
   - 色の不整合、コントラストの問題
7. レイアウトの改善提案
8. 全体的な校正提案

特に視覚的な問題（不要な線、編集痕跡など）については、具体的な位置と改善方法を詳しく説明してください。

日本語で回答してください。
""".strip()
        ),
        # pdf_corrector_gui/module: テキスト＋画像統合
        "integration": (
            """
以下のページ {page_num} のテキスト分析・画像分析（視覚）・画像配置チェック（レイアウト）の結果を統合し、重複を排除して最適化された校正結果を生成してください。

テキスト分析結果:
{text_summary}

画像分析結果（視覚）:
{image_summary}

画像配置チェック（レイアウト）結果:
{layout_summary}

統合の指示:
1. 重複する指摘を統合し、1つの明確な指摘にまとめる
2. 各分析結果を相互補完的に統合する
3. 優先度の高い問題から順に整理する
4. 具体的で実行可能な修正提案を提供する
5. 視覚的な問題・テキストの問題・レイアウトの問題を適切に組み合わせる

以下の形式で校正結果を提供してください:

【校正結果】
- 問題1: [具体的な問題と修正提案]
- 問題2: [具体的な問題と修正提案]
- 問題3: [具体的な問題と修正提案]
...

日本語で回答してください。
""".strip()
        ),
    }

    # 各テンプレートで必須となるプレースホルダー
    REQUIRED_FIELDS = {
        "text_check": {"content"},
        "image_layout_check": {"content"},
        "image_visual_check": {"page_num"},
        "integration": {"page_num", "text_summary", "image_summary", "layout_summary"},
    }

    def __init__(self):
        self._data = {}
        self._path = self._get_store_path()
        self._ensure_dir()
        self.load()

    def _get_store_path(self) -> Path:
        # Windows: %APPDATA% があればそこ、なければホーム直下
        base = os.getenv("APPDATA") or str(Path.home())
        return Path(base) / self.APP_DIR_NAME / self.FILE_NAME

    def _ensure_dir(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> None:
        if self._path.exists():
            try:
                self._data = json.load(self._path.open("r", encoding="utf-8"))
            except Exception:
                self._data = {}
        else:
            self._data = {}

    def save(self) -> None:
        try:
            with self._path.open("w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get_prompt(self, key: str) -> str:
        return self._data.get(key) or self.DEFAULTS.get(key, "")

    def set_prompt(self, key: str, value: str) -> None:
        if value is None:
            return
        self._data[key] = value

    def reset_to_defaults(self) -> None:
        self._data = {}
        self.save()

    def _parse_fields(self, template: str) -> set:
        fields = set()
        try:
            for literal_text, field_name, format_spec, conversion in string.Formatter().parse(template):
                if field_name is not None and field_name != "":
                    # ネストフィールドは想定しない
                    fields.add(field_name)
        except Exception:
            # 構文として壊れている場合
            return {"<PARSE_ERROR>"}
        return fields

    def validate_template(self, key: str, template: str) -> dict:
        """
        指定キーのテンプレートを検証する。
        戻り値: { ok: bool, missing: set, unexpected: set, parse_error: bool }
        """
        required = self.REQUIRED_FIELDS.get(key, set())
        fields = self._parse_fields(template)
        if "<PARSE_ERROR>" in fields:
            return {"ok": False, "missing": required, "unexpected": set(), "parse_error": True}
        missing = required - fields
        unexpected = fields - required
        ok = len(missing) == 0 and len(unexpected) == 0
        return {"ok": ok, "missing": missing, "unexpected": unexpected, "parse_error": False}


# シングルトン的に使えるインスタンス
prompt_manager = PromptManager()


