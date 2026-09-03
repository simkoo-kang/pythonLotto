import os
import time
import random

from util.log_util import LogUtil
from util.mydic_util import MyDic

# 💡 텐서플로우의 내부 안내 경고 메시지(C++ 로그)를 화면에서 차단합니다.
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

import tensorflow as tf
# 💡 파이썬 자체적인 텐서플로우 경고창을 차단합니다.
tf.get_logger().setLevel('ERROR') 

# --- 이후 기존 import 및 AI 코드 진행 ---
from typing import List

import numpy as np
from keras._tf_keras.keras.models import Model
from keras._tf_keras.keras.layers import LSTM, Dense, Dropout, Input, Concatenate
from sklearn.preprocessing import StandardScaler

from util.str_util import Str
from util.file_util import FileUtil
from lotto_main import LottoMain
from vo.number_vo import NumberVO

# 1. 기존에 정의된 수많은 필터 함수 및 분석 함수들 (예시)

"""
 ALL_LOTTO_FILTERS 자동 스캔:
  - 필터가 20개든 50개든, myfilter.py 내부 리스트에 담겨 있다면
    for lotto_filter in ALL_LOTTO_FILTERS:
        루프가 돌면서 행렬의 Column(열)을 자동으로 확장해 줍니다.
    개발자가 수동으로 코드를 덧붙일 필요가 없습니다.
StandardScaler(데이터 정규화) 적용:
 - 필터 결과 중 총합(100~180) 데이터와 홀짝 비율(0~6),
   필터 통과 여부(0 또는 1)는 숫자의 체급이 다릅니다.
   이 상태로 신경망에 넣으면 값이 큰 총합 필터 위주로만 AI가 학습하는 대참사가 일어납니다.
   이를 방지하기 위해 모든 값을 균일한 스케일의 소수점으로 평탄화하는 작업을 파이프라인 내에 내장했습니다.
LSTM 변환 스케줄 연계:
 - 이렇게 최종 출력된 final_filter_matrix를 이전 답변 구조의 filter_features 자리에 그대로 대입하면,
   윈도우 슬라이딩을 거쳐 대규모 필터가 결합된 [X_filter] 입력 데이터셋이 완성됩니다.
"""
class LottoAITest(LottoMain):
    def __init__(self, debug: bool=False):
        super().__init__(debug=debug)

        self.numberVos: List[NumberVO] = self.numberVos

        self.tickets = [] # 로또 추천 번호를 담을 리스트

        if debug:
            self.mydic = MyDic()
        
    
    # --- [파이프라인 단계 1: 필터 결과 수치화 함수 정의] ---
    def calculate_filter_features_for_row(self, numbers):
        """
        6개 번호를 받아 수십 개의 필터 상태를 수치(float) 리스트로 반환하는 함수.
        True/False 필터는 1.0과 0.0으로 변환하고, 통계량은 점수 그대로 활용합니다.
        """
        feature_scores = []

        # (2) 기존에 가지고 계신 수십 개의 통과/탈락 필터 자동 적용 (리스트 순회)
        # ALL_LOTTO_FILTERS 내의 모든 필터를 돌며 통과(True)->1.0, 탈락(False)->0.0 주입
        for lotto_filter in self.filter_manager._filters:
            try:
                passed = lotto_filter.filter(numbers)
                feature_scores.append(1.0 if passed else 0.0)
            except Exception as e:
                # 혹시 매개변수가 필요한 필터일 경우 기본값 예외 처리
                feature_scores.append(0.0)
                
        return feature_scores

    # --- [파이프라인 단계 2: 전체 역사 데이터 행렬 변환 매니저] ---
    def build_filter_matrix_pipeline(self):
        """
        실제 로또 CSV 파일을 로드하여 딥러닝 주입용 2차원 행렬(Matrix)로 일괄 변환
        """
        # 1. 로또 당첨 데이터 로드 (회차, 번호1, 번호2, ... 번호6 구조 가정)
        # 예시를 위해 가짜 데이터프레임 생성 (실제 가동 시 주석 해제)
        # df = pd.read_csv(csv_file_path)
        
        # # [테스트용 가짜 데이터프레임 빌드] 
        # demo_data = {
        #     'num1': [],
        #     'num2': [],
        #     'num3': [],
        #     'num4': [],
        #     'num5': [],
        #     'num6': [],
        # }
        # for numbervo in self.numberVos:
        #     nums = numbervo.numbers
        #     for i in range(0,6):
        #         cname = f"num{i+1}"
        #         demo_data[cname].append(nums[i])
        
        # df = pd.DataFrame(demo_data)
        df = self.get_number_list_data_frame();
        
        # 2. 6개 당첨 번호 열만 묶어서 리스트 형태로 추출
        lotto_numbers_list = df[['num1', 'num2', 'num3', 'num4', 'num5', 'num6']].values.tolist()

        # 3. 모든 회차를 순회하며 필터 2차원 배열 빌드
        matrix_list = []
        for numbers in lotto_numbers_list:
            # 각 행마다 수십 개 필터 점수 추출
            row_features = self.calculate_filter_features_for_row(numbers)
            matrix_list.append(row_features)
            
        # 4. 최종 넘파이 2차원 행렬(Matrix)로 변환
        filter_matrix = np.array(matrix_list, dtype=np.float32)
        
        # 💡 딥러닝 팁: 총합(140)과 홀짝수(3)처럼 수치 단위가 다르면 LSTM 학습이 잘 안 됩니다.
        # 모든 필터 점수 데이터의 단위를 평균 0, 표준편차 1 범위로 균일하게 정규화(Scaling)합니다.
        scaler = StandardScaler()
        normalized_filter_matrix = scaler.fit_transform(filter_matrix)
        
        return lotto_numbers_list, normalized_filter_matrix

    # --- [4단계: AI 확률 기반 대량 샘플링 및 최종 로또 번호 추출] ---
    def generate_final_lotto_tickets(self, prob_list, total_games=5, tried: int=10000, all: bool=False):
        final_tickets = []
        attempts = 0

        while attempts < tried:
            if not all and len(final_tickets) >= total_games:
                break

            attempts += 1
            
            # 1) AI 모델이 예측한 필터 융합 확률 가중치를 사용하여 6개 숫자 무작위 추출
            sampled = np.random.choice(range(1, 46), size=6, replace=False, p=prob_list)
            sampled.sort()
            sampled = list(map(int, sampled))

            self.tickets.append(sampled) # 생성한 모두 tickets에 추가
            
            # 2) 뽑힌 조합이 기존 수십 개의 필터를 모두 안전하게 만족하는지 더블 체크
            is_safe = True
            for lotto_filter in self.filter_manager._filters:
                if not lotto_filter.filter(sampled):
                    if self.debug:
                        self.mydic.add_dic(lotto_filter.__class__.__name__)
                    is_safe = False
                    break
                    
            if is_safe and sampled not in final_tickets:
                final_tickets.append(sampled)
                
        return final_tickets, attempts


