from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsLineItem
from PyQt5.QtWidgets import QGraphicsPolygonItem, QGraphicsEllipseItem
from PyQt5.QtCore import QPointF, QRectF, QLineF
from PyQt5.QtGui import QPolygonF, QPen


class Figure:
    """Базовый класс фигур. Все фигуры определяются
    прямоугольной областью, в которой они рисуются.
    """

    def resize(self):
        pass

    def _getRect(self, point_end: QPointF):
        """Функция вычисляет прямоугольную область, в которую
        нужно будет нарисовать фигуру. Это прямоугольная область
        меняется, когда пользователь изменяет мышкой размер фигуры.
        """
        start = self.start_point
        width = point_end.x() - start.x()
        height = point_end.y() - start.y()

        if width >= 0 and height <= 0:
            rect = QRectF(QPointF(start.x(), point_end.y()),
                          QPointF(point_end.x(), start.y()))
        elif width >= 0 and height >= 0:
            rect = QRectF(start, point_end)
        elif width <= 0 and height >= 0:
            rect = QRectF(QPointF(point_end.x(), start.y()),
                          QPointF(start.x(), point_end.y()))
        else:
            rect = QRectF(point_end, start)

        return rect

    def setStartPoint(self, start_point):
        self.start_point = start_point

    def setPen(self, pen: QPen):
        self.setPen(pen)


class Rectangle(QGraphicsRectItem, Figure):

    def __init__(self):
        super().__init__()

    def resize(self, point_end: QPointF):
        if self.start_point is None:
            return
        rect = self._getRect(point_end)
        self.setRect(rect)


class Triangle(QGraphicsPolygonItem, Figure):

    def __init__(self):
        super().__init__()

    def resize(self, point_end):
        if self.start_point is None:
            return
        rect = self._getRect(point_end)
        point1 = QPointF(rect.x(), rect.y() + rect.height())
        point2 = QPointF(rect.x() + rect.width(), rect.y() + rect.height())
        point3 = QPointF((2 * rect.x() + rect.width()) // 2, rect.y())
        polygon = QPolygonF([point1, point2, point3])
        self.setPolygon(polygon)


class Ellipse(QGraphicsEllipseItem, Figure):

    def __init__(self):
        super().__init__()

    def resize(self, point_end):
        if self.start_point is None:
            return
        rect = self._getRect(point_end)
        self.setRect(rect)


class Line(QGraphicsLineItem, Figure):

    def __init__(self):
        super().__init__()

    def resize(self, point_end):
        if self.start_point is None:
            return
        line = QLineF(self.start_point, point_end)
        self.setLine(line)
