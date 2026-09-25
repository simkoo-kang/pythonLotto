# -*- coding: utf-8 -*-
import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import execjs

js_code = """
const BOARD_SIZE = 8;
const TYPES = ['RED', 'BLUE', 'GREEN', 'YELLOW', 'PURPLE'];
let board = Array.from({length: BOARD_SIZE}, () => Array(BOARD_SIZE).fill(null));
let isFirstTurn = true;
let initialMatches = new Set();

// 1. 내부 연산용 (순수 자바스크립트 배열을 반환하는 함수)
function _internalFindMatches() {
    let matches = [];
    for (let r = 0; r < BOARD_SIZE; r++) {
        for (let c = 0; c < BOARD_SIZE - 2; c++) {
            if (board[r][c] && board[r][c+1] && board[r][c+2] &&
                board[r][c].type === board[r][c+1].type && board[r][c].type === board[r][c+2].type) {
                matches.push(board[r][c].id);
            }
        }
    }
    for (let c = 0; c < BOARD_SIZE; c++) {
        for (let r = 0; r < BOARD_SIZE - 2; r++) {
            if (board[r][c] && board[r+1][c] && board[r+2][c] &&
                board[r][c].type === board[r+1][c].type && board[r][c].type === board[r+2][c].type) {
                matches.push(board[r][c].id);
            }
        }
    }
    return Array.from(new Set(matches));
}

function initBoard() {
    for (let r = 0; r < BOARD_SIZE; r++) {
        for (let c = 0; c < BOARD_SIZE; c++) {
            board[r][c] = { id: r + "-" + c, type: TYPES[Math.floor(Math.random() * TYPES.length)] };
        }
    }
    if (isFirstTurn) {
        // 배열을 반환하는 내부 함수를 호출하여 .forEach 렉 버그 해결
        _internalFindMatches().forEach(m => initialMatches.add(m));
        isFirstTurn = false;
        return "FIRST_TURN_LAG_PREVENTED";
    }
    return "NORMAL_TURN";
}

function createItem(type, direction, x, y) {
    let item = { x: x, y: y, type: type, direction: direction, explosionRadius: 1 };
    if (type === 'MISSILE') {
        item.direction = direction === 'HORIZ' ? 'VERT' : 'HORIZ';
    } else if (type === 'BOMB') {
        item.explosionRadius = 2; 
    }
    return item;
}

function triggerItem(type, direction, x, y) {
    let item = createItem(type, direction, x, y);
    let explodedGems = [];
    if (item.type === 'MISSILE') {
        if (item.direction === 'VERT') { 
            for (let r = 0; r < BOARD_SIZE; r++) explodedGems.push({r: r, c: item.y});
        } else {
            for (let c = 0; c < BOARD_SIZE; c++) explodedGems.push({r: item.x, c: c});
        }
    } else if (item.type === 'BOMB') {
        let rad = item.explosionRadius;
        for (let r = Math.max(0, item.x - rad); r <= Math.min(BOARD_SIZE - 1, item.x + rad); r++) {
            for (let c = Math.max(0, item.y - rad); c <= Math.min(BOARD_SIZE - 1, item.y + rad); c++) {
                explodedGems.push({r: r, c: c});
            }
        }
    }
    return JSON.stringify(explodedGems); 
}

// 2. 파이썬 연동용 외부 API (JSON 문자열로 직렬화하여 유실 방지)
function findMatches() {
    return JSON.stringify(_internalFindMatches());
}

function getBoardStateJSON() {
    return JSON.stringify(board);
}
"""

try:
    ctx = execjs.compile(js_code)

    # 보드 초기화 및 첫 턴 렉 해결
    init_status = ctx.call("initBoard")
    print(f"🎮 [Engine Init]: {init_status}")

    # 보드 전체 상태 안전하게 로드
    board_json = ctx.call("getBoardStateJSON")
    current_board = json.loads(board_json)
    
    # 0행 0열(맨 위 왼쪽) 보석 데이터 확인
    print(f"📊 [Current Board Top-Left Gem]: {current_board[0][0]}") 

    # 매칭 보석 확인
    matches = json.loads(ctx.call("findMatches"))
    print(f"✨ [Matched Gems Count]: {len(matches)} units found")

    # 5x5 폭탄 범위 연산
    bomb_effect = json.loads(ctx.call("triggerItem", "BOMB", "NONE", 3, 3))
    print(f"💣 [5x5 Bomb Area Count]: {len(bomb_effect)} tiles affected")

except execjs.RuntimeError as e:
    print(f"❌ Execution Error: {e}")
