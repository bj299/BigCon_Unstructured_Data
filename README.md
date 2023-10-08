# 2023 빅콘테스트 비정형데이터 분석 분야 <와이빅타DA팀>

## 프로젝트 소개
씨름 토너먼트 경기 영상[(위더스제약 2023 민속씨름 보은장사씨름대회 금강장사결정전)](https://www.kaggle.com/t/9eb8d80301bc4ae7a9ae1568c452b1d0)과 씨름 아카이브 센터의 [경기결과 데이터](https://kpso.co.kr/ksa/Schedule/GameScheduleAndResult?page_no=1&tab=all&season_id=2023&comp_id=25&section_cd=0&gender_cd=28&weight_cd=13&t_id=0) 및 [데이터필름센터](https://kpso.co.kr/ksa/Museum/DataFilm)를 활용하여 자동 씨름기사 생성모델과 경기승패 예측모델를 구현하는 프로젝트 입니다.


## 개발환경
`Python 3.9`이상의 버전을 활용하여 프로젝트를 진행하였습니다.

## Project Structure

```
.
├── Analysis
│   ├── AlphaPose_result_visualize.ipynb
│   ├── identify_person.py
│   └── keypoints_dict_to_array.py  
├── Crawling
│   └── 씨름아카이브_크롤링.ipynb
├── Data
│   ├── Crawling_result_Data
│   |   ├── 금강장사경기_final.csv
│   |   └── 금강장사경기_문자중계.csv
│   ├── Creating_Article_Model_Data
│   |   └── Interview_And_Article_Data.zip
│   └── Win_prediction_Model_Data
│       ├── Modifieid_Json_By_Using_Identify_person_Code
│       └── Result_Json_Data_From_AlphaPose_Code
├── Model
│   ├── Creating_Article_Model
│   │   └──final_article_code_using_gui.md
│   └── Win_Prediction_Model
│       ├── LSTM_For_Win_Prediction
│       │   ├── WinPrediction 모델 최종 수정 코드.pdf
│       │   └── WinPrediction.ipynb
│       └── Pose_Estimation_AlphaPose
│           └── Body_Pose_Tracking_with_AlphaPose_v1.ipynb
├── Temporary_Files
└── README.md

```

## Crawling
* `씨름아카이브_크롤링.ipynb`코드를 활용하여 [경기결과 데이터](https://kpso.co.kr/ksa/Schedule/GameScheduleAndResult?page_no=1&tab=all&season_id=2023&comp_id=25&section_cd=0&gender_cd=28&weight_cd=13&t_id=0)를 크롤링 하여 기사생성 데이터에 활용하였습니다.
* `Data` -> `Crawling_Result_Data`폴더 안에 있는 csv파일들은 crawling 결과데이터 및 이를 수정한 데이터 입니다. 

## Analysis
* `Body_Pose_Tracking_with_AlphaPose_v1.ipynb` 코드를 활용하여 [데이터필름센터](https://kpso.co.kr/ksa/Museum/DataFilm)의 기술(손기술, 다리기술, 허리기술, 혼합기술) 별 영상데이터 40개를 Pose Estimation으로 분석하였습니다. Pose Estimation 결과 데이터는 이미지 프레임 별 key points 좌표(x, y)값을 기록한 Result_Json_Data_From_AlphaPose_Code 폴더 내 json 파일들입니다. Json 파일은 [COCO Dataset Annotation](https://github.com/MVIG-SJTU/AlphaPose/blob/master/docs/output.md)과 같은 형식입니다.
* Pose Estimation 결과 나온 json 데이터를 `identify_person.py`와 `keypoints_dict_to_array.py` 코드를 활용하여 심판 움직임 keypoint 좌표를 제거하고 이를 Model에 활용하기 위해 `np.array` 형태로 변환했습니다.
* 코드를 활용하여 수정한 json 데이터에 경기 승자가 누구인지 Labeling 하기 위해 `AlphaPose_result_visualize.ipynb` 코드를 활용하여 keypoint 좌표를 시각화한 결과와 영상속 선수를 매칭하였습니다.

## Modeling
* Anlaysis를 통해 Labeling 한 데이터를 LSTM(Long-Short Term Memory) Model의 학습데이터로 활용하였습니다. 학습 결과 Validation Data에 대하여 Accuracy 83%의 성능을 나타냈고, 학습된 LSTM Model에 [씨름 토너먼트 경기 영상](https://www.kaggle.com/t/9eb8d80301bc4ae7a9ae1568c452b1d0)을 테스트 데이터로 활용하여 씨름 경기의 승패를 예측한 결과 Accuracy 50% 성능을 나타냈습니다. 
* 금강장사결정전 우승자 인터뷰 영상을 Naver CLOVA STT(Speech To Text) API를 활용하여 Text data로 전환 후 Naver Summarization API를 통해 요약한 데이터를 얻었습니다. 그리고 Crawling한 씨름 데이터를 활용하여 기사 형태의 문장을 생성하도록 한 뒤, 해당 코드들과 GUI(Graphic User Interface) 구현 코드 `final_article_code_using_gui.md` 를 통합하여 자동 씨름 기사 생성모델을 완성했습니다.
