import pandas as pd
import os

#print("lotto","D:\\Workspace\\docs\\lotto\\numbers.txt")

filename = "D:\\Workspace\\docs\\lotto\\numbers.txt"

if not os.path.exists(filename):
    print(f"❌ 파일을 찾을 수 없습니다. 경로를 확인해주세요: {filename}")
else:
    try:
        # 2. 텍스트 파일 읽기 (탭 구분자 '\t' 사용, 한글 깨짐 방지 cp949)
        # 만약 여전히 오류가 나면 encoding='utf-8' 또는 'utf-8-sig'로 변경해보세요.
        df = pd.read_csv(filename, sep='\t', encoding='utf-8')
        print(" 데이터 파일 로드 성공!\n")
        
        # 3. 'N1-N2-N3-N4-N5-N6' 하이픈 문자열 분리 및 정수 변환
        split_numbers = df['N1-N2-N3-N4-N5-N6'].str.split('-', expand=True)
        
        for i in range(6):
            df[f'번호{i+1}'] = split_numbers[i].astype(int)
            
        print(" 당첨번호 분리 완료 (번호1 ~ 번호6 열 생성됨)\n")
        
        # 4. 데이터 상위 5행 출력하여 확인
        print("[데이터 확인 - 상위 5행]")
        print(df[['회차', '추첨일', '번호1', '번호2', '번호3', '번호4', '번호5', '번호6', 'BN', 'SUM']].head())

    except Exception as e:
        print(f"❌ 데이터를 처리하는 중 오류가 발생했습니다:\n{e}")


try:
    # 1. '1등당첨금액' 또는 '당첨금액' 열 이름 맞추기
    # 제시해주신 열 이름 중 1등 바로 뒤의 '당첨금액'을 타겟으로 합니다.
    # 만약 판다스가 열 이름을 중복 처리했다면 '당첨금액' 또는 '당첨금액.1' 등으로 자동 지정될 수 있습니다.
    # 안전하게 처리하기 위해 인덱스로 접근하거나 열 이름을 확인 후 매칭합니다.
    
    # 데이터 내 '당첨금액' 문자열 가공 (숫자 외에 쉼표, '원' 등이 있으면 제거)
    # 열 이름이 정확히 '당첨금액'일 경우 기재:
    target_col = '당첨금액' 
    
    # 2. 금액 데이터를 깨끗한 숫자(정수형)로 변환
    df[target_col] = df[target_col].astype(str)  # 문자열로 일시 변환
    df[target_col] = df[target_col].str.replace(',', '', regex=True) # 쉼표 제거
    df[target_col] = df[target_col].str.replace('원', '', regex=True) # '원' 제거
    df[target_col] = pd.to_numeric(df[target_col], errors='coerce')  # 숫자로 변환 (공백은 NaN 처리)

    # 3. 1등 당첨금액 기준 내림차순(큰 순서대로) 정렬
    top_prize_df = df.sort_values(by=target_col, ascending=False)

    # 4. 역대 최고 당첨금 TOP 5 회차 출력
    print("🏆 [역대 1등 최고 당첨금액 TOP 5 회차] 🏆\n")
    
    # 가독성을 위해 금액에 다시 쉼표를 넣어 출력
    for rank, (idx, row) in enumerate(top_prize_df.head(5).iterrows()):
        prize_format = f"{int(row[target_col]):,}" if not pd.isna(row[target_col]) else "데이터 없음"
        print(f"🥇 {rank+1}위: {int(row['회차'])}회 (추첨일: {row['추첨일']})")
        print(f"   - 1등 당첨금액: {prize_format} 원")
        print(f"   - 당시 당첨번호: {row['N1-N2-N3-N4-N5-N6']} [보너스: {int(row['BN'])}]")
        print(f"   - 발급 방식: 자동 {row['자동']}개 / 수동 {row['수동']}개\n")

except KeyError as e:
    print(f"❌ 열 이름을 찾을 수 없습니다: {e}")
    print("현재 파일의 열 이름 목록을 확인해보세요:", df.columns.tolist())
except Exception as e:
    print(f"❌ 오류가 발생했습니다: {e}")


try:
    # 1. 수치형 데이터 변환 및 결측치(NaN)를 0으로 채우기
    # 예전 회차의 경우 '반자동' 기록이 없거나 공백일 수 있으므로 안전하게 처리합니다.
    df['자동'] = pd.to_numeric(df['자동'], errors='coerce').fillna(0).astype(int)
    df['수동'] = pd.to_numeric(df['수동'], errors='coerce').fillna(0).astype(int)
    df['반자동'] = pd.to_numeric(df['반자동'], errors='coerce').fillna(0).astype(int)

    # 2. 각 방식별 총 당첨자 수 합산
    total_auto = df['자동'].sum()
    total_manual = df['수동'].sum()
    total_semi = df['반자동'].sum()
    total_winners = total_auto + total_manual + total_semi

    # 3. 백분율(%) 비율 계산
    if total_winners > 0:
        pct_auto = (total_auto / total_winners) * 100
        pct_manual = (total_manual / total_winners) * 100
        pct_semi = (total_semi / total_winners) * 100
    else:
        pct_auto = pct_manual = pct_semi = 0

    # 4. 결과 출력
    print("📊 [역대 로또 1등 발급 방식별 누적 통계] 📊\n")
    print(f" 총 분석 회차 수: {len(df)}개 회차")
    print(f" 총 1등 당첨자 수: {total_winners:,}명\n")
    print(f" 🤖 자동 구매 당첨: {total_auto:,}명 ({pct_auto:.2f}%)")
    print(f" ✍️ 수동 구매 당첨: {total_manual:,}명 ({pct_manual:.2f}%)")
    print(f" 🌓 반자동 구매 당첨: {total_semi:,}명 ({pct_semi:.2f}%)")
    print("\n--------------------------------------------------")
    print("💡 참고: 데이터셋에 초기 회차가 포함된 경우,")
    print("   당시에는 자동/수동 구분이 기록되지 않아 0명으로 집계될 수 있습니다.")

except KeyError as e:
    print(f"❌ 열 이름을 찾을 수 없습니다: {e}")
    print("현재 파일의 열 이름들을 확인해주세요:", df.columns.tolist())
except Exception as e:
    print(f"❌ 통계 계산 중 오류가 발생했습니다: {e}")


print(f"1등 당첨자수: {df['1등'].sum():,}명")
