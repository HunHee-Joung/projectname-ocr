# GPU 가속 PaddleOCR 프로그램
import os
import json
import time
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# PaddleOCR import
try:
    from paddleocr import PaddleOCR
    print("PaddleOCR 모듈 로드 성공")
except ImportError as e:
    print(f"PaddleOCR 모듈 로드 실패: {e}")
    exit(1)

def check_gpu_availability():
    """GPU 사용 가능 여부 확인"""
    try:
        import paddle
        if paddle.is_compiled_with_cuda():
            device_count = paddle.device.cuda.device_count()
            print(f"CUDA 지원: 사용 가능한 GPU 개수 = {device_count}")
            return device_count > 0
        else:
            print("CUDA 지원: 사용 불가 (CPU only 빌드)")
            return False
    except ImportError:
        print("Paddle 모듈을 찾을 수 없습니다.")
        return False
    except Exception as e:
        print(f"GPU 확인 중 오류: {e}")
        return False

class GPUAcceleratedOCR:
    def __init__(self, lang='en', use_gpu=True):
        """
        GPU 가속 OCR 클래스
        
        Args:
            lang (str): 언어 설정 ('en', 'korean', 'ch' 등)
            use_gpu (bool): GPU 사용 여부
        """
        self.use_gpu = use_gpu and check_gpu_availability()
        
        print(f"OCR 초기화 중... 언어: {lang}, GPU 사용: {self.use_gpu}")
        
        try:
            if self.use_gpu:
                # GPU 설정
                self.ocr = PaddleOCR(
                    lang=lang,
                    use_gpu=True,
                    gpu_mem=2000,  # GPU 메모리 할당 (MB)
                    cpu_threads=8,  # CPU 스레드 수
                    enable_mkldnn=True,  # Intel MKL-DNN 최적화 활성화
                    det_model_dir=None,  # 사전 훈련된 모델 경로 (기본값 사용)
                    rec_model_dir=None,
                    cls_model_dir=None
                )
                print("GPU 가속 OCR 초기화 완료")
            else:
                # CPU 최적화 설정
                self.ocr = PaddleOCR(
                    lang=lang,
                    use_gpu=False,
                    cpu_threads=8,
                    enable_mkldnn=True
                )
                print("CPU 최적화 OCR 초기화 완료")
                
        except Exception as e:
            print(f"OCR 초기화 실패: {e}")
            # 기본 설정으로 폴백
            try:
                self.ocr = PaddleOCR(lang=lang)
                self.use_gpu = False
                print("기본 설정으로 OCR 초기화 완료")
            except Exception as e2:
                print(f"기본 설정으로도 초기화 실패: {e2}")
                raise e2
    
    def extract_text_with_timing(self, image_path):
        """
        이미지에서 텍스트 추출 (처리 시간 측정 포함)
        
        Args:
            image_path (str): 이미지 파일 경로
            
        Returns:
            tuple: (텍스트 리스트, 원시 결과, 처리 시간)
        """
        print(f"이미지 분석 중: {image_path} ({'GPU' if self.use_gpu else 'CPU'} 모드)")
        
        start_time = time.time()
        
        try:
            # OCR 실행 - 최신 API 사용
            try:
                result = self.ocr.predict(image_path)
                print("predict() 메서드 사용")
            except AttributeError:
                # 구 버전 호환성
                result = self.ocr.ocr(image_path)
                print("ocr() 메서드 사용 (호환성 모드)")
            
            processing_time = time.time() - start_time
            print(f"OCR 처리 시간: {processing_time:.2f}초")
            
            if not result:
                print("OCR 결과가 없습니다.")
                return [], result, processing_time
            
            print(f"결과 타입: {type(result)}")
            print(f"결과 길이: {len(result) if hasattr(result, '__len__') else 'N/A'}")
            
            # 결과 처리 - 다양한 형식에 대응
            texts = []
            
            # predict() 결과가 다른 형식일 수 있으므로 먼저 확인
            if hasattr(result, 'rec_texts') and hasattr(result, 'rec_scores'):
                # 새로운 predict() 결과 형식 - 직접 속성 접근
                print("predict() 결과 형식 감지 - 직접 속성 접근")
                rec_texts = result.rec_texts
                rec_scores = result.rec_scores
                rec_boxes = getattr(result, 'rec_boxes', [])
                
                print(f"감지된 텍스트 개수: {len(rec_texts)} ({'GPU' if self.use_gpu else 'CPU'} 처리)")
                
                for i in range(len(rec_texts)):
                    text = rec_texts[i] if i < len(rec_texts) else ""
                    confidence = rec_scores[i] if i < len(rec_scores) else 0.0
                    
                    # rec_boxes에서 좌표 추출
                    if i < len(rec_boxes):
                        box = rec_boxes[i]
                        if hasattr(box, '__len__') and len(box) == 4:  # [x1, y1, x2, y2]
                            x1, y1, x2, y2 = box
                            bbox = [[int(x1), int(y1)], [int(x2), int(y1)], [int(x2), int(y2)], [int(x1), int(y2)]]
                        else:
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
            
            # 딕셔너리 형태 결과 처리 (기존 ocr() 방식)
            elif len(result) > 0 and isinstance(result[0], dict):
                page_result = result[0]
                print(f"딕셔너리 형태 결과 감지")
                
                if 'rec_texts' in page_result and 'rec_scores' in page_result:
                    rec_texts = page_result['rec_texts']
                    rec_scores = page_result['rec_scores']
                    rec_boxes = page_result.get('rec_boxes', [])
                    
                    print(f"감지된 텍스트 개수: {len(rec_texts)} ({'GPU' if self.use_gpu else 'CPU'} 처리)")
                    
                    for i in range(len(rec_texts)):
                        text = rec_texts[i] if i < len(rec_texts) else ""
                        confidence = rec_scores[i] if i < len(rec_scores) else 0.0
                        
                        # rec_boxes에서 좌표 추출
                        if i < len(rec_boxes):
                            box = rec_boxes[i]
                            if len(box) == 4:  # [x1, y1, x2, y2]
                                x1, y1, x2, y2 = box
                                bbox = [[int(x1), int(y1)], [int(x2), int(y1)], [int(x2), int(y2)], [int(x1), int(y2)]]
                            else:
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
                
            # 리스트 형태 결과 처리 (이전 버전 호환성)
            elif len(result) > 0 and isinstance(result[0], list):
                page_result = result[0]
                print(f"리스트 형태 결과 감지")
                
                if page_result:
                    for i, line in enumerate(page_result):
                        try:
                            if line and len(line) >= 2:
                                bbox = line[0]
                                text_info = line[1]
                                
                                if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                                    text = text_info[0]
                                    confidence = text_info[1]
                                elif isinstance(text_info, str):
                                    text = text_info
                                    confidence = 1.0
                                else:
                                    continue
                                
                                if text and str(text).strip():
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
            
            print(f"총 {len(texts)}개의 텍스트 블록 발견 (처리 시간: {processing_time:.2f}초)")
            return texts, result, processing_time
            
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"OCR 처리 중 오류: {e} (처리 시간: {processing_time:.2f}초)")
            import traceback
            traceback.print_exc()
            return [], None, processing_time
    
    def extract_text(self, image_path):
        """기존 호환성을 위한 메서드"""
        texts, result, _ = self.extract_text_with_timing(image_path)
        return texts, result
    
    def get_plain_text(self, image_path):
        """평문 텍스트만 추출"""
        texts, _, _ = self.extract_text_with_timing(image_path)
        
        if not texts:
            return ""
        
        plain_texts = [item['text'] for item in texts]
        return '\n'.join(plain_texts)
    
    def benchmark_performance(self, image_path, iterations=3):
        """
        GPU vs CPU 성능 비교
        
        Args:
            image_path (str): 테스트할 이미지 경로
            iterations (int): 반복 횟수
        """
        print(f"\n=== 성능 벤치마크 ({iterations}회 반복) ===")
        
        # 현재 설정으로 테스트
        current_mode = "GPU" if self.use_gpu else "CPU"
        times = []
        
        for i in range(iterations):
            print(f"\n{current_mode} 테스트 {i+1}/{iterations}")
            _, _, processing_time = self.extract_text_with_timing(image_path)
            times.append(processing_time)
        
        avg_time = sum(times) / len(times)
        print(f"\n{current_mode} 평균 처리 시간: {avg_time:.2f}초")
        print(f"{current_mode} 최소/최대 시간: {min(times):.2f}초 / {max(times):.2f}초")
        
        return avg_time
    
    def save_results_with_metadata(self, image_path, output_prefix="ocr_result"):
        """OCR 결과를 메타데이터와 함께 저장"""
        texts, raw_result, processing_time = self.extract_text_with_timing(image_path)
        
        if not texts:
            print("저장할 텍스트가 없습니다.")
            return
        
        # 텍스트 파일 저장
        txt_path = f"{output_prefix}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"# OCR 결과 - {'GPU' if self.use_gpu else 'CPU'} 처리\n")
            f.write(f"# 처리 시간: {processing_time:.2f}초\n")
            f.write(f"# 감지된 텍스트 블록: {len(texts)}개\n\n")
            for item in texts:
                f.write(f"{item['text']}\n")
        print(f"텍스트 파일 저장: {txt_path}")
        
        # JSON 파일 저장 (메타데이터 포함)
        json_path = f"{output_prefix}.json"
        json_data = {
            'image_path': image_path,
            'processing_mode': 'GPU' if self.use_gpu else 'CPU',
            'processing_time_seconds': processing_time,
            'total_blocks': len(texts),
            'results': texts,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"JSON 파일 저장: {json_path}")

