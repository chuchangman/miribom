### v1 - refrigerator / washing_machine 2-class 1차 실험

- 한 일:
  - `refrigerator`, `washing_machine` 2개 클래스로 EfficientNetV2-S 전이학습을 진행했다.
  - `04_split_dataset.ipynb`로 train/valid/test를 분리하고, `05_train_efficientnetv2.ipynb`에서 학습했다.
  - test set 예측 결과를 저장하고 오답/low confidence 이미지를 분석했다.

- 선택한 방식:
  - 데이터 분할과 학습 노트북을 분리했다.
  - pretrained EfficientNetV2-S를 사용했다.
  - 먼저 backbone을 freeze하고 classifier head만 학습한 뒤, 일부 layer를 unfreeze해 fine-tuning했다.

- 선택 이유:
  - 데이터 수가 적어서 처음부터 전체 모델을 학습하면 과적합 위험이 크기 때문이다.
  - split을 학습 노트북과 분리해야 실험을 반복해도 같은 train/valid/test 기준으로 비교할 수 있기 때문이다.
  - EfficientNetV2-S는 작은 데이터셋에서 전이학습 실험을 빠르게 돌리기 적절하다고 판단했다.

- 결과:
  - test accuracy: 97.3% (36/37)
  - 오답 1건: `refrigerator → washing_machine`
  - 오답은 소형 원도어 냉장고처럼 보이는 이미지였고, 냉장고 내부에서도 외형 다양성이 있다는 점을 확인했다.

- 다음 작업:
  - 서비스 기준에 맞게 `washing_machine` 라벨을 `washer_dryer`로 변경한다.
  - 세탁기, 건조기, 세탁건조 일체형을 같은 세부 라벨로 묶고, 서비스에서는 `세탁·건조`로 매핑한다.

### v2 Phase 1 - 라벨명 정리 및 재학습

- 한 일:
  - 기존 `washing_machine` 라벨을 `washer_dryer`로 변경했다.
  - `refrigerator / washer_dryer` 2개 클래스로 다시 split 후 재학습했다.
  - 서비스 대분류 평가를 위해 `SERVICE_LABEL_MAP`을 추가했다.

- 선택한 방식:
  - 기존 checkpoint를 그대로 쓰지 않고 재학습했다.
  - `washer_dryer`는 세탁기, 건조기, 세탁건조 일체형을 포함하는 라벨로 정의했다.
  - `wash_tower`는 아직 수집하지 않고 Phase 2에서 별도 세부 라벨로 추가하기로 했다.

- 선택 이유:
  - 서비스에서는 세탁기와 건조기를 모두 `세탁·건조`로 처리하기 때문이다.
  - checkpoint, CSV, confusion matrix의 라벨명을 현재 기준과 맞추기 위해 재학습했다.
  - `wash_tower`는 상하 결합형이라 외형이 다르지만, 서비스에서는 `washer_dryer`와 같은 `세탁·건조`로 처리하면 되기 때문이다.

- 결과:
  - test accuracy: 97.5% (39/40)
  - 오답 1건: `washer_dryer → refrigerator`
  - 오답 이미지는 제품 전체가 보이지 않는 partial crop이었다.
  - 모델 구조 문제라기보다 bbox crop 품질과 데이터 정제 문제로 판단했다.

- 다음 작업:
  - `wash_tower` 추가 전에 `washer_dryer` 데이터의 불량 crop을 먼저 정제한다.
  - 제품 일부만 보이는 이미지, 내부 부품 이미지, 식별 불가 이미지를 rejected 처리한다.
  - 통돌이세탁기와 건조기 단독 이미지를 보강한다.

  ### v2 Phase 1-1 - washer_dryer 데이터 정제

- 한 일:
  - `washer_dryer` 이미지 검토용 노트북과 contact sheet를 만들었다.
  - 오답 원인이 된 partial crop 이미지와 내부 부품 이미지를 학습 데이터에서 제외했다.
  - 제외 이미지는 삭제하지 않고 `data/rejected/`로 이동하고, `rejected_images.csv`에 기록했다.

- 선택한 방식:
  - 제거 사유를 `partial_crop`, `internal_part`, `unidentifiable`로 구분했다.
  - 판단이 애매한 이미지는 일단 유지했다.

