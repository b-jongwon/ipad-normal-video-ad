# 전체 객체 중심 공정 이상 탐지 실험

이 폴더는 이전 결과를 보존한 별도 실험이다. v1(압축 특징), v2(원본 특징, 열지도 반정밀도 저장)를 보존하고, 원본 특징의 이상 정보를 유지하면서 오프라인/실시간 점수 정밀도까지 일치시킨 v3를 최종 실험으로 사용한다.
제안한 Training 1~6, Inference 7~13을 연결하고 고정 조건의 ablation을 수행한다.
IPAD R01~R04를 대상으로 하며 전체16 장면, 새로운 실제 공장, 위치 정답까지 검증한 것은 아니다.

## 실행 환경

- Windows / 로컬 RTX4060 8GB / Python3.12 / 기존 `.venv`
- Torch2.7.1+cu128, Transformers4.57.6, 기존 모델 캐시
- 추가 설치: supervision0.27.0, defusedxml0.7.1
- Supervision 메타데이터는 `opencv-python`을 요구하지만 현재 환경에서는 동일 `cv2` API의 기존 `opencv-python-headless4.11.0.86`을 사용한다. 런타임과 ByteTrack ID 유지 테스트는 확인했다. 두 OpenCV 배포본을 겹쳐 설치하지 않았다. 따라서 `pip check`에는 이 의존성 이름 차이가 남는다.
- 정상 문맥 생성만 외부 네트워크 사용. 검출·학습·추론은 캐시 모델로 오프라인 실행.
- 기존 API 키 파일만 메모리에서 읽으며 키를 코드·보고서·로그·배포 자료에 넣지 않는다.

추가 추적 모듈 설치는 기존 OpenCV 환경과의 중복을 피하기 위해 `pip install supervision==0.27.0 --no-deps` 후 `pip install defusedxml==0.7.1`로 진행했다. 기존 requirements가 NumPy/SciPy/Matplotlib/Pillow/requests/PyYAML/tqdm 등을 제공한다. Torch/CUDA 설치는 별도다.

프로젝트 루트에서 PowerShell:

```powershell
& '.\.venv\Scripts\python.exe' -m local_experiments.full_pipeline.context
& '.\.venv\Scripts\python.exe' -m local_experiments.full_pipeline.review_context
& '.\.venv\Scripts\python.exe' -m local_experiments.full_pipeline.features
& '.\.venv\Scripts\python.exe' -m local_experiments.full_pipeline.train
& '.\.venv\Scripts\python.exe' -m local_experiments.full_pipeline.tests
& '.\.venv\Scripts\python.exe' -m local_experiments.full_pipeline.verify
& '.\.venv\Scripts\python.exe' -m local_experiments.full_pipeline.report
```

`context`는 저장된 규칙 재사용. 기존 `cache/contexts/api_budget.json`의 누적 $4 한도를 공유한다.
`review_context`는 이번 R01~R04 정상 접촉표에 대한 보수적 수정이며 다른 장면에 일반 적용하는 알고리즘이 아니다.
원본 자동 규칙은 `generator_original.json`에 보존된다. 사람이 확정한 규칙/약한 라벨이 아니므로 연구용 후보로 취급한다.
규칙 수정 후 기존 특징·모델 지문이 다르면 기존 결과를 덮어쓰기 위해 검사를 무력화하지 말고 새로운 버전/폴더를 사용한다.

## 독립 추론

```powershell
# 해당 장면과 같은 공정/카메라의 실제 영상
& '.\.venv\Scripts\python.exe' -m local_experiments.full_pipeline.infer --scene R01 --video 'D:\path\video.mp4'

# IPAD 영상 하나: 테스트 정답 파일을 읽지 않음. 1/01은 같은 녹화.
& '.\.venv\Scripts\python.exe' -m local_experiments.full_pipeline.infer --scene R01 --clip 1
```

실제 영상은 OpenCV로 디코딩하고 ZIP은 연속 JPG를 읽는다. 4프레임 간격의 인과적 입력, 미래 프레임 미사용.
새 공정에 R01 모델을 그대로 적용한다고 범용성이 보장되지 않는다. 신규 공정 정상영상 학습용 범용 폴더 import UI는 이번 범위 밖이다.

## 데이터/학습 프로토콜

