# 한글 OCR 최적화 가이드

프로젝트에 가장 적합한 OCR 전략을 찾아보세요.

-----

## 🚀 경로 선택기

몇 가지 질문에 답하고 프로젝트에 가장 적합한 OCR 기술 스택을 추천받으세요.

### 1\. 가장 중요한 제약 조건은 무엇인가요?

#### **최고 수준의 정확도를 원할 때**

> **추천 경로: Naver CLOVA 또는 Google Vision API 사용을 권장합니다.**
>
> **이유:** 상용 API는 방대한 데이터로 학습된 최첨단 모델을 사용하여 현재 가장 높은 수준의 한글 인식 정확도를 제공합니다.
>
> **차선책:** 비용이 부담된다면, 한글에 특화된 고성능 모델을 제공하는 **PaddleOCR**이 훌륭한 대안입니다.

#### **최소한의 비용(무료)을 원할 때**

> **추천 경로: PaddleOCR 또는 EasyOCR 사용을 권장합니다.**
>
> **이유:** 두 엔진 모두 무료 오픈소스이며, Tesseract에 비해 훨씬 적은 노력으로 높은 정확도를 얻을 수 있습니다.
>
> **선택 가이드:** 최고의 오픈소스 성능을 원한다면 **PaddleOCR**, 가장 간편한 사용법을 원한다면 **EasyOCR**을 선택하세요.

#### **직접 제어 및 튜닝을 원할 때**

> **추천 경로: Tesseract 또는 PaddleOCR 사용을 권장합니다.**
>
> **이유:** Tesseract는 모든 처리 단계를 직접 제어하고 미세 조정할 수 있는 가장 높은 자유도를 제공하지만, 상당한 노력이 필요합니다.
>
> **균형점:** **PaddleOCR**은 우수한 성능을 제공하면서도 모델 구조와 파라미터를 직접 조정할 수 있는 여지를 남겨두어, 성능과 제어 사이의 좋은 균형을 이룹니다.

-----

## 📊 엔진 비교

주요 OCR 엔진들의 예상 한글 정확도를 비교해 보세요.

### 엔진 성능 요약

| 엔진 | 예상 정확도 (%) | 타입 | 비용 |
| --- | --- | --- | --- |
| Naver CLOVA | 98 | 상용 API | 종량제 |
| Google Vision | 97 | 상용 API | 종량제 |
| PaddleOCR | 93 | 오픈소스 | 무료 |
| EasyOCR | 88 | 오픈소스 | 무료 |
| Tesseract | 75 | 오픈소스 | 무료 |

### 엔진별 상세 정보

#### **Naver CLOVA**

  - **타입:** 상용 API
  - **비용:** 종량제
  - **예상 정확도:** 98%
  - **👍 강점:** 한국어 OCR 최고 수준 정확도, 다양한 문서 처리
  - **👎 약점:** 유료, 외부 서비스 의존, 데이터 프라이버시 고려
  - **⚙️ 개발 난이도:** 높음/낮음

#### **Google Vision**

  - **타입:** 상용 API
  - **비용:** 종량제
  - **예상 정확도:** 97%
  - **👍 강점:** 뛰어난 문자 인식 정확도, 손글씨 지원
  - **👎 약점:** 유료, 레이아웃 분석이 약점일 수 있음
  - **⚙️ 개발 난이도:** 높음/낮음

#### **PaddleOCR**

  - **타입:** 오픈소스
  - **비용:** 무료
  - **예상 정확도:** 93%
  - **👍 강점:** 최상급 오픈소스 성능, 한글 특화 모델
  - **👎 약점:** 다소 복잡한 설정, 프레임워크 의존성
  - **⚙️ 개발 난이도:** 중간/중간

#### **EasyOCR**

  - **타입:** 오픈소스
  - **비용:** 무료
  - **예상 정확도:** 88%
  - **👍 강점:** 간편한 설치 및 사용, 준수한 정확도
  - **👎 약점:** 상대적으로 느린 속도, 복잡한 레이아웃 처리 한계
  - **⚙️ 개발 난이도:** 높음/낮음

#### **Tesseract**

  - **타입:** 오픈소스
  - **비용:** 무료
  - **예상 정확도:** 75%
  - **👍 강점:** 높은 제어 가능성, 오프라인 작동
  - **👎 약점:** 낮은 기본 정확도, 광범위한 전처리/튜닝 필수
  - **⚙️ 개발 난이도:** 낮음/높음

-----

## ✨ 핵심 전처리 기술

OCR 인식률을 높이는 데 필수적인 이미지 전처리 기법들을 시각적으로 확인해보세요.

### **기하학적 보정 (기울기 & 왜곡)**

