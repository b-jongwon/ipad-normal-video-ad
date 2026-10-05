# 객체·phase·공정 일관성 감사와 팀원 비교

최근감사는“pipeline코드가실행됨”을넘어객체/phase의의미가맞는지와rule가그오류를어떻게받는지확인했다. 기존v3소스/weights/scores/grammarSHA는불변이다. 새neural학습/유료API는없었다. 원본전체설명: [감사보고서](../output/pipeline_audit_20261005/검증결과_팀원설명.md).

## 1. 데이터와 검수 수준

기존normalvalidation녹화의앞ceil절반은진단calibration,나머지는evaluation후보로분리했다. scene별evaluation2녹화에서6균등프레임씩총48장을봤다.

| scene | 진단calibrationclip | evaluationclip | AI참고phase명확한표본/일치 |
|---|---|---|---|
| R01 | 03,05,12,20 | 24,26,34 | 8/4 |
| R02 | 03,05,11 | 12,22,27 | 10/10 |
| R03 | 03,05,11 | 17,20 | 10/10 |
| R04 | 05,11,12 | 20,25 | 8/5 |

먼저raw를보고pred overlay는따로참고했다. 모호한phase는제외하고,참고가명확한데unknown인경우불일치로계산했다. 참조는**AI시각판단**이며humanGT가아니다. 이전v3phaseconfidence는oldval전체를사용했으므로이normal후보를완전히독립인미접촉validation이라고주장하지않는다.

## 2. 실제 지각 문제

| scene | 주요 발견 |
|---|---|
| R01 | role0의12box가벨트아래고정빨간계측기. 이동목표가보인8frame에대응role0box없음 |
| R02 | 빈platform에instrument오역할4frame,platformmiss1frame,구조중복box모호성 |
| R03 | 검은palletbox가wholeimage를덮는2사례. 올림/내림경계가희소정지화면에서는모호 |
| R04 | 빈영역cardboardbox3개,bladebox가cutter전체를잡는5모호사례,보이는객체인데검출없는2frame |

R04의raised/down과accumulated상태는동시에성립할수있어배타phase정의문제가있다. 이진단은48장선택조건의참고이지objectmAP/IoU/identityGT나factoryactionaccuracy가아니다. 공개업데이트에는검수원본/overlay이미지를추가하지않고frame식별자/참고표만올렸다.

## 3. Oracle99개: 규칙 코드만 따로 검사

allowed/illegal non-selfphase쌍,지원되는requiredskip,expectedmissing,dwell,unknown을정답phase기호로직접주입했다. 99/99 기대한출력. rulecontract검사이므로실제영상정확도99/99가아니다.

R04effectiveexpectedclass목록은전부비어있어missingrule를지원하지않는다. requiredorder는2phase라중간requiredskip계약도없다. 지원하지않는검사를억지로통과한것으로세지않았다. [oracle원본](../output/pipeline_audit_20261005/oracle_contract_results.json).

## 4. Raw영상16건: detector부터 다시 실행

scene별첫normal evaluation clip의앞최대64관측(R01은58)을사용했다. 정상prefix/역순prefix/중간장면80반복/140반복4조건을구성했다. 실제GDINO,ByteTrack,CLIP,DINO,phaseMLP,PCA,GRU,process를모두재실행했다. 총16입력/1880관측,미래참조없음,새streamindex와sourceframe대응보존.

80반복은R04phase2의dwelllimit121보다짧을수있어실패로단정하지않았다. 모든scene에140반복후속조건을추가했고80결과도남겼다.

| scene | normal orderreason | reverse orderreason | hold140 dwellreason | reverse processalarm비율 | hold140 processalarm비율 |
|---|---|---|---|---:|---:|
| R01 | 있음 | 있음 | 있음 | 0.0% | 0.0% |
| R02 | 없음 | 있음 | 있음 | 14.1% | 0.0% |
| R03 | 없음 | 있음 | 있음 | 7.8% | 44.1% |
| R04 | 없음 | 있음 | 없음 | 0.0% | 0.0% |