- 선택 이유:
  - 이전 실험의 오답이 모델 문제보다 bbox crop 품질 문제에 가까웠기 때문이다.
  - 제품 전체 외관이 보이지 않는 이미지는 실제 서비스 입력 조건과 맞지 않는다.
  - rejected 로그를 남겨야 데이터 정제 기준을 추적할 수 있다.

- 결과:
  - `partial_crop` 1장 제거
  - `internal_part` 1장 제거
  - 현재 데이터 수: `refrigerator 172장`, `washer_dryer 223장`

- 다음 작업:
  - 추가 제거 대상이 있는지 contact sheet로 확인한다.
  - 정제 완료 후 split을 다시 생성하고 재학습한다.

  ### v2 Phase 1-2 - washer_dryer 추가 수집 파이프라인 구성

- 한 일:
  - `washer_dryer` 보강 수집을 위해 `07_collect_washer_dryer.ipynb`를 생성했다.
  - 수집 이미지를 바로 학습 데이터에 넣지 않고 `data/staging/washer_dryer/`에 먼저 저장하도록 했다.
  - 검수 후 승인한 이미지만 `processed`로 이동하기 위해 `08_approve_staging.ipynb`를 생성했다.
  - staging 이미지 검토용 HTML contact sheet를 생성하도록 구성했다.

- 선택한 방식:
  - 수집 단계와 승인 단계를 분리했다.
  - 네이버쇼핑 API로 수집한 이미지는 먼저 staging에 저장한다.
  - 사람이 확인한 이미지 경로만 `APPROVED` 리스트에 넣고 processed로 이동한다.
  - processed 이동 전 phash 중복 검사를 수행한다.

- 선택 이유:
  - 네이버쇼핑 이미지에는 상세페이지 이미지, 내부 부품, 로고/텍스트 이미지, 제품 일부만 나온 이미지가 섞일 수 있기 때문이다.
  - 바로 processed에 넣으면 학습 데이터 품질이 떨어지고 오답 원인을 추적하기 어려워진다.
  - staging과 approval 단계를 분리하면 데이터 품질을 사람이 통제할 수 있다.

- 결과:
  - `07_collect_washer_dryer.ipynb` 생성
  - `08_approve_staging.ipynb` 생성
  - 수집 → 검수 → 승인 → processed 이동 흐름을 만들었다.

- 다음 작업:
  - `07_collect_washer_dryer.ipynb`를 실행해 staging 이미지를 수집한다.
  - `washer_dryer_staging_review.html`에서 이미지를 검수한다.
  - 승인할 이미지만 `APPROVED`에 추가한다.
  - 승인 후 `04_split_dataset.ipynb`, `05_train_efficientnetv2.ipynb`를 다시 실행한다.

### v2 Phase 1-3 - washer_dryer staging 검수 및 수동 삭제 처리

- 한 일:
  - `washer_dryer` 보강 후보 360장을 staging에 수집했다.
  - 검수 중 부적절한 이미지 61장을 staging에서 수동 삭제했다.
  - 수동 삭제된 파일을 metadata에서 `deleted` 상태로 갱신했다.
  - `08_approve_staging.ipynb`가 수동 삭제된 파일을 감지하고 오류 없이 처리하도록 수정했다.

- 선택한 방식:
  - staging은 검수용 임시 공간이므로, 부적절한 이미지는 직접 삭제할 수 있게 했다.
  - metadata에 있지만 실제 파일이 없는 경우를 `deleted` 또는 `missing` 상태로 구분한다.
  - 실제 존재하는 승인 파일만 `processed/washer_dryer`로 이동한다.

- 선택 이유:
  - 네이버쇼핑 이미지에는 제품 일부, 광고 이미지, 부품 이미지 등이 섞일 수 있다.
  - 수동 삭제 후 metadata와 실제 파일 상태가 달라져도 승인 파이프라인이 멈추지 않아야 한다.
  - processed에 넣기 전 사람이 검수해야 학습 데이터 품질을 유지할 수 있다.

- 결과:
  - 전체 후보: 360장
  - 수동 삭제: 61장
  - staging 잔여: 299장
  - metadata 상태: `staged 299건`, `deleted 61건`

