# 멘토 제안1~13단계: 목적·실제 실행·한계

대상은 원 제안의 **`full_pipeline_v3`, R01~R04**다. 각 stage의 구현 완료와 그 의미/정확도 검증은 구분한다. 후속 `advanced_pipeline`은 이 구성을 그대로16개에 복제한 것이 아니라 별도 화면/객체 비교다.

이 문서의 freeze/학습 미수행 설명은 v3 범위다. E07의 강한 LLM 비교·DINO 화면 일부 층 FT·live guard·신규 MP4 입력은 [후속 문서](IMPROVEMENT_FOLLOWUP.md)를 본다. CLIP 객체 encoder 자체 FT와 사람 phase/결함 GT는 E07에도 미수행이다.

## 전체 흐름

```text
정상 녹화
  ├─ normal keyframe → GPT 후보 vocab/grammar → AI 후보 검토
  └─ 시간순 프레임 → GDINO → ByteTrack → CLIP 화면/개별crop + geometry
                                    ├─ weak phase MLP → phase normal PCA/rule
                                    ├─ joint feature AE
                                    └─ 같은ID 과거8관측 GRU
             DINO 중간층patch ──────→ patch normal PCA
새 영상 → 같은 frozen 추출 + 저장 normal 모델 → 연속score → q99경고/후보영역
```

외부 GPT는 초기 정상 문맥 준비에 사용했다. 온라인 inference에서 GPT로 매 프레임을 판단하지 않는다. CLIP은 image encoder로 남아 있으므로 “외부API 없음”과 “VLM 전혀 없음”은 다르다.

## 1. Normal videos — 기준을 배울 입력

`ipad_data.py`가 ZIP 안의 녹화/연속 이미지/정답 길이를 검사하고 `records.json` 목록을 만든다. 각 row에는 scene,split,clip,frame/ordinal,member,stride 등이 있다. 정상 녹화를 train/val로 나누고 동일 영상의 시간순서를 유지한다.

초기 R4 train10,043/normal val2,658/test7,911관측. 정상 train에서 모델을 적합하고 normal val에서 scale/q99를 정한다. anomaly label은 neural 학습에 쓰지 않는다. class label이 없다는 것과 weak phase label도 없다는 것은 다르다.

## 2. VLM/LLM — vocabulary/grammar의 후보 작성

`full_pipeline/context.py`: 정상 train 녹화3편에서12장씩 keyframe을 골라 객체 이름,phase 설명,allowed transition,required order,관측 가능한 순서 여부,evidence weak label을 구조화된 후보로 만든다. 모델은 GPT-4.1-mini이고 GPT의 가중치를 업데이트하지 않는다.

예를 들어 arrival→grasp→lift→release는 설명용 예시다. 모든 IPAD 장면이 동일한 단계로 이루어졌다는 뜻이 아니다. 정상 후보의 원본과 AI 검토 수정본을 따로 보존했다. `review_context.py`는 기존4장면에 대한 장면별 후보 검토이지 임의 공정 자동 정답 생성기가 아니다.

현재 grammar의 `human_verified`는 false다. LLM 답을 인간 공정 정답으로 사용하지 않는다. 새 공정 설정시간이 줄어들 것이라는 가설은 가능하지만 수동 작성 대비 시간을 측정하지 않았다.

원 실행의 v3까지 누적 토큰 비용 추정은 약$0.0176, 사용자 승인 한도$4, 실패 가능성을 포함한 보수적 예약액$1.20이다. 비용 추정/예약은 실청구와 다르며 고도화·감사에서는 새 API를 호출하지 않았다. 공개 코드에는 secret와 저자 비용 원장을 넣지 않았다.

## 3. GroundingDINO + Tracking — 무엇이 어디 있는지 연결

`full_pipeline/features.py:ObjectExtractor`는 각 선택 프레임을 vocabulary와 함께 frozen GroundingDINO tiny에 넣는다. 검출 threshold0.20,text0.25,입력 shortest480/longest640,class NMS0.5,클래스당 최대2/frame최대8객체다.

Supervision0.27의 ByteTrack을 객체 종류별로 따로 둔다. bbox/class/confidence와 동일ID를 저장한다. 녹화가 바뀌면 tracker/history를 reset한다. 클래스가 달라지며 같은ID를 공유하는 것을 막지만 역할/ID 정확도가 보장되지는 않는다.

