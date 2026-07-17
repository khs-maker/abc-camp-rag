const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");

// ---------------------------------------------------------------------------
// Nordic Modern Palette
// ---------------------------------------------------------------------------
const C = {
  dark:    "1B2838",  // deep navy
  mid:     "2C3E50",  // slate
  accent:  "D4726A",  // warm coral
  sage:    "7FA88E",  // sage green
  sand:    "E8DDD3",  // warm sand
  light:   "F5F0EB",  // off-white
  white:   "FFFFFF",
  text:    "1B2838",
  muted:   "6B7B8D",
  chart1:  "D4726A",
  chart2:  "7FA88E",
  chart3:  "5B8A9A",
  chart4:  "C9A96E",
  chart5:  "8B6F8E",
};

const FONT_H = "Georgia";
const FONT_B = "Calibri";

// ---------------------------------------------------------------------------
// Icon helpers
// ---------------------------------------------------------------------------
function renderIconSvg(IconComponent, color, size = 256) {
  return ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
}

async function iconToBase64Png(IconComponent, color, size = 256) {
  const svg = renderIconSvg(IconComponent, color, size);
  const pngBuf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + pngBuf.toString("base64");
}

// Shadow factory (fresh object each time)
const mkShadow = () => ({ type: "outer", blur: 4, offset: 2, angle: 135, color: "000000", opacity: 0.08 });

// ---------------------------------------------------------------------------
// Slide helpers
// ---------------------------------------------------------------------------
function addFooter(slide, pageNum, total) {
  slide.addShape("rect", { x: 0, y: 5.2, w: 10, h: 0.425, fill: { color: C.dark } });
  slide.addText("YES24 IT Bestseller Analysis", {
    x: 0.5, y: 5.22, w: 5, h: 0.4,
    fontFace: FONT_B, fontSize: 9, color: C.sand, valign: "middle", margin: 0,
  });
  slide.addText(`${pageNum} / ${total}`, {
    x: 8, y: 5.22, w: 1.5, h: 0.4,
    fontFace: FONT_B, fontSize: 9, color: C.sand, align: "right", valign: "middle", margin: 0,
  });
}