- 다음 작업:
  - 남은 299장 중 학습에 사용할 이미지를 `APPROVED` 목록에 추가한다.
  - 승인 후 phash 중복 검사를 거쳐 `processed/washer_dryer`로 이동한다.
  - 이후 split 재생성과 재학습을 진행한다.

  ### v2 Phase 1-4 - washer_dryer 승인 이미지 반영

- 한 일:
  - staging에 남아 있던 `washer_dryer` 후보 이미지를 검수 후 승인 처리했다.
  - 승인된 이미지만 `data/processed/washer_dryer/`로 이동했다.
  - 이동 전 phash 중복 검사를 수행했다.
  - 중복 이미지는 processed에 넣지 않고 `skipped_duplicate` 상태로 기록했다.

- 선택한 방식:
  - 사람이 검수한 이미지 중 승인된 것만 processed에 반영했다.
  - 기존 processed 이미지 및 이번 배치 내부 이미지와 phash 중복 검사를 수행했다.
  - 중복 이미지는 학습 데이터에 추가하지 않았다.

- 선택 이유:
  - 네이버쇼핑 이미지는 같은 제품 이미지가 여러 검색어에 중복 노출될 수 있기 때문이다.
  - 중복 이미지가 많으면 모델이 특정 상품 사진을 외울 수 있고, train/valid/test 누수 위험도 커진다.
  - 데이터 수를 무작정 늘리는 것보다 중복을 줄이고 품질을 유지하는 것이 더 중요하다고 판단했다.

- 결과:
  - 승인 이동: 124장
  - 중복 제외: 175장
  - missing: 0장
  - `washer_dryer` 최종 이미지 수: 347장
  - metadata 상태: `approved 124건`, `skipped_duplicate 175건`, `deleted 61건`

- 다음 작업:
  - `04_split_dataset.ipynb`를 다시 실행해 split을 재생성한다.
  - `05_train_efficientnetv2.ipynb`를 다시 실행해 재학습한다.
  - 재학습 후 오답과 low confidence 이미지를 다시 분석한다.

  ### v2 Phase 1-5 - washer_dryer 보강 후 재학습

- 한 일:
  - `washer_dryer` 보강 이미지 124장을 processed에 추가했다.
  - split을 다시 생성하고 EfficientNetV2-S를 재학습했다.
  - 오답과 low confidence 샘플을 다시 분석했다.

- 선택한 방식:
  - 승인된 이미지만 processed에 반영했다.
  - phash 중복 이미지는 학습 데이터에 넣지 않았다.
  - 기존과 동일하게 `refrigerator / washer_dryer` 2-class로 학습했다.

- 선택 이유:
  - 이전 오답 원인이 `washer_dryer`의 외형 다양성 부족과 partial crop 문제에 가까웠기 때문이다.
  - 특히 통돌이세탁기와 건조기 단독 이미지를 보강할 필요가 있었다.

- 결과:
  - 전체 데이터 수: 519장
  - `refrigerator`: 172장
  - `washer_dryer`: 347장
  - test accuracy: 96.2% (50/52)
  - `washer_dryer` per-class accuracy: 100.0% (35/35)
  - `refrigerator` per-class accuracy: 88.2% (15/17)

- 분석:
  - 이전에 발생했던 `washer_dryer → refrigerator` 오답은 사라졌다.
  - 대신 `refrigerator → washer_dryer` 오답이 2건 발생했다.
  - washer_dryer 보강 효과는 있었지만, 데이터 비율이 `washer_dryer` 쪽으로 치우치면서 냉장고 오답이 늘어난 것으로 판단했다.
  - 오답 이미지는 모두 냉장고였으며, 특히 소형/원도어 냉장고가 washer_dryer와 혼동될 수 있음을 확인했다.

- 다음 작업:
  - cross-split phash 유사 중복 15쌍을 확인한다.
  - `refrigerator` 데이터를 보강한다.
  - 특히 소형 냉장고, 원도어 냉장고, 미니 냉장고 이미지를 우선 수집한다.

### v2 Phase 1-6 - cross-split 중복 정리 및 refrigerator 보강 계획