원본 FPS 미확인 상태에서 tracker 내부 설정의 frame_rate30을 실제 데이터 FPS라고 발표하지 않는다. 학습과 추론에 같은 설정을 사용한 구현 parameter다.

실패: R01의 product 후보가 conveyor 위 이동 제품이 아니라 고정 계측기를 따라갔다. “bbox가 있다”는 것만으로 관심 제품을 잘 찾았다는 결론을 내리면 안 된다.

## 4. Object-centric encoder — 객체마다 특징을 만든다

동결 CLIP ViT-B/16의 normalized visual embedding을 사용한다.

| 성분 | 차원 | 의미 |
|---|---:|---|
| full frame | 512 | 화면 배경/공정 맥락 |
| 개별 object crop | 512 | 해당 검출 객체의 외형 |
| geometry | 6 | 정규화된 위치/크기/이동 성분 |
| joint | **1030** | 위 성분의 concatenate |

geometry에 `[0.1,0.1,0.1,0.1,1,1]` scale을 적용한다. 후보 class가 같은 모든 객체를 평균해 없애지 않고 개별 객체 점수를 만든 뒤 frame에서 max를 취한다. phase 입력에만 role별 pooling을 허용한다.

CLIP은 generative caption 모델이 아니다. 이 단계에서 객체 상태 설명을 문장으로 계속 생성한 것이 아니다. Backbone freeze를 선택했으며 encoder fine-tuning 비교는 하지 않았다.

## 5. Process consistency — 정상 순서/누락/지연 후보 규칙

`full_pipeline/process.py:ProcessMonitor`가 phase sequence와 present object class를 본다.

- 허용 transition에 없는 순서/필수 order의 역행.
- 필수 중간 phase 건너뜀.
- 해당phase 정상에서 거의 항상 보여야 하는 객체 누락.
- 정상phase 체류 기준보다 긴 반복.

phase는2관측 연속 확인 후 전환한다. 객체 누락은3관측 연속,reason은5관측 hold한다. normal dwell은 정상 predicted run 길이로 추정하고 여유를 주었다. expected object는 충분한 정상 표본30개/존재율90% 조건으로만 활성화한다.

잘린 clip이 완결 cycle라는 가정을 기본으로 강제하지 않는다. unknown이면 새 전이를 만들어내지 않는다. 하지만 당시 기본 구현의 score0은 “정상 확정”이 아니라 “그 규칙으로 판단할 정보 없음”일 수 있다. 최근 audit trace guard가 이를 명시한다.

R04는 effective expected 목록이 비어 있어 missing object 검사가 지원되지 않는다. 지원되지 않은 rule도 실행해 완성한 것으로 표시하지 않는다.

## 6. Phase-conditioned normal subspaces — 단계별 정상 기준

`full_pipeline/model.py`와 `compare.py:Subspace`가 정상 feature의 평균과 PCA basis를 맞춘다. 정상 분산99%를 유지하고 rank는 표본 수/차원에 의해 제한된다. rank32 하드상한은 없다.

쉬운 의미: 정상 특징이 주로 놓이는 공간을 만들고, 현재 특징의 **그 공간 밖 잔차**를 이상 점수로 쓴다. 공간 안에서 얼마나 멀리 움직였는지의 distance와 다르다.

```text
centered = x - normal_mean
score = ||centered||² - ||centered @ normal_basis||²
```

frame/객체 종류/phase별 공간을 만들되 정상 표본30개 미만 또는 phase 불확실이면 전역 기준으로 fallback한다. 기준선과 phase 모델은 실제 rank/표본이 다를 수 있어 완전한 capacity-matched 대조는 아니다.

Phase routing은 full/crop/geometry 입력을 PCA64로 투영 후 MLP `d→128→K`로 분류한다. 정상3영상 sparse keyframe의 confident phase를 가까운 frame으로 전파한 **약한 라벨**로10epoch 학습했다. AdamW lr0.001,wd0.0001,CE,batch128,clip1이다.

분류 확률은 과거3관측 평균,margin confidence cutoff는 정상validation으로 정한다. anomaly feature 자체를64차원으로 줄여 residual을 계산하는 것이 아니다. 잘못된 phase가 맞는 정상 feature를 다른 공간에 보낼 수 있다. 실제 같은 조건 비교에서 phase 조건은 손해였다.

## 7. Test video — 정답 없이 새로운 입력을 읽는다

