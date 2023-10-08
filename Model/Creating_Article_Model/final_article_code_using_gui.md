import tkinter as tk
import pandas as pd
import re
from tkinter import Scrollbar, Text, Frame, Button, Label, StringVar, OptionMenu
import requests
import json


## 사용할 데이터 (크롤링을 통해 얻은 csv)
df1 = pd.read_csv('final.csv', index_col=0)
df2 = pd.read_csv('text.csv', index_col=0)
df_ = pd.concat([df2[['contest_name', 'play_date', 'event', 'play_category', 'winner', 'match_result']], df1], axis=1)

## 경기별 기사 생성을 위한 text 전처리
def process_text(df, selected_winner):
    def merge_sentences(text):
        # Your merge_sentences function code here
        # ...
        pattern = r"(\d+)초가 경과되었을 때 ([\w\s\(\)]+) 공격시도\. (\d+)초가 경과되었을 때 ([\w\s\(\)]+) 기술방어\."
        def change(match):
            start_time1 = match.group(1)
            action1 = match.group(2)
            action2 = match.group(4)
            merged_sentence = f" {start_time1}초가 경과되었을 때 {action1} 공격시도를 하였고 이를 {action2} 기술방어하였다."
            return merged_sentence
        
        modified_text = re.sub(pattern, change, text)
        return modified_text
    
    article_text = ""

    for index, row in df.iterrows():
        winner = row['winner']
        
        if winner == selected_winner:
            contest_name = row['contest_name']
            play_date = row['play_date']
            
            play_level = row['play_level']
            player_name_A = row['player_name_A']
            player_name_B = row['player_name_B']
            team_name_A = row['team_name_A']
            team_name_B = row['team_name_B']
            birth_date_A = row['birth_date_A']
            birth_date_B = row['birth_date_B']
            weight_A = row['weight_A']
            height_A = row['height_A']
            weight_B = row['weight_B']
            height_B = row['height_B']
            specialized_technique_A = row['specialized_technique_A']
            specialized_technique_B = row['specialized_technique_B']
            pro_debut_year_A = row['pro_debut_year_A']
            pro_debut_year_B = row['pro_debut_year_B']
            text = row['text_relay']
            # 텍스트 데이터를 줄 단위로 분할
            lines = text.strip().split('\n')

            # DataFrame을 만들기 위한 빈 리스트 초기화
            data = []
            round_number = 0
            time = 0

            # 주어진 텍스트를 분석하여 데이터 추출
            for line in lines:
                if line.endswith("라운드 경기시작"):
                    round_number += 1
                    time = 0
                elif line.endswith("초"):
                    time = int(line[:-1])
                else:
                    data.append([round_number, time, line])

            # DataFrame 생성
            new_df = pd.DataFrame(data, columns=['round', 'second', 'detail'])
            new_df['detail'] = new_df['detail'].apply(lambda x:str(x).replace('홍 ', '홍샅바 ') if str(x).startswith('홍 ') else (str(x).replace('청 ', '청샅바 ') if str(x).startswith('청 ') else (str(x))))
            new_df = new_df[(new_df['detail'] != '청샅바 {}'.format(player_name_A)) & (new_df['detail'] != '홍샅바 {}'.format(player_name_B))]

            article = f'''{play_date}일 열린 {contest_name} {play_level}에서 {player_name_A}({team_name_A}) 선수와 {player_name_B}({team_name_B}) 선수가 맞붙었다. 청샅바인 {player_name_A} 선수는 {birth_date_A} 출생으로 신장은 {height_A} 이며 체중은 {weight_A}이다. {pro_debut_year_A} 씨름대회에 데뷔하였고 {specialized_technique_A} 기술이 주특기이다. 홍샅바인 {player_name_B} 선수는 {birth_date_B} 출생으로 신장은 {height_B}이며 체중은 {weight_B}이다. {pro_debut_year_B} 씨름대회에 데뷔하였고 {specialized_technique_B} 기술이 주특기이다. 경기는 {winner[-3:]} 선수가 주도하며 흘러갔다.\n\n'''


            ## 라운드별 조건
            max_round = new_df['round'].max()
            if max_round == 1:
                round1 = new_df[new_df['round'] == 1][['second' ,'detail']].values
                sentence1 = ''
                for second, detail in round1:
                    sentence1 += ('{}초가 경과되었을 때 {}. '.format(60-second, detail))

                modified_sentence1 = merge_sentences(sentence1)
                
                article_text += article + ' 1라운드 시작 직후 ' + modified_sentence1+ "\n"

            elif max_round == 2:
                round1 = new_df[new_df['round'] == 1][['second' ,'detail']].values
                sentence1 = ''
                for second, detail in round1:
                    sentence1 += ('{}초가 경과되었을 때 {}. '.format(60-second, detail))

                modified_sentence1 = merge_sentences(sentence1)

                round2 = new_df[new_df['round'] == 2][['second' ,'detail']].values
                sentence2 = ''
                for second, detail in round2:
                    sentence2 += ('{}초가 경과되었을 때 {}. '.format(60-second, detail))

                modified_sentence2 = merge_sentences(sentence2)
                
                article_text += article + ' 1라운드 시작 직후 ' + modified_sentence1 + '\n\n 2라운드 시작 직후 ' + modified_sentence2 + "\n" + "\n"
            
            elif max_round == 3:
                round1 = new_df[new_df['round'] == 1][['second' ,'detail']].values
                sentence1 = ''
                for second, detail in round1:
                    sentence1 += ('{}초가 경과되었을 때 {}. '.format(60-second, detail))

                modified_sentence1 = merge_sentences(sentence1)

                round2 = new_df[new_df['round'] == 2][['second' ,'detail']].values
                sentence2 = ''
                for second, detail in round2:
                    sentence2 += ('{}초가 경과되었을 때 {}. '.format(60-second, detail))

                modified_sentence2 = merge_sentences(sentence2)

                round3 = new_df[new_df['round'] == 3][['second' ,'detail']].values
                sentence3 = ''
                for second, detail in round3:
                    sentence3 += ('{}초가 경과되었을 때 {}. '.format(60-second, detail))

                modified_sentence3 = merge_sentences(sentence3)
                
                article_text += article + ' 1라운드 시작 직후 ' + modified_sentence1 + '\n\n 2라운드 시작 직후 ' + modified_sentence2 + '\n\n 3라운드 시작 직후 ' + modified_sentence3 + "\n" + "\n"
            
            else:
                article_text += article + "\n" + "\n"

    return article_text