- 한 일:
  - washer_dryer 보강 후 재학습 결과를 분석했다.
  - split 재생성 과정에서 발견된 cross-split phash 유사 중복 15쌍을 확인했다.
  - phash distance 0인 동일 이미지 후보 4쌍을 정리했다.
  - 동일 이미지 중 한 장씩을 `data/processed/`에서 제외하고 `data/rejected/duplicate/`로 이동했다.
  - 이동 내역은 `data/metadata/rejected_images.csv`에 기록했다.
  - 재학습 후 발생한 `refrigerator → washer_dryer` 오답 2건을 분석했다.
  - refrigerator 보강용 검색어를 정리하고 `09_collect_refrigerator.ipynb`를 생성했다.

- 선택한 방식:
  - cross-split 유사 중복 전체를 바로 삭제하지 않고, phash distance 0인 동일 이미지부터 우선 정리했다.
  - 동일 이미지 쌍에서는 한 장만 유지하고, 나머지는 삭제하지 않고 `data/rejected/duplicate/{class}/`로 이동했다.
  - `data/raw/`는 수정하지 않았다.
  - refrigerator 보강은 전체 냉장고 이미지를 무작정 늘리는 것이 아니라, 소형/단문/미니 냉장고를 우선 수집하는 방향으로 정했다.
  - 수집 이미지는 기존 washer_dryer와 동일하게 staging에서 검수한 뒤 approved 이미지만 processed에 반영하기로 했다.

- 선택 이유:
  - 동일 이미지가 train과 valid/test에 동시에 있으면 평가 정확도가 실제보다 높게 나올 수 있기 때문이다.
  - 단순 삭제가 아니라 rejected로 이동해야 복구와 추적이 가능하기 때문이다.
  - `04_split_dataset.ipynb`는 `data/processed/{class}/`를 기준으로 split을 생성하므로, 중복 파일을 processed에서 제외해야 split 재생성 시 같은 문제가 재발하지 않는다.
  - 이번 오답 2건은 모두 `refrigerator → washer_dryer` 방향이었다.
  - 특히 소형/단문 냉장고가 통돌이세탁기나 건조기와 비슷한 직사각형 외형을 가져 혼동될 가능성이 있었다.
  - 현재 데이터 수가 `refrigerator 171장`, `washer_dryer 344장`으로 불균형하기 때문에 refrigerator 보강이 필요하다고 판단했다.

- 결과:
  - cross-split phash 유사 중복 후보: 15쌍
  - 클래스 간 leakage: 없음
  - phash distance 0 identical 후보: 4쌍
  - 중복 파일 4장 rejected 이동
    - `refrigerator`: 1장 제외
    - `washer_dryer`: 3장 제외
  - `rejected_images.csv`에 `duplicate_cross_split` 사유로 4건 기록
  - processed 최종 수:
    - `refrigerator`: 171장
    - `washer_dryer`: 344장
    - 합계: 515장
  - 현재 split 총수도 515장으로 processed와 일치
  - 04 재실행 시 동일 중복이 다시 들어오지 않도록 처리 완료
  - `09_collect_refrigerator.ipynb` 생성 완료

- 분석:
  - washer_dryer 보강은 효과가 있었다. 이전에 발생했던 `washer_dryer → refrigerator` 오답은 사라졌다.
  - 대신 데이터 비율이 washer_dryer 쪽으로 커지면서, 소형/단문 냉장고가 washer_dryer로 분류되는 문제가 나타났다.
  - 따라서 다음 병목은 모델 구조가 아니라 refrigerator 데이터의 양과 다양성 부족이라고 판단했다.
  - cross-split 동일 이미지는 processed에서 제외했기 때문에, 이후 split을 다시 생성해도 동일 이미지가 train/valid/test에 나뉘어 들어갈 가능성을 줄였다.

- 다음 작업:
  - `09_collect_refrigerator.ipynb`를 실행해 refrigerator 후보 이미지를 수집한다.
  - 우선 수집 대상은 단문냉장고, 소형냉장고, 원룸냉장고, 미니냉장고다.
  - 수집 이미지는 staging에서 검수 후 approved 이미지만 processed에 반영한다.
  - refrigerator를 250~300장 수준까지 보강한 뒤 split 재생성과 재학습을 진행한다.

  ### v2 Phase 1-7 - refrigerator 데이터 보강 및 재학습

