import torch
import torch.nn as nn
import torch.nn.functional as F


class GomokuNet(nn.Module):
    def __init__(self, board_size=15):
        super(GomokuNet, self).__init__()
        self.board_size = board_size

        # 1. 공통 특징 추출 레이어 (Feature Extraction via CNN)
        # 입력 채널 수: 3 (1채널: 현재 턴 플레이어 돌, 2채널: 상대방 돌, 3채널: 직전 착점 위치)
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=64, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(64)

        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(128)

        self.conv3 = nn.Conv2d(128, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)

        # 2. 정책 헤드 (Policy Head) - 어디에 둘 것인가?
        self.policy_conv = nn.Conv2d(128, 4, kernel_size=1)
        self.policy_bn = nn.BatchNorm2d(4)
        # 보드 전체 크기만큼의 확률을 출력 (15 * 15 = 225)
        self.policy_fc = nn.Linear(4 * board_size * board_size, board_size * board_size)

        # 3. 가치 헤드 (Value Head) - 내가 얼마나 유리한가?
        self.value_conv = nn.Conv2d(128, 2, kernel_size=1)
        self.value_bn = nn.BatchNorm2d(2)
        self.value_fc1 = nn.Linear(2 * board_size * board_size, 64)
        self.value_fc2 = nn.Linear(64, 1)

    def forward(self, x):
        # x의 형태: (배치 크기, 3, 15, 15)

        # 공통 합성곱 레이어 통과 (렐루 활성화 함수 및 배치 정규화)
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = F.relu(self.bn3(self.conv3(x)))

        # --- 정책 헤드 연산 ---
        p = F.relu(self.policy_bn(self.policy_conv(x)))
        p = p.view(-1, 4 * self.board_size * self.board_size)
        # 최종 출력에 LogSoftmax를 취해 각 자리별 착점 확률을 구함
        policy_out = F.log_softmax(self.policy_fc(p), dim=1)

        # --- 가치 헤드 연산 ---
        v = F.relu(self.value_bn(self.value_conv(x)))
        v = v.view(-1, 2 * self.board_size * self.board_size)
        v = F.relu(self.value_fc1(v))
        # Tanh를 사용하여 현재 형세를 -1(패배)에서 1(승리) 사이의 값으로 수치화
        value_out = torch.tanh(self.value_fc2(v))

        return policy_out, value_out


# --- 모델 생성 및 작동 테스트 ---
if __name__ == "__main__":
    # 가상의 입력 데이터 생성 (배치 크기=1, 채널=3, 15x15 보드 크기)
    dummy_input = torch.randn(1, 3, 15, 15)

    # 모델 초기화
    model = GomokuNet(board_size=15)
    model.eval()  # 평가 모드 전환

    with torch.no_grad():
        policy, value = model(dummy_input)

    print("=== 인공신경망 예측 결과 ===")
    print(f"정책 헤드 출력 크기 (각 자리의 착점 확률 225개): {policy.shape}")
    print(f"가치 헤드 출력 크기 (현재 승률 판단 값 1개): {value.shape}")
    print(f"예측된 판세 가치 (양수면 유리, 음수면 불리): {value.item():.4f}")
