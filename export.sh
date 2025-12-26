#!/bin/bash
# 웹 서비스에 필요한 파일만 export

OUTPUT_DIR="${1:-dist}"

echo "📦 웹 서비스 파일 Export"
echo "========================"
echo "출력 디렉토리: $OUTPUT_DIR"
echo ""

# 기존 출력 디렉토리 삭제
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/data"

# 필수 파일 복사
echo "📄 파일 복사 중..."

cp index.html "$OUTPUT_DIR/"
cp app.js "$OUTPUT_DIR/"
cp styles.css "$OUTPUT_DIR/"

# data 폴더에서 필요한 JSON만 복사 (lists.json + 숫자.json + lines.json)
cp data/lists.json "$OUTPUT_DIR/data/"
cp data/[0-9]*.json "$OUTPUT_DIR/data/" 2>/dev/null
cp data/*_lines.json "$OUTPUT_DIR/data/" 2>/dev/null

# 결과 출력
echo ""
echo "✅ Export 완료!"
echo ""
echo "📁 $OUTPUT_DIR/"
ls -la "$OUTPUT_DIR/"
echo ""
echo "📁 $OUTPUT_DIR/data/"
ls -la "$OUTPUT_DIR/data/"
echo ""

# 용량 계산
TOTAL_SIZE=$(du -sh "$OUTPUT_DIR" | cut -f1)
echo "📊 총 용량: $TOTAL_SIZE"

