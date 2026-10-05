# 재현 가이드와 공개 배포 범위

이 저장소에는 코드·설명·실행 당시의 수치 근거가 있다. 원본 IPAD/특징 캐시/고도화 학습 가중치가 모두 포함된 독립 배포판은 아니다. 재현 난이도를 숨기지 않는다.

## 1. clone만으로 가능한 것

| 작업 | 별도로 필요한 것 | 현재 확인 수준 |
|---|---|---|
| README/CSV/그래프 읽기 | 없음 | 공개 자료로 가능 |
| 기능/계약 테스트 | Python/패키지 | 원본데이터·GPT·모델다운로드 없이 검사 |
| 기존v3 모델 추론 | 공식backbone + 학습head + 같은공정video | 저자환경ZIP/MP4 smoke 확인 |
| 고도화 모델 추론 | 공식backbone + 별도고도화head | 저자로컬완료,이번head공개없음 |
| 모든head 재학습 | IPAD + 정상grammar + 생성cache + CUDA | 실행절차설명,새컴퓨터전체재현은미검증 |
| 원 보고서 모든항목 재생성 | 캐시/선택weights/기존비용원장 등 | 일부원본로컬의존성별도 |

## 2. 공개 상태와 과거 자료

2026-10-05 업데이트 시 GitHub 저장소는public이다. 새로올리는범위는owncode/docs/numericJSON·CSV/데이터픽셀이없는성능그래프다. 원본/검수/overlay이미지,추가MP4/모델ZIP/weights/featurecache/APIkey는새업로드에서제외했다.

이전 비공개 시절 커밋/`pilot-v3-20261004` Release에는 시연 이미지·영상과 v3 모델 asset이 있다. 기존 자료를 임의로 삭제하거나 이력을 변경하지 않았다. 공개 상태에서 접근될 수 있으므로 별도 재배포 조건 검토가 필요하다. 접근 가능하다는 것이 이용 허가라는 뜻은 아니다.

고도화의약977MB로컬modelarchive와최근감사검수이미지ZIP은이번Git/Release에새로올리지않았다. manifest/hash에파일명이있어도Git에서파일자체를배포한다는뜻은아니다.

공통코드와사전학습모델/데이터의이용조건은각출처에따른다. IPAD사이트의웹페이지license표시를데이터상업사용허가로자동해석하지않는다. 데이터/모델상업배포권한을확보했다고주장하지않으며새라이선스를임의부여하지않았다.

## 3. 실행 환경

검증환경: Windows/Python3.12.10/RTX4060 8GiB/RAM약31.8GiB,torch2.7.1cu128,torchvision0.22.1cu128,Transformers4.57.6,sklearn1.6.1,Supervision0.27.0,OpenCV-headless4.11.0.86,defusedxml0.7.1.

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install torch==2.7.1 torchvision==0.22.1 --index-url https://download.pytorch.org/whl/cu128
& .\.venv\Scripts\python.exe -m pip install -r local_experiments\requirements.txt
& .\.venv\Scripts\python.exe -m pip install supervision==0.27.0 --no-deps
& .\.venv\Scripts\python.exe -m pip install defusedxml==0.7.1
```

GPU/드라이버가다르면맞는Torch배포판을사용한다. CPU/다른OS도지원될것이라고보장하지않는다. Supervision메타데이터는opencv-python을요구하지만동일cv2API의headless를사용해중복설치를피했다. 따라서pipcheck에는패키지이름불일치가남는다. freshclone에이명령만실행한새환경의전체학습을이번문서화작업에서검증하지않았다.

## 4. 기능 테스트

프로젝트root PowerShell:

```powershell
& .\.venv\Scripts\python.exe -m local_experiments.tests.test_protocol
& .\.venv\Scripts\python.exe -m local_experiments.full_pipeline.tests
& .\.venv\Scripts\python.exe -m local_experiments.advanced_pipeline.tests
& .\.venv\Scripts\python.exe -m local_experiments.pipeline_audit.tests
```

각각4/12/11/6검사다. backbone다운로드/유료API/실제전체학습이아니며모델탐지정확도검사가아니다. 한컴퓨터에서재실행해통과한것과새컴퓨터완전재현은구분한다.

## 5. 공식 backbone 최초 다운로드

```powershell
& .\.venv\Scripts\python.exe -m local_experiments.full_pipeline.prepare_models
```

동결DINO-S/14,CLIP-B/16,GDINOtiny공식pinnedrevision을받는다. 최초인터넷/HuggingFace접근이필요하다. 이후추출/추론은localcache를전제로한다. random가중치로조용히대체하지않는다. 모델revision은 [SOURCES](SOURCES.md)에있다.

## 6. R4 특징과v3 학습 — 기존 grammar 재사용,유료API 없음

**학습model을복사하지않은별도체크아웃**에서진행한다. `full_pipeline/train`은기존완료결과를재사용하므로이미학습한폴더에서명령재실행이새학습이될것이라고가정하지않는다.

IPAD ZIP을공식출처에서별도로받고경로를지정한다. 최초R4기준feature는`max-train5000`으로만들어야후속cachelookup과맞는다.

```powershell
& .\.venv\Scripts\python.exe local_experiments\extract_features.py --zip 'D:\data\IPAD_dataset.zip' --encoders dino clip --max-train 5000