문서 스캔이나 촬영 시 발생하는 기울어짐이나 원근 왜곡은 OCR 엔진의 라인 및 문자 탐지를 방해하는 주요 요인입니다. \*\*기울기 보정(Deskewing)\*\*은 이미지를 수평으로 바로잡아 텍스트 라인을 정렬하고, \*\*원근 변환(Dewarping)\*\*은 비스듬히 찍힌 문서를 정면에서 본 것처럼 평평하게 폅니다. 이 과정은 정확한 문자 분리의 기반이 됩니다.

```python
import cv2
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
    return rotated
```

### **이진화 (Binarization)**

대부분의 OCR 엔진은 선명한 흑백 이미지에서 최고의 성능을 냅니다. 이진화는 그레이스케일 이미지를 흑과 백으로만 변환하는 과정입니다. \*\*적응형 이진화(Adaptive Thresholding)\*\*는 이미지의 각기 다른 영역에 최적화된 임계값을 적용하여, 조명이 불균일한 실제 환경의 이미지에서 전역 이진화나 오츠 이진화보다 월등한 성능을 보입니다.

```python
import cv2

# ... 그레이스케일 이미지 'gray' 준비 ...
# blockSize는 홀수, C는 평균에서 뺄 보정 상수
binarized = cv2.adaptiveThreshold(
    gray, 255, 
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY, 11, 2
)
```

### **노이즈 제거 및 형태학적 연산**

스캔 과정의 먼지나 이미지 압축으로 인한 노이즈를 제거하고, 문자의 형태를 다듬는 과정입니다. **Median Blur** 필터는 점과 같은 노이즈 제거에 효과적입니다. **형태학적 연산(Morphological Operations)**, 특히 끊어진 획을 이어주는 '닫힘(Closing)'이나 붙어버린 글자를 떼어주는 '열림(Opening)' 연산은 한글의 복잡한 구조를 다듬어 인식률을 향상시킬 수 있습니다. 단, 과도하게 적용하면 오히려 글자가 뭉개질 수 있어 주의가 필요합니다.

```python
import cv2
import numpy as np

# ... 이진화된 이미지 'binary_img' 준비 ...
# 노이즈 제거
denoised = cv2.medianBlur(binary_img, 3)

# 닫힘 연산으로 문자 내 작은 구멍 메우기
kernel = np.ones((2,2), np.uint8)
closed = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
```

-----

## 🔧 후처리로 정확도 완성하기

OCR 엔진이 놓친 오류를 수정하여 최종 결과물의 완성도를 높이는 두 가지 방법을 소개합니다.

### **💡 방법 1: 한국어 맞춤법 검사기 활용**

OCR 엔진은 시각적 유사성 때문에 'ㅇ'을 'o'로, 'ㅣ'를 'l'처럼 오인하는 경우가 많습니다. 이렇게 생성된 텍스트를 **한국어 맞춤법 검사 라이브러리**(예: kospellpy, symspellpy-ko)에 통과시키면, 문법적으로 명백한 오류들을 상당수 자동으로 교정할 수 있습니다. 이는 후처리의 가장 기본적이면서도 효과적인 단계입니다.

```python
# OCR 결과가 "인공지능이너무 재밓따!" 라고 가정
from kospellpy import spell_checker

raw_text = "인공지능이너무 재밓따!"
corrected_text = spell_checker.check(raw_text).as_dict()['checked']
# 결과: "인공지능이 너무 재밌다!"
```

### **🧠 방법 2: 대규모 언어 모델(LLM) 기반 교정**

최신 접근법으로, ChatGPT나 Gemini와 같은 LLM을 활용하는 것입니다. OCR로 추출된 텍스트를 "다음은 OCR 텍스트입니다. 문맥에 맞게 오류를 수정해주세요."와 같은 프롬프트와 함께 LLM에 전달하면, 단순 맞춤법 오류를 넘어 복잡한 문맥적 오류까지 교정할 수 있습니다. 하지만 원문에 없던 내용을 추가하는 **'환각(Hallucination)'** 현상이 발생할 수 있고, API 호출 비용과 지연 시간이 발생하므로 사용 시 주의가 필요합니다.

```python
# 가상 API 호출 예시
import ai_service

prompt = f"""다음은 OCR로 추출한 텍스트입니다. 
원래 의미와 형식을 유지하면서 철자법과 문법 오류를 수정해주세요.
---
텍스트: {raw_ocr_text}
---
"""
llm_corrected_text = ai_service.generate(prompt)
```

-----

\<p align="center"\>이 애플리케이션은 제공된 '한글 OCR 인식률 극대화' 보고서를 기반으로 생성되었습니다.\</p\>
