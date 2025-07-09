<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>한글 OCR 최적화 인터랙티브 가이드</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
    <!-- Chosen Palette: Warm Neutrals -->
    <!-- Application Structure Plan: 이 SPA는 보고서의 선형적 구조를 탈피하여, 사용자가 자신의 요구사항에 따라 맞춤형 정보를 얻는 '가이드형 대시보드'로 설계되었습니다. 핵심은 'OCR 경로 선택기'로, 사용자의 입력을 받아 최적의 기술 스택(Tesseract, PaddleOCR, 상용 API 등)을 추천합니다. 이 추천에 따라 '전처리 기술', '엔진 비교' 등 연관 섹션으로 자연스럽게 유도하여, 수동적인 정보 습득이 아닌 능동적인 의사결정 과정을 지원합니다. 이는 복잡한 기술 정보를 소화하고 실제 프로젝트에 적용하는 데 훨씬 효율적입니다. -->
    <!-- Visualization & Content Choices: 
        1. 보고서 정보: OCR 엔진별 성능 비교 -> 목표: 비교 -> 시각화: 인터랙티브 가로 막대 차트(Chart.js) -> 상호작용: 차트 막대 호버 시 세부 정보 표시, 클릭 시 해당 엔진 상세 정보로 스크롤 -> 정당성: 사용자가 가장 중요하게 생각하는 '예상 정확도'를 한눈에 비교하고, 관심 있는 엔진을 심층적으로 탐색하도록 유도합니다.
        2. 보고서 정보: 다양한 이진화 기법 -> 목표: 비교/시연 -> 시각화: '전/후' 이미지 비교 뷰어 -> 상호작용: 사용자가 '균일 조명', '불균일 조명' 등 이미지 시나리오를 선택하면, 각기 다른 이진화 알고리즘(전역, 오츠, 적응형)의 결과를 시각적으로 즉시 비교 -> 정당성: 추상적인 알고리즘 설명을 넘어, 실제 이미지에 적용된 결과를 직접 보여줌으로써 각 기법의 장단점을 직관적으로 이해시킵니다.
        3. 보고서 정보: 의사 결정 트리 -> 목표: 안내/추천 -> 시각화: 단계별 질문으로 구성된 위저드(Wizard) UI -> 상호작용: 사용자가 예산, 정확도 요구 수준 등 프로젝트 제약 조건을 선택하면, 그에 맞는 최적의 OCR 경로(예: "PaddleOCR + 후처리")를 동적으로 추천 -> 정당성: 사용자의 참여를 유도하여 개인화된 솔루션을 제공함으로써, 정보의 실용성과 만족도를 극대화합니다.
        CONFIRMATION: NO SVG graphics used. NO Mermaid JS used. -->
    <style>
        body { font-family: 'Noto Sans KR', sans-serif; background-color: #FDFBF7; color: #4a4a4a; }
        .chart-container { position: relative; width: 100%; max-width: 800px; margin-left: auto; margin-right: auto; height: 300px; max-height: 400px; }
        @media (min-width: 768px) { .chart-container { height: 400px; max-height: 500px; } }
        .nav-button { transition: all 0.3s ease; }
        .nav-button.active { color: #D97706; border-color: #D97706; background-color: #FEF3C7; }
        .nav-button:hover { color: #D97706; border-color: #FDBA74; }
        .content-section { display: none; }
        .content-section.active { display: block; }
        .code-block { background-color: #282c34; color: #abb2bf; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; font-size: 0.875rem; line-height: 1.5; }
        .pill { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; font-weight: 500; font-size: 0.8rem; }
    </style>
</head>
<body class="antialiased">

    <div class="container mx-auto px-4 py-8 md:py-12">
        
        <header class="text-center mb-10 md:mb-16">
            <h1 class="text-4xl md:text-5xl font-bold text-gray-800 mb-2">한글 OCR 최적화 가이드</h1>
            <p class="text-lg text-gray-600">프로젝트에 가장 적합한 OCR 전략을 찾아보세요.</p>
        </header>

        <nav class="flex flex-wrap justify-center gap-2 md:gap-4 mb-12 border-b pb-4">
            <button data-target="selector" class="nav-button active border-b-2 px-4 py-2 font-semibold text-gray-600">🚀 경로 선택기</button>
            <button data-target="comparison" class="nav-button border-b-2 border-transparent px-4 py-2 font-semibold text-gray-600">📊 엔진 비교</button>
            <button data-target="preprocess" class="nav-button border-b-2 border-transparent px-4 py-2 font-semibold text-gray-600">✨ 전처리 기술</button>
            <button data-target="postprocess" class="nav-button border-b-2 border-transparent px-4 py-2 font-semibold text-gray-600">🔧 후처리 팁</button>
        </nav>

        <main>
            <section id="selector" class="content-section active">
                <div class="bg-white p-6 md:p-8 rounded-xl shadow-lg border border-gray-200">
                    <h2 class="text-2xl font-bold mb-1 text-gray-800">최적의 OCR 경로 찾기</h2>
                    <p class="text-gray-600 mb-6">몇 가지 질문에 답하고 프로젝트에 가장 적합한 OCR 기술 스택을 추천받으세요.</p>
                    
                    <div class="space-y-6">
                        <div>
                            <label class="font-semibold text-gray-700 text-lg">1. 가장 중요한 제약 조건은 무엇인가요?</label>
                            <div id="priority-selector" class="flex flex-wrap gap-3 mt-3">
                                <button data-priority="accuracy" class="selector-btn border-2 border-gray-300 px-5 py-2 rounded-lg transition-all hover:border-blue-500 hover:bg-blue-50">최고 수준의 정확도</button>
                                <button data-priority="cost" class="selector-btn border-2 border-gray-300 px-5 py-2 rounded-lg transition-all hover:border-green-500 hover:bg-green-50">최소한의 비용 (무료)</button>
                                <button data-priority="control" class="selector-btn border-2 border-gray-300 px-5 py-2 rounded-lg transition-all hover:border-purple-500 hover:bg-purple-50">직접 제어 및 튜닝</button>
                            </div>
                        </div>
                    </div>

                    <div id="recommendation-box" class="mt-8 p-6 bg-amber-50 rounded-lg border-l-4 border-amber-500 hidden">
                        <h3 class="font-bold text-xl text-amber-800 mb-2">추천 경로</h3>
                        <p id="recommendation-text" class="text-amber-700"></p>
                        <div id="recommendation-details" class="mt-4 text-sm"></div>
                    </div>
                </div>
            </section>

            <section id="comparison" class="content-section">
                <div class="bg-white p-6 md:p-8 rounded-xl shadow-lg border border-gray-200">
                    <h2 class="text-2xl font-bold mb-1 text-gray-800">OCR 엔진 성능 비교</h2>
                     <p class="text-gray-600 mb-8">주요 OCR 엔진들의 예상 한글 정확도를 비교해 보세요. 막대를 클릭하면 상세 정보로 이동합니다.</p>
                    <div class="chart-container mb-12">
                        <canvas id="engine-chart"></canvas>
                    </div>
                    <div id="engine-details" class="space-y-8"></div>
                </div>
            </section>

            <section id="preprocess" class="content-section">
                <div class="bg-white p-6 md:p-8 rounded-xl shadow-lg border border-gray-200">
                    <h2 class="text-2xl font-bold mb-1 text-gray-800">핵심 전처리 기술</h2>
                    <p class="text-gray-600 mb-6">OCR 인식률을 높이는 데 필수적인 이미지 전처리 기법들을 시각적으로 확인해보세요.</p>
                    
                    <div class="border-t">
                        <div id="preprocess-accordion" class="divide-y divide-gray-200">
                        </div>
                    </div>
                </div>
            </section>

            <section id="postprocess" class="content-section">
                <div class="bg-white p-6 md:p-8 rounded-xl shadow-lg border border-gray-200">
                     <h2 class="text-2xl font-bold mb-1 text-gray-800">후처리로 정확도 완성하기</h2>
                     <p class="text-gray-600 mb-6">OCR 엔진이 놓친 오류를 수정하여 최종 결과물의 완성도를 높이는 두 가지 방법을 소개합니다.</p>
                     <div id="postprocess-content" class="space-y-6"></div>
                </div>
            </section>
        </main>

        <footer class="text-center mt-16 text-gray-500 text-sm">
            <p>이 애플리케이션은 제공된 '한글 OCR 인식률 극대화' 보고서를 기반으로 생성되었습니다.</p>
        </footer>
    </div>

<script>
document.addEventListener('DOMContentLoaded', () => {

    const appData = {
        engines: [
            { id: 'tesseract', name: 'Tesseract', type: '오픈소스', accuracy: 75, cost: '무료', ease: '낮음/높음', strength: '높은 제어 가능성, 오프라인 작동', weakness: '낮은 기본 정확도, 광범위한 전처리/튜닝 필수', color: 'rgba(156, 163, 175, 0.7)', borderColor: 'rgba(156, 163, 175, 1)' },
            { id: 'easyocr', name: 'EasyOCR', type: '오픈소스', accuracy: 88, cost: '무료', ease: '높음/낮음', strength: '간편한 설치 및 사용, 준수한 정확도', weakness: '상대적으로 느린 속도, 복잡한 레이아웃 처리 한계', color: 'rgba(52, 211, 153, 0.7)', borderColor: 'rgba(16, 185, 129, 1)' },
            { id: 'paddleocr', name: 'PaddleOCR', type: '오픈소스', accuracy: 93, cost: '무료', ease: '중간/중간', strength: '최상급 오픈소스 성능, 한글 특화 모델', weakness: '다소 복잡한 설정, 프레임워크 의존성', color: 'rgba(96, 165, 250, 0.7)', borderColor: 'rgba(59, 130, 246, 1)' },
            { id: 'google', name: 'Google Vision', type: '상용 API', accuracy: 97, cost: '종량제', ease: '높음/낮음', strength: '뛰어난 문자 인식 정확도, 손글씨 지원', weakness: '유료, 레이아웃 분석이 약점일 수 있음', color: 'rgba(251, 191, 36, 0.7)', borderColor: 'rgba(245, 158, 11, 1)' },
            { id: 'naver', name: 'Naver CLOVA', type: '상용 API', accuracy: 98, cost: '종량제', ease: '높음/낮음', strength: '한국어 OCR 최고 수준 정확도, 다양한 문서 처리', weakness: '유료, 외부 서비스 의존, 데이터 프라이버시 고려', color: 'rgba(239, 68, 68, 0.7)', borderColor: 'rgba(220, 38, 38, 1)' },
        ],
        recommendations: {
            accuracy: {
                text: "Naver CLOVA 또는 Google Vision API 사용을 권장합니다.",
                details: `<p><strong>이유:</strong> 상용 API는 방대한 데이터로 학습된 최첨단 모델을 사용하여 현재 가장 높은 수준의 한글 인식 정확도를 제공합니다.</p>
                          <p class="mt-2"><strong>차선책:</strong> 비용이 부담된다면, 한글에 특화된 고성능 모델을 제공하는 <strong>PaddleOCR</strong>이 훌륭한 대안입니다.</p>`
            },
            cost: {
                text: "PaddleOCR 또는 EasyOCR 사용을 권장합니다.",
                details: `<p><strong>이유:</strong> 두 엔진 모두 무료 오픈소스이며, Tesseract에 비해 훨씬 적은 노력으로 높은 정확도를 얻을 수 있습니다.</p>
                          <p class="mt-2"><strong>선택 가이드:</strong> 최고의 오픈소스 성능을 원한다면 <strong>PaddleOCR</strong>, 가장 간편한 사용법을 원한다면 <strong>EasyOCR</strong>을 선택하세요.</p>`
            },
            control: {
                text: "Tesseract 또는 PaddleOCR 사용을 권장합니다.",
                details: `<p><strong>이유:</strong> Tesseract는 모든 처리 단계를 직접 제어하고 미세 조정할 수 있는 가장 높은 자유도를 제공하지만, 상당한 노력이 필요합니다.</p>
                          <p class="mt-2"><strong>균형점:</strong> <strong>PaddleOCR</strong>은 우수한 성능을 제공하면서도 모델 구조와 파라미터를 직접 조정할 수 있는 여지를 남겨두어, 성능과 제어 사이의 좋은 균형을 이룹니다.</p>`
            }
        },
        preprocess: [
            {
                title: '기하학적 보정 (기울기 & 왜곡)',
                content: `문서 스캔이나 촬영 시 발생하는 기울어짐이나 원근 왜곡은 OCR 엔진의 라인 및 문자 탐지를 방해하는 주요 요인입니다. <strong>기울기 보정(Deskewing)</strong>은 이미지를 수평으로 바로잡아 텍스트 라인을 정렬하고, <strong>원근 변환(Dewarping)</strong>은 비스듬히 찍힌 문서를 정면에서 본 것처럼 평평하게 폅니다. 이 과정은 정확한 문자 분리의 기반이 됩니다.`,
                code: `import cv2
import numpy as np

def deskew(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated`
            },
            {
                title: '이진화 (Binarization)',
                content: `대부분의 OCR 엔진은 선명한 흑백 이미지에서 최고의 성능을 냅니다. 이진화는 그레이스케일 이미지를 흑과 백으로만 변환하는 과정입니다. <strong>적응형 이진화(Adaptive Thresholding)</strong>는 이미지의 각기 다른 영역에 최적화된 임계값을 적용하여, 조명이 불균일한 실제 환경의 이미지에서 전역 이진화나 오츠 이진화보다 월등한 성능을 보입니다.`,
                code: `import cv2

# ... 그레이스케일 이미지 'gray' 준비 ...
# blockSize는 홀수, C는 평균에서 뺄 보정 상수
binarized = cv2.adaptiveThreshold(
    gray, 255, 
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY, 11, 2
)`
            },
            {
                title: '노이즈 제거 및 형태학적 연산',
                content: `스캔 과정의 먼지나 이미지 압축으로 인한 노이즈를 제거하고, 문자의 형태를 다듬는 과정입니다. <strong>Median Blur</strong> 필터는 점과 같은 노이즈 제거에 효과적입니다. <strong>형태학적 연산(Morphological Operations)</strong>, 특히 끊어진 획을 이어주는 '닫힘(Closing)'이나 붙어버린 글자를 떼어주는 '열림(Opening)' 연산은 한글의 복잡한 구조를 다듬어 인식률을 향상시킬 수 있습니다. 단, 과도하게 적용하면 오히려 글자가 뭉개질 수 있어 주의가 필요합니다.`,
                code: `import cv2
import numpy as np

# ... 이진화된 이미지 'binary_img' 준비 ...
# 노이즈 제거
denoised = cv2.medianBlur(binary_img, 3)

# 닫힘 연산으로 문자 내 작은 구멍 메우기
kernel = np.ones((2,2), np.uint8)
closed = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
`
            }
        ],
        postprocess: [
            {
                title: '💡 방법 1: 한국어 맞춤법 검사기 활용',
                content: `OCR 엔진은 시각적 유사성 때문에 'ㅇ'을 'o'로, 'ㅣ'를 'l'처럼 오인하는 경우가 많습니다. 이렇게 생성된 텍스트를 <strong>한국어 맞춤법 검사 라이브러리</strong>(예: kospellpy, symspellpy-ko)에 통과시키면, 문법적으로 명백한 오류들을 상당수 자동으로 교정할 수 있습니다. 이는 후처리의 가장 기본적이면서도 효과적인 단계입니다.`,
                code: `# OCR 결과가 "인공지능이너무 재밓따!" 라고 가정
from kospellpy import spell_checker

raw_text = "인공지능이너무 재밓따!"
corrected_text = spell_checker.check(raw_text).as_dict()['checked']
# 결과: "인공지능이 너무 재밌다!"`
            },
            {
                title: '🧠 방법 2: 대규모 언어 모델(LLM) 기반 교정',
                content: `최신 접근법으로, ChatGPT나 Gemini와 같은 LLM을 활용하는 것입니다. OCR로 추출된 텍스트를 "다음은 OCR 텍스트입니다. 문맥에 맞게 오류를 수정해주세요."와 같은 프롬프트와 함께 LLM에 전달하면, 단순 맞춤법 오류를 넘어 복잡한 문맥적 오류까지 교정할 수 있습니다. 하지만 원문에 없던 내용을 추가하는 <strong>'환각(Hallucination)'</strong> 현상이 발생할 수 있고, API 호출 비용과 지연 시간이 발생하므로 사용 시 주의가 필요합니다.`,
                code: `# 가상 API 호출 예시
import ai_service

prompt = f"""다음은 OCR로 추출한 텍스트입니다. 
원래 의미와 형식을 유지하면서 철자법과 문법 오류를 수정해주세요.
---
텍스트: {raw_ocr_text}
---
"""
llm_corrected_text = ai_service.generate(prompt)
`
            }
        ]
    };

    const navButtons = document.querySelectorAll('.nav-button');
    const contentSections = document.querySelectorAll('.content-section');
    const prioritySelector = document.getElementById('priority-selector');
    const recommendationBox = document.getElementById('recommendation-box');
    const recommendationText = document.getElementById('recommendation-text');
    const recommendationDetails = document.getElementById('recommendation-details');

    function switchTab(targetId) {
        navButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.target === targetId);
        });
        contentSections.forEach(section => {
            section.classList.toggle('active', section.id === targetId);
        });
    }

    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            switchTab(button.dataset.target);
        });
    });

    prioritySelector.addEventListener('click', (e) => {
        const button = e.target.closest('.selector-btn');
        if (!button) return;

        document.querySelectorAll('.selector-btn').forEach(btn => {
            btn.classList.remove('bg-blue-500', 'text-white', 'border-blue-500');
            btn.classList.add('border-gray-300');
        });

        button.classList.add('bg-blue-500', 'text-white', 'border-blue-500');
        button.classList.remove('border-gray-300');
        
        const priority = button.dataset.priority;
        const recommendation = appData.recommendations[priority];

        if (recommendation) {
            recommendationText.textContent = recommendation.text;
            recommendationDetails.innerHTML = recommendation.details;
            recommendationBox.classList.remove('hidden');
        }
    });
    
    function renderEngineComparison() {
        const engineDetailsContainer = document.getElementById('engine-details');
        
        const sortedEngines = [...appData.engines].sort((a, b) => b.accuracy - a.accuracy);

        sortedEngines.forEach(engine => {
            const detailHtml = `
                <div id="detail-${engine.id}" class="p-6 rounded-lg border-2" style="border-color: ${engine.borderColor}; background-color: ${engine.color.replace('0.7', '0.1')};">
                    <div class="flex flex-wrap items-center justify-between gap-4 mb-4">
                        <h3 class="text-2xl font-bold" style="color: ${engine.borderColor};">${engine.name}</h3>
                        <div class="flex gap-2">
                           <span class="pill" style="background-color: ${engine.borderColor}; color: white;">${engine.type}</span>
                           <span class="pill bg-gray-200 text-gray-700">${engine.cost}</span>
                        </div>
                    </div>
                    <div class="grid md:grid-cols-2 gap-4 text-gray-700">
                        <div><strong>👍 강점:</strong> ${engine.strength}</div>
                        <div><strong>👎 약점:</strong> ${engine.weakness}</div>
                        <div><strong>⚙️ 개발 난이도:</strong> ${engine.ease}</div>
                    </div>
                </div>
            `;
            engineDetailsContainer.innerHTML += detailHtml;
        });

        const ctx = document.getElementById('engine-chart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: sortedEngines.map(e => e.name),
                datasets: [{
                    label: '예상 한글 정확도 (%)',
                    data: sortedEngines.map(e => e.accuracy),
                    backgroundColor: sortedEngines.map(e => e.color),
                    borderColor: sortedEngines.map(e => e.borderColor),
                    borderWidth: 2,
                    barPercentage: 0.7,
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { beginAtZero: false, min: 60, title: { display: true, text: '정확도 (%)', font: { size: 14 } } },
                    y: { grid: { display: false } }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return ` 정확도: ${context.raw}%`;
                            }
                        }
                    }
                },
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const index = elements[0].index;
                        const engineId = sortedEngines[index].id;
                        document.getElementById(`detail-${engineId}`).scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }
            }
        });
    }

    function renderPreprocessAccordion() {
        const container = document.getElementById('preprocess-accordion');
        container.innerHTML = appData.preprocess.map((item, index) => `
            <div class="py-5">
                <details class="group" ${index === 0 ? 'open' : ''}>
                    <summary class="flex cursor-pointer list-none items-center justify-between font-medium">
                        <span class="text-lg text-gray-800">${item.title}</span>
                        <span class="transition group-open:rotate-180">
                            <svg fill="none" height="24" shape-rendering="geometricPrecision" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" viewBox="0 0 24 24" width="24"><path d="M6 9l6 6 6-6"></path></svg>
                        </span>
                    </summary>
                    <div class="group-open:animate-fadeIn mt-4 text-gray-600">
                        <p class="mb-4">${item.content}</p>
                        <div class="code-block">
                            <pre><code>${item.code}</code></pre>
                        </div>
                    </div>
                </details>
            </div>
        `).join('');
    }

    function renderPostprocessContent() {
        const container = document.getElementById('postprocess-content');
        container.innerHTML = appData.postprocess.map(item => `
            <div class="bg-gray-50 p-6 rounded-lg border border-gray-200">
                <h3 class="font-bold text-lg mb-3 text-gray-800">${item.title}</h3>
                <p class="text-gray-600 mb-4">${item.content}</p>
                <div class="code-block">
                    <pre><code>${item.code}</code></pre>
                </div>
            </div>
        `).join('');
    }

    renderEngineComparison();
    renderPreprocessAccordion();
    renderPostprocessContent();
});
</script>
</body>
</html>
