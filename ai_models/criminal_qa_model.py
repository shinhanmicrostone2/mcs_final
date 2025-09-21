"""
===============================================================================
주의: 이 파일은 형사법 AI 모델(LLM + LoRA)의 핵심 로직을 담고 있습니다.
팀 작업 시 절대 수정하지 마세요. (AI 팀/모델 담당자만 변경)

사용 가이드
- 공개 API: CriminalQAModel.generate_answer(question: str) -> str
- 모델은 서버 시작 시 또는 최초 호출 시 로드됩니다.
- 디바이스 선택: GPU 가능 시 4비트 양자화 + device_map="auto", 실패/미지원 시 CPU 폴백
- 어댑터 경로: 기본값은 이 폴더의 "criminal-qa-best" (로컬 배포용)

환경변수
- (선택) CUDA 관련 설정은 시스템/드라이버에 따릅니다.

문의: 모델/AI 관련 변경은 담당자에게 요청하세요.
===============================================================================
"""

import torch
import logging
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from typing import Optional

# 메모리 효율성을 위한 설정
torch.set_grad_enabled(False)  # 그래디언트 계산 비활성화

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# [수정 금지] 형사법 LLM 핵심 클래스 — 인터페이스/로직 변경 금지 (AI 담당자 승인 필요)
class CriminalQAModel:
    """형사법 QA 모델 클래스"""
    
    # [수정 금지] 초기화: 경로/디바이스/양자화 기본 설정 (배포 호환성 영향)
    def __init__(self, base_model_path: str = "beomi/Llama-3-Open-Ko-8B-Instruct-preview",
                 adapter_path: str = None):
        """
        형사법 QA 모델 초기화
        
        Args:
            base_model_path: 베이스 모델 경로
            adapter_path: LoRA 어댑터 경로
        """
        self.base_model_path = base_model_path
        
        # 어댑터 경로 자동 설정
        if adapter_path is None:
            import os
            # 현재 파일의 위치를 기준으로 상대 경로 계산
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # ai_models 폴더 내부의 어댑터 폴더를 기본값으로 사용
            adapter_path = os.path.join(current_dir, "criminal-qa-best")
        
        self.adapter_path = adapter_path
        self.model = None
        self.tokenizer = None
        # 모델이 실제로 CUDA에서 동작 중인지 여부 (입력 텐서 이동 판단용)
        self.is_model_on_cuda = False
        # GPU 사용 가능하면 GPU, 아니면 CPU
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # GPU 메모리 정보 출력
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f"GPU 메모리: {gpu_memory:.1f}GB")
            if gpu_memory < 8:
                logger.warning("GPU 메모리가 8GB 미만입니다. 4비트 양자화를 사용합니다.")
        
        logger.info(f"Device: {self.device}")
        logger.info(f"Adapter path: {self.adapter_path}")
        self._load_model()
    
    # [수정 금지] 모델/토크나이저/LoRA 로드 로직 (메모리/성능/안정성 영향)
    def _load_model(self):
        """모델과 토크나이저 로드"""
        try:
            # 어댑터 경로 확인
            import os
            if not os.path.exists(self.adapter_path):
                raise FileNotFoundError(f"어댑터 경로를 찾을 수 없습니다: {self.adapter_path}")
            
            adapter_config_path = os.path.join(self.adapter_path, "adapter_config.json")
            if not os.path.exists(adapter_config_path):
                raise FileNotFoundError(f"adapter_config.json 파일을 찾을 수 없습니다: {adapter_config_path}")
            
            logger.info("베이스 모델 로딩 중...")
            # 4비트 양자화로 메모리 사용량 감소
            if torch.cuda.is_available():
                # GPU 사용 시 (8GB VRAM 최적화)
                try:
                    from transformers import BitsAndBytesConfig
                    # 4비트 양자화 설정
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4"
                    )

                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.base_model_path,
                        quantization_config=quantization_config,  # 4비트 양자화
                        device_map="auto",
                        torch_dtype=torch.float16,
                        max_memory={0: "7GB", "cpu": "8GB"}  # GPU 7GB + CPU 8GB
                    )
                    self.is_model_on_cuda = True
                except Exception as quant_error:
                    logger.warning(
                        f"4비트 양자화 로딩 실패 또는 bitsandbytes 문제 발생. CPU 모드로 폴백합니다: {quant_error}"
                    )
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.base_model_path,
                        torch_dtype=torch.float32,
                        device_map=None,
                        low_cpu_mem_usage=True
                    )
                    self.is_model_on_cuda = False
            else:
                # CPU 사용 시 - 8비트 양자화 비활성화
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.base_model_path,
                    torch_dtype=torch.float32,
                    device_map=None,
                    low_cpu_mem_usage=True
                )
                self.is_model_on_cuda = False
            
            logger.info("토크나이저 로딩 중...")
            # 어댑터 폴더에 토크나이저 파일이 있으면 우선 사용, 없으면 베이스 모델 토크나이저 사용
            try:
                adapter_tokenizer_path = os.path.join(self.adapter_path, "tokenizer.json")
                if os.path.exists(adapter_tokenizer_path):
                    self.tokenizer = AutoTokenizer.from_pretrained(self.adapter_path)
                else:
                    self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_path)
            except Exception as tok_err:
                logger.warning(f"어댑터 토크나이저 로딩 실패, 베이스 토크나이저 사용: {tok_err}")
                self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_path)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
            
            logger.info("LoRA 어댑터 로딩 중...")
            try:
                self.model = PeftModel.from_pretrained(self.model, self.adapter_path)
            except Exception as e:
                logger.warning(f"LoRA 어댑터 로딩 실패, 베이스 모델만 사용: {e}")
                logger.info("베이스 모델만으로 추론을 진행합니다.")
            
            self.model.eval()
            logger.info("모델 로딩 완료!")
            
        except Exception as e:
            logger.error(f"모델 로딩 실패: {e}")
            logger.error("다음 사항을 확인해주세요:")
            logger.error(f"1. 어댑터 경로: {self.adapter_path}")
            logger.error("2. 필요한 파일들이 있는지 확인:")
            logger.error("   - adapter_config.json")
            logger.error("   - adapter_model.safetensors")
            logger.error("   - tokenizer.json")
            logger.error("3. 현재 작업 디렉토리: " + os.getcwd())
            raise
    
    # [수정 금지] 추론 프롬프트/생성 파라미터/후처리 (응답 품질/일관성에 영향)
    def generate_answer(self, question: str, instruction: str = "형사법 질문에 답변하세요") -> str:
        """
        질문에 대한 답변 생성
        
        Args:
            question: 질문
            instruction: 지시사항
            
        Returns:
            생성된 답변
        """
        try:
            # 입력 텍스트 구성
            user_template = f'''지시 : {instruction}\n
주어진 질문에 적합한 내용의 답변을 생성합니다. 질문 : "{question}"\n'''
            
            # ChatML 형식으로 변환
            messages = [
                {"role": "system", "content": "주어진 지시대로 질문에 대한 답변을 생성합니다\n\n"},
                {"role": "user", "content": f"{user_template}\n\n"},
                {"role": "assistant", "content": ""}
            ]
            
            # 토크나이징
            try:
                input_text = self.tokenizer.apply_chat_template(messages, tokenize=False)
            except Exception:
                # Chat template이 없거나 구버전일 때의 안전한 대체 프롬프트
                input_text = (
                    f"[SYSTEM]\n주어진 지시대로 질문에 대한 답변을 생성합니다\n\n\n"
                    f"[USER]\n지시 : {instruction}\n주어진 질문에 적합한 내용의 답변을 생성합니다. 질문 : \"{question}\"\n\n\n"
                    f"[ASSISTANT]"
                )
            inputs = self.tokenizer(
                input_text,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            )
            
            # 디바이스로 이동 (모델이 실제로 CUDA에서 동작할 때만 이동)
            if self.is_model_on_cuda:
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
            # 추론 (GPU 메모리 최적화)
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=128,
                    do_sample=True,
                    temperature=0.1,
                    top_p=0.9,
                    eos_token_id=self.tokenizer.eos_token_id,
                    pad_token_id=self.tokenizer.pad_token_id,
                    repetition_penalty=1.1,
                    use_cache=True  # GPU 캐시 사용으로 속도 향상
                )
            
            # 결과 디코딩: 프롬프트를 제외한 신규 생성 부분만 추출
            try:
                input_length = inputs["input_ids"].shape[1]
                new_tokens = outputs[0][input_length:]
                answer = self.tokenizer.decode(new_tokens.tolist(), skip_special_tokens=True).strip()
                if not answer:
                    # 비어 있으면 전체에서 후처리
                    generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                    answer = generated_text.split("질문 :")[-1].strip()
            except Exception:
                generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                answer = generated_text
            
            return answer
            
        except Exception as e:
            logger.error(f"답변 생성 중 오류: {e}")
            return f"답변 생성 중 오류가 발생했습니다: {e}"
    
    # [수정 금지] 배치 추론 헬퍼 (외부 사용 시 인터페이스 유지)
    def batch_generate(self, questions: list, instruction: str = "형사법 질문에 답변하세요") -> list:
        """
        여러 질문에 대한 배치 답변 생성
        
        Args:
            questions: 질문 리스트
            instruction: 지시사항
            
        Returns:
            답변 리스트
        """
        answers = []
        for question in questions:
            answer = self.generate_answer(question, instruction)
            answers.append(answer)
        return answers

if __name__ == "__main__":
    # 테스트 코드
    qa_model = CriminalQAModel()
    
    test_questions = [
        "절도죄의 구성요건은 무엇인가요?",
        "강도죄와 절도죄의 차이점은 무엇인가요?",
        "형사법에서 자백의 증거능력은 어떻게 되나요?"
    ]
    
    print("=== 형사법 QA 모델 테스트 ===")
    for question in test_questions:
        print(f"\n질문: {question}")
        answer = qa_model.generate_answer(question)
        print(f"답변: {answer}")
        print("-" * 50) 