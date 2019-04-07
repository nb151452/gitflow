import sys
from graphic_editor import *

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)  # создаем экземпляр приложения
    editor = Editor()  # создаем экземпляр редактора
    sys.exit(app.exec_())  # запускаем цикл приложения