def compare_gpu_cpu_performance(image_path):
    """GPU와 CPU 성능 직접 비교"""
    print("\n=== GPU vs CPU 성능 비교 ===")
    
    # GPU 사용 가능 여부 확인
    gpu_available = check_gpu_availability()
    
    if not gpu_available:
        print("GPU를 사용할 수 없습니다. CPU 모드만 테스트합니다.")
        cpu_ocr = GPUAcceleratedOCR(use_gpu=False)
        cpu_time = cpu_ocr.benchmark_performance(image_path)
        return
    
    # CPU 테스트
    print("\n--- CPU 테스트 ---")
    cpu_ocr = GPUAcceleratedOCR(use_gpu=False)
    cpu_time = cpu_ocr.benchmark_performance(image_path)
    
    # GPU 테스트
    print("\n--- GPU 테스트 ---")
    gpu_ocr = GPUAcceleratedOCR(use_gpu=True)
    gpu_time = gpu_ocr.benchmark_performance(image_path)
    
    # 비교 결과
    speedup = cpu_time / gpu_time if gpu_time > 0 else 0
    print(f"\n=== 성능 비교 결과 ===")
    print(f"CPU 평균 시간: {cpu_time:.2f}초")
    print(f"GPU 평균 시간: {gpu_time:.2f}초")
    print(f"GPU 가속비: {speedup:.2f}x {'빠름' if speedup > 1 else '느림'}")

