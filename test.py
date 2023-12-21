import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton, QGraphicsView, \
    QGraphicsScene, QGraphicsPixmapItem, QListWidget
from PyQt5.QtCore import Qt, QEventLoop
import chess.pgn
import chess.svg
import io
from PyQt5.QtGui import QPixmap


class ChessboardWidget(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.showing_moves = False
        self.current_board = None
        self.cell_size = None

        self.scene = QGraphicsScene(self)
        self.scene.mousePressEvent = lambda e: self.on_mouse_press(e)

        self.setScene(self.scene)

        self.rects = dict()

        # Загрузка изображений фигур
        self.piece_images = {
            chess.Piece(chess.PAWN, chess.WHITE): QPixmap("piece_images\\w_pawn_png_128px.png"),
            chess.Piece(chess.KNIGHT, chess.WHITE): QPixmap("piece_images\\w_knight_png_128px.png"),
            chess.Piece(chess.BISHOP, chess.WHITE): QPixmap("piece_images\\w_bishop_png_128px.png"),
            chess.Piece(chess.ROOK, chess.WHITE): QPixmap("piece_images\\w_rook_png_128px.png"),
            chess.Piece(chess.QUEEN, chess.WHITE): QPixmap("piece_images\\w_queen_png_128px.png"),
            chess.Piece(chess.KING, chess.WHITE): QPixmap("piece_images\\w_king_png_128px.png"),
            chess.Piece(chess.PAWN, chess.BLACK): QPixmap("piece_images\\b_pawn_png_128px.png"),
            chess.Piece(chess.KNIGHT, chess.BLACK): QPixmap("piece_images\\b_knight_png_128px.png"),
            chess.Piece(chess.BISHOP, chess.BLACK): QPixmap("piece_images\\b_bishop_png_128px.png"),
            chess.Piece(chess.ROOK, chess.BLACK): QPixmap("piece_images\\b_rook_png_128px.png"),
            chess.Piece(chess.QUEEN, chess.BLACK): QPixmap("piece_images\\b_queen_png_128px.png"),
            chess.Piece(chess.KING, chess.BLACK): QPixmap("piece_images\\b_king_png_128px.png"),
        }

    def draw_board(self, board):
        self.current_board = board

        # Очистим сцену перед отрисовкой нового положения
        self.scene.clear()

        # Определение размеров ячейки
        cell_size = min(self.width() // 8, self.height() // 8)
        self.cell_size = cell_size

        # Отрисовка шахматной доски
        for row in range(8):
            for col in range(8):
                rect = self.scene.addRect(col * cell_size, row * cell_size, cell_size, cell_size)
                color = Qt.lightGray if (row + col) % 2 == 0 else Qt.darkGray
                rect.setBrush(color)
                self.rects[(7 - row) * 8 + col] = rect

        # Отрисовка фигур
        for row in range(8):
            for col in range(8):
                square = chess.square(col, 7 - row)
                piece = board.piece_at(square)
                if piece is not None:
                    image = self.piece_images[piece]
                    image = image.scaled(cell_size, cell_size, Qt.KeepAspectRatio)
                    item = QGraphicsPixmapItem(image)
                    item.setPos(col * cell_size, row * cell_size)
                    self.scene.addItem(item)

    def on_mouse_press(self, event):
        if self.showing_moves:
            self.draw_board(self.current_board)

        col, row = event.scenePos().x() // self.cell_size, event.scenePos().y() // self.cell_size
        clicked_square = chess.square(int(col), int(7 - row))

        for move in self.current_board.legal_moves:
            if move.from_square == clicked_square:
                self.showing_moves = True

                next_board = self.current_board.copy()
                next_board.push(move)
                if next_board.is_attacked_by(next_board.turn, move.to_square):
                    self.rects[move.to_square].setBrush(Qt.red)
                else:
                    self.rects[move.to_square].setBrush(Qt.yellow)


class ChessApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chess Game")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.layout.addWidget(self.text_edit)

        self.load_button = QPushButton("Load Game")
        self.load_button.clicked.connect(self.load_game)
        self.layout.addWidget(self.load_button)

        self.save_button = QPushButton("Save Game")
        self.save_button.clicked.connect(self.save_game)
        self.layout.addWidget(self.save_button)

        self.browse_button = QPushButton("Browse Games")
        self.browse_button.clicked.connect(self.browse_games)
        self.layout.addWidget(self.browse_button)

        self.chessboard_widget = ChessboardWidget()
        self.layout.addWidget(self.chessboard_widget)

        self.central_widget.setLayout(self.layout)

    def load_game(self):
        game_description = self.text_edit.toPlainText()
        board = chess.Board()
        game = chess.pgn.read_game(io.StringIO(game_description))

        for move in game.mainline_moves():
            board.push(move)
            self.chessboard_widget.draw_board(board)

    def save_game(self):
        connection = sqlite3.connect('chess.db')
        cursor = connection.cursor()

        cursor.execute(f'''
        INSERT INTO Games(notation)
        VALUES ('{self.text_edit.toPlainText()}')
        ''')

        connection.commit()
        connection.close()

    def browse_games(self):
        games_list = GamesList(self.text_edit)
        games_list.show()
        loop = QEventLoop()
        games_list.destroyed.connect(loop.quit)
        loop.exec()


class GamesList(QListWidget):
    def __init__(self, text_edit):
        super().__init__()
        self.setStyleSheet('font-size: 14px')

        self.text_edit = text_edit

        connection = sqlite3.connect('chess.db')
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM Games')
        games = cursor.fetchall()

        connection.close()

        self.games_dict = dict()
        for game in games:
            name = "Game " + str(game[0])
            self.games_dict[name] = game
            self.addItem(name)

        self.itemDoubleClicked.connect(self.select_game)

    def select_game(self, item):
        self.text_edit.setPlainText(self.games_dict[item.text()][1])
        self.close()


def db_init():
    connection = sqlite3.connect('chess.db')
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Games (
    id INTEGER PRIMARY KEY,
    notation TEXT NOT NULL
    )
    ''')

    connection.commit()
    connection.close()


if __name__ == "__main__":
    db_init()
    app = QApplication(sys.argv)
    window = ChessApp()
    window.show()
    sys.exit(app.exec_())