- 한 일:
  - `refrigerator → washer_dryer` 오답을 줄이기 위해 refrigerator 데이터를 보강했다.
  - 소형/단문/미니 냉장고 중심으로 네이버쇼핑 이미지를 수집했다.
  - 수집 이미지는 staging에서 검수한 뒤 approved 이미지만 `processed/refrigerator`에 반영했다.
  - phash 중복 이미지는 학습 데이터에 추가하지 않았다.
  - 이후 split을 다시 생성하고 EfficientNetV2-S를 재학습했다.

- 선택한 방식:
  - 수집 이미지를 바로 processed에 넣지 않고 staging → 검수 → 승인 흐름을 유지했다.
  - refrigerator 보강은 일반 냉장고보다 소형/단문/미니 냉장고를 우선했다.
  - 기존과 동일하게 `refrigerator / washer_dryer` 2-class 구조로 학습했다.

- 선택 이유:
  - 이전 실험에서 오답 2건이 모두 `refrigerator → washer_dryer` 방향으로 발생했다.
  - 당시 데이터 수는 `refrigerator 171장`, `washer_dryer 344장`으로 불균형했다.
  - 특히 소형/단문 냉장고는 건조기나 통돌이세탁기와 비슷한 직사각형 외형을 가져 혼동 가능성이 있었다.
  - 따라서 모델 구조 변경보다 refrigerator 데이터의 양과 다양성 보강이 먼저라고 판단했다.

- 결과:
  - refrigerator 후보 이미지 480장을 수집했다.
  - 검수 후 80장을 `processed/refrigerator`에 추가했다.
  - phash 중복 187장은 제외했다.
  - 최종 processed 수:
    - `refrigerator`: 251장
    - `washer_dryer`: 344장
    - 전체: 595장
  - split 결과:
    - train: 476장
    - valid: 59장
    - test: 60장
  - cross-split distance=0 중복은 없었다.
  - test accuracy: 100.0% (60/60)
  - `refrigerator` per-class accuracy: 100.0% (25/25)
  - `washer_dryer` per-class accuracy: 100.0% (35/35)
  - 오답: 0건
  - confidence < 0.80 정답: 0건

- 분석:
  - refrigerator 보강 전에는 `refrigerator → washer_dryer` 오답이 2건 발생했지만, 보강 후 해당 오답이 사라졌다.
  - washer_dryer 성능도 100%로 유지되었기 때문에, refrigerator 보강이 기존 washer_dryer 분류 성능을 해치지 않았다.
  - 현재 데이터셋 기준으로는 `refrigerator / washer_dryer` 2-class 분류가 안정화됐다고 판단했다.
  - 다만 test set이 60장이고, 실제 사용자 촬영 이미지는 아직 별도로 검증하지 않았기 때문에 실서비스 일반화 성능으로 단정하지 않는다.

- 다음 작업:
  - Phase 1은 완료로 보고, 이후 `wash_tower` 클래스를 추가하는 Phase 2를 진행할 수 있다.
  - 또는 실제 사용자 촬영 환경을 가정한 external test를 먼저 구성해 현재 모델의 일반화 성능을 확인할 수 있다.

### v2 Phase 2 - wash_tower 추가 및 3-class 재학습

- 한 일:
  - `wash_tower` 클래스를 추가해 `refrigerator / washer_dryer / wash_tower` 3-class 구조로 확장했다.
  - 네이버쇼핑 API로 wash_tower 후보 이미지를 수집하고, 검수 후 approved 이미지만 `processed/wash_tower`에 반영했다.
  - 수집 과정에서 발생한 phash 중복과 cross-class label noise를 정리했다.
  - `PROJECT_LABELS`를 3-class 기준으로 변경한 뒤 split을 다시 생성하고 EfficientNetV2-S를 재학습했다.
  - 세부 라벨 기준 평가와 서비스 대분류 기준 평가를 분리해서 확인했다.

- 선택한 방식:
  - `wash_tower`는 일반 세탁기/건조기와 외형이 다르기 때문에 별도 세부 라벨로 분리했다.
  - 하지만 서비스에서는 `washer_dryer`와 `wash_tower`를 모두 `washing_drying`으로 매핑했다.
  - 수집 이미지는 바로 processed에 넣지 않고 staging에서 검수한 뒤 approved 이미지만 반영했다.
  - 같은 이미지가 `washer_dryer`와 `wash_tower` 양쪽에 들어간 cross-class 중복은 `rejected/duplicate/`로 이동했다.

