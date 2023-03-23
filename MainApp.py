import subprocess

import cv2
import openpyxl
from PIL import Image, ImageQt
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage, QIcon
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QHBoxLayout, QFileDialog, QTableWidgetItem, \
    QCheckBox, QComboBox, \
    QMessageBox
from imageai.Detection import ObjectDetection, VideoObjectDetection
from pylab import *

import numpy
from View.EditImageView import EditImageView
from View.MainView import MainView


class ImageViewer(QLabel):

    def __init__(self, path, pixmap="", factor=0):
        print("ImageViewer init")
        super().__init__()
        self.path = path
        if factor == 0:
            pix_map = QPixmap(path)
        else:
            pix_map = pixmap
        self.setPixmap(pix_map)
        self.scale_factor = 2.0

    def _update(self, path=''):
        print("_update")
        pix_map = QPixmap(path)
        self.setPixmap(pix_map)

    def set_pixmap(self, pixmap):
        print('set_pixmap')
        self.setPixmap(pixmap)

    def scale_image(self, factor):
        print('scale_image')
        self.scale_factor *= factor
        pix_max = self.pixmap()
        width = int(self.scale_factor * pix_max.width())
        height = int(self.scale_factor * pix_max.height())
        self.setPixmap(pix_max.scaled(width, height, QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                      QtCore.Qt.TransformationMode.SmoothTransformation))


