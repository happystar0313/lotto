import streamlit as st
import pandas as pd
import os
import requests
import json

# 파일 저장 경로
data_file = "lotto_history.csv"

# 데이터 로드 함수
def load_data():
    if os.path.exists(data_file):
        return pd.read_csv(data_file)
    else:
        return pd.DataFrame(columns=["회차", "번호1", "번호2", "번호3", "번호4", "번호5", "번호6", "보너스번호", "당첨결과"])

# 데이터 저장 함수
def save_data(df):
    df.to_csv(data_file, index=False)

# 동행복권 API에서 최신 로또 번호 가져오기
def fetch_latest_lotto():
    url = "https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo="
    
    # 최신 회차 찾기 (적당히 큰 숫자로 테스트)
    latest_round = 1163  # 여기에 최신 회차 예상 숫자 넣기
    while True:
        response = requests.get(url + str(latest_round))
        data = response.json()
        if data["returnValue"] == "fail":
            latest_round -= 1  # 최신 회차가 없으면 -1 해서 다시 시도
        else:
            break

    # 최신 회차의 당첨번호 가져오기
    win_numbers = [data[f"drwtNo{i}"] for i in range(1, 7)]
    bonus_number = data["bnusNo"]

    return latest_round, win_numbers, bonus_number

# 당첨 여부 확인 함수
def check_winnings(fixed_sets, winning):
    results = []
    for fixed in fixed_sets:
        matching = len(set(fixed) & set(winning[:6]))
        bonus_match = 1 if winning[6] in fixed else 0

        if matching == 6:
            results.append(f"🎉 1등 당첨! ({fixed})")
        elif matching == 5 and bonus_match:
            results.append(f"🥈 2등 당첨! ({fixed})")
        elif matching == 5:
            results.append(f"🥉 3등 당첨! ({fixed})")
        elif matching == 4:
            results.append(f"💰 4등 당첨! ({fixed})")
        elif matching == 3:
            results.append(f"🎊 5등 당첨! ({fixed})")
    
    return results if results else ["❌ 꽝!"]

# 초기 데이터 로드
df = load_data()

# Streamlit UI
st.title("🎰 로또 기록 관리 시스템 (자동 업데이트)")

# 고정된 로또 번호 여러 개 입력 가능하도록 변경
st.header("💡 나의 고정 로또 번호들")
fixed_numbers_input = st.text_area("고정 로또 번호 입력 (각 줄마다 6개의 숫자 입력)", "6, 12, 23, 25, 31, 44\n2, 8, 9, 17, 33, 43\n6, 23, 26, 30, 33, 34")
fixed_numbers_list = [[int(n.strip()) for n in line.split(",") if n.strip().isdigit()] for line in fixed_numbers_input.split("\n") if line.strip()]
st.write(f"🔢 현재 설정된 고정 번호 세트: {fixed_numbers_list}")

# 최신 당첨번호 자동 업데이트
st.header("🔄 최신 로또 당첨번호 자동 가져오기")
if st.button("📡 최신 당첨번호 가져오기"):
    try:
        latest_round, latest_win_numbers, latest_bonus = fetch_latest_lotto()
        latest_numbers = latest_win_numbers + [latest_bonus]

        # 당첨 결과 확인
        result = check_winnings(fixed_numbers_list, latest_numbers)

        # 기록 추가
        new_entry = pd.DataFrame({
            "회차": [latest_round],
            "번호1": [latest_win_numbers[0]],
            "번호2": [latest_win_numbers[1]],
            "번호3": [latest_win_numbers[2]],
            "번호4": [latest_win_numbers[3]],
            "번호5": [latest_win_numbers[4]],
            "번호6": [latest_win_numbers[5]],
            "보너스번호": [latest_bonus],
            "당첨결과": [", ".join(result)]
        })
        df = pd.concat([df, new_entry], ignore_index=True)
        save_data(df)
        st.success(f"✅ 최신 회차 {latest_round} 당첨번호 업데이트 완료! 결과: {', '.join(result)}")

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")

# 기록된 데이터 표시
st.header("📊 당첨 기록")
st.dataframe(df)
