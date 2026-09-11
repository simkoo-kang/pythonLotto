# -*- coding: utf-8 import sys
import sys
import io

# 윈도우 터미널 출력 인코딩을 UTF-8로 강제 설정하여 깨짐 방지
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import execjs

# 1. 모든 한글 문구를 영문으로 교체 (인코딩 에러 원천 차단)
js_code = """
function optimizeInitialMatch(isFirstTurn) {
    return isFirstTurn ? "LAG_PREVENTION_ACTIVATED" : "NORMAL_TURN";
}

function createItem(type, direction, x, y) {
    let item = { x: x, y: y, type: type, direction: direction };
    if (type === 'MISSILE') {
        item.direction = direction === 'HORIZ' ? 'VERT' : 'HORIZ';
    } else if (type === 'BOMB') {
        item.explosionRadius = 2; 
    }
    return item;
}
"""

try:
    ctx = execjs.compile(js_code)

    # 2. 함수 호출 및 결과 출력 (파이썬 print문에서 한글 라벨링 처리)
    turn_test = ctx.call("optimizeInitialMatch", True)
    print(f"[Match Test]: {turn_test}")
    
    missile_result = ctx.call("createItem", "MISSILE", "HORIZ", 3, 4)
    print(f"[Missile Test]: {missile_result}")
    
    bomb_result = ctx.call("createItem", "BOMB", "NONE", 2, 2)
    print(f"[Bomb Test]: {bomb_result}")

except execjs.RuntimeError as e:
    print(f"Runtime Error: {e}")
