# 재현 범위

이 저장소는 완료된4장면 파일럿 소스·결과를 보존합니다. 대형 특징 캐시, 원본IPAD, 사전학습 가중치는 포함하지 않습니다. Releases에는 학습된 정상 공간/학습 head와 결과 시연을 제공합니다.

## 바로 가능한 것

1. CSV/설명서 확인: GPU/API/데이터 없이 가능.
2. 결과 시연: Releases의 results ZIP을 풀고 `결과보기.html`을 브라우저로 열기.
3. 독립 추론: 원README의 환경 설치 + 공식 모델 다운로드 + Releases 학습 모델 복사 + 같은 공정MP4 입력.
4. 기능 테스트: `python -m local_experiments.full_pipeline.tests`. 합성 검사12개이지 실제 위치·단계 정확도 측정이 아닙니다.

## 기존 정상 규칙으로 재학습

학습 모델을 복사하지 않은 별도 체크아웃에서 수행합니다. 학습 데이터ZIP 위치는 본인 환경으로 바꾸세요. 아래 예시는 PowerShell입니다.

```powershell
& .\.venv\Scripts\python.exe -m local_experiments.full_pipeline.prepare_models
& .\.venv\Scripts\python.exe local_experiments\extract_features.py --zip 'D:\data\IPAD_dataset.zip' --encoders dino clip --max-train 5000

foreach ($scene in @('R01','R02','R03','R04')) {
    $destination = "local_experiments\cache\full_pipeline_v1\$scene"
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    Copy-Item -LiteralPath "output\full_pipeline_20261004\$scene\normal_grammar_candidate.json" -Destination "$destination\grammar.json"
    Copy-Item -LiteralPath "output\full_pipeline_20261004\$scene\normal_evidence.jpg" -Destination "$destination\normal_evidence.jpg"
}

& .\.venv\Scripts\python.exe -m local_experiments.full_pipeline.features --zip 'D:\data\IPAD_dataset.zip'
& .\.venv\Scripts\python.exe -m local_experiments.full_pipeline.train --zip 'D:\data\IPAD_dataset.zip'
& .\.venv\Scripts\python.exe -m local_experiments.full_pipeline.verify
```

위 절차는 저장된 정상 규칙을 재사용하므로 유료API를 호출하지 않습니다. 결과는 `local_experiments/runs/full_pipeline_v3/`에 생성됩니다. 동일 버전이라도 GPU/라이브러리에 따른 수치 변동이 가능하며 완전 비트 단위 재현을 보장하지 않습니다.

`report.py`는 로컬 누적 API 비용기록을 읽고, `stats.py`는 이전 DINO 기준 모델의 프레임 점수도 필요로 합니다. 이 두 원본 의존성은 소스 저장소에 포함하지 않았습니다. 업로드한 보고서/불확실성 결과는 당시 실행 결과이며 위 명령만으로 자동 재생성된다고 주장하지 않습니다.

## 새 공정/새 규칙 생성

- 기본4장면의 `review_context.py`는 AI가 검토한 장면별 후보 수정입니다. 임의의 새 공정에 적용되는 일반 알고리즘이 아닙니다.
- 신규 공정의 정상 영상, 객체 이름, 단계 후보를 별도로 구성하고 사람이 확인해야 합니다.
- `context.py`는 사전에 초기화된 누적 비용 원장을 요구합니다. 키만 넣어서 무제한 자동 실행하도록 만들지 않았습니다.
- 신규API 실행에는 실행자의 별도 승인·키·예산 초기화가 필요합니다. 이전 사용자 승인$4를 승계하지 않습니다.
- 이상 라벨을 임계값/결합 가중치에 사용하거나 테스트 최고 결과를 독립 검증 결과로 발표하지 마세요.

## 수행하지 않은 것

전체16장면 학습, backbone fine-tuning, 현장30FPS 성능 검증, 픽셀 결함 정답 평가, 새로운 공장 zero-shot 검증, 범용 신규공정 import UI.