alarm비율은이인위적입력의전체관측중진단normalprocessq99를strict>`한비율이다. 실제불량recall/사건탐지율이아니다. reason발생과thresholdalarm이같지않다. 이산score에서q99가높으면이유가있어도경보가없을수있다. 테스트를보고threshold를임의로낮추지않았다.

- R01은normal에도잘못된orderreason이있어reverse에서도reason이생겼다는것만으로성공이라고할수없다.
- R02/R03은선택한normalprefix에는orderreason없고reverse에는생겼다는제한적기능근거가있다.
- R04hold140은204중143관측unknown(70.10%)이라dwell검사를못했다. 지각불가가processscore0으로이어지는반례다.

[raw요약](../output/pipeline_audit_20261005/raw_stress_results.json), [긴반복후속protocol](../output/pipeline_audit_20261005/long_hold_followup_protocol.json).

## 5. 교정 후보: 시도했지만 채택하지 않은 것

R01에서manualnoun `black object`를fullframe/normaltrainbeltROI `[0,.27,1,.65]`에검출했다. train6+참고12총18이미지×2view=36검출호출. 제품보다큰frame/beltbox가남아채택하지않았다.

다음은normaltrain160프레임의medianbackground,RNG20261005,RGBmeandiff35,3×3open/close,contourarea50~1600,ratio0.25~2.5로movingcandidate를찾았다. 반사/누락/복수candidate문제,AI참고phaseagreement3/8로기존4/8보다낮았다. 역시미채택이다. 이두후보에새네트워크학습이나유료API는없다.

교정후보를정상참고표를본뒤설계해같은표로다시봤으므로독립평가라고주장하지않는다. [교정판단](../output/pipeline_audit_20261005/repair_pilot_decision.json).

## 6. 안전한 출력의 범위

`pipeline_audit/safety.py:process_status`는audittrace에다음metadata를붙인다.

| 조건 | 상태 |
|---|---|
| phase<0 | `unavailable_uncertain_phase`,판단불가 |
| humanrule미검증,reason없음 | `unverified_no_rule_violation` |
| humanrule미검증,reason있음 | `unverified_anomaly_candidate` |

zero는확정normal근거가아니라고표시한다. 16audittrace에적용했지만**기존추론runtime전체를이guard로수정한것이아니다**. oldscore/threshold/default/weights를바꾸지않았다. 정확도향상을입증한모델교정이라고쓰지않는다.

`human_annotation_template.json`에는48표본과AI후보가있지만reviewer/humanphase/objectroles는null,verified는false다. 사람이실제검수없이플래그만true로바꾸면안된다.

## 7. 모듈이 왜 필요한가: 기존v3의 같은조건 대조

| 변경 | 전→후AUROC | 변화95%구간 |
|---|---|---|
| framephase조건 | 72.21→67.27% | −4.94pp,[−7.91,−1.65] |
| objectjointphase조건 | 73.32→70.05% | −3.27pp,[−5.42,−0.66] |
| frame→objectjointglobal | 72.21→73.32% | +1.10pp,[−4.53,+5.96] |
| visual→visualprocess | 70.31→70.35% | +0.04pp,[−0.25,+0.40] |
| visualGRU→Full10 | 72.31→72.08% | −0.23pp,[−0.72,+0.15] |

500녹화pairedbootstrap,seed0,R4조건부,다중비교보정없음. 이구현phase의손해/공정규칙의미미한효과를확인했다. objectjoint에는geometry/차원변화도있어purecrop대조가아니다. no-process는no-LLM이아니므로LLM본체의효용은별도실험이필요하다.

## 8. 팀원과 다른 숫자를 같은 결과로 취급하면 안 된다

참고: [팀vLLM](https://github.com/PigeonLabs/KNU_Capstone1_VAD_vLLM),commit`ab0a72e466cbd602425fb571183163cd34e29a5c`. 원격/참고checkout을수정하거나통째로재업로드하지않았다.

| 항목 | 우리v3 | 팀초기experiment01 |
|---|---|---|
| 범위 | R4macro | R01단일 |
| 문맥 | GPT후보+AI검토 | 로컬Qwen/normal2영상 |
| CLIP | B/16 | B/32 |
| phase | weakMLP10ep+unknown | image/textsimilarity |
| tracking | ByteTrack | HungarianIoU |
| PCA | 99%,rank32상한없음 | 95%,maxrank32 |
| process | skip/order/missing/dwell | 전이확률/순서벌점 |
| calibration | normalrobustscale | normalempiricalpercentile |
| 결합 | visual.6+GRU.2+process.2 | visual/process.5씩 |
| 평가 | stride4관측 | causalhold원본전체frame |
| normalsplit | seed0 | seed42 |

평가단위만맞춰우리R01을3685원본frame에causalhold했을때visual67.63%,ST10 69.66%,Full10 **68.20%**였다. R4macro72.08%가아니다. 팀experiment01Combined53.71%는초기값이지팀최신최종성능이아니다. 아키텍처/split차이가남아점수차이의원인을한요소로단정하지못한다.

팀experiment06은motionprogress의phase조건만제거하고appearancePCA의phase조건은남겼다. 그것을allphase제거라고인용하면안된다. experiment43은teacher/learnedphase를분리하며일부개선하지만humanGT는없다. 해당글이특정어느최신실험을가리키는지는확정하지않았다.

팀의DINOprototypememory/temporal/tracking스토리는논리적인연구가설이다. 그러나팀결과를우리실행으로옮겨쓰지않는다. 우리저장소에서prototypehead학습/같은조건prototype최종비교는아직없다.

## 9. 정리

이번완료는원인감사·기능검증·실패교정후보·감사출력구분·비교조건해석이다. 사람object/phaseGT와실제semanticerrorGT없는상태에서핵심정확성문제가다해결됐다고말하지않는다. 다음은사람role/phase검수→새feature/head/calibration버전→독립평가순서다.
