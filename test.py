import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import Qt
import chess.pgn
import chess.svg
import io
from PyQt5.QtGui import QPixmap

class ChessboardWidget(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Загрузка изображений фигур
        self.piece_images = {
            chess.Piece(chess.PAWN, chess.WHITE): QPixmap("piece_images\white_pawn.png"),
            chess.Piece(chess.KNIGHT, chess.WHITE): QPixmap("piece_images\white_knight.png"),
            chess.Piece(chess.BISHOP, chess.WHITE): QPixmap("piece_images\white_bishop.png"),
            chess.Piece(chess.ROOK, chess.WHITE): QPixmap("piece_images\white_rook.png"),
            chess.Piece(chess.QUEEN, chess.WHITE): QPixmap("piece_images\white_queen.png"),
            chess.Piece(chess.KING, chess.WHITE): QPixmap("piece_images\white_king.png"),
            chess.Piece(chess.PAWN, chess.BLACK): QPixmap("piece_images\\black_pawn.png"),
            chess.Piece(chess.KNIGHT, chess.BLACK): QPixmap("piece_images\\black_knight.png"),
            chess.Piece(chess.BISHOP, chess.BLACK): QPixmap("piece_images\\black_bishop.png"),
            chess.Piece(chess.ROOK, chess.BLACK): QPixmap("piece_images\\black_rook.png"),
            chess.Piece(chess.QUEEN, chess.BLACK): QPixmap("piece_images\\black_queen.png"),
            chess.Piece(chess.KING, chess.BLACK): QPixmap("piece_images\\black_king.png"),
        }

    def draw_board(self, board):
        # Очистим сцену перед отрисовкой нового положения
        self.scene.clear()

        # Определение размеров ячейки
        cell_size = min(self.width() // 8, self.height() // 8)

        # Отрисовка шахматной доски
        for row in range(8):
            for col in range(8):
                rect = self.scene.addRect(col * cell_size, row * cell_size, cell_size, cell_size)
                color = Qt.lightGray if (row + col) % 2 == 0 else Qt.darkGray
                rect.setBrush(color)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChessApp()
    window.show()
    sys.exit(app.exec_())
