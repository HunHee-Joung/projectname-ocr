# 간단하고 안정적인 PaddleOCR 프로그램
import os
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# PaddleOCR import
try:
    from paddleocr import PaddleOCR
    print("PaddleOCR 모듈 로드 성공")
except ImportError as e:
    print(f"PaddleOCR 모듈 로드 실패: {e}")
    exit(1)

class SimpleOCR:
    def __init__(self, lang='en'):
        """
        간단한 OCR 클래스
        
        Args:
            lang (str): 언어 설정 ('en', 'korean', 'ch' 등)
        """
        print(f"OCR 초기화 중... 언어: {lang}")
        try:
            # 최소한의 설정으로 시작
            self.ocr = PaddleOCR(lang=lang)
            print("OCR 초기화 완료")
        except Exception as e:
            print(f"OCR 초기화 실패: {e}")
            # 언어 설정 없이 재시도
            try:
                self.ocr = PaddleOCR()
                print("OCR 초기화 완료 (기본 설정)")
            except Exception as e2:
                print(f"기본 설정으로도 초기화 실패: {e2}")
                raise e2
    
    def extract_text(self, image_path):
        """
        이미지에서 텍스트 추출
        
        Args:
            image_path (str): 이미지 파일 경로
            
        Returns:
            tuple: (텍스트 리스트, 원시 결과)
        """
        print(f"이미지 분석 중: {image_path}")
        
        try:
            # OCR 실행
            result = self.ocr.ocr(image_path)
            
            print(f"OCR 결과 타입: {type(result)}")
            print(f"OCR 결과 길이: {len(result) if result else 0}")
            
            if not result:
                print("OCR 결과가 없습니다.")
                return [], result
            
            # 결과 처리 - 딕셔너리 형태 결과 처리
            texts = []
            
            # result[0]이 딕셔너리인 경우 (최신 PaddleOCR 형태)
            if len(result) > 0 and isinstance(result[0], dict):
                page_result = result[0]
                print(f"딕셔너리 형태 결과 감지")
                print(f"딕셔너리 키들: {list(page_result.keys())}")
                
                if 'rec_texts' in page_result and 'rec_scores' in page_result:
                    rec_texts = page_result['rec_texts']
                    rec_scores = page_result['rec_scores']
                    rec_boxes = page_result.get('rec_boxes', [])
                    
                    print(f"감지된 텍스트 개수: {len(rec_texts)}")
                    print(f"신뢰도 개수: {len(rec_scores)}")
                    print(f"박스 개수: {len(rec_boxes)}")
                    
                    for i in range(len(rec_texts)):
                        text = rec_texts[i] if i < len(rec_texts) else ""
                        confidence = rec_scores[i] if i < len(rec_scores) else 0.0
                        
                        # rec_boxes에서 좌표 추출
                        if i < len(rec_boxes):
                            # rec_boxes는 [x1, y1, x2, y2] 형태일 수 있음
                            box = rec_boxes[i]
                            if len(box) == 4:  # [x1, y1, x2, y2]
                                x1, y1, x2, y2 = box
                                bbox = [[int(x1), int(y1)], [int(x2), int(y1)], [int(x2), int(y2)], [int(x1), int(y2)]]
                            else:
                                # NumPy 배열을 Python 리스트로 변환
                                bbox = [[int(p[0]), int(p[1])] for p in box] if hasattr(box, '__iter__') else []
                        else:
                            bbox = []
                        
                        if text and str(text).strip():
                            texts.append({
                                'text': str(text),
                                'confidence': float(confidence),
                                'bbox': bbox
                            })
                            print(f"텍스트 {i+1}: '{text}' (신뢰도: {confidence:.3f})")
                
            # 기존 리스트 형태 결과 처리 (이전 버전 호환성)
            elif len(result) > 0 and isinstance(result[0], list):
                page_result = result[0]
                print(f"리스트 형태 결과 감지")
                print(f"감지된 텍스트 블록 개수: {len(page_result) if page_result else 0}")
                
                if page_result:
                    for i, line in enumerate(page_result):
                        try:
                            if line and len(line) >= 2:
                                bbox = line[0]  # 좌표
                                text_info = line[1]  # 텍스트 정보
                                
                                # text_info의 형식 확인
                                if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                                    # 표준 형식: (text, confidence)
                                    text = text_info[0]
                                    confidence = text_info[1]
                                elif isinstance(text_info, str):
                                    # 텍스트만 있는 경우
                                    text = text_info
                                    confidence = 1.0
                                else:
                                    print(f"예상하지 못한 text_info 형식: {text_info}")
                                    continue
                                
                                if text and str(text).strip():
                                    # NumPy 배열을 JSON 호환 형태로 변환
                                    json_bbox = []
                                    if bbox and hasattr(bbox, '__iter__'):
                                        try:
                                            if hasattr(bbox, 'tolist'):
                                                json_bbox = bbox.tolist()
                                            else:
                                                json_bbox = [[int(p[0]), int(p[1])] for p in bbox]
                                        except:
                                            json_bbox = []
                                    
                                    texts.append({
                                        'text': str(text),
                                        'confidence': float(confidence),
                                        'bbox': json_bbox
                                    })
                                    print(f"텍스트 {i+1}: '{text}' (신뢰도: {confidence:.3f})")
                                    
                        except Exception as line_error:
                            print(f"라인 {i+1} 처리 중 오류: {line_error}")
                            continue
            
            else:
                print(f"예상하지 못한 결과 형태: {type(result[0]) if len(result) > 0 else 'empty'}")
            
            print(f"총 {len(texts)}개의 텍스트 블록 발견")
            return texts, result
            
        except Exception as e:
            print(f"OCR 처리 중 오류: {e}")
            import traceback
            traceback.print_exc()
            return [], None
    
    def get_plain_text(self, image_path):
        """
        이미지에서 평문 텍스트만 추출
        
        Args:
            image_path (str): 이미지 파일 경로
            
        Returns:
            str: 추출된 텍스트
        """
        texts, _ = self.extract_text(image_path)
        
        if not texts:
            return ""
        
        # 텍스트만 추출하여 줄바꿈으로 연결
        plain_texts = [item['text'] for item in texts]
        return '\n'.join(plain_texts)
    
    def save_results(self, image_path, output_prefix="ocr_result"):
        """
        OCR 결과를 다양한 형태로 저장
        
        Args:
            image_path (str): 이미지 파일 경로
            output_prefix (str): 출력 파일 접두사
        """
        texts, raw_result = self.extract_text(image_path)
        
        if not texts:
            print("저장할 텍스트가 없습니다.")
            return
        
        # 1. 텍스트 파일로 저장
        txt_path = f"{output_prefix}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            for item in texts:
                f.write(f"{item['text']}\n")
        print(f"텍스트 파일 저장: {txt_path}")
        
        # 2. JSON 파일로 저장 (상세 정보 포함)
        json_path = f"{output_prefix}.json"
        json_data = {
            'image_path': image_path,
            'total_blocks': len(texts),
            'results': texts
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"JSON 파일 저장: {json_path}")
        
        # 3. 시각화 이미지 저장
        self.visualize_results(image_path, texts, f"{output_prefix}_visual.jpg")
    
    def visualize_results(self, image_path, texts, output_path):
        """
        OCR 결과를 시각화하여 이미지로 저장
        
        Args:
            image_path (str): 원본 이미지 경로
            texts (list): 추출된 텍스트 리스트
            output_path (str): 출력 이미지 경로
        """
        try:
            # 원본 이미지 로드
            image = Image.open(image_path).convert('RGB')
            draw = ImageDraw.Draw(image)
            
            # 기본 폰트 사용
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            # 각 텍스트 블록에 대해 박스와 텍스트 그리기
            for i, item in enumerate(texts):
                bbox = item['bbox']
                text = item['text']
                confidence = item['confidence']
                
                if len(bbox) >= 4:
                    # 박스 좌표 추출 (4개 점의 좌표)
                    points = [(int(p[0]), int(p[1])) for p in bbox]
                    
                    # 박스 그리기
                    draw.polygon(points, outline='red', width=2)
                    
                    # 텍스트 표시
                    text_to_show = f"{text} ({confidence:.2f})"
                    text_x = int(bbox[0][0])
                    text_y = int(bbox[0][1]) - 20
                    
                    # 배경 박스
                    if font:
                        try:
                            bbox_text = draw.textbbox((text_x, text_y), text_to_show, font=font)
                            draw.rectangle(bbox_text, fill='yellow', outline='red')
                            draw.text((text_x, text_y), text_to_show, fill='black', font=font)
                        except:
                            draw.text((text_x, text_y), text_to_show, fill='red')
                    else:
                        draw.text((text_x, text_y), text_to_show, fill='red')
            
            # 이미지 저장
            image.save(output_path)
            print(f"시각화 이미지 저장: {output_path}")
            
        except Exception as e:
            print(f"시각화 중 오류: {e}")