## 우승자 기사 생성을 위한 csv
data = pd.read_csv('text.csv')
df = pd.read_csv('final.csv')
df['contest_name'] = data['contest_name']
df['play_date'] = data['play_date']
df['play_category'] = data['play_category']
df['result'] = data['match_result']

third_name = df[df['play_level'] == '3,4위 결정전']['match_result'].tolist()[0].split()[-1]
df[df['play_level'] == '3,4위 결정전']
if(third_name == df[df['play_level'] == '3,4위 결정전']['player_name_A'].tolist()):
    third_team = df[df['play_level'] == '3,4위 결정전']['team_name_A'].tolist()[0]
else:
    third_team = df[df['play_level'] == '3,4위 결정전']['team_name_B'].tolist()[0]
    
    
# 우승자 이름
winner_name = df[df['play_level'] == '결승']['match_result'].tolist()[0].split()[-1]

# 우승자 데이터프레임
winner_df = pd.DataFrame()
winner_df = df[(df['player_name_A'] == winner_name) | (df['player_name_B'] == winner_name)].copy()

winner_df.drop(winner_df.columns[0], axis = 1, inplace = True)

winner_df.reset_index(drop = True)
winner_df['player_list'] = winner_df['player_name_A'] + " " + df['player_name_B']
winner_df['opponent_name'] = winner_df['player_list'].apply(lambda names: ' '.join([name for name in names.split() if name != winner_name]))

winner_df['profile_A'] = winner_df.apply(lambda row: [row['player_name_A'], row['team_name_A'], row['specialized_technique_A']], axis=1)
winner_df['profile_B'] = winner_df.apply(lambda row: [row['player_name_B'], row['team_name_B'], row['specialized_technique_B']], axis=1)

winner_df = winner_df[['contest_name', 'play_date', 'play_category','opponent_name', 'result', 'play_level', 'text_relay', 'profile_A', 'profile_B']].copy()

def opponent(play_level):
    opponent = []
    row =  winner_df[winner_df['play_level'] == play_level]
    player_name = row['opponent_name'].tolist()[0]
    if(row['profile_B'].tolist()[0][0] == player_name):
        opponent = row['profile_B'].tolist()[0]
    else:
        opponent = row['profile_A'].tolist()[0]
    opponent.append(row['result'].tolist()[0])
    return opponent

final_row = winner_df[winner_df['play_level'] == '결승']
winner = [winner_name]


if(winner_name == final_row['profile_A'].tolist()[0][0]):
    winner.append(final_row['profile_A'].tolist()[0][1])
    winner.append(final_row['profile_A'].tolist()[0][2])
else:
    winner.append(final_row['profile_B'].tolist()[0][1])
    winner.append(final_row['profile_B'].tolist()[0][2])

## 우승자 정보
    
winner_name = winner[0]
winner_team = winner[1]
winner_tech = winner[2]

## 대회 정보