function addNote(slide, text) {
  slide.addNotes(text);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
async function main() {
  // Load icons
  const { FaBook, FaChartBar, FaUsers, FaStar, FaMoneyBillWave, FaBrain, FaRobot, FaLightbulb, FaBullseye, FaCalendarAlt, FaBuilding, FaSearch, FaChartLine, FaRocket, FaCheckCircle } = require("react-icons/fa");

  const icons = {
    book:     await iconToBase64Png(FaBook, "#" + C.white),
    chart:    await iconToBase64Png(FaChartBar, "#" + C.white),
    users:    await iconToBase64Png(FaUsers, "#" + C.white),
    star:     await iconToBase64Png(FaStar, "#" + C.white),
    money:    await iconToBase64Png(FaMoneyBillWave, "#" + C.white),
    brain:    await iconToBase64Png(FaBrain, "#" + C.white),
    robot:    await iconToBase64Png(FaRobot, "#" + C.white),
    bulb:     await iconToBase64Png(FaLightbulb, "#" + C.white),
    target:   await iconToBase64Png(FaBullseye, "#" + C.white),
    calendar: await iconToBase64Png(FaCalendarAlt, "#" + C.white),
    building: await iconToBase64Png(FaBuilding, "#" + C.white),
    search:   await iconToBase64Png(FaSearch, "#" + C.white),
    line:     await iconToBase64Png(FaChartLine, "#" + C.white),
    rocket:   await iconToBase64Png(FaRocket, "#" + C.white),
    check:    await iconToBase64Png(FaCheckCircle, "#" + C.white),
    bookDark: await iconToBase64Png(FaBook, "#" + C.accent),
    robotDark:await iconToBase64Png(FaRobot, "#" + C.accent),
    brainDark:await iconToBase64Png(FaBrain, "#" + C.accent),
    bulbDark: await iconToBase64Png(FaLightbulb, "#" + C.sage),
    starDark: await iconToBase64Png(FaStar, "#" + C.accent),
  };

  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.author = "YES24 Data Analysis Team";
  pres.title = "YES24 IT Bestseller New Book Planning";

  const TOTAL = 15;

  // =====================================================================
  // SLIDE 1: Title
  // =====================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.dark };

    // Decorative circle
    s.addShape("ellipse", { x: 7.5, y: -1, w: 4, h: 4, fill: { color: C.accent, transparency: 85 } });
    s.addShape("ellipse", { x: 8.2, y: 2.5, w: 3, h: 3, fill: { color: C.sage, transparency: 85 } });

    s.addImage({ data: icons.book, x: 0.8, y: 1.2, w: 0.6, h: 0.6 });

    s.addText("YES24 IT 베스트셀러\n신규 도서 기획 제안", {
      x: 0.8, y: 1.9, w: 7, h: 2,
      fontFace: FONT_H, fontSize: 38, color: C.white, bold: true, lineSpacingMultiple: 1.2, margin: 0,
    });

    s.addShape("rect", { x: 0.8, y: 4.1, w: 1.2, h: 0.04, fill: { color: C.accent } });

    s.addText("DATA-DRIVEN BOOK PLANNING  |  2026", {
      x: 0.8, y: 4.3, w: 6, h: 0.4,
      fontFace: FONT_B, fontSize: 12, color: C.muted, charSpacing: 3, margin: 0,
    });

    addNote(s, "안녕하세요. 오늘 발표할 내용은 YES24 IT 분야 베스트셀러 1,000권의 데이터를 분석하여 신규 도서 기획 방향을 제안하는 내용입니다. 데이터 기반으로 시장 트렌드와 기회 영역을 파악하고, 실제 기획안을 제시하겠습니다. 약 15분 정도 소요되겠습니다.");
  }

  // =====================================================================
  // SLIDE 2: Agenda
  // =====================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.light };

    s.addText("목차", {
      x: 0.8, y: 0.5, w: 4, h: 0.7,
      fontFace: FONT_H, fontSize: 32, color: C.dark, bold: true, margin: 0,
    });

    const items = [
      { num: "01", title: "시장 개요", desc: "IT 도서 시장 현황 및 핵심 지표" },
      { num: "02", title: "가격 분석", desc: "가격대별 도서 분포 및 전략" },
      { num: "03", title: "트렌드 분석", desc: "키워드 트렌드 및 주요 출판사" },
      { num: "04", title: "신규 기획안", desc: "AI/자동화 중심 도서 기획 제안" },
    ];

    items.forEach((item, i) => {
      const yBase = 1.5 + i * 0.95;
      s.addShape("rect", { x: 0.8, y: yBase, w: 8.4, h: 0.8, fill: { color: C.white }, shadow: mkShadow() });
      s.addShape("rect", { x: 0.8, y: yBase, w: 0.06, h: 0.8, fill: { color: C.accent } });
      s.addText(item.num, {
        x: 1.1, y: yBase, w: 0.6, h: 0.8,
        fontFace: FONT_H, fontSize: 22, color: C.accent, bold: true, valign: "middle", margin: 0,
      });
      s.addText(item.title, {
        x: 1.8, y: yBase + 0.08, w: 5, h: 0.4,
        fontFace: FONT_H, fontSize: 16, color: C.dark, bold: true, margin: 0,
      });
      s.addText(item.desc, {
        x: 1.8, y: yBase + 0.42, w: 5, h: 0.3,
        fontFace: FONT_B, fontSize: 11, color: C.muted, margin: 0,
      });
    });

    addFooter(s, 2, TOTAL);
    addNote(s, "오늘 발표는 4개 섹션으로 구성됩니다. 먼저 시장 개요를 통해 IT 도서 시장의 전체적인 현황을 살펴보고, 가격 분석에서 어떤 가격대가 시장을 주도하는지 확인하겠습니다. 트렌드 분석에서는 AI 관련 키워드의 급증을 확인하고, 마지막으로 데이터 기반 신규 도서 기획안을 제시하겠습니다.");
  }

  // =====================================================================
  // SLIDE 3: Key Metrics Overview
  // =====================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.white };

    s.addText("시장 개요", {
      x: 0.8, y: 0.4, w: 5, h: 0.6,
      fontFace: FONT_H, fontSize: 28, color: C.dark, bold: true, margin: 0,
    });
    s.addText("KEY MARKET INDICATORS", {
      x: 0.8, y: 0.95, w: 5, h: 0.3,
      fontFace: FONT_B, fontSize: 10, color: C.muted, charSpacing: 2, margin: 0,
    });

    const metrics = [
      { icon: icons.book, value: "1,000", label: "분석 도서 수", bg: C.dark },
      { icon: icons.money, value: "22,845", label: "평균 가격 (원)", bg: C.mid },
      { icon: icons.star, value: "7.32", label: "평균 평점", bg: C.sage },
      { icon: icons.users, value: "19.4", label: "평균 리뷰 수", bg: C.accent },
    ];

    metrics.forEach((m, i) => {
      const x = 0.8 + i * 2.25;
      s.addShape("rect", { x, y: 1.6, w: 2.0, h: 2.8, fill: { color: m.bg }, shadow: mkShadow() });
      s.addImage({ data: m.icon, x: x + 0.7, y: 1.9, w: 0.55, h: 0.55 });
      s.addText(m.value, {
        x, y: 2.65, w: 2.0, h: 0.7,
        fontFace: FONT_H, fontSize: 36, color: C.white, bold: true, align: "center", valign: "middle", margin: 0,
      });
      s.addText(m.label, {
        x, y: 3.4, w: 2.0, h: 0.5,
        fontFace: FONT_B, fontSize: 11, color: C.white, align: "center", valign: "top", margin: 0,
      });
    });

    s.addText("YES24 IT/모바일 분야 베스트셀러 Top 1,000권 기준  |  2026년 7월 기준", {
      x: 0.8, y: 4.7, w: 8.4, h: 0.3,
      fontFace: FONT_B, fontSize: 9, color: C.muted, align: "center", margin: 0,
    });

    addFooter(s, 3, TOTAL);
    addNote(s, "YES24 IT 분야 베스트셀러 1,000권의 핵심 지표입니다. 평균 가격은 22,845원이며, 평균 평점 7.32, 평균 리뷰 수 19.4개입니다. 이 수치들은 향후 신규 도서 기획 시 가격 설정과 마케팅 전략 수립의 기준이 됩니다.");
  }

  // =====================================================================
  // SLIDE 4: Price Distribution
  // =====================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.white };

    s.addText("가격 분석", {
      x: 0.8, y: 0.4, w: 5, h: 0.6,
      fontFace: FONT_H, fontSize: 28, color: C.dark, bold: true, margin: 0,
    });
    s.addText("PRICE DISTRIBUTION", {
      x: 0.8, y: 0.95, w: 5, h: 0.3,
      fontFace: FONT_B, fontSize: 10, color: C.muted, charSpacing: 2, margin: 0,
    });

    // Bar chart
    s.addChart(pres.charts.BAR, [{
      name: "도서 수",
      labels: ["~1만", "1~2만", "2~3만", "3~4만", "4만~"],
      values: [6, 424, 424, 115, 31],
    }], {
      x: 0.5, y: 1.4, w: 5.5, h: 3.2, barDir: "col",
      chartColors: [C.sage, C.accent, C.chart3, C.chart4, C.chart5],
      showValue: true, dataLabelPosition: "outEnd", dataLabelColor: C.dark,
      catAxisLabelColor: C.muted, valAxisLabelColor: C.muted,
      valGridLine: { color: "E8E8E8", size: 0.5 },
      catGridLine: { style: "none" },
      showLegend: false,
      chartArea: { fill: { color: C.white } },
    });

    // Right side insights
    s.addShape("rect", { x: 6.5, y: 1.4, w: 3.2, h: 3.2, fill: { color: C.light }, shadow: mkShadow() });

    const insights = [
      { value: "84.8%", label: "1~3만원대 집중", color: C.accent },
      { value: "21,600원", label: "중앙값 (median)", color: C.mid },
      { value: "5,625~65,000원", label: "가격 범위", color: C.sage },
    ];

    insights.forEach((ins, i) => {
      const yBase = 1.65 + i * 0.95;
      s.addShape("rect", { x: 6.7, y: yBase, w: 0.06, h: 0.7, fill: { color: ins.color } });
      s.addText(ins.value, {
        x: 6.95, y: yBase, w: 2.5, h: 0.4,
        fontFace: FONT_H, fontSize: 18, color: C.dark, bold: true, margin: 0,
      });
      s.addText(ins.label, {
        x: 6.95, y: yBase + 0.38, w: 2.5, h: 0.3,
        fontFace: FONT_B, fontSize: 10, color: C.muted, margin: 0,
      });
    });

    addFooter(s, 4, TOTAL);
    addNote(s, "가격 분석 결과입니다. 전체 도서의 84.8%가 1만~3만원대에 집중되어 있습니다. 이는 IT 도서 시장에서 이 가격대가 소비자에게 가장 적합한 가격대로 인식되고 있음을 보여줍니다. 신규 도서 기획 시 2만원대 초반을 기본 가격으로 설정하는 것이 효과적일 것입니다.");
  }

  // =====================================================================
  // SLIDE 5: Price Strategy
  // =====================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.light };

    s.addText("가격 전략 제안", {
      x: 0.8, y: 0.4, w: 5, h: 0.6,
      fontFace: FONT_H, fontSize: 28, color: C.dark, bold: true, margin: 0,
    });
    s.addText("PRICING STRATEGY RECOMMENDATION", {
      x: 0.8, y: 0.95, w: 6, h: 0.3,
      fontFace: FONT_B, fontSize: 10, color: C.muted, charSpacing: 2, margin: 0,
    });

    const strategies = [
      { tier: "Entry", price: "15,000~19,000원", desc: "입문자 대상\n실습 중심 가이드", color: C.sage, icon: icons.bookDark },
      { tier: "Core", price: "21,000~25,000원", desc: "핵심 개념 + 심화\n가장 높은 수요", color: C.accent, icon: icons.starDark },
      { tier: "Premium", price: "30,000~40,000원", desc: "전문가 대상\n프로젝트 기반", color: C.mid, icon: icons.brainDark },
    ];

    strategies.forEach((st, i) => {
      const x = 0.8 + i * 3.05;
      s.addShape("rect", { x, y: 1.5, w: 2.8, h: 3.0, fill: { color: C.white }, shadow: mkShadow() });
      s.addShape("rect", { x, y: 1.5, w: 2.8, h: 0.06, fill: { color: st.color } });
      s.addImage({ data: st.icon, x: x + 1.05, y: 1.75, w: 0.6, h: 0.6 });
      s.addText(st.tier, {
        x, y: 2.5, w: 2.8, h: 0.4,
        fontFace: FONT_H, fontSize: 18, color: C.dark, bold: true, align: "center", margin: 0,
      });
      s.addText(st.price, {
        x, y: 2.9, w: 2.8, h: 0.4,
        fontFace: FONT_H, fontSize: 20, color: st.color, bold: true, align: "center", margin: 0,
      });
      s.addText(st.desc, {
        x: x + 0.3, y: 3.4, w: 2.2, h: 0.8,
        fontFace: FONT_B, fontSize: 11, color: C.muted, align: "center", margin: 0,
      });
    });

    addFooter(s, 5, TOTAL);
    addNote(s, "가격 전략으로 3가지 티어를 제안합니다. Entry 티어는 15,000~19,000원대로 입문자 대상 실습 가이드, Core 티어는 21,000~25,000원대로 가장 높은 수요가 예상되는 핵심 개념서, Premium 티어는 30,000~40,000원대로 전문가 대상 프로젝트 기반 도서입니다. 시장 데이터 기반으로 가장 효과적인 가격대를 설정했습니다.");
  }

  // =====================================================================
  // SLIDE 6: Rating Analysis
  // =====================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.white };

    s.addText("평점 & 리뷰 분석", {
      x: 0.8, y: 0.4, w: 5, h: 0.6,
      fontFace: FONT_H, fontSize: 28, color: C.dark, bold: true, margin: 0,
    });
    s.addText("RATING & REVIEW ANALYSIS", {
      x: 0.8, y: 0.95, w: 6, h: 0.3,
      fontFace: FONT_B, fontSize: 10, color: C.muted, charSpacing: 2, margin: 0,
    });

    // Rating distribution chart
    s.addChart(pres.charts.BAR, [{
      name: "도서 수",
      labels: ["0~2", "2~4", "4~6", "6~8", "8~10"],
      values: [45, 30, 120, 350, 455],
    }], {
      x: 0.5, y: 1.4, w: 4.5, h: 3.0, barDir: "col",
      chartColors: [C.chart5, C.chart4, C.chart3, C.sage, C.accent],
      showValue: true, dataLabelPosition: "outEnd", dataLabelColor: C.dark,
      catAxisLabelColor: C.muted, valAxisLabelColor: C.muted,
      valGridLine: { color: "E8E8E8", size: 0.5 },
      catGridLine: { style: "none" },
      showLegend: false,
      showTitle: true, title: "평점 분포", titleColor: C.dark, titleFontFace: FONT_H, titleFontSize: 12,
      chartArea: { fill: { color: C.white } },
    });

    // Top reviewed books
    s.addShape("rect", { x: 5.5, y: 1.4, w: 4.2, h: 3.2, fill: { color: C.light }, shadow: mkShadow() });
    s.addText("리뷰 Top 5", {
      x: 5.7, y: 1.55, w: 3.8, h: 0.35,
      fontFace: FONT_H, fontSize: 14, color: C.dark, bold: true, margin: 0,
    });

    const topBooks = [
      { title: "오늘부터 자율주행 차량을 만듭니다", reviews: 388, rating: 9.8 },
      { title: "20가지 비즈니스 모델로 만드는 Notion", reviews: 370, rating: 9.7 },
      { title: "자동화 학습 자동코드와 파이썬 기초", reviews: 310, rating: 9.8 },
      { title: "처음 만나는 SNS 마케팅 캠페인", reviews: 273, rating: 10.0 },
      { title: "이거슨? ChatGPT 친구 활용법 71가지", reviews: 259, rating: 9.6 },
    ];

    topBooks.forEach((b, i) => {
      const y = 2.05 + i * 0.5;
      s.addText(`${i + 1}.`, {
        x: 5.7, y, w: 0.3, h: 0.4,
        fontFace: FONT_H, fontSize: 11, color: C.accent, bold: true, valign: "middle", margin: 0,
      });
      s.addText(b.title.length > 25 ? b.title.substring(0, 25) + "..." : b.title, {
        x: 6.0, y, w: 2.3, h: 0.4,
        fontFace: FONT_B, fontSize: 10, color: C.dark, valign: "middle", margin: 0,
      });
      s.addText(`${b.reviews}개`, {
        x: 8.5, y, w: 0.9, h: 0.4,
        fontFace: FONT_B, fontSize: 10, color: C.accent, bold: true, align: "right", valign: "middle", margin: 0,
      });
    });

    addFooter(s, 6, TOTAL);
    addNote(s, "평점 분석 결과입니다. 전체 도서의 45.5%가 8점 이상의 높은 평점을 받고 있습니다. 이는 IT 도서 독자들이 만족도가 높다는 것을 보여줍니다. 리뷰 수 기준으로는 자율주행, Notion, 자동화 관련 도서가 상위에 랭크되어 있으며, 실용적인 콘텐츠가 높은 반응을 얻고 있습니다.");
  }

  // =====================================================================
  // SLIDE 7: Publisher Analysis
  // =====================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.white };

    s.addText("주요 출판사 분석", {
      x: 0.8, y: 0.4, w: 5, h: 0.6,
      fontFace: FONT_H, fontSize: 28, color: C.dark, bold: true, margin: 0,
    });
    s.addText("TOP PUBLISHERS", {
      x: 0.8, y: 0.95, w: 5, h: 0.3,
      fontFace: FONT_B, fontSize: 10, color: C.muted, charSpacing: 2, margin: 0,
    });

    // Horizontal bar chart
    s.addChart(pres.charts.BAR, [{
      name: "도서 수",
      labels: ["한빛미디어", "길벗", "위키북스", "كون텐츠미디어", "인피니티북스", "영진닷컴", "프로텍미디어", "인사이트", "에이콘출판", "로드북"],
      values: [146, 80, 53, 52, 47, 40, 35, 31, 31, 27],
    }], {
      x: 0.5, y: 1.3, w: 9, h: 3.5, barDir: "bar",
      chartColors: [C.accent],
      showValue: true, dataLabelPosition: "outEnd", dataLabelColor: C.dark,
      catAxisLabelColor: C.dark, valAxisLabelColor: C.muted,
      valGridLine: { color: "E8E8E8", size: 0.5 },
      catGridLine: { style: "none" },
      showLegend: false,
      chartArea: { fill: { color: C.white } },
    });

    addFooter(s, 7, TOTAL);
    addNote(s, "출판사 분석입니다. 한빛미디어가 146권으로 압도적인 1위를 차지하고 있으며, 그 다음으로 길벗 80권, 위키북스 53권 순입니다. 상위 3개 출판사가 전체의 약 28%를 차지하고 있어 시장 집중도가 높습니다. 신규 진입 시 이 출판사들의 출판 패턴과 주제 선택을 참고하는 것이 중요합니다.");
  }

  // =====================================================================
  // SLIDE 8: Keyword Trends
  // =====================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.dark };

    s.addText("키워드 트렌드", {
      x: 0.8, y: 0.4, w: 5, h: 0.6,
      fontFace: FONT_H, fontSize: 28, color: C.white, bold: true, margin: 0,
    });
    s.addText("TOP KEYWORDS IN IT BOOK TITLES", {
      x: 0.8, y: 0.95, w: 6, h: 0.3,
      fontFace: FONT_B, fontSize: 10, color: C.muted, charSpacing: 2, margin: 0,
    });

    // Keyword bubbles (visual representation)
    const keywords = [
      { word: "AI", count: 225, x: 1.2, y: 1.6, size: 1.6, color: C.accent },
      { word: "개발", count: 74, x: 3.2, y: 2.0, size: 1.0, color: C.sage },
      { word: "프로그래밍", count: 60, x: 5.0, y: 1.5, size: 0.9, color: C.chart3 },
      { word: "자동화", count: 57, x: 4.5, y: 3.2, size: 0.85, color: C.chart4 },
      { word: "기초", count: 44, x: 2.5, y: 3.5, size: 0.8, color: C.chart5 },
      { word: "ChatGPT", count: 38, x: 6.5, y: 2.5, size: 0.75, color: C.accent },
      { word: "프롬프트", count: 37, x: 7.8, y: 1.8, size: 0.7, color: C.sage },
      { word: "실습", count: 37, x: 6.8, y: 3.8, size: 0.7, color: C.chart3 },
      { word: "ẢN", count: 36, x: 8.2, y: 3.5, size: 0.65, color: C.chart4 },
      { word: "데이터", count: 33, x: 3.8, y: 4.0, size: 0.65, color: C.chart5 },
    ];

    keywords.forEach(k => {
      s.addShape("ellipse", { x: k.x, y: k.y, w: k.size, h: k.size, fill: { color: k.color, transparency: 70 } });
      s.addText(k.word, {
        x: k.x, y: k.y, w: k.size, h: k.size,
        fontFace: FONT_H, fontSize: k.count > 100 ? 18 : 12, color: C.white, bold: true,
        align: "center", valign: "middle", margin: 0,
      });
    });

    // Legend
    s.addText("버블 크기 = 제목 출현 빈도", {
      x: 0.8, y: 4.7, w: 4, h: 0.3,
      fontFace: FONT_B, fontSize: 9, color: C.muted, margin: 0,
    });

    addFooter(s, 8, TOTAL);
    addNote(s, "키워드 트렌드 분석입니다. AI가 225건으로 압도적인 1위를 차지하고 있으며, 개발 74건, 프로그래밍 60건, 자동화 57건 순입니다. 특히 ChatGPT와 프롬프트 관련 키워드가 급증하고 있어, AI 관련 도서 시장이 급속히 확대되고 있음을 확인할 수 있습니다.");
  }

  // =====================================================================
  // SLIDE 9: AI Topic Deep Dive
  // =====================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.white };

    s.addText("AI 도서 트렌드 심화 분석", {
      x: 0.8, y: 0.4, w: 6, h: 0.6,
      fontFace: FONT_H, fontSize: 28, color: C.dark, bold: true, margin: 0,
    });
    s.addText("AI BOOK TRENDS DEEP DIVE", {
      x: 0.8, y: 0.95, w: 6, h: 0.3,
      fontFace: FONT_B, fontSize: 10, color: C.muted, charSpacing: 2, margin: 0,
    });

    // Left: AI book count vs others
    s.addChart(pres.charts.DOUGHNUT, [{
      name: "주제별 비중",
      labels: ["AI/ChatGPT", "프로그래밍", "자동화/기초", "기타"],
      values: [225, 134, 101, 540],
    }], {
      x: 0.3, y: 1.3, w: 4.5, h: 3.5,
      chartColors: [C.accent, C.sage, C.chart3, C.chart4],
      showPercent: true,
      showLegend: true, legendPos: "b", legendColor: C.dark,
      chartArea: { fill: { color: C.white } },
    });

    // Right: Key insights
    s.addShape("rect", { x: 5.3, y: 1.3, w: 4.3, h: 3.5, fill: { color: C.light }, shadow: mkShadow() });
    s.addText("핵심 인사이트", {
      x: 5.5, y: 1.5, w: 3.9, h: 0.35,
      fontFace: FONT_H, fontSize: 16, color: C.dark, bold: true, margin: 0,
    });

    const aiInsights = [
      { num: "22.5%", desc: "전체 도서 중 AI 관련 도서 비중" },
      { num: "ChatGPT", desc: "가장 많이 등장하는 AI 도구 브랜드" },
      { num: "프롬프트", desc: "AI 활용법을 다루는 도서 급증" },
      { num: "실습 중심", desc: "이론보다 실습/프로젝트 기반 선호" },
    ];

    aiInsights.forEach((ins, i) => {
      const y = 2.05 + i * 0.65;
      s.addText(ins.num, {
        x: 5.5, y, w: 1.5, h: 0.5,
        fontFace: FONT_H, fontSize: 16, color: C.accent, bold: true, valign: "middle", margin: 0,
      });
      s.addText(ins.desc, {
        x: 7.0, y, w: 2.4, h: 0.5,
        fontFace: FONT_B, fontSize: 11, color: C.dark, valign: "middle", margin: 0,
      });
    });

    addFooter(s, 9, TOTAL);
    addNote(s, "AI 도서 트렌드 심화 분석입니다. 전체 1,000권 중 225권이 AI 관련으로, 전체의 22.5%를 차지합니다. ChatGPT와 프롬프트 관련 도서가 급증하고 있으며, 독자들은 이론보다 실습과 프로젝트 중심의 콘텐츠를 선호하는 경향이 강합니다.");
  }

  // =====================================================================
  // SLIDE 10: Year Trend
  // =====================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.white };

    s.addText("연도별 출판 동향", {
      x: 0.8, y: 0.4, w: 5, h: 0.6,
      fontFace: FONT_H, fontSize: 28, color: C.dark, bold: true, margin: 0,
    });
    s.addText("PUBLICATION TREND BY YEAR", {
      x: 0.8, y: 0.95, w: 6, h: 0.3,
      fontFace: FONT_B, fontSize: 10, color: C.muted, charSpacing: 2, margin: 0,
    });

    s.addChart(pres.charts.LINE, [{
      name: "도서 수",
      labels: ["2020", "2021", "2022", "2023", "2024", "2025", "2026"],
      values: [19, 16, 38, 35, 114, 319, 422],
    }], {
      x: 0.5, y: 1.3, w: 9, h: 3.5,
      lineSize: 3, lineSmooth: true,
      chartColors: [C.accent],
      showMarker: true, markerSize: 8,
      showValue: true, dataLabelPosition: "t", dataLabelColor: C.dark,
      catAxisLabelColor: C.muted, valAxisLabelColor: C.muted,
      valGridLine: { color: "E8E8E8", size: 0.5 },
      catGridLine: { style: "none" },
      showLegend: false,
      chartArea: { fill: { color: C.white } },
    });

    addFooter(s, 10, TOTAL);
    addNote(s, "연도별 출판 동향입니다. 2020년 19권에서 2026년 422권으로 약 22배 성장했습니다. 특히 2024년부터 급격한 증가세를 보이고 있으며, 이는 AI 열풍과 맞물려 IT 도서 시장이 폭발적으로 성장하고 있음을 보여줍니다. 이러한 성장세는 향후 2~3년간 지속될 것으로 예상됩니다.");
  }

  // =====================================================================
  // SLIDE 11: Market Opportunity
  // =====================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.light };

    s.addText("시장 기회 분석", {
      x: 0.8, y: 0.4, w: 5, h: 0.6,
      fontFace: FONT_H, fontSize: 28, color: C.dark, bold: true, margin: 0,
    });
    s.addText("MARKET OPPORTUNITY MATRIX", {
      x: 0.8, y: 0.95, w: 6, h: 0.3,
      fontFace: FONT_B, fontSize: 10, color: C.muted, charSpacing: 2, margin: 0,
    });

    // 2x2 Matrix
    // High demand, Low competition
    const matrix = [
      { x: 0.8, y: 1.5, title: "높은 수요\n낮은 경쟁", items: ["AI 자동화 실습", "노코드/로코드", "DevOps 입문"], color: C.sage, label: "기회 영역" },
      { x: 5.2, y: 1.5, title: "높은 수요\n높은 경쟁", items: ["ChatGPT 활용법", "파이썬 기초", "웹개발 입문"], color: C.chart4, label: "차별화 필요" },
      { x: 0.8, y: 3.2, title: "낮은 수요\n낮은 경쟁", items: ["블록체인 심화", "임베디드 시스템", "양자 컴퓨팅"], color: C.chart5, label: "니치 영역" },
      { x: 5.2, y: 3.2, title: "낮은 수요\n높은 경쟁", items: ["일반 CS 이론", "전공 서적", "자격증 문제집"], color: C.chart3, label: "피드 영역" },
    ];

    matrix.forEach(m => {
      s.addShape("rect", { x: m.x, y: m.y, w: 4.0, h: 1.5, fill: { color: C.white }, shadow: mkShadow() });
      s.addShape("rect", { x: m.x, y: m.y, w: 4.0, h: 0.06, fill: { color: m.color } });
      s.addText(m.label, {
        x: m.x + 0.15, y: m.y + 0.15, w: 1.5, h: 0.25,
        fontFace: FONT_B, fontSize: 9, color: m.color, bold: true, margin: 0,
      });
      s.addText(m.title, {
        x: m.x + 0.15, y: m.y + 0.4, w: 1.6, h: 0.7,
        fontFace: FONT_H, fontSize: 12, color: C.dark, bold: true, margin: 0,
      });
      m.items.forEach((item, i) => {
        s.addText(`• ${item}`, {
          x: m.x + 1.8, y: m.y + 0.4 + i * 0.35, w: 2.0, h: 0.3,
          fontFace: FONT_B, fontSize: 10, color: C.muted, margin: 0,
        });
      });
    });

    addFooter(s, 11, TOTAL);
    addNote(s, "시장 기회 매트릭스입니다. 높은 수요에 비해 경쟁이 적은 기회 영역으로 AI 자동화 실습, 노코드/로코드, DevOps 입문 분야가 있습니다. 반면 ChatGPT 활용법이나 파이썬 기초는 수요가 높지만 경쟁도 치열하므로 차별화된 접근이 필요합니다.");
  }

  // =====================================================================
  // SLIDE 12: New Book Proposal - Concept
  // =====================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.dark };

    s.addImage({ data: icons.rocket, x: 0.8, y: 0.5, w: 0.5, h: 0.5 });

    s.addText("신규 도서 기획안", {
      x: 0.8, y: 1.1, w: 8, h: 0.7,
      fontFace: FONT_H, fontSize: 32, color: C.white, bold: true, margin: 0,
    });
    s.addText("NEW BOOK PROPOSAL", {
      x: 0.8, y: 1.75, w: 8, h: 0.3,
      fontFace: FONT_B, fontSize: 11, color: C.muted, charSpacing: 3, margin: 0,
    });

    s.addShape("rect", { x: 0.8, y: 2.3, w: 1.2, h: 0.04, fill: { color: C.accent } });

    s.addText("AI로 만드는 자동화 워크플로우\n실습으로 배우는 프롬프트 엔지니어링", {
      x: 0.8, y: 2.6, w: 8, h: 1.2,
      fontFace: FONT_H, fontSize: 28, color: C.white, bold: true, lineSpacingMultiple: 1.3, margin: 0,
    });

    s.addText("데이터 기반 시장 분석을 통해 도출된 최적의 도서 기획안", {
      x: 0.8, y: 4.0, w: 8, h: 0.4,
      fontFace: FONT_B, fontSize: 13, color: C.sand, italic: true, margin: 0,
    });

    // Decorative elements
    s.addShape("ellipse", { x: 8.0, y: 3.5, w: 2.5, h: 2.5, fill: { color: C.accent, transparency: 88 } });

    addNote(s, "이제 구체적인 신규 도서 기획안을 제시하겠습니다. 제목은 'AI로 만드는 자동화 워크플로우: 실습으로 배우는 프롬프트 엔지니어링'입니다. 앞서 분석한 시장 데이터를 기반으로, 가장 높은 수요와 가장 적절한 경쟁 강도를 가진 영역을 타겟으로 설정했습니다.");
  }

  // =====================================================================
  // SLIDE 13: Book Details
  // =====================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.white };

    s.addText("도서 상세 기획", {
      x: 0.8, y: 0.4, w: 5, h: 0.6,
      fontFace: FONT_H, fontSize: 28, color: C.dark, bold: true, margin: 0,
    });
    s.addText("BOOK PLANNING DETAILS", {
      x: 0.8, y: 0.95, w: 6, h: 0.3,
      fontFace: FONT_B, fontSize: 10, color: C.muted, charSpacing: 2, margin: 0,
    });

    // Left column
    const leftItems = [
      { label: "제목", value: "AI로 만드는 자동화 워크플로우" },
      { label: "부제", value: "실습으로 배우는 프롬프트 엔지니어링" },
      { label: "대상 독자", value: "직장인, 마케터, 기획자" },
      { label: "분량", value: "320페이지 / A4 변형" },
      { label: "가격", value: "22,000원 (Core 티어)" },
      { label: "출간 목표", value: "2026년 4분기" },
    ];

    leftItems.forEach((item, i) => {
      const y = 1.4 + i * 0.55;
      s.addText(item.label, {
        x: 0.8, y, w: 1.8, h: 0.4,
        fontFace: FONT_B, fontSize: 11, color: C.muted, bold: true, valign: "middle", margin: 0,
      });
      s.addText(item.value, {
        x: 2.6, y, w: 2.5, h: 0.4,
        fontFace: FONT_B, fontSize: 12, color: C.dark, valign: "middle", margin: 0,
      });
    });

    // Right column - chapter outline
    s.addShape("rect", { x: 5.5, y: 1.2, w: 4.2, h: 3.8, fill: { color: C.light }, shadow: mkShadow() });
    s.addText(".chapter outline", {
      x: 5.7, y: 1.35, w: 3.8, h: 0.35,
      fontFace: FONT_H, fontSize: 14, color: C.dark, bold: true, margin: 0,
    });

    const chapters = [
      "Ch.1  AI와 자동화의 이해",
      "Ch.2  프롬프트 엔지니어링 기초",
      "Ch.3  실습: 업무 자동화 만들기",
      "Ch.4  ChatGPT/Claude 활용법",
      "Ch.5  이미지 생성 AI 실습",
      "Ch.6  API 연동 자동화",
      "Ch.7  팀 협업 워크플로우",
      "Ch.8  실제 프로젝트 5가지",
    ];

    chapters.forEach((ch, i) => {
      s.addText(ch, {
        x: 5.7, y: 1.85 + i * 0.38, w: 3.8, h: 0.35,
        fontFace: FONT_B, fontSize: 10, color: C.dark, margin: 0,
      });
    });

    addFooter(s, 13, TOTAL);
    addNote(s, "도서 상세 기획입니다. 대상 독자는 직장인, 마케터, 기획자로 설정했으며, 가격은 시장 분석 기반으로 22,000원으로 책정했습니다. 8개 챕터로 구성되며, 이론 30%, 실습 70% 비율로 구성할 계획입니다. 출간 목표는 2026년 4분기입니다.");
  }

  // =====================================================================
  // SLIDE 14: Differentiation Strategy
  // =====================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.light };

    s.addText("차별화 전략", {
      x: 0.8, y: 0.4, w: 5, h: 0.6,
      fontFace: FONT_H, fontSize: 28, color: C.dark, bold: true, margin: 0,
    });
    s.addText("DIFFERENTIATION STRATEGY", {
      x: 0.8, y: 0.95, w: 6, h: 0.3,
      fontFace: FONT_B, fontSize: 10, color: C.muted, charSpacing: 2, margin: 0,
    });

    const strategies = [
      { icon: icons.robotDark, title: "실습 중심 구성", desc: "이론 30% / 실습 70%\n각 챕터마다 실제 프로젝트 포함\n코드 소스 GitHub 제공" },
      { icon: icons.bulbDark, title: "비개발자 친화적", desc: "코딩 경험 없이도 따라할 수 있는 구조\n스크린샷 기반 단계별 가이드\n용어 사전 부록 제공" },
      { icon: icons.brainDark, title: "업무 적용 중심", desc: "실제 업무 자동화 사례 20가지\n마케팅/기획/운영 분야 타겟\n즉시 적용 가능한 템플릿 제공" },
    ];

    strategies.forEach((st, i) => {
      const x = 0.8 + i * 3.05;
      s.addShape("rect", { x, y: 1.5, w: 2.8, h: 3.2, fill: { color: C.white }, shadow: mkShadow() });
      s.addShape("rect", { x, y: 1.5, w: 0.06, h: 3.2, fill: { color: C.accent } });
      s.addImage({ data: st.icon, x: x + 0.3, y: 1.75, w: 0.5, h: 0.5 });
      s.addText(st.title, {
        x: x + 0.3, y: 2.4, w: 2.2, h: 0.4,
        fontFace: FONT_H, fontSize: 15, color: C.dark, bold: true, margin: 0,
      });
      s.addText(st.desc, {
        x: x + 0.3, y: 2.9, w: 2.2, h: 1.5,
        fontFace: FONT_B, fontSize: 11, color: C.muted, margin: 0,
      });
    });

    addFooter(s, 14, TOTAL);
    addNote(s, "차별화 전략입니다. 첫째, 실습 중심 구성을 통해 기존 도서와 차별화합니다. 둘째, 비개발자도 쉽게 따라할 수 있는 구조로 접근성을 높입니다. 셋째, 실제 업무에 즉시 적용할 수 있는 사례와 템플릿을 제공하여 실용성을 극대화합니다. 이 세 가지 전략이 시장에서의 경쟁 우위를 확보할 것입니다.");
  }

  // =====================================================================
  // SLIDE 15: Conclusion & Next Steps
  // =====================================================================
  {
    const s = pres.addSlide();
    s.background = { color: C.dark };

    // Decorative circles
    s.addShape("ellipse", { x: -1, y: -1, w: 3, h: 3, fill: { color: C.accent, transparency: 88 } });
    s.addShape("ellipse", { x: 8.5, y: 3.5, w: 2.5, h: 2.5, fill: { color: C.sage, transparency: 88 } });

    s.addText("다음 단계", {
      x: 0.8, y: 0.5, w: 5, h: 0.6,
      fontFace: FONT_H, fontSize: 28, color: C.white, bold: true, margin: 0,
    });
    s.addText("NEXT STEPS", {
      x: 0.8, y: 1.05, w: 5, h: 0.3,
      fontFace: FONT_B, fontSize: 10, color: C.muted, charSpacing: 3, margin: 0,
    });

    const steps = [
      { num: "01", title: "원고 집필 착수", date: "2026년 8월", desc: "챕터별 집필 일정 수립 및 저자 매칭" },
      { num: "02", title: "편집 디자인 확정", date: "2026년 9월", desc: "표지/내지 디자인 및 레이아웃 확정" },
      { num: "03", title: "교정 & 검수", date: "2026년 10월", desc: "전문가 리뷰 및 기술 검증" },
      { num: "04", title: "출간 & 마케팅", date: "2026년 11월", desc: "YES24 독점 예약판매 시작" },
    ];

    steps.forEach((step, i) => {
      const y = 1.6 + i * 0.85;
      s.addShape("rect", { x: 0.8, y, w: 8.4, h: 0.7, fill: { color: C.white, transparency: 90 } });
      s.addShape("rect", { x: 0.8, y, w: 0.06, h: 0.7, fill: { color: C.accent } });
      s.addText(step.num, {
        x: 1.1, y, w: 0.6, h: 0.7,
        fontFace: FONT_H, fontSize: 18, color: C.accent, bold: true, valign: "middle", margin: 0,
      });
      s.addText(step.title, {
        x: 1.8, y: y + 0.05, w: 3, h: 0.35,
        fontFace: FONT_H, fontSize: 14, color: C.white, bold: true, margin: 0,
      });
      s.addText(step.date, {
        x: 5.5, y: y + 0.05, w: 1.5, h: 0.35,
        fontFace: FONT_B, fontSize: 11, color: C.accent, bold: true, margin: 0,
      });
      s.addText(step.desc, {
        x: 1.8, y: y + 0.35, w: 6, h: 0.3,
        fontFace: FONT_B, fontSize: 10, color: C.sand, margin: 0,
      });
    });

    // Closing
    s.addText("감사합니다", {
      x: 0.8, y: 4.6, w: 8.4, h: 0.5,
      fontFace: FONT_H, fontSize: 18, color: C.white, bold: true, align: "center", margin: 0,
    });

    addNote(s, "마지막으로 다음 단계입니다. 8월 원고 집필 착수, 9월 편집 디자인 확정, 10월 교정 검수, 11월 출간 및 마케팅 시작으로 일정을 잡았습니다. 데이터 기반으로 검증된 시장 기회를 통해 성공적인 도서 출간이 될 것으로 기대합니다. 감사합니다. 질문 있으시면 말씀해 주세요.");
  }

  // =====================================================================
  // Save
  // =====================================================================
  const outPath = "C:\\ABC-LAG\\data\\yes24_it_book_proposal.pptx";
  await pres.writeFile({ fileName: outPath });
  console.log("PPTX saved to:", outPath);
}

main().catch(err => { console.error(err); process.exit(1); });