`full_pipeline/infer.py`는 저장된scene 모델을 읽고 ZIP clip 또는 MP4를 처리한다. 추론 자체에는 anomaly label/API key가 필요 없다. raw smoke에서는 detector부터 다시 실행했다. 캐시 feature로 모델 재실행하는 roundtrip과 원본 image 재추론 smoke는 다른 검사다.

새 공정에 R01 모델을 넣는다고 적용이 보장되지 않는다. 기존 공정의 normal model을 쓰거나 새 공정 정상 데이터를 따로 적합해야 한다.

## 8. Frame/clip sampling — 시간순서를 지키며 간격을 둔다

기본 stride4로 원본4프레임마다1개를 읽는다. 영상 전체를 image tensor로 처리하더라도 frame index/clip ID를 유지한다. GRU/phase/progress/alarm의 상태는 clip 경계를 넘지 않는다.

장점은 계산량 감소다. 단점은 샘플 사이의 짧은 이상을 놓칠 수 있고8관측의 실제 초 길이는 원본FPS에 따라 달라진다는 것이다. preview10FPS는 처리 성능이 아니다.

## 9~10. 검출/추적 → crop/trajectory

훈련과 같은 vocabulary/extractor를 재사용한다. bbox 위치/크기와 시간에 따른 displacement를 기록하고 ID별 history로 연결한다. lookup grammar만 사용하므로 GPT API는 새로 호출하지 않는다.

그러나 **9단계에 API가 없다고11단계CLIP까지 사라지는 것은 아니다**. 객체 crop의 외형,geometry,track sequence가 이후 점수에 쓰인다. tracking ID가 틀리면 forecast error가 공정 이상이 아닌 ID 교환 때문에 커질 수 있다. HOTA/IDF1 GT는 없다.

## 11. Object encoder/state — 같은 특징과 학습 phase head

CLIP image/full/crop embedding과 geometry를 같은 방식으로 만든다. weak phase MLP가현재phase/unknown을 추정한다. 외부 VLM이 프레임마다 object/state/phase를 문장으로 출력하는 경로를 구현한 것은 아니다.

현재 phase head가 사람 공정 의미를 정확히 표현한다는 검증은 미완료다. 정상48프레임 AI 참고 검수는 진단일 뿐 human action accuracy가 아니다.

## 12. Visual anomaly score

frame PCA,crop/joint PCA,motion정상분포,patch PCA residual을 독립 비교한다. DINOv2-S/14의4/7/10중간층 patch를 평균하고224입력의16×16patch를 사용한다. patch score는 가장 큰3개 residual 평균이다.

AE는 joint1030→128→32→128→1030 정상 특징 재구성(MSE)이다. 영상 픽셀을 생성하지 않는다. GRU는joint→64projection,hidden96,과거8관측→현재joint예측이다. 동일class/ID history,최대gap16원본frame,clip경계 reset을 적용해 미래를 보지 않는다.

두 모델을 정상5/10epoch로 비교했다. 같은 훈련의 중간/최종 checkpoint이며 모든구성을 새로10번씩 돌린 뜻이 아니다. phase head는두 구성에서 모두10epoch다.

## 13. Semantic/process score와 고정 결합

normal val의 robust scalar calibration으로 서로 다른 branch scale을 맞춘다. 결합 가중치는 test로 조정하지 않았다.

| 이름 | 식 |
|---|---|
| visual | frame0.35 + objectjoint0.35 + patch0.20 + motion0.10 |
| visual_process | visual0.8 + process0.2 |
| spatial_temporal | visual0.7 + GRU0.3 |
| full_pipeline | visual0.6 + GRU0.2 + process0.2 |

**Full에 AE는 없다.** AE는 별도 score method다. q99 threshold는 정상validation에서 정한다. 설명/모델이 더 복잡해도 기여가 늘지는 않았고 process 단독은 평균AUROC50.22%였다.

## 후보 위치와 검증 범위

object residual이 큰 bbox, DINO patch heatmap,expected missing region을 보여주는 기능이 있다. 객체/픽셀 결함 GT가 없어pixelAUROC,IoU,mAP를 계산하지 못했다. 검출 box는 object region이고 defect region일 필요가 없다.

정리하면 원 제안의 **동결 encoder 선택지 + 후보 weak phase + 후보 process rule**은 연결했다. encoder fine-tuning,online generative VLM state,인간검증 phase,실제 공정별 semantic fault recall은 수행/입증하지 않았다. 같은 말의 서로 다른 수준을 혼동하지 않는다.
