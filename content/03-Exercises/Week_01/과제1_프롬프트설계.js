const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
  WidthType, ShadingType, VerticalAlign, PageNumber, UnderlineType
} = require("docx");

// Colors
const ACCENT = "1B4F72";
const ACCENT_LIGHT = "D6EAF8";
const GRAY = "666666";
const TIP_BG = "E8F8F5";
const TIP_BORDER = "1ABC9C";

const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "BBBBBB" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

const doc = new Document({
  styles: {
    default: { document: { run: { font: "맑은 고딕", size: 22 } } },
    paragraphStyles: [
      {
        id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 44, bold: true, color: ACCENT, font: "맑은 고딕" },
        paragraph: { spacing: { before: 0, after: 100 }, alignment: AlignmentType.CENTER }
      },
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: ACCENT, font: "맑은 고딕" },
        paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0 }
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: "2C3E50", font: "맑은 고딕" },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 }
      }
    ]
  },
  numbering: {
    config: [
      {
        reference: "req-list",
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      },
      {
        reference: "checklist",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u25A2", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      },
      {
        reference: "eval-list",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      },
      {
        reference: "sub-eval-list",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 1080, hanging: 360 } } }
        }]
      },
      {
        reference: "tip-list",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      }
    ]
  },
  sections: [{
    properties: {
      page: {
        margin: { top: 1440, right: 1260, bottom: 1260, left: 1260 },
        size: { width: 12240, height: 15840 }
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          spacing: { after: 0 },
          children: [
            new TextRun({ text: "대형언어모델활용건축공학인공지능구현", font: "맑은 고딕", size: 16, color: GRAY }),
            new TextRun({ text: "  |  Week 01 과제", font: "맑은 고딕", size: 16, color: GRAY })
          ]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "Page ", size: 16, color: GRAY }),
            new TextRun({ children: [PageNumber.CURRENT], size: 16, color: GRAY }),
            new TextRun({ text: " / ", size: 16, color: GRAY }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 16, color: GRAY })
          ]
        })]
      })
    },
    children: [
      // === Title Section ===
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 40 },
        children: [new TextRun({ text: "경희대학교 건축공학과 대학원", size: 20, color: GRAY, font: "맑은 고딕" })]
      }),
      new Paragraph({
        heading: HeadingLevel.TITLE,
        children: [new TextRun({ text: "과제 1: 프롬프트 설계" })]
      }),
      // Subtitle line
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 60 },
        children: [new TextRun({ text: "LLM활용건축공학AI구현  |  2026학년도 1학기  |  Week 01", size: 20, color: GRAY, font: "맑은 고딕" })]
      }),
      // Divider
      new Paragraph({
        spacing: { before: 100, after: 200 },
        border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: ACCENT } },
        children: [new TextRun("")]
      }),

      // === 과제 설명 ===
      new Paragraph({
        spacing: { after: 200 },
        children: [
          new TextRun({ text: "자신의 ", size: 22 }),
          new TextRun({ text: "전공/관심 분야 문서를 분석", bold: true, size: 22 }),
          new TextRun({ text: "하기 위한 ", size: 22 }),
          new TextRun({ text: "최적 프롬프트", bold: true, size: 22 }),
          new TextRun({ text: "를 개발하세요.", size: 22 })
        ]
      }),

      // === 주제 예시 (Tip Box) ===
      new Table({
        columnWidths: [9720],
        rows: [new TableRow({
          children: [new TableCell({
            borders: {
              top: { style: BorderStyle.SINGLE, size: 1, color: TIP_BORDER },
              bottom: { style: BorderStyle.SINGLE, size: 1, color: TIP_BORDER },
              left: { style: BorderStyle.SINGLE, size: 6, color: TIP_BORDER },
              right: { style: BorderStyle.SINGLE, size: 1, color: TIP_BORDER }
            },
            shading: { fill: TIP_BG, type: ShadingType.CLEAR },
            width: { size: 9720, type: WidthType.DXA },
            children: [
              new Paragraph({
                spacing: { before: 120, after: 80 },
                children: [new TextRun({ text: "💡 주제 예시", bold: true, size: 22, color: "117A65" })]
              }),
              ...[
                ["건축공학", "시방서, KDS 기준서"],
                ["경영", "재무제표, 사업계획서"],
                ["법학", "판례문, 법률 조문"],
                ["이공계", "실험 보고서, 논문 초록"],
                ["인문계", "학술 논문, 원전 텍스트"]
              ].map(([field, example]) =>
                new Paragraph({
                  numbering: { reference: "tip-list", level: 0 },
                  spacing: { before: 40, after: 40 },
                  children: [
                    new TextRun({ text: field, bold: true, size: 20 }),
                    new TextRun({ text: `: ${example}`, size: 20 })
                  ]
                })
              ),
              new Paragraph({
                spacing: { before: 60, after: 120 },
                indent: { left: 360 },
                children: [new TextRun({ text: "※ 위 예시 외에도 본인 전공/관심 분야의 문서를 자유롭게 선택하세요.", size: 20, italics: true, color: GRAY })]
              })
            ]
          })]
        })]
      }),

      // === 요구사항 ===
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("요구사항")] }),
      ...[
        [new TextRun({ text: "6가지 기법 중 최소 3가지 이상", bold: true }), new TextRun(" 적용")],
        [new TextRun({ text: "Claude, GPT, Gemini", bold: true }), new TextRun(" 세 플랫폼에서 동일 프롬프트 테스트")],
        [new TextRun("각 플랫폼별 응답 품질 비교 (정확성, 상세도, 형식)")],
        [new TextRun("본인의 평가 및 용도별 추천")]
      ].map(children =>
        new Paragraph({
          numbering: { reference: "req-list", level: 0 },
          spacing: { before: 60, after: 60 },
          children
        })
      ),

      // === 제출 양식 ===
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("제출 양식")] }),

      // 1) 프롬프트 전문
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1) 프롬프트 전문")] }),
      // Code-like box
      new Table({
        columnWidths: [9720],
        rows: [new TableRow({
          children: [new TableCell({
            borders: {
              top: { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" },
              bottom: { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" },
              left: { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" },
              right: { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" }
            },
            shading: { fill: "F5F5F5", type: ShadingType.CLEAR },
            width: { size: 9720, type: WidthType.DXA },
            children: [
              new Paragraph({
                spacing: { before: 160, after: 160 },
                indent: { left: 200 },
                children: [new TextRun({ text: "[여기에 작성한 프롬프트 붙여넣기]", font: "Consolas", size: 20, color: GRAY, italics: true })]
              })
            ]
          })]
        })]
      }),

      // 적용한 기법 체크리스트
      new Paragraph({
        spacing: { before: 240, after: 120 },
        children: [new TextRun({ text: "적용한 기법 체크리스트:", bold: true, size: 22 })]
      }),
      ...["맥락 제공", "예시 보여주기", "출력 제약 명시", "단계별 분해", "먼저 생각하도록 요청", "역할/스타일/톤 정의"].map(item =>
        new Paragraph({
          numbering: { reference: "checklist", level: 0 },
          spacing: { before: 40, after: 40 },
          children: [new TextRun({ text: `  ${item}`, size: 22 })]
        })
      ),

      // 2) 플랫폼별 비교표
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2) 플랫폼별 비교표")] }),

      // Comparison table
      new Table({
        columnWidths: [2400, 2440, 2440, 2440],
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        rows: [
          // Header row
          new TableRow({
            tableHeader: true,
            children: ["비교 항목", "Claude", "GPT", "Gemini"].map(text =>
              new TableCell({
                borders: cellBorders,
                width: { size: text === "비교 항목" ? 2400 : 2440, type: WidthType.DXA },
                shading: { fill: ACCENT_LIGHT, type: ShadingType.CLEAR },
                verticalAlign: VerticalAlign.CENTER,
                children: [new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text, bold: true, size: 20, color: ACCENT })]
                })]
              })
            )
          }),
          // Data rows
          ...["정확성 (0~5)", "상세도 (0~5)", "형식 준수 (0~5)", "주요 장점", "주요 단점"].map(label =>
            new TableRow({
              children: [
                new TableCell({
                  borders: cellBorders,
                  width: { size: 2400, type: WidthType.DXA },
                  shading: { fill: "F8F9FA", type: ShadingType.CLEAR },
                  verticalAlign: VerticalAlign.CENTER,
                  children: [new Paragraph({
                    children: [new TextRun({ text: label, bold: true, size: 20 })]
                  })]
                }),
                ...Array(3).fill(null).map(() =>
                  new TableCell({
                    borders: cellBorders,
                    width: { size: 2440, type: WidthType.DXA },
                    verticalAlign: VerticalAlign.CENTER,
                    children: [new Paragraph({
                      alignment: AlignmentType.CENTER,
                      spacing: { before: 120, after: 120 },
                      children: [new TextRun({ text: "", size: 20 })]
                    })]
                  })
                )
              ]
            })
          )
        ]
      }),

      // 3) 평가 및 추천
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3) 평가 및 추천")] }),
      new Paragraph({
        numbering: { reference: "eval-list", level: 0 },
        spacing: { before: 80, after: 80 },
        children: [
          new TextRun({ text: "종합 평가: ", bold: true, size: 22 }),
          new TextRun({ text: "________________________________________", color: "CCCCCC", size: 22 })
        ]
      }),
      new Paragraph({
        numbering: { reference: "eval-list", level: 0 },
        spacing: { before: 80, after: 40 },
        children: [new TextRun({ text: "용도별 추천:", bold: true, size: 22 })]
      }),
      ...["빠른 요약이 필요할 때 →", "정확한 기준 인용이 필요할 때 →", "상세한 분석이 필요할 때 →"].map(text =>
        new Paragraph({
          numbering: { reference: "sub-eval-list", level: 0 },
          spacing: { before: 40, after: 40 },
          children: [
            new TextRun({ text: text + " ", size: 22 }),
            new TextRun({ text: "________________", color: "CCCCCC", size: 22 })
          ]
        })
      ),

      // === 제출 안내 ===
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("제출 안내")] }),
      new Table({
        columnWidths: [9720],
        rows: [new TableRow({
          children: [new TableCell({
            borders: {
              top: { style: BorderStyle.SINGLE, size: 1, color: "E74C3C" },
              bottom: { style: BorderStyle.SINGLE, size: 1, color: "E74C3C" },
              left: { style: BorderStyle.SINGLE, size: 6, color: "E74C3C" },
              right: { style: BorderStyle.SINGLE, size: 1, color: "E74C3C" }
            },
            shading: { fill: "FDEDEC", type: ShadingType.CLEAR },
            width: { size: 9720, type: WidthType.DXA },
            children: [
              new Paragraph({
                spacing: { before: 120, after: 60 },
                children: [new TextRun({ text: "📌 제출 방법", bold: true, size: 22, color: "C0392B" })]
              }),
              new Paragraph({
                spacing: { before: 40, after: 40 },
                indent: { left: 200 },
                children: [
                  new TextRun({ text: "형식: ", bold: true, size: 20 }),
                  new TextRun({ text: "PDF 또는 Word", size: 20 })
                ]
              }),
              new Paragraph({
                spacing: { before: 40, after: 120 },
                indent: { left: 200 },
                children: [
                  new TextRun({ text: "필수: ", bold: true, size: 20 }),
                  new TextRun({ text: "각 플랫폼(Claude, GPT, Gemini) 응답 ", size: 20 }),
                  new TextRun({ text: "스크린샷 첨부", bold: true, underline: { type: UnderlineType.SINGLE }, size: 20 })
                ]
              })
            ]
          })]
        })]
      }),

      // Footer note
      new Paragraph({
        spacing: { before: 400 },
        alignment: AlignmentType.CENTER,
        border: { top: { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" } },
        children: []
      }),
      new Paragraph({
        spacing: { before: 120 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "경희대학교 건축공학과  |  백장운 교수", size: 18, color: GRAY })]
      })
    ]
  }]
});

const outPath = process.argv[2] || "과제1_프롬프트설계.docx";
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(outPath, buffer);
  console.log("Created: " + outPath);
});
