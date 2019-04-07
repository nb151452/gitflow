from abc import ABCMeta, abstractmethod
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from figures import *


class StatePainter:
    """ Базовый класс состояния графического редактора.

    В разных состояниях графический редактор по-разному
    реагирует на нажатие и отпускание клавиши мыши, а также
    передвижение мыши.

    """

    __mataclass__ = ABCMeta

    def __init__(self, painter):
        self.painter = painter

    @abstractmethod
    def mousePressEvent(self, event):
        """Обработчик нажатия клавиши мыши"""
        pass

    @abstractmethod
    def mouseReleaseEvent(self, event):
        """Обработчик отпускания клавиши мыши"""
        pass

    @abstractmethod
    def mouseMoveEvent(self, event):
        """Обработчик передвижения мыши"""
        pass


class StatePainterAddFigure(StatePainter):
    """Состояние редактора, позволяющее добавлять разные фигуры.

    Можно изменять размер фигуры при ее создании. Для этого нужно,
    не отпуская клавишу мыши передвигать ею до тех пор, пока
    вас не устроит полученный размер фигуры. Фигура добавляется после
    отпускания клавиши мыши.

    """

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.start_point = event.scenePos()
            self.last_point = event.scenePos()

            self.figure = self.painter.curr_figure()
            self.figure.setStartPoint(self.start_point)
            self.figure.setPen(self.painter.curr_pen)
            command = CommandAddFigure(self.painter, self.figure)
            command.execute()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            self.last_point = event.scenePos()
            self.figure.resize(self.last_point)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False


class StatePainterDrawing(StatePainter):
    """ Состояние графическое редактора, позволяющее рисовать различные кривые.
    Каждая кривая фактически представляет собой линии длиной в 1px.
    """

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.start_point = event.scenePos()
            self.list_line = list()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            line = QGraphicsLineItem(
                QLineF(self.start_point, event.scenePos()))
            line.setPen(self.painter.curr_pen)
            self.list_line.append(line)
            self.painter.addItem(line)
            self.start_point = event.scenePos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
            command = CommandAddCurve(self.painter, self.list_line)


class PainterCommand:
    """ Базовый класс команд графического редактора."""

    def __init__(self, painter):
        self.painter = painter

    def execute(self):
        pass


class CommandChangeColorPen(PainterCommand):

    def execute(self, color: QColor):
        self.painter.curr_pen.setColor(color)


class CommandChangeState(PainterCommand):

    def execute(self, figure: Figure):
        if figure:
            self.painter.curr_state = self.painter.state_add_figure
        else:
            self.painter.curr_state = self.painter.state_drawing
        self.painter.curr_figure = figure


class CommandChangeWidthPen(PainterCommand):

    def execute(self, width: int):
        self.painter.curr_pen.setWidth(width)


class CommandAddFigure(PainterCommand):

    def __init__(self, painter, figure):
        super().__init__(painter)
        self.figure = figure

    def execute(self):
        self.painter.addItem(self.figure)


class CommandAddCurve(PainterCommand):

    def __init__(self, painter, list_line):
        super().__init__(painter)
        self.list_line = list_line

    def execute(self):
        for line in self.list_line:
            self.painter.addItem(line)


class Painter(QtWidgets.QGraphicsScene):
    BACKGROUND_COLOR = Qt.white

    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 545, 400)

        # установка заднего фона редактора
        color = self.BACKGROUND_COLOR
        brush = QBrush(color)
        self.setBackgroundBrush(brush)

        # состояния редактора
        self.state_add_figure = StatePainterAddFigure(self)
        self.state_drawing = StatePainterDrawing(self)

        # установка начального состояния
        self._curr_pen_color = Qt.red
        self._curr_pen_width = 2

        self.curr_pen = QPen(self._curr_pen_color)
        self.curr_pen.setWidth(self._curr_pen_width)

        self.curr_figure = Line
        self.curr_state = self.state_drawing

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.curr_state.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.curr_state.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.curr_state.mouseReleaseEvent(event)


class CentralWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.painter = Painter()
        self.view = QtWidgets.QGraphicsView(self.painter, self)
        self.view.setSceneRect(0, 0, 500, 350)
        self.view.centerOn(0, 0)

        # команды редактора
        self.command_change_state = CommandChangeState(self.painter)
        self.command_change_color_pen = CommandChangeColorPen(self.painter)
        self.command_change_width_pen = CommandChangeWidthPen(self.painter)

        self.initUI()

    def initUI(self):
        main_vertical_box = QtWidgets.QVBoxLayout()
        main_vertical_box.addWidget(self.view)

        btn_box = QtWidgets.QHBoxLayout()
        self.btn_add_rectangle = QtWidgets.QPushButton('Прямоугольник')
        self.btn_add_triangle = QtWidgets.QPushButton('Треугольник')
        self.btn_add_line = QtWidgets.QPushButton('Линия')
        self.btn_add_ellipse = QtWidgets.QPushButton('Эллипс')
        self.btn_drawing = QtWidgets.QPushButton('Рисование')

        btn_box_settings = QtWidgets.QHBoxLayout()
        self.btn_color = QtWidgets.QPushButton('Цвет')
        self.btn_width = QtWidgets.QPushButton('Толщина')
        self.btn_clear = QtWidgets.QPushButton('Очистить')
        self.btn_save = QtWidgets.QPushButton('Сохранить')

        btn_box.addWidget(self.btn_add_rectangle)
        btn_box.addWidget(self.btn_add_triangle)
        btn_box.addWidget(self.btn_add_line)
        btn_box.addWidget(self.btn_add_ellipse)
        btn_box.addWidget(self.btn_drawing)

        btn_box_settings.addWidget(self.btn_color)
        btn_box_settings.addWidget(self.btn_width)
        btn_box_settings.addWidget(self.btn_clear)
        btn_box_settings.addWidget(self.btn_save)

        self.btn_add_rectangle.clicked.connect(self.btnAddScquareHandler)
        self.btn_add_triangle.clicked.connect(self.btnAddTrianglelHandler)
        self.btn_add_line.clicked.connect(self.btnAddLineHandler)
        self.btn_drawing.clicked.connect(self.btnDrawingHandler)
        self.btn_add_ellipse.clicked.connect(self.btnAddEllipseHandler)

        self.btn_color.clicked.connect(self.btnColorHandler)
        self.btn_width.clicked.connect(self.btnWidthHandler)
        self.btn_clear.clicked.connect(self.btnClearHandler)
        self.btn_save.clicked.connect(self.btnSaveHandler)

        main_vertical_box.addLayout(btn_box)
        main_vertical_box.addLayout(btn_box_settings)
        self.setLayout(main_vertical_box)

    def btnAddScquareHandler(self):
        self.command_change_state.execute(Rectangle)

    def btnAddTrianglelHandler(self):
        self.command_change_state.execute(Triangle)

    def btnAddLineHandler(self):
        self.command_change_state.execute(Line)

    def btnDrawingHandler(self):
        self.command_change_state.execute(None)

    def btnAddEllipseHandler(self):
        self.command_change_state.execute(Ellipse)

    def btnClearHandler(self):
        self.painter.clear()
        self.painter._index = -1

    def btnColorHandler(self):
        color = QtWidgets.QColorDialog.getColor(
            parent=self, title='Выберете цвет')
        if color.isValid():
            self.command_change_color_pen.execute(color)

    def btnWidthHandler(self):
        n, ok = QtWidgets.QInputDialog.getInt(self, 'Введите толщину пера',
                                              'Текст подсказки', value=self.painter._curr_pen_width,
                                              min=1, max=10, step=2)
        if ok:
            self.command_change_width_pen.execute(n)

    def btnSaveHandler(self):
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Image", "", "PNG(*.png);;JPEG(*.jpg *.jpeg);; ALL Files(*.*)")
        if file_path == "":
            return
        pixmap = self.view.grab()
        pixmap.save(file_path)


class Editor(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()

    def initWindow(self):
        central_widget = CentralWidget()
        self.setCentralWidget(central_widget)
        self.setWindowTitle('PyQt5')
        self.show()