- 선택 이유:
  - 워시타워는 상하 결합형 구조라 일반 세탁기/건조기와 구분되는 외형을 가진다.
  - 다만 사용자에게 필요한 서비스 대분류는 둘 다 `세탁·건조`이므로, 세부 라벨과 서비스 라벨을 분리하는 구조가 적절하다고 판단했다.
  - 같은 이미지가 서로 다른 라벨에 존재하면 모델이 같은 이미지를 두 개의 정답으로 학습하게 되므로, cross-class label noise를 제거했다.
  - 서비스에서는 `refrigerator`와 `washing_drying`의 경계가 가장 중요하기 때문에, 세부 라벨 정확도와 서비스 대분류 정확도를 따로 확인했다.

- 결과:
  - 최종 processed 수:
    - `refrigerator`: 251장
    - `wash_tower`: 288장
    - `washer_dryer`: 342장
    - 합계: 881장
  - split 결과:
    - train: 704장
    - valid: 88장
    - test: 89장
  - cross-class label noise:
    - 4건 제거
    - 제거 후 cross-class distance=0 중복 0건
  - 재학습 결과:
    - Phase 2 best val_loss: 0.1029
    - Phase 2 best val_acc: 97.7%
  - test 결과:
    - 세부 라벨 기준 accuracy: 94.4% (84/89)
    - 서비스 대분류 기준 accuracy: 100.0% (89/89)
  - 클래스별 정확도:
    - `refrigerator`: 100.0% (25/25)
    - `wash_tower`: 93.1% (27/29)
    - `washer_dryer`: 91.4% (32/35)

- 분석:
  - 세부 라벨 기준 오답 5건은 모두 `wash_tower ↔ washer_dryer` 사이에서 발생했다.
  - 이 5건은 서비스 기준에서는 모두 `washing_drying`으로 매핑되므로 실질 오답은 아니다.
  - `refrigerator ↔ washing_drying` 경계에서는 오답이 발생하지 않았다.
  - 따라서 현재 데이터셋 기준으로는 서비스 대분류 분류 목표를 달성한 것으로 판단했다.
  - 다만 test set은 89장이고, 실제 사용자 촬영 이미지는 아직 별도 검증하지 않았으므로 실서비스 일반화 성능으로 단정하지 않는다.

- 다음 작업:
  - 현재 모델을 Phase 2 기준 모델로 저장한다.
  - 실제 사용자 촬영 환경을 가정한 external test set을 구성한다.
  - 어두운 조명, 저화질, 배경이 있는 이미지, 제품 일부가 잘린 이미지를 따로 테스트한다.
  - 이후 결과에 따라 데이터 보강 또는 촬영 가이드 문구를 추가한다.

### v2 Phase 2-1 - external test 검증

- 한 일:
  - Phase 2 기준 모델을 external test 이미지 160장으로 평가했다.
  - external test는 `refrigerator / washing_drying` 서비스 대분류 기준으로 평가했다.
  - 오답 17건을 직접 확인해 원인을 분류했다.
  - 라벨 오류와 서비스 범위 밖 이미지는 `external_test_rejected`로 이동하고, 정제된 external test 기준으로 다시 평가했다.

- 선택한 방식:
  - external test 이미지는 학습 데이터와 분리해서 관리했다.
  - 오답은 `label_error`, `out_of_scope`, `ambiguous_product`, `model_error`, `bad_input`으로 나누어 분석했다.
  - 라벨이 잘못된 이미지와 서비스 범위 밖 이미지는 삭제하지 않고 `data/external_test_rejected/`로 이동했다.
  - 정제 후에도 ambiguous product는 유지해서 경계 케이스로 확인했다.

- 선택 이유:
  - 처음 external test 정확도 하락이 모델 문제인지, 수집 데이터 문제인지 구분해야 했기 때문이다.
  - 실제로 이미지 검색 결과에는 다른 가전 이미지나 서비스 범위 밖 제품이 섞여 있었다.
  - 잘못된 이미지를 그대로 평가하면 모델 성능이 아니라 테스트셋 품질 문제를 측정하게 된다.