contest_name = final_row.iloc[-1]['contest_name']
contest_date = final_row.iloc[-1]['play_date']
player_category = final_row.iloc[-1]['play_category']

## 우승자 상대 정보

final_name = opponent('결승')[0]
final_team = opponent('결승')[1]
final_tech = opponent('결승')[2]
final_result = opponent('결승')[3]

quarter_name = opponent('8강')[0]
quarter_team = opponent('8강')[1]
quarter_tech = opponent('8강')[2]
quarter_result = opponent('8강')[3]

semi_name = opponent('4강')[0]
semi_team = opponent('4강')[1]
semi_tech = opponent('4강')[2]
semi_result = opponent('4강')[3]

final_text = final_row['text_relay'].tolist()[0]
lines = final_text.strip().split('\n')
data = []
round_number = 0
time = 0
for line in lines:
    if line.endswith("라운드 경기시작"):
        round_number += 1
        time = 0
    elif line.endswith("초"):
        time = int(line[:-1])
    else:
        data.append([round_number, time, line])

df = pd.DataFrame(data, columns=["라운드", "초", "내용"])

victory_techniques = []
for index, row in df.iterrows():
    if '승리기술' in row['내용']:
        technique = row['내용'].split(' ')[-2]  # 승리기술이 마지막 단어로 기재되어 있음
        victory_techniques.append(technique)

victory_text = ", ".join(victory_techniques)


## Clova Speech API 활용

class ClovaSpeechClient:
    # Clova Speech invoke URL
    invoke_url = 'https://clovaspeech-gw.ncloud.com/external/v1/5775/c637a3d7ed044f678e92e388297d269fd9b8818fd9ec4d199b529babd301e1d6'
    # Clova Speech secret key
    secret = 'd87dddbb8a264129abf6c57247a78bb4'

    def req_url(self, url, completion, callback=None, userdata=None, forbiddens=None, boostings=None, wordAlignment=True, fullText=True, diarization=None):
        request_body = {
            'url': url,
            'language': 'ko-KR',
            'completion': completion,
            'callback': callback,
            'userdata': userdata,
            'wordAlignment': wordAlignment,
            'fullText': fullText,
            'forbiddens': forbiddens,
            'boostings': boostings,
            'diarization': diarization,
        }
        headers = {
            'Accept': 'application/json;UTF-8',
            'Content-Type': 'application/json;UTF-8',
            'X-CLOVASPEECH-API-KEY': self.secret
        }
        return requests.post(headers=headers,
                             url=self.invoke_url + '/recognizer/url',
                             data=json.dumps(request_body).encode('UTF-8'))

    def req_object_storage(self, data_key, completion, callback=None, userdata=None, forbiddens=None, boostings=None,
                           wordAlignment=True, fullText=True, diarization=None):
        request_body = {
            'dataKey': data_key,
            'language': 'ko-KR',
            'completion': completion,
            'callback': callback,
            'userdata': userdata,
            'wordAlignment': wordAlignment,
            'fullText': fullText,
            'forbiddens': forbiddens,
            'boostings': boostings,
            'diarization': diarization,
        }
        headers = {
            'Accept': 'application/json;UTF-8',
            'Content-Type': 'application/json;UTF-8',
            'X-CLOVASPEECH-API-KEY': self.secret
        }
        return requests.post(headers=headers,
                             url=self.invoke_url + '/recognizer/object-storage',
                             data=json.dumps(request_body).encode('UTF-8'))

    def req_upload(self, file, completion, callback=None, userdata=None, forbiddens=None, boostings=None,
                   wordAlignment=True, fullText=True, diarization=None):
        request_body = {
            'language': 'ko-KR',
            'completion': completion,
            'callback': callback,
            'userdata': userdata,
            'wordAlignment': wordAlignment,
            'fullText': fullText,
            'forbiddens': forbiddens,
            'boostings': boostings,
            'diarization': diarization,
        }
        headers = {
            'Accept': 'application/json;UTF-8',
            'X-CLOVASPEECH-API-KEY': self.secret
        }
        print(json.dumps(request_body, ensure_ascii=False).encode('UTF-8'))
        files = {
            'media': open(file, 'rb'),
            'params': (None, json.dumps(request_body, ensure_ascii=False).encode('UTF-8'), 'application/json')
        }
        response = requests.post(headers=headers, url=self.invoke_url + '/recognizer/upload', files=files)
        return response
    
fulltext = ''

res = ClovaSpeechClient().req_upload(file='interview.wav', completion='sync')
result = res.json()

    # Extract speaker-segmented results
segments = result.get('segments', [])
speaker_segments = []
    
for segment in segments:
    speaker_label = segment['speaker']['label']
    text = segment['text']
    speaker_segments.append({'speaker': speaker_label, 'text': text})

    # Print speaker-segmented results