class ImageEditor(QMainWindow):
    def __init__(self, parent=None):
        print("ImageEditor init")
        QWidget.__init__(self, parent)
        super(ImageEditor, self).__init__(parent)
        self.parent = parent
        self.image_path = ""
        self.color_pixmap = ""
        self.lru = []
        self.lru_contrast = []
        self.lru_solar = []
        self.lru_bin = []
        self.lru_dis = []
        self.lru_den = []
        self.chosen_points = []
        self.inter = EditImageView()
        self.inter.setupUi(self)
        self.inter.pushButton_Enhance.clicked.connect(self.Zoom_in)
        self.inter.pushButton_Reduce.clicked.connect(self.Zoom_out)
        self.inter.pushButton_Undo.clicked.connect(self.undo)
        self.inter.pushButton_Finish.clicked.connect(self.finish)
        self.inter.pushButton_Init.clicked.connect(self.initial_image)
        self.inter.action_Open.triggered.connect(self.open_image)
        self.inter.action_Save.triggered.connect(self.save_image)
        self.inter.pushButton_Frame.clicked.connect(self.get_frame)
        self.inter.action_Gray.triggered[bool].connect(self.checker)
        self.inter.button_LinearContrast.pressed.connect(self.expand_coolapse_LS)
        self.inter.button_Denoise.pressed.connect(self.expand_coolapse_DN)
        self.inter.button_Dissection.pressed.connect(self.expand_coolapse_D)
        self.inter.button_Solarization.pressed.connect(self.expand_coolapse_S)
        self.inter.button_Binarization.pressed.connect(self.expand_coolapse_B)

        self.inter.Implement_LC.clicked.connect(self.linear_contrast)
        self.inter.Implement_S.clicked.connect(self.solarization)
        self.inter.Implement_B.clicked.connect(self.binarization)
        self.inter.Implement_D.clicked.connect(self.dissection)

        self.inter.sld_h.valueChanged[int].connect(self.denoise)  ##########################
        self.inter.sld_tws.valueChanged[int].connect(self.denoise)  ##########################
        self.inter.sld_stw.valueChanged[int].connect(self.denoise)  ##########################

        self.inter.undo_DN.clicked.connect(self.undo_denoise)

        self.inter.undo_LC.clicked.connect(self.undo_contrast)
        self.inter.undo_S.clicked.connect(self.undo_solar)
        self.inter.undo_B.clicked.connect(self.undo_binarization)
        self.inter.undo_D.clicked.connect(self.undo_dis)
        self.label = ""

    def denoise(self):
        print("denoise")
        # Кэширование старого значения
        self.lru_den.append(self.label.pixmap().toImage())
        if len(self.lru_den) > 5:
            del self.lru_den[0]
        # Преобразование в Image модуля PIL из ImageQt
        pil_image = ImageQt.fromqimage(self.label.pixmap().toImage())
        # Получение набора пикселей
        pil_arrray = numpy.array(pil_image)

        h_val = self.inter.sld_h.value()  # + 30
        # print(h_val, '))))')
        tws_val = self.inter.sld_tws.value() + 2
        stw_val = self.inter.sld_stw.value() + 2

        # copy_pixels = numpy.copy(pil_arrray).astype('uint8')#int)
        copy_pixels = cv2.fastNlMeansDenoising(
            pil_arrray,
            templateWindowSize=tws_val,
            searchWindowSize=stw_val,
            h=float(h_val)
        )

        img = Image.fromarray(copy_pixels.astype('uint8'))
        pix = self.pil2pixmap(img)
        self.label.set_pixmap(pix)

    def close_checker(self):
        print("close_checker")
        if self.inter.Implement_LC.isVisible():
            self.expand_coolapse_LS()
        elif self.inter.Implement_DN.isVisible():
            self.expand_coolapse_DN()
        elif self.inter.Implement_S.isVisible():
            self.expand_coolapse_S()
        elif self.inter.Implement_B.isVisible():
            self.expand_coolapse_B()
        elif self.inter.Implement_D.isVisible():
            self.expand_coolapse_D()

    def undo_contrast(self):
        """
        Возвращение к предыдущему изображению относительно контрастности
        """
        print('undo_contrast')
        if len(self.lru_contrast) != 0:
            self.label.set_pixmap(QPixmap.fromImage(self.lru_contrast[-1]))
            del self.lru_contrast[-1]

    def undo_solar(self):
        """
        Возвращение к предыдущему изображению относительно соляризации
        """
        print('undo_solar')
        if len(self.lru_solar) != 0:
            self.label.set_pixmap(QPixmap.fromImage(self.lru_solar[-1]))
            del self.lru_solar[-1]

    def undo_binarization(self):
        print('undo_binarization')
        """
        Возвращение к предыдущему изображению относительно бинаризации
        """
        if len(self.lru_bin) != 0:
            self.label.set_pixmap(QPixmap.fromImage(self.lru_bin[-1]))
            del self.lru_bin[-1]

    def undo_denoise(self):
        """
        Возвращение к предыдущему изображению относительно удаления шума
        """
        print('undo_denoise')
        if len(self.lru_den) != 0:
            self.label.set_pixmap(QPixmap.fromImage(self.lru_den[-1]))
            del self.lru_den[-1]

    def undo_dis(self):
        """
        Возвращение к предыдущему изображению относительно препарирования
        """
        print('undo_dis')
        if len(self.lru_dis) != 0:
            self.label.set_pixmap(QPixmap.fromImage(self.lru_dis[-1]))
            del self.lru_dis[-1]

    def linear_contrast(self):
        print('linear_contrast')
        """
        Функция линейного контрастирования
        """
        # Кэширование старого значения
        self.lru_contrast.append(self.label.pixmap().toImage())
        if len(self.lru_contrast) > 5:
            del self.lru_contrast[0]
        # Преобразование в Image модуля PIL из ImageQt
        pil_image = ImageQt.fromqimage(self.label.pixmap().toImage())
        # Получение набора пикселей
        pil_arrray = numpy.array(pil_image)
        # Нижняя граница диапазона яркостей текущего изображения
        f_min = pil_arrray.min()
        # Верхняя граница диапазона яркостей текущего изображения
        f_max = pil_arrray.max()
        g_min_text = self.inter.g_min_textbox.text()
        # Желаемая нижняя граница диапазона яркостей
        g_min = 0 if not g_min_text.isnumeric() else int(g_min_text)
        g_max_text = self.inter.g_max_textbox.text()
        # Желаемая верхняя граница диапазона яркостей
        g_max = 255 if not g_max_text.isnumeric() else int(g_max_text)
        if g_min > g_max:
            raise Exception("g_max должен быть больше g_min")
        copy_pixels = numpy.copy(pil_arrray).astype(int)
        # Формула попиксельного повышения контрастности
        new_pixels = numpy.round((copy_pixels - f_min) / (f_max - f_min) * (g_max - g_min) + g_min, 0).astype(int)
        new_pixels = numpy.clip(new_pixels[:, :, :], 0, 255)
        img = Image.fromarray(new_pixels.astype('uint8'))
        pix = self.pil2pixmap(img)
        self.label.set_pixmap(pix)

    def solarization(self):
        print('solarization')
        """
        Функция соляризации
        """
        # Кэширование старого значения
        self.lru_solar.append(self.label.pixmap().toImage())
        if len(self.lru_solar) > 5:
            del self.lru_solar[0]
        # Преобразование в Image модуля PIL из ImageQt
        pil_image = ImageQt.fromqimage(self.label.pixmap().toImage())
        # Получение набора пикселей
        pil_arrray = numpy.array(pil_image)
        # Верхняя граница диапазона яркостей текущего изображения
        f_max = pil_arrray.max()
        k_text = self.inter.k_textbox.text()
        # Константный параметр соляризации (по умолчанию берется значение,
        # при котором g_max = f_max
        k = 4 / f_max if not k_text.replace('.', '', 1).isnumeric() else float(k_text)
        self.inter.k_textbox.setText(str(k))
        copy_pixels = numpy.copy(pil_arrray).astype(int)
        # Формула соляризации
        new_pixels = numpy.round(k * copy_pixels * (f_max - copy_pixels)).astype(int)
        new_pixels = numpy.clip(new_pixels[:, :, :], 0, 255)
        img = Image.fromarray(new_pixels.astype('uint8'))
        pix = self.pil2pixmap(img)
        self.label.set_pixmap(pix)

    def binarization(self):
        print('binarization')
        """
        Функция бинаризации
        """
        # Кэширование старого значения
        self.lru_bin.append(self.label.pixmap().toImage())
        if len(self.lru_bin) > 5:
            del self.lru_bin[0]
        # Преобразование в Image модуля PIL из ImageQt
        pil_image = ImageQt.fromqimage(self.label.pixmap().toImage())
        # Получение набора пикселей
        pil_arrray = numpy.array(pil_image)
        # Нижняя граница диапазона яркостей текущего изображения
        f_min = pil_arrray.min()
        # Верхняя граница диапазона яркостей текущего изображения
        f_max = pil_arrray.max()
        threshold_text = self.inter.threshold_textbox.text()
        # Значение параметра - граница
        threshold = (int(f_min) + int(f_max)) // 2 if not threshold_text.isnumeric() else int(threshold_text)
        self.inter.threshold_textbox.setText(str(threshold))
        copy_pixels = numpy.copy(pil_arrray).astype(int)
        # Формула бинаризации
        _indices = np.where(copy_pixels < threshold)
        copy_pixels[_indices] = 0
        _indices = np.where(copy_pixels >= threshold)
        copy_pixels[_indices] = 255
        img = Image.fromarray(copy_pixels.astype('uint8'))
        pix = self.pil2pixmap(img)
        self.label.set_pixmap(pix)

    def dissection(self):
        print('dissection')
        """
        Функция препарирования
        """
        # Кэширование старого значения
        self.lru_dis.append(self.label.pixmap().toImage())
        if len(self.lru_dis) > 5:
            del self.lru_dis[0]
        # Преобразование в Image модуля PIL из ImageQt
        pil_image = ImageQt.fromqimage(self.label.pixmap().toImage())
        # Получение набора пикселей
        pil_arrray = numpy.array(pil_image)
        # Нижняя граница диапазона яркостей текущего изображения
        f_min = pil_arrray.min()
        # Верхняя граница диапазона яркостей текущего изображения
        f_max = pil_arrray.max()
        low_border_text = self.inter.low_border_textbox.text()
        # Желаемая нижняя граница диапазона яркостей
        low_border = 0 if not low_border_text.isnumeric() else int(low_border_text)
        high_border_text = self.inter.high_border_textbox.text()
        # Желаемая верхняя граница диапазона яркостей
        high_border = 255 if not high_border_text.isnumeric() else int(high_border_text)
        if low_border > high_border:
            raise Exception("g_max должен быть больше g_min")
        copy_pixels = numpy.copy(pil_arrray).astype(int)
        # 1 этап препарирования:  линейное контрастирование
        new_pixels = numpy.round((copy_pixels - f_min) / (f_max - f_min) * 255, 0).astype(int)
        new_pixels = numpy.clip(new_pixels[:, :, :], 0, 255)
        # 2 этап препарирования:  задание черного фона
        _indices = np.where((new_pixels < low_border) | (new_pixels > high_border))
        new_pixels[_indices] = 0
        img = Image.fromarray(new_pixels.astype('uint8'))
        pix = self.pil2pixmap(img)
        self.label.set_pixmap(pix)

    def expand_coolapse_DN(self):
        print('expand_coolapse_DN')
        if self.inter.Implement_DN.isVisible():
            # Сокрытие формы настройки удаления шумов
            self.inter.scrollArea_3.setVisible(False)
            self.inter.Implement_DN.setVisible(False)
            self.inter.undo_DN.setVisible(False)
            self.inter.h_label.setVisible(False)
            self.inter.sld_h.setVisible(False)
            self.inter.tws_label.setVisible(False)
            self.inter.sld_tws.setVisible(False)
            self.inter.stw_label.setVisible(False)
            self.inter.sld_stw.setVisible(False)
        else:
            # Открытие формы настройки удаления шумов
            self.close_checker()
            self.inter.scrollArea_3.setVisible(True)
            self.inter.Implement_DN.setVisible(True)
            self.inter.undo_DN.setVisible(True)
            self.inter.h_label.setVisible(True)
            self.inter.sld_h.setVisible(True)
            self.inter.tws_label.setVisible(True)
            self.inter.sld_tws.setVisible(True)
            self.inter.stw_label.setVisible(True)
            self.inter.sld_stw.setVisible(True)

    def expand_coolapse_LS(self):
        print('expand_coolapse_LS')
        if self.inter.Implement_LC.isVisible():
            # Сокрытие формы настройки контрастирования
            self.inter.scrollArea_3.setVisible(False)
            self.inter.g_min_label.setVisible(False)
            self.inter.g_max_label.setVisible(False)
            self.inter.g_min_textbox.setVisible(False)
            self.inter.g_max_textbox.setVisible(False)
            self.inter.undo_LC.setVisible(False)
            self.inter.Implement_LC.setVisible(False)
        else:
            # Открытие формы настройки контрастирования
            self.close_checker()
            self.inter.scrollArea_3.setVisible(True)
            self.inter.g_min_label.setVisible(True)
            self.inter.g_max_label.setVisible(True)
            self.inter.g_min_textbox.setVisible(True)
            self.inter.g_max_textbox.setVisible(True)
            self.inter.undo_LC.setVisible(True)
            self.inter.Implement_LC.setVisible(True)
            self.inter.button_LinearContrast.setIcon(QIcon('Black_active.png'))

    def expand_coolapse_S(self):
        print('expand_coolapse_S')
        if self.inter.Implement_S.isVisible():
            # Сокрытие формы настройки соляризации
            self.inter.scrollArea_3.setVisible(False)
            self.inter.k_label.setVisible(False)
            self.inter.k_textbox.setVisible(False)
            self.inter.undo_S.setVisible(False)
            self.inter.Implement_S.setVisible(False)
            # self.inter.button_Solarization.setIcon(QIcon('Black_triangle.svg'))
        else:
            # Открытие формы настройки соляризации
            self.close_checker()
            self.inter.scrollArea_3.setVisible(True)
            self.inter.k_label.setVisible(True)
            self.inter.k_textbox.setVisible(True)
            self.inter.undo_S.setVisible(True)
            self.inter.Implement_S.setVisible(True)
            # self.inter.button_Solarization.setIcon(QIcon('Black_active.png'))

    def expand_coolapse_B(self):
        print('expand_coolapse_B')
        if self.inter.Implement_B.isVisible():
            # Сокрытие формы настройки бинаризации
            self.inter.scrollArea_3.setVisible(False)
            self.inter.threshold_label.setVisible(False)
            self.inter.threshold_textbox.setVisible(False)
            self.inter.undo_B.setVisible(False)
            self.inter.Implement_B.setVisible(False)
            # self.inter.button_Binarization.setIcon(QIcon('Black_triangle.svg'))
        else:
            # Открытие формы настройки бинаризации
            self.close_checker()
            self.inter.scrollArea_3.setVisible(True)
            self.inter.threshold_label.setVisible(True)
            self.inter.threshold_textbox.setVisible(True)
            self.inter.undo_B.setVisible(True)
            self.inter.Implement_B.setVisible(True)
            # self.inter.button_Binarization.setIcon(QIcon('Black_active.png'))

    def expand_coolapse_D(self):
        print('expand_coolapse_D')
        if self.inter.Implement_D.isVisible():
            # Сокрытие формы настройки препарирования
            self.inter.scrollArea_3.setVisible(False)
            self.inter.low_border_label.setVisible(False)
            self.inter.high_border_label.setVisible(False)
            self.inter.low_border_textbox.setVisible(False)
            self.inter.high_border_textbox.setVisible(False)
            self.inter.undo_D.setVisible(False)
            self.inter.Implement_D.setVisible(False)
            # self.inter.button_Dissection.setIcon(QIcon('Black_triangle.svg'))
        else:
            # Открытие формы настройки препарирования
            self.close_checker()
            self.inter.scrollArea_3.setVisible(True)
            self.inter.low_border_label.setVisible(True)
            self.inter.high_border_label.setVisible(True)
            self.inter.low_border_textbox.setVisible(True)
            self.inter.high_border_textbox.setVisible(True)
            self.inter.undo_D.setVisible(True)
            self.inter.Implement_D.setVisible(True)
            # self.inter.button_Dissection.setIcon(QIcon('Black_active.png'))

    def checker(self, active):
        print('checker')
        """
        Логика включения/выключения режима "Оттенки серого"
        """
        # Флаг активации режима "Оттенки серого"
        if active:
            self.inter.toolBar.setVisible(True)
            if self.image_path != "":
                self.color_pixmap = self.label.pixmap()
                # Преобразование в Image модуля PIL из ImageQt
                pil_image = ImageQt.fromqimage(self.label.pixmap().toImage())
                # Получение набора пикселей
                pil_arrray = numpy.array(pil_image)
                # Cливаем в один канал цвета для получения кадра в серых тонах
                gray_image = cv2.cvtColor(pil_arrray, cv2.COLOR_BGR2GRAY)
                # Преобразование в Image модуля PIL из набора пикселей
                img = Image.fromarray(gray_image)
                pix = self.pil2pixmap(img)
                self.label.set_pixmap(pix)
        else:
            self.inter.toolBar.setVisible(False)
            if self.image_path != "":
                self.label.set_pixmap(self.color_pixmap)

    def initial_image(self):
        print('initial_image')
        """
        Возвращение к исходному изображению
        """
        self.label = ImageViewer(self.image_path)
        self.label.scale_factor = 0.5
        self.inter.scrollArea.setWidget(self.label)

    def get_frame(self):
        print('get_frame')
        """
        Вырезка изображения
        """
        fig, ax = plt.subplots()
        self.lru.append(self.label.pixmap().toImage())
        if len(self.lru) > 5:
            del self.lru[0]
        im = array(ImageQt.fromqimage(self.label.pixmap().toImage()))
        ax.imshow(im)
        # Демонстрация графика с изображением
        plt.show()
        while True:
            # Ожидание выставления пользователем точек
            self.chosen_points = ginput(2)
            if self.chosen_points[0][0] < self.chosen_points[1][0] and self.chosen_points[0][1] < self.chosen_points[1][
                1]:
                pil_image = ImageQt.fromqimage(self.label.pixmap().toImage())
                # Формирование границ нового изображения
                box = self.chosen_points[0] + self.chosen_points[1]
                # Извлечение нужного куска изображения
                region = pil_image.crop(box)
                pix = self.pil2pixmap(region)
                self.label.set_pixmap(pix)
                break
        plt.close()

    def Zoom_in(self):
        print('zoom_in')
        """
        Увеличение изображения
        """
        factor = 1.25
        # Аудит действий
        self.lru.append(self.label.pixmap().toImage())
        if len(self.lru) > 5:
            del self.lru[0]
        # Масштабирование изображения по переданному множителю
        self.label.scale_image(factor)
        # Растяжение scrollbarов
        self.adjust_scroll_bar(self.inter.scrollArea.horizontalScrollBar(), factor)
        self.adjust_scroll_bar(self.inter.scrollArea.verticalScrollBar(), factor)

    def Zoom_out(self):
        print('zoom_out')
        """
        Уменьшение изображения
        """
        factor = 0.8
        # Аудит действий
        self.lru.append(self.label.pixmap().toImage())
        if len(self.lru) > 5:
            del self.lru[0]
        # Масштабирование изображения по переданному множителю
        self.label.scale_image(factor)
        # Растяжение scrollbarов
        self.adjust_scroll_bar(self.inter.scrollArea.horizontalScrollBar(), factor)
        self.adjust_scroll_bar(self.inter.scrollArea.verticalScrollBar(), factor)

    def adjust_scroll_bar(self, scroll_bar, factor):
        print('adjust_scroll_bar')
        scroll_bar.setValue(
            int(factor * scroll_bar.value() + ((factor - 1) * scroll_bar.pageStep() / 2)))

    def undo(self):
        print('undo')
        """
        Возвращение к предыдущему изображению
        """
        if len(self.lru) != 0:
            self.label.set_pixmap(QPixmap.fromImage(self.lru[-1]))
            del self.lru[-1]

    def finish(self):
        print('finish')
        im = self.label.pixmap().toImage()
        # Сохранение изображения
        im.save("editor_image.jpg")
        # Закрытие дочернего окна
        self.close()
        self.destroy()
        # Открытие изображения в родительском окне для последующего анализа
        self.parent.open_file_by_path("editor_image.jpg")

    def pil2pixmap(self, im):
        print('pil2pixmap')
        if im.mode == "RGB":
            r, g, b = im.split()
            im = Image.merge("RGB", (b, g, r))
        elif im.mode == "RGBA":
            r, g, b, a = im.split()
            im = Image.merge("RGBA", (b, g, r, a))
        elif im.mode == "L":
            im = im.convert("RGBA")
        im2 = im.convert("RGBA")
        data = im2.tobytes("raw", "RGBA")
        qim = QImage(data, im.size[0], im.size[1], QImage.Format.Format_ARGB32)
        pixmap = QPixmap.fromImage(qim)
        return pixmap

    def open_image(self):
        print('open_image')
        dialog = QtWidgets.QFileDialog()
        options = dialog.options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image file", os.getcwd(),
                                                   "*.jpg *.jpeg ", options=options)
        if not file_name:
            return
        self.image_path = file_name
        self.label = ImageViewer(file_name)
        self.label.scale_factor = 1.0
        self.inter.scrollArea.setWidget(self.label)

    def save_image(self):
        print('save_image')
        now = datetime.datetime.now()
        name = str(now.year) + "_" + str(now.month) + "_" + str(now.day) + "_" + \
               str(now.hour) + "_" + str(now.minute) + "_" + str(now.second) + ".jpg"
        im = self.label.pixmap().toImage()
        im.save(name)