foreach ($scene in @('R01','R02','R03','R04')) {
    $destination = "local_experiments\cache\full_pipeline_v1\$scene"
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    Copy-Item -LiteralPath "output\full_pipeline_20261004\$scene\normal_grammar_candidate.json" -Destination "$destination\grammar.json"
}

& .\.venv\Scripts\python.exe -m local_experiments.full_pipeline.features --zip 'D:\data\IPAD_dataset.zip'
& .\.venv\Scripts\python.exe -m local_experiments.full_pipeline.train --zip 'D:\data\IPAD_dataset.zip'
& .\.venv\Scripts\python.exe -m local_experiments.full_pipeline.verify
```

이 절차는 사람 미검증 grammar 후보를 재사용하는 역사적 재현이지 올바른 role/phase로 자동 교정하는 절차가 아니다. 새 정의는 새 cache/run version에서 재추출·재fit·재calibration한다. 원래 결과를 덮어쓰고 같은 실험이라고 부르지 않는다.

`full_pipeline/report.py`는 과거 API cost ledger, `stats.py`는 초기 DINO score cache에도 의존한다. 이 자료는 Git에 없으므로 위 명령만으로 당시 보고서를 모두 재생성할 수 있다고 주장하지 않는다. 당시 보고서/CSV는 공개한다.

## 7. 고도화 재학습 — 중요한 출력 경로 설정

`advanced_pipeline/config.py`의 `ZIP`을 본인 환경으로 바꾼다. 공개된 `output/advanced_20261005`에는 과거 봉인/평가 시작 marker가 있어서 **이 출력 경로를 그대로 재학습에 쓰지 않는다**. state-PCA는 평가가 시작됐으면 새 fit을 거부하거나 기존 결과를 재사용하는 설계다.

재현용 copy에서 아래 3개 경로를 새 빈 version으로 바꾼다. 알고리즘 설정까지 바꿔 비교한다면 새 protocol/이름으로 기록한다. 문서만 읽는 이용에는 필요 없다.

```python
# local_experiments/advanced_pipeline/config.py의 예
RUN = ROOT / 'runs' / 'my_reproduction'
CACHE = ROOT / 'cache' / 'my_reproduction'
OUT = ROOT.parent / 'output' / 'my_reproduction'
ZIP = Path('D:/data/IPAD_dataset.zip')
```

R4 base frame cache와 `cache/full_pipeline_v1`은 앞 단계에서 생성한다. S12 DINO feature는 새로 추출한다. 아래는 전체16/3seed를 순서대로 실행하는 진입점이다.

```powershell
& .\.venv\Scripts\python.exe -m local_experiments.advanced_pipeline.features
& .\.venv\Scripts\python.exe -m local_experiments.advanced_pipeline.train --wait-features
& .\.venv\Scripts\python.exe -m local_experiments.advanced_pipeline.subspaces
& .\.venv\Scripts\python.exe -m local_experiments.advanced_pipeline.evaluate
& .\.venv\Scripts\python.exe -m local_experiments.advanced_pipeline.checkpoints
& .\.venv\Scripts\python.exe -m local_experiments.advanced_pipeline.verify