def echo_time(stime, etime) -> str:
    elapsed_time = etime - stime
    minutes = int(elapsed_time // 60)
    seconds = elapsed_time % 60
    return f"⏱️ 시작={stime}, 종료={etime} 총 소요 시간: {minutes}분 {seconds:.2f}초"


def main(debug: bool=False, isAll: bool=False):

    # LottoTest 인스턴스 생성
    lotto_ai_test = LottoAITest(debug=debug)
    logger = LogUtil.get_logger(Str.get_class_name(lotto_ai_test))

    start_time = time.perf_counter()

    logger.debug("--- [파이프라인 실행 및 데이터 형태 검증] ---")
    # --- [파이프라인 실행 및 데이터 형태 검증] ---
    raw_numbers, final_filter_matrix = lotto_ai_test.build_filter_matrix_pipeline()

    logger.debug("📊 [필터 전처리 파이프라인 처리 결과]")
    logger.debug(f"총 처리된 회차 수: {Str.number_format(len(raw_numbers))} 회차")
    logger.debug(f"생성된 필터 행렬 형태 (Shape): {final_filter_matrix.shape}")
    logger.debug(f"-> 각 회차마다 {final_filter_matrix.shape[1]}개의 필터 지표가 2차원 Matrix로 압축되었습니다.")
    logger.debug("\n첫 번째 회차의 전처리된 필터 행렬 샘플:\n%s", final_filter_matrix[0])

    end_time = time.perf_counter()
    echo_str = echo_time(start_time, end_time)
    logger.debug(echo_str)

    # Hyperparameters 설정
    LOOKBACK_WINDOW = 5  # 과거 5개 회차의 흐름을 분석
    NUM_CLASSES = 45     # 1 ~ 45번 번호
    NUM_FILTERS = final_filter_matrix.shape[1] # 파이프라인이 계산해낸 총 필터 개수

    logger.debug("--- [1단계: 딥러닝 학습용 시퀀스 데이터셋 구성] ---")

    # --- [1단계: 딥러닝 학습용 시퀀스 데이터셋 구성] ---
    X_num, X_filter, Y_train = [], [], []

    for i in range(len(raw_numbers) - LOOKBACK_WINDOW):
        # 과거 5개 회차의 원-핫 인코딩 번호 흐름
        # raw_numbers를 원-핫 행렬로 변환한 encoded_history 배열을 사용한다고 가정합니다.
        # (여기서는 이전 답변의 데이터셋 빌드 로직 연계)
        encoded_window = np.zeros((LOOKBACK_WINDOW, NUM_CLASSES))
        for w in range(LOOKBACK_WINDOW):
            for num in raw_numbers[i + w]:
                encoded_window[w, num - 1] = 1
                
        X_num.append(encoded_window)
        # 💡 핵심: 전처리 파이프라인으로 만든 2차원 필터 행렬을 똑같이 5개씩 쪼개어 주입합니다.
        X_filter.append(final_filter_matrix[i : i + LOOKBACK_WINDOW])
        
        # 다음 회차의 정답 원-핫 벡터
        target_window = np.zeros(NUM_CLASSES)
        for num in raw_numbers[i + LOOKBACK_WINDOW]:
            target_window[num - 1] = 1
        Y_train.append(target_window)

    end_time = time.perf_counter()
    echo_str = echo_time(start_time, end_time)
    logger.debug(echo_str)

    X_num = np.array(X_num, dtype=np.float32)
    X_filter = np.array(X_filter, dtype=np.float32)
    Y_train = np.array(Y_train, dtype=np.float32)

    logger.debug("--- [2단계: 다중 입력(Multi-Input) 딥러닝 모델 빌드] ---")

    # --- [2단계: 다중 입력(Multi-Input) 딥러닝 모델 빌드] ---
    # 입력 1: 번호 흐름 데이터 파트
    input_num = Input(shape=(LOOKBACK_WINDOW, NUM_CLASSES), name="Lotto_Numbers")
    lstm_num = LSTM(64, return_sequences=False)(input_num)

    # 입력 2: 전처리된 필터 행렬 데이터 파트
    input_filter = Input(shape=(LOOKBACK_WINDOW, NUM_FILTERS), name="Filter_Matrices")
    lstm_filter = LSTM(32, return_sequences=False)(input_filter)

    # 두 신경망의 특징을 하나로 결합 (번호 시퀀스 정보 + 필터 밸런스 정보 융합)
    combined = Concatenate()([lstm_num, lstm_filter])
    x = Dense(64, activation='relu')(combined)
    x = Dropout(0.2)(x)
    output = Dense(NUM_CLASSES, activation='sigmoid')(x) # 1~45번 각각의 확률 출력

    model = Model(inputs=[input_num, input_filter], outputs=output)
    model.compile(optimizer='adam', loss='binary_crossentropy')

    # 모델 학습 진행
    model.fit([X_num, X_filter], Y_train, epochs=20, batch_size=4, verbose=0)

    end_time = time.perf_counter()
    echo_str = echo_time(start_time, end_time)
    logger.debug(echo_str)

    logger.debug("--- [3단계: 최신 데이터를 모델에 넣어 '다음 회차 확률 예측'] ---")

    # --- [3단계: 최신 데이터를 모델에 넣어 '다음 회차 확률 예측'] ---
    # 가장 최근 5개 회차의 원-핫 번호 데이터 가공
    latest_num_seq = np.zeros((LOOKBACK_WINDOW, NUM_CLASSES))
    for w in range(LOOKBACK_WINDOW):
        for num in raw_numbers[-(LOOKBACK_WINDOW-w)]:
            latest_num_seq[w, num - 1] = 1

    # 💡 가장 최근 5개 회차의 전처리된 필터 행렬 데이터 추출
    latest_filter_seq = final_filter_matrix[-LOOKBACK_WINDOW:]

    # 3차원 배치 형태로 변환 (1, 5, 45) 및 (1, 5, 필터 수)
    latest_num_seq = np.expand_dims(latest_num_seq, axis=0)
    latest_filter_seq = np.expand_dims(latest_filter_seq, axis=0)

    # 최종 AI 확률값 도출 (45차원 배열)
    predicted_probabilities = model.predict([latest_num_seq, latest_filter_seq])[0]
    predicted_probabilities /= np.sum(predicted_probabilities) # 확률 총합 1로 정규화

    games = 9
    tried = 10000*100

    end_time = time.perf_counter()
    echo_str = echo_time(start_time, end_time)
    logger.debug(echo_str)

    logger.debug(f"--- 최종 로또 생성 실행 ({Str.number_format(tried)})번 ---")
    
    # 최종 로또 생성 실행
    lucky_tickets, total_search = lotto_ai_test.generate_final_lotto_tickets(predicted_probabilities, total_games=games, tried=tried, all=isAll)

    tickets_len = len(lucky_tickets)

    logger.debug(f"총 {Str.number_format(len(lotto_ai_test.tickets))}개의 로또 추천 번호가 추출되었습니다.")
    logger.debug(f"(필터를 통과한 번호가 총 {Str.number_format(tickets_len)}개 추출되었습니다.)")
    
    if lotto_ai_test.debug:
        lotto_ai_test.mydic.sort(key=False, reverse=True)
        dicstr = lotto_ai_test.mydic.toString()
        logger.debug(dicstr)
        logger.debug("")

    end_time = time.perf_counter()
    echo_str = echo_time(start_time, end_time)
    logger.debug(echo_str)

    lastVo = lotto_ai_test.getLastVo()
    round = lastVo.round

    logger.debug("🚀 [AI 필터 융합형 딥러닝 최종 로또 추천 번호]")

    filename = os.path.join(FileUtil.CONF_PATH,f"make\{round+1}_all.txt")
    lotto_ai_test.save_file(filename, lotto_ai_test.tickets)

    filename = os.path.join(FileUtil.CONF_PATH,f"make\{round+1}_filtered.txt")
    lotto_ai_test.save_file(filename, lucky_tickets)

    # random.sample(대상_리스트, 뽑을_개수)
    # 중복 없이 완벽히 서로 다른 5개의 요소를 리스트로 반환합니다.
    selected_games = random.sample(lucky_tickets, min(games, len(lucky_tickets)))

    selected_vos = []

    ncounts = [0]*45
    for i, ticket in enumerate(selected_games, 1):
        selected_vos.append(NumberVO(0, ticket, 0))
        for n in ticket:
            ncounts[n-1] += 1

    # selected_vos.sort()
    selected_vos.sort(key=lambda vo: vo.numbers)

    volines = []

    for i, vo in enumerate(selected_vos, 1):
        line = vo.toString(isSum=True)
        volines.append(line)

        # range(3, 10, 3)은 정확히 [3, 6, 9] 리스트를 의미합니다.
        # if i == 3 or i == 6 or i == 9:
        if i in range(3, 10, 3):
            volines.append("")

    lni = 0
    for i, line in enumerate(volines, 1):
        if 0<len(line):
            lni += 1
            logger.debug(f"{lni}게임:\t{line}")
        else:
            logger.debug("")

    applines = []
    sumc = 0
    if 0<len(selected_vos):
        applines.append("");
        volines.append("");
        for i, c in enumerate(ncounts, 1):
            if 0 < c:
                applines.append(f"{i:02d} = {c}")
                volines.append(f"{i:02d} = {c}")
                sumc += 1

        applines.append("");
        volines.append("");
        applines.append(f"총 {sumc}개 번호가 선택되었습니다.")
        volines.append(f"총 {sumc}개 번호가 선택되었습니다.")
        applines.append("")
        volines.append("")

        filename = os.path.join(FileUtil.CONF_PATH,f"make\{round+1}.txt")
        FileUtil.write_lines(filename, volines, "w")

        logger.debug(f"최종 로또 추천 번호 save to {filename} {sumc}개")

        logger.debug(f"\nApplied lines: {applines}")
    else:
        logger.debug("최종 로또 추천 번호가 없습니다.")

    end_time = time.perf_counter()
    echo_str = echo_time(start_time, end_time)
    logger.debug(echo_str)

    logger.debug("--- 최종 종료 - 끝 ---")


if __name__ == "__main__":
    debug: bool=False
    isAll: bool=True

    main(debug=debug, isAll=isAll)
 