- 결과:
  - 정제 전 external test:
    - 전체: 160장
    - 정확도: 89.4% (143/160)
    - `refrigerator`: 91.2% (73/80)
    - `washing_drying`: 87.5% (70/80)

  - 오답 원인:
    - `label_error`: 13건
    - `out_of_scope`: 3건
    - `ambiguous_product`: 1건
    - `model_error`: 0건
    - `bad_input`: 0건

  - 정제 후 external test:
    - 전체: 144장
    - 정확도: 99.3% (143/144)
    - `refrigerator`: 98.6% (73/74)
    - `washing_drying`: 100.0% (70/70)

- 분석:
  - 정제 전 정확도 하락의 주원인은 모델이 아니라 external test 수집 노이즈였다.
  - `model_error`는 발견되지 않았다.
  - 남은 오답 1건은 `ambiguous_product`로, 제품 자체가 냉장고와 세탁·건조 경계에 가까운 케이스였다.
  - 현재 모델은 내부 test와 정제된 external test 기준에서 서비스 대분류 분류가 안정적으로 동작한다고 판단했다.

- 다음 작업:
  - 재학습은 하지 않는다.
  - 이후 external test를 추가 수집할 때는 이미지 검색 결과를 그대로 쓰지 않고 검수 단계를 유지한다.
  - 경계 케이스는 라벨 정책으로 관리한다.
  - 실제 사용자 업로드 이미지가 쌓이면 오답을 별도로 수집해 추가 검증한다.

### v3 Phase 3 - 18-class 확장 학습 (baseline)

- 한 일:
  - `refrigerator / washer_dryer / wash_tower` 3-class 구조에서 15개 클래스를 추가해 18-class 구조로 확장했다.
  - 추가 클래스: `rice_cooker`, `microwave`, `air_fryer`, `electric_kettle`, `vacuum_cleaner`, `robot_vacuum`, `fan`, `air_conditioner`, `heater`, `dehumidifier`, `humidifier`, `monitor`, `keyboard`, `mouse`, `beam_projector`
  - 네이버쇼핑 API로 클래스별 이미지를 수집하고 Gemini API로 자동 검수한 뒤 처리 기준에 맞는 이미지만 processed에 반영했다.
  - 수집 → 검수 → 승인 파이프라인을 스크립트화했다 (`run_collection.py`, `approve_staging_gemini.py`).
  - `run_split.py`로 4,444장을 stratified split하고 EfficientNetV2-S를 Phase 1(backbone freeze) → Phase 2(features.6/7/classifier unfreeze) 순서로 학습했다.
  - `SERVICE_LABEL_MAP`을 18-class 기준으로 확장해 세부 라벨 8개 서비스 카테고리로 매핑했다.

- 선택한 방식:
  - 기존 3-class checkpoint를 재사용하지 않고 18-class를 처음부터 학습했다.
  - WeightedRandomSampler로 클래스 불균형을 보정했다.
  - ReduceLROnPlateau(patience=3, factor=0.5)로 학습률을 자동 조정했다.
  - 크래시 복구를 위해 매 에폭 `last.pth`를 별도 저장했다.

- 결과:
  - 전체 processed: 4,444장
  - split: train 3,551 / valid 444 / test 449
  - baseline best: epoch 7, val_acc 94.36% (`phase3_18class_resumed_best.pth`)
  - test 세부 라벨 acc: **92.6%** (415/449)
  - test 서비스 acc: **95.8%** (430/449)

- 분석:
  - `beam_projector → heater`, `humidifier → electric_kettle`, `heater → beam_projector` 방향 오답이 주요 병목이었다.
  - heater 데이터가 기본 형태 위주로만 구성되어 다이슨 타워형 같은 비정형 히터를 beam_projector로 혼동하는 경향이 있었다.
  - humidifier는 원통형 제품이 전기포트·밥솥과 외형 유사성이 높아 서비스 오답이 발생했다.

- 다음 작업:
  - beam_projector 오염 이미지 15장을 제거한다.
  - humidifier/heater 형태 다양성 보강을 위해 신규 검색어로 추가 수집 후 Gemini 검수를 진행한다.
  - 보강 후 split 재생성 및 Phase 2 fine-tuning을 재개한다.

### v3 Phase 3-1 - 데이터 정제 및 보강 (beam_projector / humidifier / heater)