class DetectionForm(QMainWindow):
    all_frames = 0
    cur_frame = 0

    def __init__(self, parent=None):
        self.flag_camera = False
        print("DetectionForm init")
        QWidget.__init__(self, parent)
        super(DetectionForm, self).__init__(parent)
        self.ui = MainView()
        self.ui.setupUi(self)
        self.is_video = False
        self.is_web = False
        self.path = ""
        self.dict_video = {}

        self.Web = Web()
        self.Im = Im()
        self.all_flags = True
        self.Web.ImageUpdate.connect(self.update_image)
        self.Im.int_value_1.connect(self.f)
        self.Im.int_value_2.connect(self.f1)
        self.Im.int_value_3.connect(self.f2)
        self.translations = {}
        self.reverse_translations = {}
        self.conditions = False

        self.running = True
        self.running_res = True

        self.ui.play.setVisible(False)
        self.ui.pause.setVisible(False)
        self.ui.recording.setVisible(False)
        self.ui.play_record_video.setVisible(False)
        self.ui.shot_photo.setVisible(False)
        self.ui.text_record.setVisible(False)
        self.ui.play_again.setVisible(False)
        self.ui.play_2.setVisible(False)
        self.ui.pause_2.setVisible(False)

        self.ui.action.triggered.connect(self.open_file)
        self.ui.action_2.triggered.connect(self.camera)
        self.ui.action_3.triggered.connect(self.all_objects)
        self.ui.action_4.triggered.connect(self.some_objects)
        self.ui.action_5.triggered.connect(self.create_conditions)
        self.ui.action_6.triggered.connect(self.open_editor)
        self.ui.algo.clicked.connect(self.execute_algorithm)
        self.ui.play.clicked.connect(self.play)
        self.ui.pause.clicked.connect(self.pause)
        self.ui.play_again.clicked.connect(self.play_again)
        self.ui.shot_photo.clicked.connect(self.shot_photo_web)
        self.ui.recording.clicked.connect(self.record_video)
        self.ui.play_record_video.clicked.connect(self.play_record)
        self.ui.play_2.clicked.connect(self.play_2)
        self.ui.pause_2.clicked.connect(self.pause_2)

    def open_editor(self):
        print('open_editor')
        self.editor = ImageEditor(self)
        # self.ui.centralwidget.setEnabled(False)
        # self.ui.menubar.setEnabled(False)
        pix = self.ui.video.pixmap()
        # Проверка на открытие изображения/видео в родительском окне
        # В случае открытия видео, в редактор помещается текущий кадр
        if pix is not None:
            self.editor.label = ImageViewer("", pix, 1)
            self.editor.image_path = self.path
            self.editor.label.scale_factor = 1.0
            self.editor.inter.scrollArea.setWidget(self.editor.label)
        self.editor.show()

    def create_conditions(self):
        print('create_conditions')
        # Флаг, отвечающий за применение таблицы с условиями
        self.conditions = True
        # Чтение из  Excel файла
        excel_file = openpyxl.open("db.xlsx", read_only=True)
        sheet = excel_file.active
        # Заполнение словарей объектами с их переводами
        for row in range(1, 6):
            self.translations[sheet[row][0].value] = sheet[row][1].value
            self.reverse_translations[sheet[row][1].value] = sheet[row][0].value

        self.ui.tableWidget_2.setVisible(False)
        self.ui.tableWidget_3.setVisible(True)
        # Указание размерности таблицы
        self.ui.tableWidget_3.setColumnCount(4)
        self.ui.tableWidget_3.setRowCount(0)
        # Формирование заголовков колонок
        self.ui.tableWidget_3.setHorizontalHeaderLabels(["", "Наименование объекта", "Условие", "Количество"])
        # Заполнение таблицы
        for k in self.translations.keys():
            rowPosition = self.ui.tableWidget_3.rowCount()
            widget = QWidget()
            checkbox = QCheckBox()
            checkbox.setCheckState(Qt.CheckState.Unchecked)
            layoutH = QHBoxLayout(widget)
            layoutH.addWidget(checkbox)
            layoutH.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layoutH.setContentsMargins(0, 0, 0, 0)
            widget2 = QWidget()
            cb = QComboBox()
            # Формирование типов условий
            cb.addItem(">")
            cb.addItem("<")
            cb.addItem("<=")
            cb.addItem(">=")
            cb.addItem("==")
            cb.addItem("!=")
            layoutH = QHBoxLayout(widget2)
            layoutH.addWidget(cb)
            layoutH.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layoutH.setContentsMargins(0, 0, 0, 0)
            self.ui.tableWidget_3.insertRow(rowPosition)
            self.ui.tableWidget_3.setCellWidget(rowPosition, 0, widget)
            self.ui.tableWidget_3.setItem(rowPosition, 1, QTableWidgetItem(str(k)))
            self.ui.tableWidget_3.setCellWidget(rowPosition, 2, widget2)
            self.ui.tableWidget_3.setItem(rowPosition, 3, QTableWidgetItem(str(0)))
        self.ui.tableWidget_3.resizeColumnsToContents()

    def all_objects(self):
        print('all_objects')
        self.all_flags = True
        self.conditions = False
        # self.ui.widget_3.setVisible(False)

    def some_objects(self):
        print('some_objects')
        self.all_flags = False
        self.conditions = False
        # self.ui.widget_3.setVisible(False)
        # Чтение из  Excel файла
        excel_file = openpyxl.open("db.xlsx", read_only=True)
        sheet = excel_file.active
        # Заполнение словарей объектами с их переводами
        for row in range(1, 6):
            self.translations[sheet[row][0].value] = sheet[row][1].value
            self.reverse_translations[sheet[row][1].value] = sheet[row][0].value
        self.ui.tableWidget_2.setVisible(True)
        self.ui.tableWidget_3.setVisible(False)
        # Указание размерности таблицы
        self.ui.tableWidget_2.setColumnCount(2)
        self.ui.tableWidget_2.setRowCount(0)
        # Формирование заголовков колонок
        self.ui.tableWidget_2.setHorizontalHeaderLabels(["", "Наименование объекта"])
        # Заполнение таблицы
        for k in self.translations.keys():
            rowPosition = self.ui.tableWidget_2.rowCount()
            widget = QWidget()
            checkbox = QCheckBox()
            checkbox.setCheckState(Qt.CheckState.Unchecked)
            layoutH = QHBoxLayout(widget)
            layoutH.addWidget(checkbox)
            layoutH.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layoutH.setContentsMargins(0, 0, 0, 0)
            self.ui.tableWidget_2.insertRow(rowPosition)
            self.ui.tableWidget_2.setCellWidget(rowPosition, 0, widget)
            self.ui.tableWidget_2.setItem(rowPosition, 1, QTableWidgetItem(str(k)))
        self.ui.tableWidget_2.resizeColumnsToContents()

    def f(self, s):
        print("f")
        self.ui.label.setText(s)

    def f1(self, d):
        print('f1')
        self.dict_video = d

    def f2(self, f):
        print('f2')
        if f:
            if self.conditions:
                fl = self.checker_video(self.dict_video, self.Im.tuple[1])
                if fl:
                    subprocess.run(["afplay", "/System/Library/Sounds/Submarine.aiff"])
                    QMessageBox.about(self, "Оповещение", "Одно или несколько условий удовлетворены")
            self.ui.tableWidget.setVisible(True)
            self.ui.label_2.setVisible(True)
            if "temp_video" not in self.path:

                self.ui.tableWidget.setColumnCount(3)
                self.ui.tableWidget.setRowCount(0)
                # Формирование заголовков колонок
                self.ui.tableWidget.setHorizontalHeaderLabels(["Номер кадра", "Наименование объекта", "Количество"])
                # Заполнение таблицы
                for k, v in self.dict_video.items():
                    for k1, v2 in v.items():
                        rowPosition = self.ui.tableWidget.rowCount()
                        self.ui.tableWidget.insertRow(rowPosition)
                        self.ui.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(str(k)))
                        self.ui.tableWidget.setItem(rowPosition, 1,
                                                    QTableWidgetItem(self.reverse_translations.get(k1, k1)))
                        self.ui.tableWidget.setItem(rowPosition, 2, QTableWidgetItem(str(v2)))
            else:
                self.ui.tableWidget.setColumnCount(3)
                self.ui.tableWidget.setRowCount(0)
                # Формирование заголовков колонок
                self.ui.tableWidget.setHorizontalHeaderLabels(["Дата", "Наименование объекта", "Количество"])
                # Заполнение таблицы
                for k, v in self.dict_video.items():
                    for k1, v2 in v.items():
                        rowPosition = self.ui.tableWidget.rowCount()
                        self.ui.tableWidget.insertRow(rowPosition)
                        self.ui.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(str(self.Web.web_time[k - 1])))
                        self.ui.tableWidget.setItem(rowPosition, 1,
                                                    QTableWidgetItem(self.reverse_translations.get(k1, k1)))
                        self.ui.tableWidget.setItem(rowPosition, 2, QTableWidgetItem(str(v2)))

            self.ui.tableWidget.resizeColumnsToContents()
            self.ui.play_2.setVisible(True)
            self.ui.pause_2.setVisible(True)
            self.cap = cv2.VideoCapture("new_traffic.mp4")
            self.running_res = True
            self.flag_camera = False
            self.is_video = True
            self.ui.play_2.setVisible(False)
            self.ui.pause_2.setVisible(True)
            self.display_video_stream_res()

    def update_image(self, Image):
        print('update_image')
        self.ui.video.setPixmap(QPixmap.fromImage(Image))

    def abc_play(self, obj, file_name=""):
        print('abc_play')
        try:
            self.is_web = True
            # if file_name == "":
            #     file_name = self.path
            # cap = cv2.VideoCapture(file_name)
            # self.running = True
            # while cap.isOpened() and self.running:
            #     ret, frame = cap.read()
            #     if not ret:
            #         break
            #
            #     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #     img = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
            #     pix = QPixmap.fromImage(img)
            #     pix = pix.scaled(720, 405, Qt.AspectRatioMode.KeepAspectRatio,
            #                      Qt.TransformationMode.SmoothTransformation)
            #     obj.setPixmap(pix)
            #     self.ui.frame = pix
            #
            #     if cv2.waitKey(50) & 0xFF == ord('q'):
            #         break
            #
            # cap.release()
        except Exception as e:
            print(e)

    def play(self):
        self.ui.play.setVisible(False)
        self.ui.pause.setVisible(True)
        print("play")
        if self.flag_camera:
            self.Web.start()
            self.abc_play(self.ui.video)
        else:
            self.running = True
            self.display_video_stream()

    def play_2(self):
        print('play2')
        self.ui.pause_2.setVisible(True)
        self.ui.play_2.setVisible(False)
        self.running_res = True
        self.display_video_stream_res()

    def camera_pause(self, obj):
        print('abc_pause')
        self.is_web = False
        self.ui.play.setVisible(True)
        self.ui.pause.setVisible(False)
        self.Web.stop()
        self.path = "temp_video.avi"

    def shot_photo_web(self):
        self.ui.shot_photo.setVisible(False)
        self.ui.recording.setVisible(False)
        self.ui.pause.setVisible(False)
        self.ui.play.setVisible(False)
        self.is_web = False
        self.Web.shot()
        self.Web.stop()

    def pause(self):
        print("pause")
        self.ui.shot_photo.setVisible(False)
        self.ui.recording.setVisible(False)
        self.ui.pause.setVisible(False)
        self.ui.play.setVisible(True)
        if self.flag_camera:
            self.camera_pause(self.ui.video)
        else:
            self.running = False

    def pause_2(self):
        print('pause2')
        self.ui.pause_2.setVisible(False)
        self.ui.play_2.setVisible(True)
        self.camera_pause(self.ui.res)

    def record_video(self):
        self.ui.recording.setVisible(False)
        self.ui.shot_photo.setVisible(False)
        self.ui.text_record.setVisible(True)
        self.Web.record()
        self.ui.play_record_video.setVisible(True)
        self.ui.text_record.setText('Запись успешно сделана, для воспроизведения ее на экране нажмите play')
        self.path = "output.mp4"

    def camera(self):
        print("camera")
        self.ui.algo.setVisible(True)
        self.ui.widget1.setVisible(True)
        self.flag_camera = True
        self.ui.greeting.setVisible(False)
        self.is_web = True
        self.ui.play.setVisible(False)
        self.ui.pause.setVisible(False)
        self.ui.shot_photo.setVisible(True)
        self.ui.recording.setVisible(True)
        self.Web.start()
        self.display_shot()

    def display_shot(self):
        file_name = '/Users/ilgam/PycharmProjects/imageio/photo.jpg'
        self.path = file_name
        self.cap = cv2.VideoCapture(file_name)
        self.flag_camera = False
        ret, frame = self.cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(img)
        pix = pix.scaled(self.ui.video.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                         QtCore.Qt.TransformationMode.SmoothTransformation)
        self.ui.video.setPixmap(pix)
        self.ui.frame = pix
        self.ui.video.setPixmap(pix)
        self.ui.frame = pix
        self.is_video = False
        self.ui.play.setVisible(False)
        self.ui.pause.setVisible(False)

    def open_file_by_path(self, path):
        print("open_file_by_path")
        try:
            if self.is_web:
                self.Web.stop()
            self.ui.res.clear()
            self.ui.tableWidget.clear()
            self.ui.tableWidget.setVisible(False)
            self.ui.label_2.setVisible(False)

            self.ui.play_2.setVisible(False)
            self.ui.pause_2.setVisible(False)
            self.path = path
            self.ui.video.setPixmap(QPixmap(path))
            self.is_video = False
            self.ui.play.setVisible(False)
            self.ui.pause.setVisible(False)
        except Exception as e:
            print(e)

    def display_video_stream(self):
        ret, frame = self.cap.read()
        if ret and self.running:
            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB, frame)
            pixmap = QPixmap.fromImage(QImage(frame, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888))
            pixmap = pixmap.scaled(self.ui.video.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                   QtCore.Qt.TransformationMode.FastTransformation)
            self.ui.video.setPixmap(pixmap)
            QtCore.QTimer.singleShot(1, self.display_video_stream)

    def display_video_stream_res(self):
        ret, frame = self.cap.read()
        if ret and self.running_res:
            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB, frame)
            pixmap = QPixmap.fromImage(QImage(frame, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888))
            pixmap = pixmap.scaled(self.ui.res.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                   QtCore.Qt.TransformationMode.FastTransformation)
            self.ui.res.setPixmap(pixmap)
            QtCore.QTimer.singleShot(1, self.display_video_stream_res)

    def play_again(self):
        try:
            if self.is_web:
                self.Web.stop()
            self.ui.label_2.setVisible(True)
            self.ui.play_2.setVisible(False)
            self.ui.pause_2.setVisible(True)
            file_name = '/Users/ilgam/PycharmProjects/imageio/new_traffic.mp4'
            self.path = file_name
            self.cap = cv2.VideoCapture(file_name)
            self.running_res = True
            self.flag_camera = False
            self.is_video = True
            self.ui.play_2.setVisible(False)
            self.ui.pause_2.setVisible(True)
            self.display_video_stream_res()
            self.flag_camera = False
            self.is_video = True
        except e:
            pass

    def play_record(self):
        try:
            if self.is_web:
                self.Web.stop()
            self.ui.res.clear()
            self.ui.tableWidget.clear()
            self.ui.tableWidget.setVisible(False)
            self.ui.label_2.setVisible(False)
            self.ui.play_2.setVisible(False)
            self.ui.pause_2.setVisible(False)
            file_name = '/Users/ilgam/PycharmProjects/imageio/output.mp4'
            self.path = file_name
            self.cap = cv2.VideoCapture(file_name)
            self.running = True
            self.flag_camera = False
            self.is_video = True
            self.ui.play.setVisible(False)
            self.ui.pause.setVisible(True)
            self.display_video_stream()
            self.ui.play_record_video.setVisible(False)
            self.ui.text_record.setVisible(False)
        except e:
            pass

    # Открытие медиафайла из памяти
    def open_file(self):
        print('open_file')
        try:
            if self.is_web:
                self.Web.stop()
            self.ui.res.clear()
            self.ui.tableWidget.clear()
            self.ui.tableWidget.setVisible(False)
            self.ui.label_2.setVisible(False)
            self.ui.play_2.setVisible(False)
            self.ui.pause_2.setVisible(False)
            self.ui.greeting.setVisible(False)
            self.ui.algo.setVisible(True)
            self.ui.widget1.setVisible(True)
            dialog = QtWidgets.QFileDialog()
            options = dialog.options()
            file_name, _ = QFileDialog.getOpenFileName(self, "Open Image (Video) file", os.getcwd(),
                                                       "*.jpg *.jpeg *.mp4 *.avi *.mov", options=options)
            print(file_name)
            self.path = file_name
            self.cap = cv2.VideoCapture(file_name)
            self.running = True
            if '.mp4' in file_name or '.mov' in file_name or '.avi' in file_name:
                self.flag_camera = False
                self.is_video = True
                self.ui.play.setVisible(False)
                self.ui.pause.setVisible(True)
                self.display_video_stream()
            else:
                self.flag_camera = False
                ret, frame = self.cap.read()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
                pix = QPixmap.fromImage(img)
                pix = pix.scaled(self.ui.video.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                 QtCore.Qt.TransformationMode.SmoothTransformation)
                self.ui.video.setPixmap(pix)
                self.ui.frame = pix
                self.ui.video.setPixmap(pix)
                self.ui.frame = pix
                self.is_video = False
                self.ui.play.setVisible(False)
                self.ui.pause.setVisible(False)
        except Exception as e:
            print(e)

    def image_proc_all(self):
        print('image_proc_all')
        prob = self.ui.probability.text()
        return self.detector.detectObjectsFromImage(input_image=os.path.join(os.getcwd(), self.path),
                                                    output_image_path=
                                                    os.path.join(os.getcwd(), "new_objects2.jpg"),
                                                    minimum_percentage_probability=0 if not prob.isnumeric()
                                                    else int(prob), )

    def image_proc_some(self):
        print('image_proc_some')
        prob = self.ui.probability.text()
        return self.detector.detectObjectsFromImage(input_image=os.path.join(os.getcwd(), self.path),
                                                    output_image_path=
                                                    os.path.join(os.getcwd(), "new_objects2.jpg"),
                                                    minimum_percentage_probability=0 if not prob.isnumeric()
                                                    else int(prob),
                                                    custom_objects=self.chosen_objects())

    def image_proc_conditions(self, custom):
        print('image_proc_conditions')
        prob = self.ui.probability.text()
        return self.detector.detectObjectsFromImage(input_image=os.path.join(os.getcwd(), self.path),
                                                    output_image_path=
                                                    os.path.join(os.getcwd(), "new_objects2.jpg"),
                                                    minimum_percentage_probability=0 if not prob.isnumeric()
                                                    else int(prob),
                                                    custom_objects=custom)

    def chosen_objects(self):
        print('chosen_objects')
        checked_list = []
        custom = self.detector.CustomObjects()
        print(self.ui.tableWidget_2.rowCount())
        for i in range(self.ui.tableWidget_2.rowCount()):
            print("flag")
            print(self.ui.tableWidget_2.cellWidget(i, 0).findChild(type(QCheckBox())).isChecked())
            if self.ui.tableWidget_2.cellWidget(i, 0).findChild(type(QCheckBox())).isChecked():
                checked_list.append(self.ui.tableWidget_2.item(i, 1).text())
        print(checked_list)
        for i in checked_list:
            print(self.translations[i])
            custom[self.translations[i]] = "valid"
        print(custom)
        return custom

    def chosen_conditions(self):
        print('chosen_conditions')
        checked_list = []
        custom = self.detector.CustomObjects()
        for i in range(self.ui.tableWidget_3.rowCount()):
            if self.ui.tableWidget_3.cellWidget(i, 0).findChild(type(QCheckBox())).isChecked():
                checked_list.append((self.ui.tableWidget_3.item(i, 1).text(),
                                     self.ui.tableWidget_3.cellWidget(i, 2).findChild(
                                         type(QComboBox())).currentText(),
                                     self.ui.tableWidget_3.item(i, 3).text()))
        for i in checked_list:
            custom[self.translations[i[0]]] = "valid"
        return custom, checked_list

    def checker_image(self, d, l):
        print('checker_image')
        for i, j, k in l:
            obj = self.translations[i]

            if eval("".join([str(d[obj]), j, str(k)])):
                return True
        return False

    def checker_video(self, d, l):
        print('checker_video')
        for i, j, k in l:
            obj = self.translations[i]
            for v in d.values():
                if eval("".join([str(v[obj]), j, str(k)])):
                    return True
        return False

    def execute_algorithm(self):
        print('execute_algorithm')
        try:
            if not self.is_video:
                self.detector = ObjectDetection()
                self.detector.setModelTypeAsRetinaNet()
                self.detector.setModelPath(os.path.join(os.getcwd(), "retinanet_resnet50_fpn_coco-eeacb38b.pth"))
                self.detector.loadModel()
                if self.conditions:
                    custom, l = self.chosen_conditions()
                    list = self.image_proc_conditions(custom)
                else:
                    if not self.all_flags:
                        list = self.image_proc_some()
                    else:
                        list = self.image_proc_all()
                # Формирование словаря с наименованием и
                # количеством обнаружененных объектов
                image_dict = {}
                for i in list:
                    if i["name"] not in image_dict:
                        image_dict[i["name"]] = 1
                    else:
                        image_dict[i["name"]] += 1

                if self.conditions:
                    f = self.checker_image(image_dict, l)

                    print(f)
                    if f:
                        subprocess.run(["afplay", "/System/Library/Sounds/Submarine.aiff"])
                        QMessageBox.about(self, "Оповещение", "Одно или несколько условий удовлетворены")
                self.ui.tableWidget.setVisible(True)
                self.ui.label_2.setVisible(True)

                self.ui.tableWidget.setColumnCount(2)
                self.ui.tableWidget.setRowCount(0)
                # Формирование заголовков колонок
                self.ui.tableWidget.setHorizontalHeaderLabels(["Наименование объекта", "Количество"])
                # Заполнение таблицы
                for k, v in image_dict.items():
                    rowPosition = self.ui.tableWidget.rowCount()
                    self.ui.tableWidget.insertRow(rowPosition)
                    if not self.all_flags:
                        self.ui.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(self.reverse_translations[k]))
                    else:
                        self.ui.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(k))
                    self.ui.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(str(v)))

                self.ui.tableWidget.resizeColumnsToContents()
                img = QImage("new_objects2.jpg")
                pix = QPixmap.fromImage(img)
                if img.width() > 720 or img.height() > 405:
                    pix = pix.scaled(720, 405, Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation)
                self.ui.res.setPixmap(pix)
            else:
                self.detector = VideoObjectDetection()
                self.detector.setModelTypeAsRetinaNet()
                self.detector.setModelPath(os.path.join(os.getcwd(), "retinanet_resnet50_fpn_coco-eeacb38b.pth"))
                self.detector.loadModel()
                prob = self.ui.probability.text()
                cap = cv2.VideoCapture(os.path.join(os.getcwd(), self.path))
                DetectionForm.all_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self.Im.path = self.path
                self.Im.all_flags = self.all_flags
                self.Im.conditions = self.conditions
                self.Im.detector = self.detector
                if self.conditions:
                    self.Im.tuple = self.chosen_conditions()
                else:
                    if not self.all_flags:
                        self.Im.chosen_objects = self.chosen_objects()
                self.Im.prob = prob
                self.Im.start()
                # while not self.Im.progress:
                #     continue
                # file_name = '/Users/ilgam/PycharmProjects/imageio/new_traffic.mp4'
                # self.path = file_name
                # self.cap = cv2.VideoCapture(file_name)
                # self.display_video_stream_res()
        except Exception as e:
            print(e)


