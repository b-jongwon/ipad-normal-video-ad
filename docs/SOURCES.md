# 출처와 사용 범위

## 공식 모듈/데이터/논문

- IPAD: https://ljf1113.github.io/IPAD_VAD/ — 원본 데이터는 별도로 받습니다.
- DINOv2: https://github.com/facebookresearch/dinov2 — 동결 `facebook/dinov2-small`.
- CLIP: https://github.com/openai/CLIP — 동결 `openai/clip-vit-base-patch16` 시각 encoder.
- GroundingDINO: https://github.com/IDEA-Research/GroundingDINO — `IDEA-Research/grounding-dino-tiny`.
- ByteTrack/Supervision0.27: https://supervision.roboflow.com/0.27.0/trackers/.
- SubspaceAD: https://arxiv.org/html/2602.23013v3 — 정상 PCA 공간과 직교 잔차의 아이디어 참고. 원 논문의 backbone/해상도/증강/전체 평가를 재현한 것이 아닙니다.
- OpenAI Structured Outputs: https://developers.openai.com/api/docs/guides/structured-outputs — 정상 규칙 후보 생성용.

## 고정한 모델 revision

| 모델 | Hugging Face revision |
|---|---|
| facebook/dinov2-small | ed25f3a31f01632728cabb09d1542f84ab7b0056 |
| openai/clip-vit-base-patch16 | 57c216476eefef5ab752ec549e440a49ae4ae5f3 |
| IDEA-Research/grounding-dino-tiny | a2bb814dd30d776dcf7e30523b00659f4f141c71 |

## 참고용 팀 저장소

- https://github.com/PigeonLabs/KNU_Capstone1_VAD
- https://github.com/PigeonLabs/KNU_Capstone1_VAD_VERA
- https://github.com/PigeonLabs/KNU_Capstone1_VAD_vLLM — 감사 비교의 참고 commit `ab0a72e466cbd602425fb571183163cd34e29a5c`. experiment01/06/43 등 서로 다른 변경 범위를 구분합니다. 해당 실험 결과는 우리의 측정값이 아닙니다.

위 저장소는 아이디어·실험 맥락의 참고이며 원격 저장소를 수정하거나 해당 팀의 이전 결과를 본 파일럿 측정값으로 표시하지 않았습니다. 참고 저장소 checkout 전체는 포함하지 않습니다.

이 파일럿은 기존 모듈을 연결하고 구성별 효과를 비교한 연구용 구현입니다. 모든 layer를 새로 만든 모델, 독창적 신방법 또는 국제논문 최고 성능을 주장하지 않습니다. 각 모듈·체크포인트·데이터의 라이선스는 별도로 적용되며 공개·상업 배포 전 확인해야 합니다.

## 이번 업데이트의 실험 근거

- 초기/v3/고도화/탐색/감사는 자체 로컬 실행의 원본 JSON·CSV에 기반합니다. 복사 파일의 SHA와 범위는 [publication manifest](PUBLICATION_MANIFEST.json)에 있습니다.
- AE/GRU/normal fitting 구현과 결합은 이 실험의 downstream 모듈입니다. 사전학습 extractor를 자체 개발 모델이라고 표시하지 않습니다.
- [scikit-learn ROC AUC](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html), [AP](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html)는 지표 정의 참고입니다. 실험 평가 코드는 별도로 공개합니다.
- VERA/LAVAD/LogicAD/LogicQA 등은 프로젝트 논의의 배경 자료입니다. 본 실행에 해당 논문의 전체 공식 파이프라인을 재현한 결과가 있다는 뜻은 아닙니다.
- 원 IPAD 프레임워크의 완전 재현, SubspaceAD 원 논문의 DINO-G/해상도/증강/평가 전체 재현 또는 최신 SOTA 비교를 수행했다고 주장하지 않습니다.
- 공개 상태가 모듈/데이터/가중치의 상업 라이선스를 자동 부여하지 않습니다. 웹사이트 라이선스와 데이터 이용 조건을 구분합니다.
