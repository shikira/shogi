#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将棋ゲーム - PyGame実装（文字化け修正版）
グラフィカルインターフェースを持つ将棋ゲーム
"""

import pygame
import sys
import os
import copy
from typing import List, Tuple, Optional, Dict
from shogi_game import ShogiPiece, ShogiBoard

# 色の定義
COLORS = {
    'BOARD': (222, 184, 135),      # 将棋盤の色
    'GRID': (139, 69, 19),         # 格子線の色
    'BACKGROUND': (245, 245, 220),  # 背景色
    'TEXT': (0, 0, 0),             # テキスト色
    'HIGHLIGHT': (255, 255, 0),     # ハイライト色
    'SELECTED': (255, 200, 200),    # 選択された駒の色
    'POSSIBLE_MOVE': (200, 255, 200), # 可能な移動先の色
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'RED': (255, 0, 0),
    'BLUE': (0, 0, 255)
}

class PyGameShogi:
    """PyGameを使った将棋ゲーム"""
    
    def __init__(self):
        pygame.init()
        
        # 画面設定
        self.WINDOW_WIDTH = 800
        self.WINDOW_HEIGHT = 700
        self.BOARD_SIZE = 540  # 将棋盤のサイズ
        self.CELL_SIZE = self.BOARD_SIZE // 9
        self.BOARD_OFFSET_X = (self.WINDOW_WIDTH - self.BOARD_SIZE) // 2
        self.BOARD_OFFSET_Y = 50
        
        # PyGameの初期化
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Shogi Game / 将棋ゲーム")
        self.clock = pygame.time.Clock()
        
        # フォント設定
        self.setup_fonts()
        
        # ゲーム状態
        self.game = ShogiBoard()
        self.selected_pos = None
        self.possible_moves = []
        self.promotion_dialog = None
        
        # 駒の表示用辞書（日本語と英語の両方）
        self.piece_display = {
            # 日本語表記（正式ルール：先手=王将、後手=玉将）
            '王': {'jp': '王', 'en': 'K'},
            '玉': {'jp': '玉', 'en': 'K'},
            '飛': {'jp': '飛', 'en': 'R'},
            '角': {'jp': '角', 'en': 'B'},
            '金': {'jp': '金', 'en': 'G'},
            '銀': {'jp': '銀', 'en': 'S'},
            '桂': {'jp': '桂', 'en': 'N'},
            '香': {'jp': '香', 'en': 'L'},
            '歩': {'jp': '歩', 'en': 'P'},
            # 成り駒
            '龍': {'jp': '龍', 'en': '+R'},
            '馬': {'jp': '馬', 'en': '+B'},
            '全': {'jp': '全', 'en': '+S'},
            '圭': {'jp': '圭', 'en': '+N'},
            '杏': {'jp': '杏', 'en': '+L'},
            'と': {'jp': 'と', 'en': '+P'}
        }
        
        # 日本語フォントが使用可能かチェック
        self.use_japanese = self.test_japanese_font()
    
    def setup_fonts(self):
        """フォントを設定"""
        # 基本フォント
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # 日本語フォントの候補
        japanese_fonts = [
            # macOS
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/Arial Unicode MS.ttf",
            "/Library/Fonts/Arial Unicode MS.ttf",
            # 一般的なフォント名
            "NotoSansCJK-Regular.ttc",
            "Arial Unicode MS",
            "MS Gothic",
            "Yu Gothic",
            "Hiragino Sans",
        ]
        
        self.font_japanese = None
        
        # 利用可能な日本語フォントを探す
        for font_path in japanese_fonts:
            try:
                if os.path.exists(font_path):
                    self.font_japanese = pygame.font.Font(font_path, 28)
                    print(f"日本語フォントを読み込みました: {font_path}")
                    break
                else:
                    # システムフォント名で試す
                    self.font_japanese = pygame.font.SysFont(font_path, 28)
                    if self.font_japanese:
                        print(f"システムフォントを読み込みました: {font_path}")
                        break
            except:
                continue
        
        # フォールバック
        if not self.font_japanese:
            self.font_japanese = pygame.font.Font(None, 32)
            print("日本語フォントが見つかりません。英語表記を使用します。")
    
    def test_japanese_font(self) -> bool:
        """日本語フォントが正しく動作するかテスト"""
        if not self.font_japanese:
            return False
        
        try:
            # テスト用の日本語文字をレンダリング
            test_surface = self.font_japanese.render("王", True, COLORS['BLACK'])
            return True
        except:
            return False
    
    def get_piece_display_text(self, piece_str: str) -> str:
        """駒の表示テキストを取得"""
        # vプレフィックスを除去
        clean_piece = piece_str.replace('v', '').strip()
        
        if clean_piece in self.piece_display:
            if self.use_japanese:
                return self.piece_display[clean_piece]['jp']
            else:
                return self.piece_display[clean_piece]['en']
        
        # フォールバック
        return clean_piece if clean_piece else '?'
    
    def screen_to_board_pos(self, screen_x: int, screen_y: int) -> Optional[Tuple[int, int]]:
        """スクリーン座標を盤面座標に変換"""
        board_x = screen_x - self.BOARD_OFFSET_X
        board_y = screen_y - self.BOARD_OFFSET_Y
        
        if 0 <= board_x < self.BOARD_SIZE and 0 <= board_y < self.BOARD_SIZE:
            col = board_x // self.CELL_SIZE
            row = board_y // self.CELL_SIZE
            return (row, col)
        return None
    
    def board_to_screen_pos(self, row: int, col: int) -> Tuple[int, int]:
        """盤面座標をスクリーン座標に変換"""
        x = self.BOARD_OFFSET_X + col * self.CELL_SIZE
        y = self.BOARD_OFFSET_Y + row * self.CELL_SIZE
        return (x, y)
    
    def draw_board(self):
        """将棋盤を描画"""
        # 背景
        self.screen.fill(COLORS['BACKGROUND'])
        
        # 将棋盤の背景
        board_rect = pygame.Rect(
            self.BOARD_OFFSET_X, self.BOARD_OFFSET_Y,
            self.BOARD_SIZE, self.BOARD_SIZE
        )
        pygame.draw.rect(self.screen, COLORS['BOARD'], board_rect)
        
        # 格子線を描画
        for i in range(10):  # 0から9まで（10本の線）
            # 縦線
            x = self.BOARD_OFFSET_X + i * self.CELL_SIZE
            pygame.draw.line(
                self.screen, COLORS['GRID'],
                (x, self.BOARD_OFFSET_Y),
                (x, self.BOARD_OFFSET_Y + self.BOARD_SIZE), 2
            )
            
            # 横線
            y = self.BOARD_OFFSET_Y + i * self.CELL_SIZE
            pygame.draw.line(
                self.screen, COLORS['GRID'],
                (self.BOARD_OFFSET_X, y),
                (self.BOARD_OFFSET_X + self.BOARD_SIZE, y), 2
            )
    
    def draw_coordinates(self):
        """座標を描画"""
        # 列番号（9-1）
        for col in range(9):
            text = self.font_medium.render(str(9 - col), True, COLORS['TEXT'])
            x = self.BOARD_OFFSET_X + col * self.CELL_SIZE + self.CELL_SIZE // 2 - text.get_width() // 2
            y = self.BOARD_OFFSET_Y - 25
            self.screen.blit(text, (x, y))
        
        # 行番号（1-9）
        for row in range(9):
            text = self.font_medium.render(str(row + 1), True, COLORS['TEXT'])
            x = self.BOARD_OFFSET_X - 25
            y = self.BOARD_OFFSET_Y + row * self.CELL_SIZE + self.CELL_SIZE // 2 - text.get_height() // 2
            self.screen.blit(text, (x, y))
    
    def draw_highlights(self):
        """ハイライトを描画"""
        # 選択された駒のハイライト
        if self.selected_pos:
            row, col = self.selected_pos
            x, y = self.board_to_screen_pos(row, col)
            highlight_rect = pygame.Rect(x, y, self.CELL_SIZE, self.CELL_SIZE)
            pygame.draw.rect(self.screen, COLORS['SELECTED'], highlight_rect, 3)
        
        # 可能な移動先のハイライト
        for row, col in self.possible_moves:
            x, y = self.board_to_screen_pos(row, col)
            highlight_rect = pygame.Rect(x + 5, y + 5, self.CELL_SIZE - 10, self.CELL_SIZE - 10)
            pygame.draw.rect(self.screen, COLORS['POSSIBLE_MOVE'], highlight_rect, 2)
    
    def draw_pieces(self):
        """駒を描画"""
        for row in range(9):
            for col in range(9):
                piece = self.game.board[row][col]
                if piece:
                    self.draw_piece(piece, row, col)
    
    def draw_piece(self, piece: ShogiPiece, row: int, col: int):
        """個別の駒を描画"""
        x, y = self.board_to_screen_pos(row, col)
        center_x = x + self.CELL_SIZE // 2
        center_y = y + self.CELL_SIZE // 2
        
        # 駒の背景（五角形風の形）
        piece_color = COLORS['WHITE']
        piece_rect = pygame.Rect(x + 5, y + 5, self.CELL_SIZE - 10, self.CELL_SIZE - 10)
        pygame.draw.rect(self.screen, piece_color, piece_rect)
        pygame.draw.rect(self.screen, COLORS['BLACK'], piece_rect, 2)
        
        # 駒の文字を取得
        piece_str = str(piece).strip()
        display_text = self.get_piece_display_text(piece_str)
        
        # 色を決定
        if piece_str.startswith('v'):
            color = COLORS['RED']  # 後手は赤色
        else:
            color = COLORS['BLACK']  # 先手は黒色
        
        # テキストをレンダリング
        text = self.font_japanese.render(display_text, True, color)
        text_rect = text.get_rect(center=(center_x, center_y))
        
        # 後手の駒は上下反転
        if piece.player == 2:
            text = pygame.transform.rotate(text, 180)
            text_rect = text.get_rect(center=(center_x, center_y))
        
        self.screen.blit(text, text_rect)
    
    def draw_status(self):
        """ゲーム状態を描画"""
        # ゲーム状態を取得
        game_status = self.game.get_game_status()
        
        # 現在のプレイヤー
        if self.use_japanese:
            player_text = "先手の番" if self.game.current_player == 1 else "後手の番"
            text = self.font_japanese.render(player_text, True, COLORS['TEXT'])
        else:
            player_text = "Player 1 Turn" if self.game.current_player == 1 else "Player 2 Turn"
            text = self.font_large.render(player_text, True, COLORS['TEXT'])
        
        self.screen.blit(text, (10, 10))
        
        # 王手の表示
        y_offset = 40
        if game_status['player1_in_check']:
            if self.use_japanese:
                check_text = "⚠️ 先手王手！"
                text = self.font_japanese.render(check_text, True, COLORS['RED'])
            else:
                check_text = "⚠️ Player 1 in Check!"
                text = self.font_medium.render(check_text, True, COLORS['RED'])
            self.screen.blit(text, (10, y_offset))
            y_offset += 25
        
        if game_status['player2_in_check']:
            if self.use_japanese:
                check_text = "⚠️ 後手王手！"
                text = self.font_japanese.render(check_text, True, COLORS['RED'])
            else:
                check_text = "⚠️ Player 2 in Check!"
                text = self.font_medium.render(check_text, True, COLORS['RED'])
            self.screen.blit(text, (10, y_offset))
        
        # 詰みの表示
        if game_status['game_over']:
            if game_status['winner'] == 1:
                if self.use_japanese:
                    winner_text = "🎉 先手の勝利！"
                    text = self.font_japanese.render(winner_text, True, COLORS['BLUE'])
                else:
                    winner_text = "🎉 Player 1 Wins!"
                    text = self.font_large.render(winner_text, True, COLORS['BLUE'])
            elif game_status['winner'] == 2:
                if self.use_japanese:
                    winner_text = "🎉 後手の勝利！"
                    text = self.font_japanese.render(winner_text, True, COLORS['BLUE'])
                else:
                    winner_text = "🎉 Player 2 Wins!"
                    text = self.font_large.render(winner_text, True, COLORS['BLUE'])
            
            # 勝利メッセージを中央に表示
            text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, 100))
            self.screen.blit(text, text_rect)
        
        # 持ち駒表示
        self.draw_captured_pieces()
    
    def draw_captured_pieces(self):
        """持ち駒を描画"""
        # 先手の持ち駒（下側）
        y_pos = self.BOARD_OFFSET_Y + self.BOARD_SIZE + 20
        
        if self.use_japanese:
            label_text = "先手持ち駒:"
            text = self.font_japanese.render(label_text, True, COLORS['TEXT'])
        else:
            label_text = "Player 1 Captured:"
            text = self.font_medium.render(label_text, True, COLORS['TEXT'])
        
        self.screen.blit(text, (self.BOARD_OFFSET_X, y_pos))
        
        x_offset = self.BOARD_OFFSET_X + 150
        for i, piece in enumerate(self.game.captured_pieces[1]):
            piece_text = self.get_piece_display_text(str(piece).strip())
            text = self.font_japanese.render(piece_text, True, COLORS['BLACK'])
            self.screen.blit(text, (x_offset + i * 35, y_pos))
        
        # 後手の持ち駒（上側）
        y_pos = self.BOARD_OFFSET_Y - 40
        
        if self.use_japanese:
            label_text = "後手持ち駒:"
            text = self.font_japanese.render(label_text, True, COLORS['TEXT'])
        else:
            label_text = "Player 2 Captured:"
            text = self.font_medium.render(label_text, True, COLORS['TEXT'])
        
        self.screen.blit(text, (self.BOARD_OFFSET_X, y_pos))
        
        x_offset = self.BOARD_OFFSET_X + 150
        for i, piece in enumerate(self.game.captured_pieces[2]):
            piece_text = self.get_piece_display_text(str(piece).strip())
            text = self.font_japanese.render(piece_text, True, COLORS['RED'])
            self.screen.blit(text, (x_offset + i * 35, y_pos))
    
    def draw_promotion_dialog(self):
        """成り選択ダイアログを描画"""
        if self.promotion_dialog:
            # ダイアログ背景
            dialog_rect = pygame.Rect(
                self.WINDOW_WIDTH // 2 - 120, self.WINDOW_HEIGHT // 2 - 60,
                240, 120
            )
            pygame.draw.rect(self.screen, COLORS['WHITE'], dialog_rect)
            pygame.draw.rect(self.screen, COLORS['BLACK'], dialog_rect, 3)
            
            # テキスト（日本語フォントを使用）
            if self.use_japanese:
                text1 = self.font_japanese.render("成りますか？", True, COLORS['TEXT'])
                text2 = self.font_japanese.render("Y: 成る  N: 成らない", True, COLORS['TEXT'])
            else:
                text1 = self.font_medium.render("Promote piece?", True, COLORS['TEXT'])
                text2 = self.font_small.render("Y: Promote  N: Don't promote", True, COLORS['TEXT'])
            
            text1_rect = text1.get_rect(center=(dialog_rect.centerx, dialog_rect.y + 30))
            text2_rect = text2.get_rect(center=(dialog_rect.centerx, dialog_rect.y + 70))
            
            self.screen.blit(text1, text1_rect)
            self.screen.blit(text2, text2_rect)
    
    def is_valid_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """移動が有効かチェック"""
        if not self.game.is_valid_position(from_row, from_col) or not self.game.is_valid_position(to_row, to_col):
            return False
        
        piece = self.game.board[from_row][from_col]
        if not piece or piece.player != self.game.current_player:
            return False
        
        # 移動可能かチェック
        valid_moves = self.game.get_piece_moves(from_row, from_col)
        return (to_row, to_col) in valid_moves
    
    def can_promote(self, piece: ShogiPiece, from_row: int, to_row: int) -> bool:
        """成ることができるかチェック"""
        return self.game._can_promote(piece, to_row)
    
    def move_piece_with_promotion(self, from_row: int, from_col: int, to_row: int, to_col: int, promote: bool):
        """成り選択付きで駒を移動"""
        if not self.is_valid_move(from_row, from_col, to_row, to_col):
            return False
        
        piece = self.game.board[from_row][from_col]
        
        # 移動が自分の王を王手に晒すかチェック
        captured_piece = self.game.board[to_row][to_col]
        self.game.board[to_row][to_col] = piece
        self.game.board[from_row][from_col] = None
        
        if self.game.is_in_check(self.game.current_player):
            # 移動を元に戻す
            self.game.board[from_row][from_col] = piece
            self.game.board[to_row][to_col] = captured_piece
            print("その移動は自分の王を王手に晒すため無効です。")
            return False
        
        # 移動を元に戻してから正式に実行
        self.game.board[from_row][from_col] = piece
        self.game.board[to_row][to_col] = captured_piece
        
        # 相手の駒を取る場合
        if captured_piece:
            # 持ち駒に追加（成りを解除）
            captured_piece.promoted = False
            self.game.captured_pieces[self.game.current_player].append(captured_piece)
        
        # 駒を移動
        self.game.board[to_row][to_col] = piece
        self.game.board[from_row][from_col] = None
        
        # 成り処理
        if promote:
            piece.promoted = True
        
        # プレイヤー交代
        self.game.current_player = 2 if self.game.current_player == 1 else 1
        return True
    
    def handle_click(self, pos: Tuple[int, int]):
        """マウスクリックを処理"""
        board_pos = self.screen_to_board_pos(pos[0], pos[1])
        
        if not board_pos:
            return
        
        row, col = board_pos
        
        if self.selected_pos is None:
            # 駒を選択
            piece = self.game.board[row][col]
            if piece and piece.player == self.game.current_player:
                self.selected_pos = (row, col)
                # 可能な移動先を計算
                self.possible_moves = self.game.get_piece_moves(row, col)
        else:
            # 移動を試行
            from_row, from_col = self.selected_pos
            
            if (row, col) == self.selected_pos:
                # 同じ駒をクリック - 選択解除
                self.selected_pos = None
                self.possible_moves = []
            elif self.is_valid_move(from_row, from_col, row, col):
                # 有効な移動
                piece = self.game.board[from_row][from_col]
                
                # 成りの判定
                can_promote = self.can_promote(piece, from_row, row)
                
                if can_promote:
                    self.promotion_dialog = {
                        'from': (from_row, from_col),
                        'to': (row, col),
                        'piece': piece
                    }
                else:
                    # 移動実行
                    self.move_piece_with_promotion(from_row, from_col, row, col, False)
                    self.selected_pos = None
                    self.possible_moves = []
            else:
                # 無効な移動 - 新しい駒を選択
                piece = self.game.board[row][col]
                if piece and piece.player == self.game.current_player:
                    self.selected_pos = (row, col)
                    self.possible_moves = self.game.get_piece_moves(row, col)
                else:
                    self.selected_pos = None
                    self.possible_moves = []
    
    def handle_promotion_input(self, promote: bool):
        """成り選択を処理"""
        if self.promotion_dialog:
            from_pos = self.promotion_dialog['from']
            to_pos = self.promotion_dialog['to']
            
            self.move_piece_with_promotion(from_pos[0], from_pos[1], to_pos[0], to_pos[1], promote)
            
            self.promotion_dialog = None
            self.selected_pos = None
            self.possible_moves = []
    
    def run(self):
        """メインゲームループ"""
        running = True
        
        print("=== 将棋ゲーム / Shogi Game ===")
        print(f"日本語フォント使用: {'はい' if self.use_japanese else 'いいえ (英語表記を使用)'}")
        print("操作方法:")
        print("- マウスで駒を選択・移動")
        print("- 成り選択: Y/N キー")
        print("- 終了: ESC キー")
        print("=" * 30)
        
        while running:
            # ゲーム状態をチェック
            game_status = self.game.get_game_status()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左クリック
                        if not self.promotion_dialog and not game_status['game_over']:
                            self.handle_click(event.pos)
                
                elif event.type == pygame.KEYDOWN:
                    if self.promotion_dialog:
                        if event.key == pygame.K_y:
                            self.handle_promotion_input(True)
                        elif event.key == pygame.K_n:
                            self.handle_promotion_input(False)
                    
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
                    # ゲーム終了後にスペースキーで再開
                    if game_status['game_over'] and event.key == pygame.K_SPACE:
                        self.game = ShogiBoard()
                        self.selected_pos = None
                        self.possible_moves = []
                        self.promotion_dialog = None
            
            # 描画
            self.draw_board()
            self.draw_coordinates()
            self.draw_highlights()
            self.draw_pieces()
            self.draw_status()
            
            if self.promotion_dialog:
                self.draw_promotion_dialog()
            
            # ゲーム終了時の追加メッセージ
            if game_status['game_over']:
                if self.use_japanese:
                    restart_text = "スペースキーで再開 / ESCで終了"
                    text = self.font_japanese.render(restart_text, True, COLORS['TEXT'])
                else:
                    restart_text = "Press SPACE to restart / ESC to quit"
                    text = self.font_medium.render(restart_text, True, COLORS['TEXT'])
                
                text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, 130))
                self.screen.blit(text, text_rect)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

def main():
    """メイン関数"""
    game = PyGameShogi()
    game.run()

if __name__ == "__main__":
    main()