# 추론용 기존 vocabulary 복사. API 호출 없음
& .\.venv\Scripts\python.exe -c "from local_experiments.advanced_pipeline.package import vocabularies; vocabularies()"
& .\.venv\Scripts\python.exe -m local_experiments.advanced_pipeline.roundtrip
& .\.venv\Scripts\python.exe -m local_experiments.advanced_pipeline.report
```

`features/train`의 `--scenes`는 작은 확인에 쓸 수 있으나 전체 평가/verify는16scene×3seed 완성을 전제로 한다. 부분 실험에서도 통과한다고 주장하지 않는다. `finish`는 학습 봉인을 기다린 뒤 raw smoke와 로컬 ZIP 생성까지 연결하므로 계산/저장 용량을 확인해 사용한다.

추가 crop 탐색은 주 학습 후 `python -m local_experiments.advanced_pipeline.crop_roi`, 검증은 `...check_crop`이다. 원 실행은 R test를 본 뒤 사후 설계했다. 같은 코드 재실행으로 원 실험이 독립 검증으로 자동 바뀌지는 않는다.

## 8. 저장 모델 독립 추론

v3 학습 모델과 backbone이 있는 경우:

```powershell
& .\.venv\Scripts\python.exe -m local_experiments.full_pipeline.infer --scene R01 --video 'D:\path\video.mp4' --out 'output\my_video'
```

고도화 학습 모델이 있는 경우:

```powershell
& .\.venv\Scripts\python.exe -m local_experiments.advanced_pipeline.infer --scene R01 --video 'D:\path\video.mp4'
& .\.venv\Scripts\python.exe -m local_experiments.advanced_pipeline.infer --scene R01 --frame-only --video 'D:\path\video.mp4'
& .\.venv\Scripts\python.exe -m local_experiments.advanced_pipeline.infer --scene R01 --crop-roi --video 'D:\path\video.mp4'
```

advanced 기본값 `--limit100`은 짧은 확인용이다. 전체 동영상 처리에는 `--limit0`을 명시하고 저장 용량/운영 리스크를 확인한다. crop 옵션은 해당 가중치 학습 후에만 쓴다. 출력 MP4/이미지는 입력 데이터에서 파생되므로 공개 Git에 자동 추가하지 않는다.

이 추론은 test label/외부 API를 읽지 않는다. 같은 scene의 정상 모델이 범위다. 새 공정 자동 적응 UI나 보편적 zero-shot 성능은 제공하지 않는다.

## 9. 감사 재실행

`pipeline_audit`에는 기존v3/cache/IPAD가 필요하다. ZIP/RUN/OUT 및 Windowsfont 경로가 하드코딩된 부분은 본인 환경에 맞춘다. 원래 스냅샷을 덮어쓰지 않고 별도 copy/output에서 실행한다.

순서는prepare→analyze→stress→grounding_pilot→foreground_pilot→tests→report다. report는normal/reverse/80repeat/140repeat 전16건을 전제로 한다. 새 실행의sourcehash가 같은지 확인하는 것만으로 의미 정확성이 보장되지는 않는다.

새 API 생성은 필요 없다. 이번48phase 참고는 해당 실행의AI 판단이며 재실행한다고humanGT로 바뀌지 않는다. 의미 정확성에는 실제 사람 annotation이 필요하다.

## 10. 새 API를 쓰는 경우

공개 코드에key는 없다. 과거 사용자$4 승인/비용 원장을 새 실행자에게 승계하지 않는다. `context.py`는 초기화한 비용 원장을 전제로 하므로 환경변수만 넣으면 무제한 실행하는 처리가 아니다.

재현 절차는 저장 후보를 재사용하고 API를 호출하지 않는다. 새 문맥 생성은 별도 명시 승인/secret 관리/예산 초기화 후 실행한다. key값을README/로그/Git에 넣지 않는다.

## 11. 검증된 것과 미검증

검증됨: 기존 로컬 환경의 정상 학습,model/scoreSHA,disjointsplit,normalq99,선택epoch,finite,첫test 순차replay,짧은 원본ZIP/MP4,기능 테스트.

미검증: 새PCfreshclone 전체학습,완전bitwise재현,CPU/Linux,전체testraw재처리,장시간production,humanphase/object/pixelGT,신규공장zero-shot,상업재배포허가.

## 12. 최신 E07 재현 범위

E07의 새 코드/명령과 필요한 기존 cache는 [후속 실험 문서](IMPROVEMENT_FOLLOWUP.md)에 정리했다. 기존 모델을 덮어쓰지 않는다. 새 normal MP4 manifest 적응 CLI는 기존 IPAD clip ID가 필요 없는 별도 frame-memory 경로이며,Full13단계 적응과 다르다. 새 API key와 개인 env 파일은 공개하지 않는다. 유료 실행의 누적 예산은 유지해야 한다.