- 기존 CLIP/DINO 캐시와 같은 녹화 분리·표본 목록 사용.
- 정상 녹화 단위 80% train / 20% normal validation, seed0.
- 정상 학습 녹화3편에서 객체 vocabulary, 순서 후보, 희소 단계 약한 라벨 생성.
- 단계 분류기10ep, 객체 결합 AE/개별 추적 GRU10ep 학습, 5ep/10ep 체크포인트·점수 저장.
- Backbone은 동결. 추출기 자체를 파인튜닝한 실험으로 부르지 않음.
- 결합 가중치 고정. 정상 검증만으로 스케일·q99 임계값 계산.
- 이상 라벨은 모델/점수/임계값 고정 뒤 평가에만 사용.
- 단계·객체 불량 위치 GT가 없어 그 정확도는 측정하지 않음.

## 구조

1. GroundingDINO tiny: 매 표본 프레임 검출, 클래스별 NMS, 클래스당 최대2개/프레임 최대8개.
2. 클래스별 ByteTrack: 개별 객체 ID/궤적, 녹화 경계에서 초기화.
3. 동결 CLIP ViT-B/16: 화면512차원과 각 객체512차원을 이상 판정에 그대로 유지.
4. 화면512 + 개별 객체512 + bbox/속도6 = 1030차원 결합. 단계 분류에만 각각 최대64차원 PCA 축소. 객체별 점수를 별도로 유지.
5. 정상 약한 단계 라벨의 MLP, 3관측 인과 평활화, 낮은 margin은 unknown.
6. 단계별 화면/객체별 PCA. 표본<30이면 전역 정상 공간 fallback.
7. 객체별 geometry 정상 분포, AE 재구성 잔차, 같은 ID의 과거8관측 GRU 예측 잔차.
8. 명시적 skip/order/required-object/dwell 규칙, 2관측 확인·필수 객체3관측 누락 확인.
9. DINOv2-S/14 중간4/7/10층 패치의 단계별 잔차 지도. 224px/16×16이며 SubspaceAD 원 논문 전체 재현 아님.
10. 고정 가중치의 visual/spatial-temporal/process/full 조합 및18가지 대조 구성.

공정 시간은 원본 FPS 미확인으로 sampled observations로 다룬다. 미리보기10 FPS는 처리 FPS가 아니다.
검출·단계 추론이 틀리면 이후 점수도 틀릴 수 있다. 누락 예상 영역은 정상 객체 위치의 추정치이며 탐지된 불량 bbox가 아니다.

## 주요 파일

- `context.py`, `review_context.py`: 예산·정상 증거·규칙 후보와 보수적 수정.
- `features.py`: 실제 검출/추적/개별 crop 특징.
- `model.py`, `process.py`: 정상 공간·학습 head·명시적 규칙.
- `train.py`: 정상-only fit/18 ablations/평가.
- `infer.py`: 독립 인과 추론, MP4/JSONL 출력.
- `verify.py`: 데이터 누출·유효값·저장 모델의 순차 추론 round-trip 검증.
- `tests.py`: 기능 테스트. 합성 시퀀스는 벤치마크 정확도 증거 아님.
- `report.py`: 실제 결과표/시연/팀 공유용 설명.

검증된 모델 revision pin을 유지했다. GitHub 원격 변경 없음.
기존 모듈과 정상 특징 공간의 조합이다. 독창적 신방법이나 무조건 성능 개선을 주장하지 않는다.

## 공유 ZIP

- 회의공유 ZIP: HTML 결과 화면, 표, 시연, 검증 기록. 별도 API 키 불필요.
- 코드모델 ZIP: 소스와 4장면의 학습된 정상 공간/학습 head. 원본 데이터, API 키, `.env`, 대형 사전학습 가중치 제외.
- 팀원은 맞는 Python/CUDA 환경과 requirements를 준비한 다음, 공식 가중치를 받으려는 경우에만 `python -m local_experiments.full_pipeline.prepare_models`를 실행한다. 이 명령은 네트워크로 공개 모델을 다운로드한다.
- 이후 `infer --scene R01 --video ...`로 같은 공정의 영상을 판정한다. IPAD ZIP이나 정답은 파일 입력 추론에 필요 없다.
- 새 규칙을 API로 생성하려면 별도 키/예산 승인이 필요하다. 현재 사용자 승인 $4를 다른 사용자에게 자동 승계하지 않는다.
- 검증 원시 데이터/캐시는 공유 ZIP에 없어 전체 재학습·round-trip 검증은 IPAD와 로컬 캐시를 다시 준비해야 한다.