def find_image_files(directory="."):
    """현재 디렉토리에서 이미지 파일 찾기"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    image_files = []
    
    for file in os.listdir(directory):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            image_files.append(file)
    
    return image_files

def main():
    print("=== 간단한 PaddleOCR 텍스트 추출 프로그램 ===\n")
    
    # 이미지 파일 찾기
    image_files = find_image_files()
    
    if not image_files:
        print("현재 디렉토리에 이미지 파일이 없습니다.")
        print("지원 형식: jpg, jpeg, png, bmp, tiff, webp")
        return
    
    print(f"발견된 이미지 파일: {image_files}")
    image_path = image_files[0]
    print(f"첫 번째 이미지 사용: {image_path}\n")
    
    # 언어별로 시도
    languages_to_try = ['korean', 'ch', 'en']
    
    ocr = None
    for lang in languages_to_try:
        try:
            print(f"언어 '{lang}'로 OCR 초기화 시도...")
            ocr = SimpleOCR(lang=lang)
            
            # 바로 테스트해보기
            test_texts, _ = ocr.extract_text(image_path)
            if test_texts:
                print(f"언어 '{lang}'로 텍스트 감지 성공!")
                break
            else:
                print(f"언어 '{lang}'로는 텍스트가 감지되지 않음")
                
        except Exception as e:
            print(f"언어 '{lang}' 초기화 실패: {e}")
            continue
    
    if not ocr:
        print("모든 언어 설정으로 OCR 초기화에 실패했습니다.")
        return
    
    # 1. 간단한 텍스트 추출
    print("\n1. 평문 텍스트 추출:")
    plain_text = ocr.get_plain_text(image_path)
    if plain_text:
        print(plain_text)
    else:
        print("추출된 텍스트가 없습니다.")
    
    print("\n" + "="*50 + "\n")
    
    # 2. 상세 결과
    print("2. 상세 결과:")
    texts, _ = ocr.extract_text(image_path)
    
    if texts:
        for i, item in enumerate(texts, 1):
            print(f"{i}. 텍스트: '{item['text']}'")
            print(f"   신뢰도: {item['confidence']:.4f}")
            print(f"   위치: {item['bbox']}")
            print()
    else:
        print("상세 결과가 없습니다.")
        
        # 디버깅을 위해 다른 설정도 시도
        print("\n다른 설정으로 재시도...")
        try_different_settings(image_path)
    
    # 3. 결과 저장
    if texts:
        print("3. 결과 저장 중...")
        ocr.save_results(image_path, "ocr_output")
        print("저장 완료!")
    else:
        print("3. 저장할 결과가 없습니다.")

def try_different_settings(image_path):
    """다양한 설정으로 OCR 시도"""
    print("다양한 설정으로 OCR 재시도 중...")
    
    settings_to_try = [
        {'lang': 'korean'},
        {'lang': 'ch'},
        {'lang': 'en'},
        {}  # 기본 설정
    ]
    
    for i, settings in enumerate(settings_to_try):
        try:
            print(f"\n설정 {i+1}: {settings}")
            
            ocr = PaddleOCR(**settings)
            
            # OCR 실행
            result = ocr.ocr(image_path)
            
            print(f"결과: {result}")
            
            if result and len(result) > 0 and result[0]:
                print(f"텍스트 감지됨! 결과 개수: {len(result[0])}")
                if result[0]:
                    first_result = result[0][0]
                    print(f"첫 번째 결과: {first_result}")
                return result
            
        except Exception as e:
            print(f"설정 {i+1} 실패: {e}")
            continue
    
    print("모든 설정으로 시도했지만 텍스트를 감지하지 못했습니다.")
    return None

def batch_process(input_folder, output_folder):
    """
    폴더 내 모든 이미지 일괄 처리
    
    Args:
        input_folder (str): 입력 폴더
        output_folder (str): 출력 폴더
    """
    print(f"배치 처리 시작: {input_folder} -> {output_folder}")
    
    # 출력 폴더 생성
    os.makedirs(output_folder, exist_ok=True)
    
    # OCR 초기화
    ocr = SimpleOCR(lang='en')
    
    # 이미지 파일 찾기
    image_files = find_image_files(input_folder)
    
    if not image_files:
        print("처리할 이미지가 없습니다.")
        return
    
    for filename in image_files:
        print(f"\n처리 중: {filename}")
        image_path = os.path.join(input_folder, filename)
        
        # 텍스트 추출
        plain_text = ocr.get_plain_text(image_path)
        
        if plain_text:
            # 텍스트 파일로 저장
            base_name = os.path.splitext(filename)[0]
            output_file = os.path.join(output_folder, f"{base_name}.txt")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(plain_text)
            
            print(f"저장됨: {output_file}")
        else:
            print("텍스트가 감지되지 않았습니다.")

if __name__ == "__main__":
    # 기본 실행
    main()
    
    # 배치 처리 예제 (주석 해제하여 사용)
    # batch_process("input_images", "output_texts")
