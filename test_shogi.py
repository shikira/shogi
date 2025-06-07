#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将棋ゲームのテスト用ファイル
"""

from shogi_game import ShogiGame, ShogiBoard, ShogiPiece

def test_basic_moves():
    """基本的な移動のテスト"""
    board = ShogiBoard()
    
    print("=== 初期盤面 ===")
    board.display_board()
    
    # 先手の歩を前進
    print("\n=== 先手 77-76 ===")
    success = board.move_piece(6, 2, 5, 2)  # 77-76
    print(f"移動成功: {success}")
    board.display_board()
    
    # 後手の歩を前進
    print("\n=== 後手 33-34 ===")
    success = board.move_piece(2, 6, 3, 6)  # 33-34
    print(f"移動成功: {success}")
    board.display_board()

def test_piece_moves():
    """各駒の移動可能範囲をテスト"""
    board = ShogiBoard()
    
    # 先手の歩の移動可能範囲
    print("=== 先手の歩(77)の移動可能範囲 ===")
    moves = board.get_piece_moves(6, 2)  # 77の位置
    print(f"移動可能な位置: {moves}")
    
    # 先手の角の移動可能範囲
    print("\n=== 先手の角(88)の移動可能範囲 ===")
    moves = board.get_piece_moves(7, 1)  # 88の位置
    print(f"移動可能な位置: {moves}")

def demo_game():
    """デモゲーム"""
    print("=== 将棋ゲーム デモ ===")
    board = ShogiBoard()
    
    # いくつかの手を自動で進める
    moves = [
        (6, 2, 5, 2),  # 先手: 77-76
        (2, 6, 3, 6),  # 後手: 33-34
        (6, 6, 5, 6),  # 先手: 73-74
        (2, 2, 3, 2),  # 後手: 37-36
    ]
    
    for i, (fr, fc, tr, tc) in enumerate(moves):
        print(f"\n=== 手番 {i+1} ===")
        player = "先手" if board.current_player == 1 else "後手"
        print(f"{player}の手")
        
        success = board.move_piece(fr, fc, tr, tc)
        print(f"移動成功: {success}")
        board.display_board()

if __name__ == "__main__":
    print("将棋ゲームのテストを開始します\n")
    
    # 基本的な移動テスト
    test_basic_moves()
    
    print("\n" + "="*50 + "\n")
    
    # 駒の移動範囲テスト
    test_piece_moves()
    
    print("\n" + "="*50 + "\n")
    
    # デモゲーム
    demo_game()