- 한 일:
  - `beam_projector` 학습 데이터에서 오분류 원인 이미지 15장을 제거했다.
    - `wrong_product` 7장, `ambiguous_product` 6장, `bad_input` 1장, `text_image` 1장
    - 제거 이미지는 `data/rejected/beam_projector/{reason}/`으로 이동하고 로그를 기록했다.
  - `humidifier` 신규 검색어 4개 추가: 가열식/타워형/원통형/대용량 가습기.
  - `heater` 신규 검색어 4개 추가: 타워형/다이슨/소형 전기/라디에이터 히터.
  - 기존 `*_제품사진` 쿼리 9개 클래스 전면 제거 (이미지 품질 불량 확인).
  - 추가 수집한 humidifier/heater 이미지를 Gemini API로 검수해 OK 이미지만 processed에 반영했다.
    - humidifier: OK 13장 추가 (`naver_0323` ~ `naver_0335`)
    - heater: OK 77장 추가 (`naver_0181` ~ `naver_0257`)
  - `run_split.py`로 split을 재생성했다.

- 결과:
  - beam_projector: 305장 → 290장 (-15)
  - humidifier: 323장 → 336장 (+13)
  - heater: 181장 → 258장 (+77)
  - 전체 processed: 4,701장
  - split 재생성: train 3,754 / valid 470 / test 477

- 다음 작업:
  - 보강된 split 기준으로 Phase 2 fine-tuning을 재개한다.
  - 기존 baseline checkpoint(`phase3_18class_resumed_best.pth`)에서 시작한다.

### v3 Phase 3-2 Refined - 18-class Fine-tuning 재개 (최종 서비스 모델)

- 한 일:
  - beam_projector 정제 + humidifier/heater 보강 후 새로운 split(4,701장)에서 Phase 2 fine-tuning을 재개했다.
  - 입력 checkpoint: `phase3_18class_resumed_best.pth` (epoch 7, val_acc 94.36%)
  - `features.6`, `features.7`, `classifier` 레이어 unfreeze, Adam lr=1e-4 fresh 적용.
  - 10 에폭 학습, 매 에폭 `phase3_18class_refined_last.pth` 저장, val_loss 개선 시 `phase3_18class_refined_best.pth` 갱신.
  - 학습 완료 후 test 평가 및 baseline 비교 분석을 수행했다.
  - 최종 모델을 `phase3_18class_service_best.pth`로 복사해 API/CLI 기준 checkpoint로 고정했다.

- 결과:
  - best epoch: 8 / val_loss 0.1303 / val_acc 95.96%
  - **test 세부 라벨 acc: 94.8%** (452/477) — baseline 대비 +2.2%
  - **test 서비스 acc: 97.7%** (466/477) — baseline 대비 +1.9%
  - low confidence (< 0.70): 22건 → 16건 (-6건)

  | 클래스 | baseline | refined | 변화 |
  |---|---|---|---|
  | humidifier | 75.8% | **94.1%** | +18.4% |
  | heater | 84.2% | **100.0%** | +15.8% |
  | beam_projector | 96.8% | **100.0%** | +3.2% |
  | dehumidifier | 91.3% | 82.6% | -8.7% |
  | wash_tower | 85.7% | 81.0% | -4.8% |

- 분석:
  - humidifier/heater 보강 수집과 beam_projector 오염 이미지 제거 효과가 세부 라벨 정확도에 직접적으로 반영됐다.
  - `wash_tower ↔ washer_dryer` 혼동 9건이 가장 큰 오답 패턴이나, 서비스 기준으로는 같은 `washing_drying`이므로 실질 오답이 아니다.
  - `dehumidifier` 세부 정확도 하락(-8.7%)은 heater/beam_projector와의 혼동 패턴이나, 서비스 오답은 3건으로 제한적이다.
  - 서비스 acc 97.7%는 실서비스 기준 충분한 수준으로 판단해 추가 학습 없이 최종 모델로 고정했다.

- 최종 체크포인트:
  - `checkpoints/phase3_18class_service_best.pth` (epoch 8, val_acc 95.96%, val_loss 0.1303, 18-class)

- 다음 작업:
  - dehumidifier 세부 정확도 보강이 필요하다면 새 검색어로 데이터를 수집하고 재학습한다.
  - 실제 사용자 업로드 이미지로 external test를 구성해 18-class 서비스 정확도를 검증한다.