#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将棋ゲーム - Python実装
基本的な将棋のルールと盤面表示を含む
"""

import copy
from typing import List, Tuple, Optional, Dict

class ShogiPiece:
    """将棋の駒を表すクラス"""
    
    def __init__(self, piece_type: str, player: int, promoted: bool = False):
        self.piece_type = piece_type  # 駒の種類
        self.player = player  # プレイヤー (1: 先手, 2: 後手)
        self.promoted = promoted  # 成り駒かどうか
    
    def __str__(self):
        # 駒の表示用文字列
        pieces = {
            '王': '王', '玉': '玉', '飛': '飛', '角': '角',
            '金': '金', '銀': '銀', '桂': '桂', '香': '香', '歩': '歩'
        }
        
        promoted_pieces = {
            '飛': '龍', '角': '馬', '銀': '全', '桂': '圭', '香': '杏', '歩': 'と'
        }
        
        if self.promoted and self.piece_type in promoted_pieces:
            piece_str = promoted_pieces[self.piece_type]
        else:
            piece_str = pieces.get(self.piece_type, self.piece_type)
        
        # 後手の駒は逆さまに表示（実際のゲームでは色分けなど）
        if self.player == 2:
            return f"v{piece_str}"
        else:
            return f" {piece_str}"

class ShogiBoard:
    """将棋盤を表すクラス"""
    
    def __init__(self):
        self.board = [[None for _ in range(9)] for _ in range(9)]
        self.captured_pieces = {1: [], 2: []}  # 持ち駒
        self.current_player = 1  # 現在のプレイヤー
        self.setup_initial_position()
    
    def setup_initial_position(self):
        """初期配置を設定"""
        # 後手の駒配置 (上側)
        self.board[0][0] = ShogiPiece('香', 2)
        self.board[0][1] = ShogiPiece('桂', 2)
        self.board[0][2] = ShogiPiece('銀', 2)
        self.board[0][3] = ShogiPiece('金', 2)
        self.board[0][4] = ShogiPiece('玉', 2)  # 後手は玉将
        self.board[0][5] = ShogiPiece('金', 2)
        self.board[0][6] = ShogiPiece('銀', 2)
        self.board[0][7] = ShogiPiece('桂', 2)
        self.board[0][8] = ShogiPiece('香', 2)
        
        self.board[1][1] = ShogiPiece('飛', 2)
        self.board[1][7] = ShogiPiece('角', 2)
        
        for i in range(9):
            self.board[2][i] = ShogiPiece('歩', 2)
        
        # 先手の駒配置 (下側)
        for i in range(9):
            self.board[6][i] = ShogiPiece('歩', 1)
        
        self.board[7][1] = ShogiPiece('角', 1)
        self.board[7][7] = ShogiPiece('飛', 1)
        
        self.board[8][0] = ShogiPiece('香', 1)
        self.board[8][1] = ShogiPiece('桂', 1)
        self.board[8][2] = ShogiPiece('銀', 1)
        self.board[8][3] = ShogiPiece('金', 1)
        self.board[8][4] = ShogiPiece('王', 1)
        self.board[8][5] = ShogiPiece('金', 1)
        self.board[8][6] = ShogiPiece('銀', 1)
        self.board[8][7] = ShogiPiece('桂', 1)
        self.board[8][8] = ShogiPiece('香', 1)
    
    def display_board(self):
        """盤面を表示"""
        print("\n  ９８７６５４３２１")
        print("  " + "─" * 18)
        
        for i in range(9):
            row_str = f"{i+1}|"
            for j in range(9):
                if self.board[i][j]:
                    row_str += str(self.board[i][j])
                else:
                    row_str += "  "
            row_str += f"|{i+1}"
            print(row_str)
        
        print("  " + "─" * 18)
        print("  ９８７６５４３２１")
        
        # 持ち駒表示
        print(f"\n後手の持ち駒: {[str(p.piece_type) for p in self.captured_pieces[2]]}")
        print(f"先手の持ち駒: {[str(p.piece_type) for p in self.captured_pieces[1]]}")
        print(f"\n現在のプレイヤー: {'先手' if self.current_player == 1 else '後手'}")
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """座標が盤面内かチェック"""
        return 0 <= row < 9 and 0 <= col < 9
    
    def get_piece_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        """指定位置の駒の可能な移動先を取得"""
        piece = self.board[row][col]
        if not piece or piece.player != self.current_player:
            return []
        
        moves = []
        piece_type = piece.piece_type
        player = piece.player
        promoted = piece.promoted
        
        # 各駒の移動パターンを定義
        if piece_type == '歩':
            if not promoted:
                # 前進のみ
                dr = -1 if player == 1 else 1
                new_row = row + dr
                if self.is_valid_position(new_row, col):
                    if not self.board[new_row][col] or self.board[new_row][col].player != player:
                        moves.append((new_row, col))
            else:  # と金
                # 金将と同じ動き
                moves.extend(self._get_gold_moves(row, col, player))
        
        elif piece_type in ['王', '玉']:
            # 全方向1マス
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    new_row, new_col = row + dr, col + dc
                    if self.is_valid_position(new_row, new_col):
                        if not self.board[new_row][new_col] or self.board[new_row][new_col].player != player:
                            moves.append((new_row, new_col))
        
        elif piece_type == '金':
            moves.extend(self._get_gold_moves(row, col, player))
        
        elif piece_type == '銀':
            if not promoted:
                # 斜め4方向と前1マス
                directions = [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 1)]
                if player == 2:  # 後手の場合は方向を反転
                    directions = [(dr * -1, dc) for dr, dc in directions]
                
                for dr, dc in directions:
                    new_row, new_col = row + dr, col + dc
                    if self.is_valid_position(new_row, new_col):
                        if not self.board[new_row][new_col] or self.board[new_row][new_col].player != player:
                            moves.append((new_row, new_col))
            else:  # 成銀
                moves.extend(self._get_gold_moves(row, col, player))
        
        elif piece_type == '桂':
            if not promoted:
                # 桂馬の動き
                if player == 1:
                    knight_moves = [(-2, -1), (-2, 1)]
                else:
                    knight_moves = [(2, -1), (2, 1)]
                
                for dr, dc in knight_moves:
                    new_row, new_col = row + dr, col + dc
                    if self.is_valid_position(new_row, new_col):
                        if not self.board[new_row][new_col] or self.board[new_row][new_col].player != player:
                            moves.append((new_row, new_col))
            else:  # 成桂
                moves.extend(self._get_gold_moves(row, col, player))
        
        elif piece_type == '香':
            if not promoted:
                # 香車の動き（前方直進）
                direction = -1 if player == 1 else 1
                for i in range(1, 9):
                    new_row = row + direction * i
                    if not self.is_valid_position(new_row, col):
                        break
                    if self.board[new_row][col]:
                        if self.board[new_row][col].player != player:
                            moves.append((new_row, col))
                        break
                    moves.append((new_row, col))
            else:  # 成香
                moves.extend(self._get_gold_moves(row, col, player))
        
        elif piece_type == '角':
            if not promoted:
                # 角行の動き（斜め）
                directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
                for dr, dc in directions:
                    for i in range(1, 9):
                        new_row, new_col = row + dr * i, col + dc * i
                        if not self.is_valid_position(new_row, new_col):
                            break
                        if self.board[new_row][new_col]:
                            if self.board[new_row][new_col].player != player:
                                moves.append((new_row, new_col))
                            break
                        moves.append((new_row, new_col))
            else:  # 馬
                # 角行の動き + 王将の動き
                moves.extend(self.get_piece_moves_for_type('角', row, col, player, False))
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if abs(dr) + abs(dc) == 1:  # 縦横1マス
                            new_row, new_col = row + dr, col + dc
                            if self.is_valid_position(new_row, new_col):
                                if not self.board[new_row][new_col] or self.board[new_row][new_col].player != player:
                                    moves.append((new_row, new_col))
        
        elif piece_type == '飛':
            if not promoted:
                # 飛車の動き（縦横）
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                for dr, dc in directions:
                    for i in range(1, 9):
                        new_row, new_col = row + dr * i, col + dc * i
                        if not self.is_valid_position(new_row, new_col):
                            break
                        if self.board[new_row][new_col]:
                            if self.board[new_row][new_col].player != player:
                                moves.append((new_row, new_col))
                            break
                        moves.append((new_row, new_col))
            else:  # 龍
                # 飛車の動き + 王将の動き
                moves.extend(self.get_piece_moves_for_type('飛', row, col, player, False))
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if abs(dr) == abs(dc) == 1:  # 斜め1マス
                            new_row, new_col = row + dr, col + dc
                            if self.is_valid_position(new_row, new_col):
                                if not self.board[new_row][new_col] or self.board[new_row][new_col].player != player:
                                    moves.append((new_row, new_col))
        
        return moves
    
    def get_piece_moves_for_type(self, piece_type: str, row: int, col: int, player: int, promoted: bool) -> List[Tuple[int, int]]:
        """特定の駒タイプの移動を取得（再帰防止用）"""
        moves = []
        if piece_type == '角' and not promoted:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                for i in range(1, 9):
                    new_row, new_col = row + dr * i, col + dc * i
                    if not self.is_valid_position(new_row, new_col):
                        break
                    if self.board[new_row][new_col]:
                        if self.board[new_row][new_col].player != player:
                            moves.append((new_row, new_col))
                        break
                    moves.append((new_row, new_col))
        elif piece_type == '飛' and not promoted:
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                for i in range(1, 9):
                    new_row, new_col = row + dr * i, col + dc * i
                    if not self.is_valid_position(new_row, new_col):
                        break
                    if self.board[new_row][new_col]:
                        if self.board[new_row][new_col].player != player:
                            moves.append((new_row, new_col))
                        break
                    moves.append((new_row, new_col))
        return moves
    
    def _get_gold_moves(self, row: int, col: int, player: int) -> List[Tuple[int, int]]:
        """金将の移動パターン"""
        moves = []
        # 前、左右、斜め前2方向、後ろ
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0)]
        if player == 2:  # 後手の場合は方向を反転
            directions = [(dr * -1, dc) for dr, dc in directions]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position(new_row, new_col):
                if not self.board[new_row][new_col] or self.board[new_row][new_col].player != player:
                    moves.append((new_row, new_col))
        
        return moves
    
    def move_piece(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """駒を移動"""
        if not self.is_valid_position(from_row, from_col) or not self.is_valid_position(to_row, to_col):
            return False
        
        piece = self.board[from_row][from_col]
        if not piece or piece.player != self.current_player:
            return False
        
        # 移動可能かチェック
        valid_moves = self.get_piece_moves(from_row, from_col)
        if (to_row, to_col) not in valid_moves:
            return False
        
        # 移動が自分の王を王手に晒すかチェック
        captured_piece = self.board[to_row][to_col]
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        if self.is_in_check(self.current_player):
            # 移動を元に戻す
            self.board[from_row][from_col] = piece
            self.board[to_row][to_col] = captured_piece
            print("その移動は自分の王を王手に晒すため無効です。")
            return False
        
        # 移動を元に戻してから正式に実行
        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = captured_piece
        
        # 相手の駒を取る場合
        if captured_piece:
            # 持ち駒に追加（成りを解除）
            captured_piece.promoted = False
            self.captured_pieces[self.current_player].append(captured_piece)
        
        # 駒を移動
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        # 成りの判定（簡略化）
        if self._can_promote(piece, to_row):
            promote = input("成りますか？ (y/n): ").lower() == 'y'
            if promote:
                piece.promoted = True
        
        # プレイヤー交代
        self.current_player = 2 if self.current_player == 1 else 1
        return True
    
    def _can_promote(self, piece: ShogiPiece, row: int) -> bool:
        """成ることができるかチェック"""
        if piece.promoted:
            return False
        
        promotable_pieces = ['歩', '香', '桂', '銀', '角', '飛']
        if piece.piece_type not in promotable_pieces:
            return False
        
        # 敵陣（相手側の3段）に入った場合
        if piece.player == 1 and row <= 2:
            return True
        elif piece.player == 2 and row >= 6:
            return True
        
        return False
    
    def find_king(self, player: int) -> Optional[Tuple[int, int]]:
        """指定プレイヤーの王将/玉将の位置を取得"""
        king_types = ['王', '玉']
        for row in range(9):
            for col in range(9):
                piece = self.board[row][col]
                if piece and piece.player == player and piece.piece_type in king_types:
                    return (row, col)
        return None
    
    def is_in_check(self, player: int) -> bool:
        """指定プレイヤーが王手されているかチェック"""
        king_pos = self.find_king(player)
        if not king_pos:
            return False
        
        king_row, king_col = king_pos
        opponent = 2 if player == 1 else 1
        
        # 相手の全ての駒から王将/玉将への攻撃をチェック
        for row in range(9):
            for col in range(9):
                piece = self.board[row][col]
                if piece and piece.player == opponent:
                    valid_moves = self.get_piece_moves(row, col)
                    if (king_row, king_col) in valid_moves:
                        return True
        
        return False
    
    def can_escape_check(self, player: int) -> bool:
        """王手を回避できるかチェック"""
        if not self.is_in_check(player):
            return True  # 王手されていない
        
        # 自分の全ての駒で可能な移動を試す
        for from_row in range(9):
            for from_col in range(9):
                piece = self.board[from_row][from_col]
                if piece and piece.player == player:
                    valid_moves = self.get_piece_moves(from_row, from_col)
                    
                    for to_row, to_col in valid_moves:
                        # 移動をシミュレート
                        original_piece = self.board[to_row][to_col]
                        self.board[to_row][to_col] = piece
                        self.board[from_row][from_col] = None
                        
                        # 移動後に王手が解除されるかチェック
                        check_escaped = not self.is_in_check(player)
                        
                        # 移動を元に戻す
                        self.board[from_row][from_col] = piece
                        self.board[to_row][to_col] = original_piece
                        
                        if check_escaped:
                            return True
        
        return False
    
    def is_checkmate(self, player: int) -> bool:
        """指定プレイヤーが詰みかチェック"""
        return self.is_in_check(player) and not self.can_escape_check(player)
    
    def get_game_status(self) -> Dict[str, any]:
        """ゲーム状態を取得"""
        player1_in_check = self.is_in_check(1)
        player2_in_check = self.is_in_check(2)
        player1_checkmate = self.is_checkmate(1)
        player2_checkmate = self.is_checkmate(2)
        
        game_over = player1_checkmate or player2_checkmate
        winner = None
        
        if player1_checkmate:
            winner = 2
        elif player2_checkmate:
            winner = 1
        
        return {
            'game_over': game_over,
            'winner': winner,
            'player1_in_check': player1_in_check,
            'player2_in_check': player2_in_check,
            'player1_checkmate': player1_checkmate,
            'player2_checkmate': player2_checkmate
        }

class ShogiGame:
    """将棋ゲームのメインクラス"""
    
    def __init__(self):
        self.board = ShogiBoard()
    
    def parse_move(self, move_str: str) -> Tuple[int, int, int, int]:
        """移動入力を解析 (例: "77-76")"""
        try:
            parts = move_str.split('-')
            if len(parts) != 2:
                raise ValueError
            
            from_pos = parts[0]
            to_pos = parts[1]
            
            # 座標変換 (将棋の表記から配列インデックスへ)
            from_col = 9 - int(from_pos[0])
            from_row = int(from_pos[1]) - 1
            to_col = 9 - int(to_pos[0])
            to_row = int(to_pos[1]) - 1
            
            return from_row, from_col, to_row, to_col
        except:
            raise ValueError("無効な入力形式です")
    
    def play(self):
        """ゲームメインループ"""
        print("将棋ゲームを開始します！")
        print("移動は '77-76' の形式で入力してください")
        print("終了するには 'quit' と入力してください")
        
        while True:
            self.board.display_board()
            
            # ゲーム状態をチェック
            game_status = self.board.get_game_status()
            
            # 王手の表示
            if game_status['player1_in_check']:
                print("⚠️  先手の王将が王手されています！")
            if game_status['player2_in_check']:
                print("⚠️  後手の玉将が王手されています！")
            
            # 詰みのチェック
            if game_status['game_over']:
                if game_status['winner'] == 1:
                    print("🎉 先手の勝利！後手の玉将が詰みました！")
                elif game_status['winner'] == 2:
                    print("🎉 後手の勝利！先手の王将が詰みました！")
                break
            
            try:
                current_player_name = '先手' if self.board.current_player == 1 else '後手'
                move_input = input(f"\n{current_player_name}の手番: ").strip()
                
                if move_input.lower() == 'quit':
                    print("ゲームを終了します")
                    break
                
                from_row, from_col, to_row, to_col = self.parse_move(move_input)
                
                if self.board.move_piece(from_row, from_col, to_row, to_col):
                    print("移動しました")
                else:
                    print("無効な移動です")
                
            except ValueError as e:
                print(f"エラー: {e}")
            except KeyboardInterrupt:
                print("\nゲームを終了します")
                break

if __name__ == "__main__":
    game = ShogiGame()
    game.play()
