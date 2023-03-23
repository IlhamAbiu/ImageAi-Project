from PyQt6.QtCore import QRect, QMetaObject, QCoreApplication
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtWidgets import QSpinBox, QWidget, QPushButton, QLabel, QMenuBar, \
    QMenu, QHBoxLayout, QTableWidget
from pylab import *


class MainView(object):
    def setupUi(self, main_view):
        main_view.setObjectName("MainWindow")
        main_view.resize(1920, 1024)
        self.centralwidget = QWidget(main_view)
        self.centralwidget.setObjectName("centralwidget")
        self.widget = QWidget(self.centralwidget)
        self.widget.setGeometry(QRect(30, 30, 720, 470))
        self.widget.setObjectName("widget")

        # виджет отображения видео
        self.video = QLabel(self.widget)
        self.video.setGeometry(QRect(0, 0, 720, 405))
        self.video.setObjectName("video")

        # кнопка воспроизвести
        self.play = QPushButton(self.widget)
        self.play.setGeometry(QRect(300, 405, 90, 30))
        font = QFont()
        font.setPointSize(10)
        self.play.setFont(font)
        self.play.setObjectName("play")

        #  кнопка остановить
        self.pause = QPushButton(self.widget)
        self.pause.setGeometry(QRect(300, 405, 90, 30))
        font = QFont()
        font.setPointSize(10)
        self.pause.setFont(font)
        self.pause.setObjectName("pause")

        # кнопка запись видео
        self.recording = QPushButton(self.widget)
        self.recording.setGeometry(QRect(220, 405, 90, 30))
        font = QFont()
        font.setPointSize(10)
        self.recording.setFont(font)
        self.recording.setObjectName("recording")

        # кнопка воспроизведения записанного видео
        self.play_record_video = QPushButton(self.widget)
        self.play_record_video.setGeometry(QRect(570, 405, 90, 30))
        font = QFont()
        font.setPointSize(10)
        self.play_record_video.setFont(font)
        self.play_record_video.setObjectName("play_record_video")

        # Подпись того, что идет запись экрана
        self.text_record = QLabel(self.widget)
        font = QFont()
        font.setPointSize(10)
        self.text_record.setFont(font)
        self.text_record.setGeometry(QRect(150, 405, 420, 30))

        # кнопка сделать фото
        self.shot_photo = QPushButton(self.widget)
        self.shot_photo.setGeometry(QRect(320, 405, 90, 30))
        font = QFont()
        font.setPointSize(10)
        self.shot_photo.setFont(font)
        self.shot_photo.setObjectName("shot_photo")

        # Виджет для отображение контента, который был обработан Imageai
        self.widget_2 = QWidget(self.centralwidget)
        self.widget_2.setGeometry(QRect(790, 30, 720, 470))
        self.widget_2.setObjectName("widget_2")

        # Отображение контента после обработки
        self.res = QLabel(self.widget_2)
        self.res.setGeometry(QRect(0, 0, 720, 405))
        self.res.setText("")
        self.res.setObjectName("res")

        # кнопка воспроизвести
        self.play_2 = QPushButton(self.widget_2)
        self.play_2.setGeometry(QRect(220, 405, 90, 30))
        font = QFont()
        font.setPointSize(10)
        self.play_2.setFont(font)
        self.play_2.setObjectName("play2")

        # кнопка остановить
        self.pause_2 = QPushButton(self.widget_2)
        self.pause_2.setGeometry(QRect(320, 405, 90, 30))
        font = QFont()
        font.setPointSize(10)
        self.pause_2.setFont(font)
        self.pause_2.setObjectName("pause2")

        # кнопка воспроизвести заново
        self.play_again = QPushButton(self.widget_2)
        self.play_again.setGeometry(QRect(420, 405, 90, 30))
        font = QFont()
        font.setPointSize(10)
        self.play_again.setFont(font)
        self.play_again.setObjectName("play_again")


        # основной виджет
        self.widget_3 = QWidget(self.centralwidget)
        self.widget_3.setGeometry(QRect(0, 520, 1920, 500))
        self.widget_3.setObjectName("widget_3")

        # кнопка чтобы активировать Imageai
        self.algo = QPushButton(self.widget_3)
        self.algo.setGeometry(QRect(800, 0, 90, 30))
        font = QFont()
        font.setPointSize(10)
        self.algo.setFont(font)
        self.algo.setObjectName("algo")
        self.algo.setVisible(False)

        # Виджет, чтобы ввести точность совпадения
        self.widget1 = QWidget(self.widget_3)
        self.widget1.setGeometry(QRect(550, 0, 200, 30))
        self.widget1.setObjectName("widget1")
        self.widget1.setVisible(False)

        # Приветствие пользователя
        self.greeting = QLabel(self.centralwidget)
        font = QFont()
        font.setPointSize(22)
        self.greeting.setFont(font)
        self.greeting.setGeometry(QRect(450, 0, 900, 28))
        self.greeting.setText("Для начала работы выберите файл, с которым вы хотите поработать!")

        self.horizontalLayout = QHBoxLayout(self.widget1)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # текст точность совпадения
        self.label = QLabel(self.widget1)
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)

        # место ввода порога определения объектов
        self.probability = QSpinBox(self.widget1)
        self.probability.setObjectName("probability")
        self.probability.setValue(80)
        self.horizontalLayout.addWidget(self.probability)

        # Таблица отображения результатов
        self.tableWidget = QTableWidget(self.widget_3)
        self.tableWidget.setGeometry(QRect(500, 70, 480, 220))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setVisible(False)

        # Подпись таблицы с отображением результатов
        self.label_2 = QLabel(self.widget_3)
        self.label_2.setGeometry(QRect(650, 40, 150, 20))
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_2.setVisible(False)

        # Таблица 2 для отображение поиска определенных элементов
        self.tableWidget_2 = QTableWidget(self.widget_3)
        self.tableWidget_2.setGeometry(QRect(100, 70, 300, 220))
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.setColumnCount(0)
        self.tableWidget_2.setRowCount(0)
        self.tableWidget_2.setVisible(False)

        # Таблица 3 для задания условия для поиска элементов
        self.tableWidget_3 = QTableWidget(self.widget_3)
        self.tableWidget_3.setGeometry(QRect(1020, 70, 480, 220))
        self.tableWidget_3.setObjectName("tableWidget_3")
        self.tableWidget_3.setColumnCount(0)
        self.tableWidget_3.setRowCount(0)
        self.tableWidget_3.setVisible(False)

        # меню вверхнее
        main_view.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(main_view)
        self.menubar.setGeometry(QRect(0, 0, 1600, 26))
        self.menubar.setObjectName("menubar")
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")
        self.menu_3 = QMenu(self.menubar)
        self.menu_3.setObjectName("menu_3")
        self.menu_4 = QMenu(self.menubar)
        self.menu_4.setObjectName("menu_4")
        main_view.setMenuBar(self.menubar)

        self.action = QAction(main_view)
        self.action.setObjectName("action")
        self.action_2 = QAction(main_view)
        self.action_2.setObjectName("action_2")
        self.action_3 = QAction(main_view)
        self.action_3.setObjectName("action_3")
        self.action_4 = QAction(main_view)
        self.action_4.setObjectName("action_4")
        self.action_5 = QAction(main_view)
        self.action_5.setObjectName("action_5")
        self.action_6 = QAction(main_view)
        self.action_6.setObjectName("action_6")

        self.menu.addAction(self.action)
        self.menu.addAction(self.action_2)
        self.menu_2.addAction(self.action_3)
        self.menu_2.addAction(self.action_4)
        self.menu_3.addAction(self.action_5)
        self.menu_4.addAction(self.action_6)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())
        self.menubar.addAction(self.menu_3.menuAction())
        self.menubar.addAction(self.menu_4.menuAction())

        self.retranslateUi(main_view)
        QMetaObject.connectSlotsByName(main_view)

    def retranslateUi(self, main_view):
        _translate = QCoreApplication.translate
        main_view.setWindowTitle(_translate("MainWindow", ""))
        self.play.setText(_translate("MainWindow", "▶"))
        self.pause.setText(_translate("MainWindow", "||"))
        self.recording.setText(_translate("MainWindow", "☉"))
        self.play_record_video.setText(_translate("MainWindow", "play"))
        self.text_record.setText(_translate("MainWindow", "Идет запись видео..."))
        self.shot_photo.setText(_translate("MainWindow", "Сделать фото"))
        self.play_2.setText(_translate("MainWindow", "▶"))
        self.pause_2.setText(_translate("MainWindow", "||"))
        self.play_again.setText(_translate("MainWindow", "⟳"))
        self.algo.setText(_translate("MainWindow", "Выполнить"))
        self.label.setText(_translate("MainWindow", "Точность совпадения:"))
        self.label_2.setText(_translate("MainWindow", "Найденные объекты"))
        self.menu.setTitle(_translate("MainWindow", "Источник медиа"))
        self.menu_2.setTitle(_translate("MainWindow", "Найти объекты"))
        self.menu_3.setTitle(_translate("MainWindow", "Правила наблюдения"))
        self.menu_4.setTitle(_translate("MainWindow", "Редактор изображений"))
        self.action.setText(_translate("MainWindow", "Выбрать медиафайл"))
        self.action_2.setText(_translate("MainWindow", "Запустить веб камеру"))
        self.action_3.setText(_translate("MainWindow", "Все"))
        self.action_4.setText(_translate("MainWindow", "Некоторые"))
        self.action_5.setText(_translate("MainWindow", "Формирование условий"))
        self.action_6.setText(_translate("MainWindow", "Открыть редактор"))

