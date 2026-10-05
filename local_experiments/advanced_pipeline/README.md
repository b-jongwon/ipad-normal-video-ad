# IPAD normal-only AD: advanced experiment

2026-10-05 로컬 후속 실험. 이전 `full_pipeline_v3` 결과와 팀 참고 저장소는 수정하지 않는다.

## 목적

동영상 순서를 보존한 정상-only 학습으로 화면/객체/시계열 이상 점수를 만들고, 구성별 성능과 오경보·지연·속도·초기값 편차를 비교한다. Backbone은 동결하고 AE/잡음 제거 AE/GRU 헤드를 직접 학습한다. 추가 VLM/LLM API 호출은 없다.

- 실제 촬영 R01~R04 + 합성 S01~S12. 실제 공장 16곳 검증으로 부르지 않는다.
- 정상 녹화 단위 fit/tune/calibration 분리. tune의 정상 손실로 가중치 선택, calibration 정상 q99로 경고 기준 설정.
- 최대100/min10/상대개선0.5%/patience10. 모든 모델이 수렴할 때까지 무한 학습한 것이 아니다.
- 3seed. 정상 3개 영상 fit 비교는 seed0이며 추가 정상 tune/calibration 영상이 필요하다.
- 시각 상태별 PCA는 자동 군집 ID에 조건을 준 실험이지 사람이 검증한 공정 단계별 모델이 아니다.
- ROI는 이동 궤적이 충분한 경우에만 켠다. R01의 정지 배경 오검출은 이 방법으로 제거하지 못했다.
- 전체 결과·지표 정의·한계: `output/advanced_20261005/결과보고서.md`.
- 추가 `crop_roi.py`는 실제 촬영 결과를 본 뒤 배경 영향 억제를 위해 만든 탐색 실험이다. 정상 위치 ROI + crop-only518 특징 AE/GRU. 추가24헤드/48평가이며 새 독립 검증으로 부르지 않는다.

## 실행

프로젝트 루트의 기존 Windows/Python3.12 `.venv` 사용:

```powershell
.venv\Scripts\python.exe -m local_experiments.advanced_pipeline.tests
.venv\Scripts\python.exe -m local_experiments.advanced_pipeline.features
.venv\Scripts\python.exe -m local_experiments.advanced_pipeline.train --wait-features
# 학습이 끝나기를 기다렸다가 봉인/평가/추론/보고서/패키지를 연결한다.
.venv\Scripts\python.exe -m local_experiments.advanced_pipeline.finish
```

완료 후 모델 추론:

```powershell
.venv\Scripts\python.exe -m local_experiments.advanced_pipeline.infer --scene R01 --video C:/path/input.mp4
# 객체 검출 없이 DINO 화면 + 시계열 + 시각 상태 경로로 실행
.venv\Scripts\python.exe -m local_experiments.advanced_pipeline.infer --scene R01 --frame-only
# 추가 탐색 모델이 학습돼 있을 때만 사용
.venv\Scripts\python.exe -m local_experiments.advanced_pipeline.infer --scene R01 --crop-roi
```

`config.py`의 IPAD ZIP 경로는 `D:/종프 학습/IPAD_dataset.zip`. ZIP은 읽기 전용으로 직접 사용한다. 영상마다 tracker/history/alarm을 초기화한다. ZIP의 원본 FPS가 없으므로 초 단위 지연/시간당 오경보를 만들지 않는다. 새 공정은 별도 정상 데이터 수집·학습·검증이 필요하다.

## 환경 / 재현 제한

Torch2.7.1+cu128 / torchvision0.22.1+cu128 / Transformers4.57.6 / sklearn1.6.1 / supervision0.27.0 / RTX4060 8GB. 핵심 패키지는 `local_experiments/requirements.txt` 참고. Supervision은 중복 OpenCV 설치를 피하려고 기존 headless OpenCV 위에 `--no-deps`로 설치했던 환경이며 defusedxml0.7.1을 사용한다. 이번에는 새 설치나 유료 API를 하지 않았다.

사전학습 모델은 로컬 캐시가 필요하다. R 객체 학습은 이전 `cache/full_pipeline_v1/<scene>/features`와 CLIP/DINO 캐시를 재사용한다. 원본 ZIP·backbone·특징 캐시·키 파일은 공유 ZIP에 포함하지 않는다. 공유 코드는 해당 학습 캐시 없이 곧바로 전체 재학습되는 완전 독립 배포판은 아니다. 저장 모델 추론에는 별도 backbone 캐시가 필요하며 객체 vocabulary는 모델 폴더에 같이 제공한다.

전체 모델 점수를 봉인한 후 테스트 성능을 계산한다. 이전에 라벨 길이와 binary 형식 검사를 위해 라벨 파일을 로드하지만 그 값으로 학습/종료/threshold/조합을 선택하지 않는다. R02 test12/13/14, S05 test09~15, S12 test13은 frame/label 길이 불일치로 제외한다. 특히 S05 테스트의 7/15 녹화가 빠졌으므로 대표성에 주의해야 한다. 공식 전체 벤치마크 숫자와 직접 동등 비교하는 지표가 아니다.

## 주요 코드

| 파일 | 역할 |
|---|---|
| `config.py`, `data.py` | 고정 설정 / 녹화 단위 정상 3분할 |
| `networks.py`, `train.py` | 정상-only 헤드 학습 / early stopping / 3seed |
| `roi.py`, `state.py`, `subspaces.py` | 정상 이동 ROI / 자동 시각 상태 / 상태별 정상 PCA |
| `metrics.py`, `evaluate.py`, `checkpoints.py` | 프레임·영상·구간 지표 / 영상 bootstrap / 사후 epoch 비교 |
| `infer.py`, `roundtrip.py`, `verify.py`, `tests.py` | 독립 인과 추론 / 저장모델 재현 / 무결성 / 회귀 테스트 |
| `report.py`, `package.py`, `finish.py` | 읽기 쉬운 결과 / allowlist 공유 ZIP / 후처리 연결 |

API 없이 모델 가중치만으로 처리할 수 있다. 다만 `full_pipeline`의 일부 기존 도우미를 가져오기 때문에 그 소스도 함께 제공한다. 과거 후보 grammar 생성 코드는 현재 실행 경로에서 호출되지 않는다.

IPAD와 사전학습 모듈을 참조한 학부 연구 실험이다. 새 SOTA, 인간 검증 공정 단계, 불량 픽셀 위치 정확도, 미지 공장 제로샷 범용성, 상용 라이선스 충족을 주장하지 않는다.

출처: https://ljf1113.github.io/IPAD_VAD/ 및 scikit-learn 공식 지표 문서. 모듈 출처·모델 revision은 원 코드에 명시했다.