class Web(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def __init__(self):
        print("web init")
        super(Web, self).__init__()
        self.ui = MainView()
        self.open = True
        self.device_index = 0
        self.fps = 6
        self.fourcc = "mp4v"
        # self.fourcc = "MJPG"
        self.frameSize = (640, 480)
        self.video_filename = "temp_video.mp4"
        self.video_cap = cv2.VideoCapture(self.device_index)
        self.video_writer = cv2.VideoWriter_fourcc(*self.fourcc)
        self.frame_counts = 1
        self.web_time = []

    def run(self):
        print('run')
        self.video_out = cv2.VideoWriter(self.video_filename, self.video_writer, self.fps, self.frameSize)
        self.ThreadActive = True
        while self.ThreadActive:
            ret, frame = self.video_cap.read()
            if ret:
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                flip_img = cv2.flip(img, 1)
                convert_to_qt_format = QImage(flip_img.data, flip_img.shape[1], flip_img.shape[0],
                                              QImage.Format.Format_RGB888)
                pix = convert_to_qt_format.scaled(720, 480, Qt.AspectRatioMode.KeepAspectRatio)
                self.ImageUpdate.emit(pix)
                self.web_time.append(datetime.datetime.now())
                self.video_out.write(frame)
                self.frame_counts += 1
                time.sleep(0.16)

    @staticmethod
    def record():
        cap = cv2.VideoCapture(0)

        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        out = cv2.VideoWriter('output.mp4', fourcc, 30, (1920, 1080))

        for i in range(100):
            ret, frame = cap.read()
            if ret:

                # write the flipped frame
                out.write(frame)
                cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break
        # Release everything if job is finished
        cap.release()
        out.release()
        cv2.destroyAllWindows()

    @staticmethod
    def shot():
        cap = cv2.VideoCapture(0)
        for i in range(15):
            cap.read()
        # делаем снимок и сохраняем его
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        cv2.imwrite('photo.jpg', frame)
        cap.release()
        cv2.destroyAllWindows()

    def stop(self):
        print('stop')
        if self.open:
            self.open = False
            self.ThreadActive = False
            self.video_out.release()
            self.video_cap.release()
            cv2.destroyAllWindows()
            self.quit()


class Im(QThread):
    int_value_1 = pyqtSignal(str)
    int_value_2 = pyqtSignal(dict)
    int_value_3 = pyqtSignal(bool)

    def __init__(self):
        print("Im init")
        super(Im, self).__init__()
        self.path = ""
        self.prob = ""
        self.dict_video = {}
        self.chosen_objects = {}
        self.detector = ""
        self.all_flags = True
        self.conditions = True
        self.tuple = ""
        self.progress = False

    def forFrame(self, frame_number, output_array, output_count):
        print('for frame')
        """
            Формирует данные об объектах и их количестве
            с группировкой по кадру
        """
        self.dict_video[frame_number] = output_count
        self.progress = True
        # DetectionForm.cur_frame += 1
        # self.int_value_1.emit(str(DetectionForm.cur_frame / DetectionForm.all_frames))

    def run(self):
        print('run')
        if self.conditions:
            video_list = self.detector.detectCustomObjectsFromVideo(
                input_file_path=os.path.join(os.getcwd(), self.path),
                output_file_path=os.path.join(os.getcwd(), "new_traffic"),
                frames_per_second=6,
                minimum_percentage_probability=0 if not self.prob.isnumeric() else int(self.prob),
                per_frame_function=self.forFrame,
                custom_objects=self.tuple[0])
        else:
            if self.all_flags:
                video_list = self.detector.detectObjectsFromVideo(
                    input_file_path=os.path.join(os.getcwd(), self.path),
                    output_file_path=os.path.join(os.getcwd(), "new_traffic"),
                    frames_per_second=6,
                    minimum_percentage_probability=0 if not self.prob.isnumeric() else int(self.prob),
                    per_frame_function=self.forFrame)
            else:
                video_list = self.detector.detectCustomObjectsFromVideo(
                    input_file_path=os.path.join(os.getcwd(), self.path),
                    output_file_path=os.path.join(os.getcwd(), "new_traffic"),
                    frames_per_second=6,
                    minimum_percentage_probability=0 if not self.prob.isnumeric() else int(self.prob),
                    per_frame_function=self.forFrame,
                    custom_objects=self.chosen_objects)
        DetectionForm.cur_frame = 0
        self.int_value_2.emit(self.dict_video)
        self.int_value_3.emit(True)
        self.progress = True


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    detection_form = DetectionForm()
    detection_form.show()
    sys.exit(app.exec())
