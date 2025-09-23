"""
テスト用PDFファイルを作成するスクリプト
reportlabライブラリを使用して簡単なPDFファイルを生成
"""
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import os

def create_test_pdf():
    """テスト用PDFファイルを作成"""
    filename = "test_document.pdf"
    
    # PDFドキュメントを作成
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # カスタムスタイル
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # 中央揃え
    )
    
    # コンテンツを作成
    story = []
    
    # タイトル
    title = Paragraph("PDF to Image Converter テスト文書", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # サブタイトル
    subtitle = Paragraph("この文書はPDFを画像に変換するテスト用です", styles['Heading2'])
    story.append(subtitle)
    story.append(Spacer(1, 20))
    
    # 本文
    content = """
    この文書は、PDF to Image Converterのテスト用に作成されたサンプル文書です。
    
    以下の内容が含まれています：
    
    1. テキストの校正テスト
    2. 日本語の文字化けテスト
    3. 複数ページのテスト
    4. 画像変換の品質テスト
    
    この文書を使用して、PDFから画像への変換機能をテストしてください。
    各ページが正しく画像として出力されることを確認してください。
    """
    
    paragraph = Paragraph(content, styles['Normal'])
    story.append(paragraph)
    story.append(Spacer(1, 20))
    
    # 2ページ目の内容
    story.append(Paragraph("2ページ目の内容", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    page2_content = """
    これは2ページ目の内容です。
    
    複数ページのPDFファイルを画像に変換する際のテストに使用されます。
    
    各ページが個別の画像ファイルとして正しく出力されることを確認してください。
    
    変換設定：
    - DPI: 200
    - フォーマット: PNG
    - ページ範囲: 全ページ
    """
    
    paragraph2 = Paragraph(page2_content, styles['Normal'])
    story.append(paragraph2)
    
    # PDFを生成
    doc.build(story)
    
    print(f"テスト用PDFファイル '{filename}' を作成しました。")
    print(f"ファイルサイズ: {os.path.getsize(filename):,} bytes")
    
    return filename

if __name__ == "__main__":
    try:
        create_test_pdf()
    except ImportError:
        print("reportlabライブラリがインストールされていません。")
        print("以下のコマンドでインストールしてください：")
        print("pip install reportlab")
    except Exception as e:
        print(f"PDFファイルの作成中にエラーが発生しました: {e}")