def find_image_files(directory="."):
    """현재 디렉토리에서 이미지 파일 찾기"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    image_files = []
    
    for file in os.listdir(directory):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            image_files.append(file)
    
    return image_files

def main():
    print("=== GPU 가속 PaddleOCR 텍스트 추출 프로그램 ===\n")
    
    # GPU 사용 가능 여부 확인
    gpu_available = check_gpu_availability()
    
    # 이미지 파일 찾기
    image_files = find_image_files()
    
    if not image_files:
        print("현재 디렉토리에 이미지 파일이 없습니다.")
        return
    
    image_path = image_files[0]
    print(f"테스트 이미지: {image_path}")
    
    # 사용자 선택
    if gpu_available:
        choice = input("\n처리 모드를 선택하세요 (1: GPU, 2: CPU, 3: 성능 비교): ").strip()
        
        if choice == "3":
            compare_gpu_cpu_performance(image_path)
            return
        elif choice == "1":
            use_gpu = True
        else:
            use_gpu = False
    else:
        print("GPU를 사용할 수 없으므로 CPU 모드로 실행합니다.")
        use_gpu = False
    
    # OCR 실행
    print(f"\n{'GPU' if use_gpu else 'CPU'} 모드로 OCR 실행 중...")
    
    ocr = GPUAcceleratedOCR(lang='korean', use_gpu=use_gpu)
    
    # 텍스트 추출 및 결과 출력
    texts, _, processing_time = ocr.extract_text_with_timing(image_path)
    
    if texts:
        print(f"\n추출된 텍스트 ({len(texts)}개 블록, {processing_time:.2f}초 소요):")
        for i, item in enumerate(texts, 1):
            print(f"{i}. {item['text']} (신뢰도: {item['confidence']:.3f})")
        
        # 결과 저장
        output_prefix = f"ocr_output_{'gpu' if use_gpu else 'cpu'}"
        ocr.save_results_with_metadata(image_path, output_prefix)
    else:
        print("텍스트를 찾을 수 없습니다.")

if __name__ == "__main__":
    main()
