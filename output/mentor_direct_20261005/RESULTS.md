# 멘토 가이드 직접 VLM 경로 — 실제 실행 결과

기존 v3의 MLP 상태 추정을 **실제 이미지·객체 crop 입력 VLM 상태 추정**으로 교체한 별도 실험이다.
기존 v3/advanced 모델은 변경하지 않았다. 이 보고서의 숫자를 이전16장면/stride4 평균과 직접 비교하면 안 된다.

평가 장면: R01, R04. 선택된 직접 VLM 관측 597개.
새 응답 사용량 비용 추정 $0.4215; 누적 추정 $1.0995. 실제 청구서는 별도다.

| 방법 | AUROC | AP | 프레임 FPR | 프레임 Recall | 프레임 F1 |
|---|---:|---:|---:|---:|---:|
| ae_baseline | 63.97% | 51.89% | 51.21% | 61.54% | 42.42% |
| frame_global | 67.49% | 54.82% | 54.45% | 61.19% | 41.07% |
| frame_phase | 62.02% | 49.38% | 15.19% | 19.46% | 22.30% |
| global_plus_process | 70.16% | 56.60% | 50.08% | 58.74% | 38.69% |
| mentor_full | 65.06% | 51.61% | 18.85% | 27.62% | 24.44% |
| object_global | 65.73% | 52.80% | 47.09% | 50.00% | 24.53% |
| object_phase | 65.32% | 55.32% | 19.19% | 26.92% | 22.58% |
| process | 55.15% | 46.99% | 3.32% | 3.85% | 6.38% |
| visual_global | 69.59% | 56.42% | 50.08% | 58.04% | 37.68% |
| visual_phase | 64.48% | 51.25% | 19.43% | 25.99% | 22.66% |

## 학습한 것과 동결한 것

- GPT-5.4 정상 grammar 생성 결과를 원본 그대로 재사용했다. 고정 SPECS로 수정하지 않았다.
- GPT-4.1-mini가 각 선택 프레임에서 직접 phase·객체 state·정상 공정 일치 여부를 추정했다. MLP 예측을 프롬프트에 넣지 않았다.
- GDINO/ByteTrack을 새 vocabulary로 다시 실행했고, CLIP 전체 화면/개별 crop 특징을 동결 추출했다.
- 정상 영상으로 global/phase별 PCA 공간과 phase 전이 확률을 새로 추정했다. 이것은 통계적 fitting이며 에포크가 없다.
- 비교용 정상 CLIP 특징 AE를 장면당10에포크 새로 학습했다. 멘토 Full 점수에는 AE를 섞지 않았다.
- GPT/CLIP/GDINO 자체를 fine-tuning한 것이 아니다. 멘토가 허용한 frozen encoder 선택지다.

## 남은 한계

- 정상 학습72/정상 calibration32 관측씩의 작은 pilot이다. phase별8미만은 global fallback이며 phase 공간이 모두 학습됐다고 주장하지 않는다.
- 32프레임 간격이라 짧은 이상/중간 단계가 빠질 수 있다. 샘플링 간격은 초 단위가 아니다.
- 객체·단계·원인 설명 human GT가 없어 의미 추정 정확도/설명 충실도와 defect localization 성능은 입증하지 않았다.
- 테스트 영상은 이전 실험에서 이미 확인했다. 독립 최종 테스트나 새 공장 일반화 증거가 아니다.
- VLM 상태 텍스트와 confidence는 모델의 주장이지 정답/보정 확률이 아니다. 판단 불가는 정상 인증이 아니다.
- 직접 VLM 추론은 지연·비용이 발생한다. 실시간성이나 기존 모델 대비 우월성을 보장하지 않는다.
- normal-feature PCA residual은 SubspaceAD의 아이디어를 참고한 구현이며 논문의 patch DINO 전체 재현이 아니다.

## 출처

[OpenAI 이미지 입력](https://developers.openai.com/api/docs/guides/images-vision), [GPT-4.1-mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini), [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs), [SubspaceAD](https://arxiv.org/abs/2602.23013).