for speaker_segment in speaker_segments:
    speaker_label = speaker_segment['speaker']
    text = speaker_segment['text']
    print(f'Speaker {speaker_label}: {text}')
    fulltext += text + '\n'

# Clova Summary API 활용

client_id = '46i8xxtvfd'
client_secret = '41Epde5friOA0yEVgxov5mE9GfQP2CznquipDSFY'
url = 'https://naveropenapi.apigw.ntruss.com/text-summary/v1/summarize'

headers = {
            'Accept': 'application/json;UTF-8',
            'Content-Type': 'application/json;UTF-8',
            'X-NCP-APIGW-API-KEY-ID': client_id,
            'X-NCP-APIGW-API-KEY': client_secret
        }

data = {
  "document": {
    "content": fulltext
  },
  "option": {
    "language": "ko",
    "model": "news",
    "tone": 2,
    "summaryCount": 3
  }
}


## 개인 접속 키로 현재는 주석처리함.
## Speech To Text 이후, Summary API를 돌리면 last_sentence와 같은 결과를 얻음.

response = requests.post(url, headers=headers, data=json.dumps(data).encode('UTF-8'))
rescode = response.status_code
# if(rescode == 200):
#     print (response.text)
# else:
#     print("Error : " + response.text)


# interview_data = json.loads(response.text)
# print(interview_data)
# summary = interview_data['summary']
# sentences = summary.split('\n')

# last_sentence = sentences[-1]
last_sentence = '거의 한 1년 만에 장사를 한 거라서 또 작년 본 대회가 마지막 장사였는데 올해 고온에서 장사를 해서 더 뜻깊은 것 같습니다.'



# 우승자 기사 템플릿
text = winner_name + '(' + winner_team + ') ' + '선수가 ' + contest_name + '에서 ' + player_category + ' 장사에 등극했다. \n' + winner_name + '는 ' + contest_date + player_category + '결정전(5전 3승제)에서 ' + final_name + '(' + final_team + ')' + '을 ' + final_result + '로 꺾었다. \n' + '8강에서는 ' + quarter_name + '(' + quarter_team + ')을 상대로 ' + quarter_result + ', 4강에서는 ' + semi_name + "(" + semi_team + ")를 " + semi_result + "로 각각 제압했다. \n" + winner_tech + ' 기술을 주로 사용하는 ' + winner_name + '선수는 결승전에서 ' + victory_text + '을 성공하였다. \n그는 우승 이후, 인터뷰에서 ' + last_sentence + '라며 소감을 밝혔다.\n'
title = winner_name + ', ' + contest_name + ' 대회 ' + player_category + '급 우승\n'

final_text = ""
final_text += title + '\n\n'
final_text += text + '\n\n'
final_text += "◇ " + contest_name + ' 최종 순위 ◇' + '\n\n'
final_text += "금강장사 " + winner_name + " (" +  winner_team + ')\n\n'
final_text += "2위      " + final_name + " (" +  final_team + ')\n\n'
final_text += "3위      " + third_name + " (" +  third_team + ')\n\n'


## 선택한 선수 선택할 수 있도록
def display_text():
    selected_winner = winner_var.get()

    processed_text = process_text(df_, selected_winner)
    
    ## GUI 생성
    window = tk.Tk()
    window.title("Match Article")

    # 텍스트와 스크롤바 등 생성
    frame = tk.Frame(window)
    frame.pack(fill=tk.BOTH, expand=True)
    
    text_widget = Text(frame, wrap=tk.WORD, width=80, height=20)
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = Scrollbar(frame, command=text_widget.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_widget.config(yscrollcommand=scrollbar.set)

    text_widget.insert(tk.END, processed_text)

    window.mainloop()
    
def display_winner_text():
    text_widget = tk.Text(root, wrap=tk.WORD)
    text_widget.insert(tk.END, final_text)
    text_widget.pack()

root = tk.Tk()
root.geometry("800x600")
root.title("경기별 기사 생성기")

winner_label = Label(root, text="우승 선수 선택:")
winner_label.pack(pady=10)


winner_var = StringVar(root)
winner_var.set(df_['winner'].unique()[0])  # 첫 선수 default로 설정

winner_dropdown = OptionMenu(root, winner_var, *df_['winner'].unique())
winner_dropdown.pack(pady=10)


# 기사 생성 버튼
generate_button = Button(root, text="해당 기사 생성", command=display_text)
generate_button.pack(pady=10)

# 우승자 기사 확인 버튼
display_button = tk.Button(root, text="우승자 기사 확인하기", command=display_winner_text)
display_button.pack(pady=10)

# Start the main Tkinter loop
root.mainloop()