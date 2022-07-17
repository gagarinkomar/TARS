import sys
import sqlite3
import string
import os.path
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


FONTSMALL = QFont()
FONTSMALL.setPointSize(10)

FONTMEDIUM = QFont()
FONTMEDIUM.setPointSize(25)

FONTBIG = QFont()
FONTBIG.setPointSize(40)


class QWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('icon.png'))
        FONT = QFont()
        FONT.setPointSize(15)
        self.setFont(FONT)

    def center(self):
        QR = self.frameGeometry()
        CP = QDesktopWidget().availableGeometry().center()
        QR.moveCenter(CP)
        self.move(QR.topLeft())

    def closeEvent(self, event):
        self.connection.close()


class Authentication(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.connection = sqlite3.connect("UsersData.db")
        self.cursor = self.connection.cursor()

        Logins = self.cursor.execute(
            "SELECT Login FROM InputHistory ORDER BY id DESC LIMIT 5"
        ).fetchall()
        Passwords = self.cursor.execute(
            "SELECT Password FROM InputHistory ORDER BY id DESC LIMIT 5"
        ).fetchall()
        Logins = list(set(map(lambda x: x[0], Logins)))
        Passwords = list(set(map(lambda x: x[0], Passwords)))

        self.setFixedSize(700, 500)
        self.center()
        self.setWindowTitle('Авторизация')

        self.gridLayoutWidget = QGridLayout()
        self.gridLayoutWidget.setSpacing(10)
        self.gridLayoutWidget.setContentsMargins(100, 100, 150, 50)
        self.setLayout(self.gridLayoutWidget)

        self.labellogo = QLabel(self)
        self.labellogo.setPixmap(QPixmap('logo.png').scaled(160, 60))
        self.gridLayoutWidget.addWidget(self.labellogo, 0, 1, 2, 2)

        self.labelLogin = QLabel(self)
        self.labelLogin.setText('Логин')
        self.gridLayoutWidget.addWidget(self.labelLogin, 2, 0, 1, 2)

        self.labelPassword = QLabel(self)
        self.labelPassword.setText('Пароль')
        self.gridLayoutWidget.addWidget(self.labelPassword, 3, 0, 1, 2)

        self.ComboBoxlLogin = QComboBox(self)
        self.ComboBoxlLogin.setEditable(True)
        self.ComboBoxlLogin.addItems([''] + Logins)
        self.ComboBoxlLogin.setFixedSize(300, 30)
        self.gridLayoutWidget.addWidget(self.ComboBoxlLogin, 2, 1, 1, 2)

        self.ComboBoxlPassword = QComboBox(self)
        self.ComboBoxlPassword.setEditable(True)
        self.ComboBoxlPassword.addItems([''] + Passwords)
        self.ComboBoxlPassword.setFixedSize(300, 30)
        self.gridLayoutWidget.addWidget(self.ComboBoxlPassword, 3, 1, 1, 2)

        self.checkBox = QCheckBox(self)
        self.checkBox.setText('Запомнить логин и пароль')
        self.gridLayoutWidget.addWidget(self.checkBox, 4, 1, 1, 2)

        self.pushButtonTrue = QPushButton(self)
        self.pushButtonTrue.setFixedSize(150, 50)
        self.pushButtonTrue.setText('Войти')
        self.pushButtonTrue.clicked.connect(self.tryLogon)
        self.gridLayoutWidget.addWidget(self.pushButtonTrue, 5, 1)

        self.pushButtonFalse = QPushButton(self)
        self.pushButtonFalse.setFixedSize(150, 50)
        self.pushButtonFalse.setText('Отмена')
        self.pushButtonFalse.clicked.connect(self.close)
        self.gridLayoutWidget.addWidget(self.pushButtonFalse, 5, 2)

        self.pushButtonHelp = QPushButton(self)
        self.pushButtonHelp.setText('Не могу войти')
        self.pushButtonHelp.setMaximumWidth(350)
        self.pushButtonHelp.clicked.connect(self.forgotPassword)
        self.gridLayoutWidget.addWidget(self.pushButtonHelp, 6, 1, 1, 2)

        self.pushButtonReg = QPushButton(self)
        self.pushButtonReg.setText('Создать аккаунт')
        self.pushButtonReg.setMaximumWidth(350)
        self.pushButtonReg.clicked.connect(self.registration)
        self.gridLayoutWidget.addWidget(self.pushButtonReg, 7, 1, 1, 2)

        self.show()

    def tryLogon(self):
        UsersData = self.cursor.execute(
            'SELECT Login, Password FROM Users'
                           ).fetchall()
        if (self.ComboBoxlLogin.currentText(),
                self.ComboBoxlPassword.currentText()) in UsersData:
            if self.checkBox.isChecked():
                self.cursor.execute(f"INSERT INTO InputHistory(Login, "
                                    f"Password) VALUES("
                                    f"\'{self.ComboBoxlLogin.currentText()}\',"
                                    f"\'{self.ComboBoxlPassword.currentText()}"
                                    f"\')")
                self.connection.commit()

            login = self.ComboBoxlLogin.currentText()
            self.close()
            self.mainWidget = MainWidget(login)
        else:
            QMessageBox.critical(self, 'Ошибка', 'Неверный логин или пароль',
                                 QMessageBox.Ok)

    def forgotPassword(self):
        self.forgotPasswordWidget = ForgotPassword()

    def registration(self):
        self.registrationWidget = Registration()


class MainWidget(QMainWindow):
    def __init__(self, login):
        super().__init__()
        self.login = login

        self.initUI()

    def initUI(self):
        self.setWindowIcon(QIcon('icon.png'))

        self.connection = sqlite3.connect('UsersData.db')
        self.cursor = self.connection.cursor()

        FontData = self.cursor.execute(f'SELECT Font FROM Users WHERE Login = '
                                       f'\'{self.login}\'').fetchone()[0]
        Font = QFont()
        Font.fromString(FontData)
        self.setFont(Font)

        self.setFixedSize(1200, 900)
        self.center()
        self.setWindowTitle('TARS')

        bar = self.menuBar()
        main = bar.addMenu('Главное')
        anotherAccount = QAction('Сменить аккаунт', self)
        anotherAccount.setShortcut("Ctrl+A")
        anotherAccount.triggered.connect(self.authentication)
        main.addAction(anotherAccount)
        exit = QAction('Выйти', self)
        exit.setShortcut("Alt+F4")
        exit.triggered.connect(self.close)
        main.addAction(exit)

        view = bar.addMenu('Вид')
        change = QAction('Сменить шрифт', self)
        change.setShortcut("Ctrl+P")
        change.triggered.connect(self.changeFont)
        view.addAction(change)

        self.TabWidget = MainTabWidget(self.login)
        self.setCentralWidget(self.TabWidget)

        self.show()

    def authentication(self):
        self.close()

        self.Authentication = Authentication()

    def changeFont(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.setFont(font)
            self.cursor.execute(
                f"UPDATE Users SET Font = \'{font.toString()}\'"
                f"WHERE Login = \'{self.login}\'")
            self.connection.commit()

    def center(self):
        QR = self.frameGeometry()
        CP = QDesktopWidget().availableGeometry().center()
        QR.moveCenter(CP)
        self.move(QR.topLeft())

    def closeEvent(self, event):
        self.connection.close()


class MainTabWidget(QTabWidget):
    def __init__(self, login):
        super().__init__()
        self.login = login
        self.initUI()

    def initUI(self):
        self.connection = sqlite3.connect("UsersData.db")
        self.cursor = self.connection.cursor()

        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()

        self.addTab(self.tab1, 'МОЙ ПРОФИЛЬ')
        self.addTab(self.tab2, "НАЙТИ ПРОФИЛЬ")
        self.addTab(self.tab3, "РЕДАКТИРОВАТЬ ПРОФИЛЬ")

        self.tab1UI()
        self.tab2UI()
        self.tab3UI()

    def tab1UI(self):
        Data = self.cursor.execute(f"SELECT Information, CommentsGetted, "
                                   f"CommentsGiven, Avatar FROM Users WHERE "
                                   f"Login = \'{self.login}\'").fetchone()

        self.gridLayoutWidget1 = QGridLayout()
        self.gridLayoutWidget1.setSpacing(10)
        self.gridLayoutWidget1.setContentsMargins(75, 75, 75, 75)

        self.logo1 = QLabel(self)
        if os.path.isfile(Data[3]):
            self.logo1.setPixmap(QPixmap(Data[3]).scaled(300, 300))
        else:
            self.logo1.setPixmap(QPixmap('defaultavatar.jpg').scaled(300, 300))
        self.gridLayoutWidget1.addWidget(self.logo1, 0, 0, 2, 2)

        self.labelLogin1 = QLabel(self)
        self.labelLogin1.setText(self.login)
        self.labelLogin1.setFont(FONTBIG)
        self.gridLayoutWidget1.addWidget(self.labelLogin1, 2, 0, 1, 2)

        self.labelCountCommentsGiven1 = QLabel(self)
        self.labelCountCommentsGiven1.setText(f'Комментариев написано: '
                                              f'{Data[2]}')
        self.labelCountCommentsGiven1.setFont(FONTMEDIUM)
        self.gridLayoutWidget1.addWidget(self.labelCountCommentsGiven1, 3, 0,
                                         1, 2)

        self.TextBrowserInformation1 = QTextBrowser(self)
        self.TextBrowserInformation1.setText(Data[0])
        self.TextBrowserInformation1.setFont(FONTSMALL)
        self.gridLayoutWidget1.addWidget(self.TextBrowserInformation1, 0, 2,
                                         2, 2)

        self.TextBrowserComments1 = QTextBrowser(self)
        self.TextBrowserComments1.setText(Data[1])
        self.TextBrowserComments1.setFont(FONTSMALL)
        self.gridLayoutWidget1.addWidget(self.TextBrowserComments1, 2, 2, 2, 2)

        self.pushButton = QPushButton(self)
        self.pushButton.setText('Обновить')
        self.pushButton.clicked.connect(self.update1)
        self.gridLayoutWidget1.addWidget(self.pushButton, 4, 2)

        self.tab1.setLayout(self.gridLayoutWidget1)

    def update1(self):
        Data = self.cursor.execute(f"SELECT Information, CommentsGetted, "
                                   f"CommentsGiven, Avatar FROM Users WHERE "
                                   f"Login = \'{self.login}\'").fetchone()

        if os.path.isfile(Data[3]):
            self.logo1.setPixmap(QPixmap(Data[3]).scaled(300, 300))
        else:
            self.logo1.setPixmap(QPixmap('defaultavatar.jpg').scaled(300, 300))

        self.labelCountCommentsGiven1.setText(
            f'Комментариев написано: {Data[2]}')
        self.TextBrowserInformation1.setText(Data[0])
        self.TextBrowserComments1.setText(Data[1])

    def tab2UI(self):
        Data = self.cursor.execute(f"SELECT Information, CommentsGetted, "
                                   f"CommentsGiven, Avatar FROM Users WHERE "
                                   f"Login = \'{self.login}\'").fetchone()

        self.gridLayoutWidget2 = QGridLayout()
        self.gridLayoutWidget2.setSpacing(10)
        self.gridLayoutWidget2.setContentsMargins(75, 75, 75, 75)

        self.logo2 = QLabel(self)
        if os.path.isfile(Data[3]):
            self.logo2.setPixmap(QPixmap(Data[3]).scaled(300, 300))
        else:
            self.logo2.setPixmap(QPixmap('defaultavatar.jpg').scaled(300, 300))
        self.gridLayoutWidget2.addWidget(self.logo2, 0, 0, 2, 2)

        self.labelLogin2 = QLabel(self)
        self.labelLogin2.setText(self.login)
        self.labelLogin2.setFont(FONTBIG)
        self.gridLayoutWidget2.addWidget(self.labelLogin2, 2, 0, 1, 2)

        self.labelCountCommentsGiven2 = QLabel(self)
        self.labelCountCommentsGiven2.setText(f'Комментариев написано: '
                                              f'{Data[2]}')
        self.labelCountCommentsGiven2.setFont(FONTMEDIUM)
        self.gridLayoutWidget2.addWidget(self.labelCountCommentsGiven2, 3, 0,
                                         1, 2)

        self.TextBrowserInformation2 = QTextBrowser(self)
        self.TextBrowserInformation2.setText(Data[0])
        self.TextBrowserInformation2.setFont(FONTSMALL)
        self.gridLayoutWidget2.addWidget(self.TextBrowserInformation2, 0, 2, 2,
                                         2)

        self.TextBrowserComments2 = QTextBrowser(self)
        self.TextBrowserComments2.setText(Data[1])
        self.TextBrowserComments2.setFont(FONTSMALL)
        self.gridLayoutWidget2.addWidget(self.TextBrowserComments2, 2, 2, 2, 2)

        self.pushButton2 = QPushButton(self)
        self.pushButton2.setText('Добавить комментарий')
        self.pushButton2.clicked.connect(self.giveComment)
        self.gridLayoutWidget2.addWidget(self.pushButton2, 4, 3)

        self.label2 = QLabel(self)
        self.label2.setText('Введите логин\nнужного профиля:')
        self.gridLayoutWidget2.addWidget(self.label2, 4, 0, 1, 1)

        self.pushButton1 = QPushButton(self)
        self.pushButton1.setText('Найти')
        self.pushButton1.clicked.connect(self.changeProfile)
        self.gridLayoutWidget2.addWidget(self.pushButton1, 4, 2)

        self.lineEditLogin = QLineEdit(self)
        self.lineEditLogin.setFixedWidth(300)
        self.lineEditLogin.setText(self.login)
        self.gridLayoutWidget2.addWidget(self.lineEditLogin, 4, 1)

        self.tab2.setLayout(self.gridLayoutWidget2)

    def changeProfile(self):
        LoginsData = self.cursor.execute("SELECT Login FROM Users").fetchall()
        LoginsData = list(map(lambda x: x[0], LoginsData))

        if self.lineEditLogin.text() in LoginsData:
            self.update2()
        else:
            QMessageBox.critical(self, 'Ошибка',
                                 'Пользователя с таким логином не '
                                 'существует', QMessageBox.Ok)

    def update2(self):
        LoginsData = self.cursor.execute("SELECT Login FROM Users").fetchall()
        LoginsData = list(map(lambda x: x[0], LoginsData))

        if self.lineEditLogin.text() not in LoginsData:
            self.lineEditLogin.setText(self.login)

        Data = self.cursor.execute(f"SELECT Information, CommentsGetted, "
                                   f"CommentsGiven, Avatar FROM Users WHERE "
                                   f"Login = \'{self.lineEditLogin.text()}\'"
                                   ).fetchone()

        if os.path.isfile(Data[3]):
            self.logo2.setPixmap(QPixmap(Data[3]).scaled(300, 300))
        else:
            self.logo2.setPixmap(QPixmap('defaultavatar.jpg').scaled(300, 300))
        self.labelLogin2.setText(self.lineEditLogin.text())
        self.labelCountCommentsGiven2.setText(
            f'Комментариев написано: {Data[2]}')
        self.TextBrowserInformation2.setText(Data[0])
        self.TextBrowserComments2.setText(Data[1])

    def giveComment(self):
        if self.labelLogin2.text() == self.login:
            QMessageBox.critical(self, 'Ошибка',
                                 'Нельзя оставлять комментарии самому себе',
                                 QMessageBox.Ok)
        else:
            textComment, okBtnPressed = QInputDialog.getText(
                self, 'Оставить комментарий', 'Введите комментарий')
            if okBtnPressed:
                if (len(textComment) < 5) or (len(textComment) > 200):
                    QMessageBox.critical(self, 'Ошибка',
                                         'Недопустимая длина комментария',
                                         QMessageBox.Ok)
                else:
                    CommentsGetted = self.cursor.execute(
                        f"SELECT CommentsGetted FROM Users WHERE Login = "
                        f"\'{self.labelLogin2.text()}\'").fetchone()[0]
                    if CommentsGetted == 'У пользователя пока нету ' \
                                         'комментариев':
                        CommentsGetted = ''
                    CommentsGetted += textComment + f'({self.login})' + '\n\n'
                    self.cursor.execute(f"UPDATE Users SET CommentsGetted = "
                                        f"\'{CommentsGetted}\'WHERE Login = "
                                        f"\'{self.labelLogin2.text()}\'")

                    CommentsGiven = self.cursor.execute(
                        f"SELECT CommentsGiven FROM Users WHERE Login = "
                        f"\'{self.login}\'").fetchone()[0]
                    self.cursor.execute(
                        f"UPDATE Users SET CommentsGiven = "
                        f"\'{CommentsGiven + 1}\'WHERE Login = "
                        f"\'{self.login}\'")
                    self.connection.commit()

                    self.update1()
                    self.update2()

    def tab3UI(self):
        Data = self.cursor.execute(f"SELECT Information, CommentsGetted, "
                                   f"CommentsGiven, Avatar FROM Users WHERE "
                                   f"Login = \'{self.login}\'").fetchone()

        self.gridLayoutWidget3 = QGridLayout()
        self.gridLayoutWidget3.setSpacing(10)
        self.gridLayoutWidget3.setContentsMargins(75, 75, 75, 75)

        self.logo3 = QLabel(self)
        if os.path.isfile(Data[3]):
            self.logo3.setPixmap(QPixmap(Data[3]).scaled(300, 300))
        else:
            self.logo3.setPixmap(QPixmap('defaultavatar.jpg').scaled(300, 300))
        self.gridLayoutWidget3.addWidget(self.logo3, 0, 0)

        self.pushButton3 = QPushButton(self)
        self.pushButton3.setText('Сменить\nаватарку')
        self.pushButton3.setFixedSize(200, 100)
        self.pushButton3.clicked.connect(self.changeAva)
        self.gridLayoutWidget3.addWidget(self.pushButton3, 0, 1)

        self.textEditComments3 = QTextEdit(self)
        self.textEditComments3.setFixedSize(400, 300)
        self.textEditComments3.setText(Data[0])
        self.textEditComments3.setFont(FONTSMALL)
        self.gridLayoutWidget3.addWidget(self.textEditComments3, 1, 0)

        self.pushButton4 = QPushButton(self)
        self.pushButton4.setText('Сохранить\nизменения')
        self.pushButton4.setFixedSize(200, 100)
        self.pushButton4.clicked.connect(self.saveChange)
        self.gridLayoutWidget3.addWidget(self.pushButton4, 1, 1)

        self.tab3.setLayout(self.gridLayoutWidget3)

    def changeAva(self):
        fname = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]

        self.logo3.setPixmap(QPixmap(fname).scaled(300, 300))

        self.cursor.execute(
            f"UPDATE Users SET Avatar = \'{fname}\'"
            f"WHERE Login = \'{self.login}\'")
        self.connection.commit()

        self.update1()
        self.update2()

    def saveChange(self):
        self.cursor.execute(
            f"UPDATE Users SET Information = "
            f"\'{self.textEditComments3.toPlainText()}\'"
            f"WHERE Login = \'{self.login}\'")
        self.connection.commit()

        self.update1()
        self.update2()


class Registration(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.connection = sqlite3.connect('UsersData.db')
        self.cursor = self.connection.cursor()

        self.setFixedSize(900, 450)
        self.center()
        self.setWindowTitle('Регистрация')

        self.gridLayoutWidget = QGridLayout()
        self.gridLayoutWidget.setSpacing(10)
        self.gridLayoutWidget.setContentsMargins(100, 75, 100, 75)
        self.setLayout(self.gridLayoutWidget)

        self.labelLogin = QLabel(self)
        self.labelLogin.setText('Логин')
        self.gridLayoutWidget.addWidget(self.labelLogin, 0, 0)

        self.labelPassword1 = QLabel(self)
        self.labelPassword1.setText('Пароль')
        self.gridLayoutWidget.addWidget(self.labelPassword1, 1, 0)

        self.labelPassword2 = QLabel(self)
        self.labelPassword2.setText('Повторите\nпароль')
        self.gridLayoutWidget.addWidget(self.labelPassword2, 2, 0)

        self.labelQuestion = QLabel(self)
        self.labelQuestion.setText('Придумайте или\nвыберите\nсекретный '
                                   'вопрос\nи ответ на него')
        self.gridLayoutWidget.addWidget(self.labelQuestion, 3, 0, 2, 1)

        self.lineEditLogin = QLineEdit(self)
        self.lineEditLogin.setFixedSize(300, 30)
        self.gridLayoutWidget.addWidget(self.lineEditLogin, 0, 1, 1, 2)

        self.lineEditPassword1 = QLineEdit(self)
        self.lineEditPassword1.setFixedSize(300, 30)
        self.gridLayoutWidget.addWidget(self.lineEditPassword1, 1, 1, 1, 2)

        self.lineEditPassword2 = QLineEdit(self)
        self.lineEditPassword2.setFixedSize(300, 30)
        self.gridLayoutWidget.addWidget(self.lineEditPassword2, 2, 1, 1, 2)

        self.securityQuestion = QComboBox(self)
        self.securityQuestion.setEditable(True)
        self.securityQuestion.addItems(['',
                                        'Какую школу вы посещали в шестом '
                                        'классе?',
                                       'Какое отчество вашего старшего '
                                        'ребенка?',
                                        'Как звали вашего первого питомца?',
                                        'Где вы были на отдыхе в прошлом '
                                        'году?',
                                        'Какая девичья фамилия вашей матери?'])
        self.securityQuestion.setToolTip('Придумайте или выберите вопрос')
        self.gridLayoutWidget.addWidget(self.securityQuestion, 3, 1, 1, 2)

        self.lineEditQuestion = QLineEdit(self)
        self.lineEditQuestion.setFixedSize(300, 30)
        self.lineEditQuestion.setToolTip('Введите ответ на вопрос')
        self.gridLayoutWidget.addWidget(self.lineEditQuestion, 4, 1, 1, 2)

        self.RulesInput1 = QTextBrowser(self)
        self.RulesInput1.setText('В логине необходима 1 буква.\n\nВ пароле '
                                 'необходима 1 буква и 1 цифра.\n\nИ там и там'
                                 ' буквы только английские.\nМинимальная длина'
                                 ' 5, а максимальная 25.')
        self.RulesInput1.setFont(FONTSMALL)
        self.RulesInput1.setMinimumWidth(100)
        self.RulesInput1.setToolTip('Правила ввода')
        self.gridLayoutWidget.addWidget(self.RulesInput1, 0, 3, 3, 1)

        self.RulesInput2 = QTextBrowser(self)
        self.RulesInput2.setText('В вопросе максимум 50 символов.\n\n'
                                 'В ответе максимум 25 символов.\n\n'
                                 'И там и там минимум 5 символов.')
        self.RulesInput2.setFont(FONTSMALL)
        self.RulesInput2.setToolTip('Правила ввода')
        self.gridLayoutWidget.addWidget(self.RulesInput2, 3, 3, 2, 1)

        self.pushButtonTrue = QPushButton(self)
        self.pushButtonTrue.setText('Зарегистрироваться')
        self.pushButtonTrue.setMinimumHeight(50)
        self.pushButtonTrue.clicked.connect(self.tryRegistration)
        self.gridLayoutWidget.addWidget(self.pushButtonTrue, 5, 1)

        self.pushButtonFalse = QPushButton(self)
        self.pushButtonFalse.setText('Отмена')
        self.pushButtonFalse.setMinimumHeight(50)
        self.pushButtonFalse.clicked.connect(self.close)
        self.gridLayoutWidget.addWidget(self.pushButtonFalse, 5, 2)

        self.show()

    def tryRegistration(self):
        LoginsData = self.cursor.execute('SELECT Login FROM Users').fetchall()
        LoginsData = list(map(lambda x: x[0], LoginsData))
        error = ''

        if len(set(self.lineEditLogin.text()) &
               set(string.ascii_letters)) == 0:
            error = 'Нету букв в логине'
        elif len(set(self.lineEditLogin.text()) - set(string.printable)) > 0:
            error = 'Недопустимые символы в логине'
        elif (len(self.lineEditLogin.text()) < 5) or (len(
                self.lineEditLogin.text()) > 25):
            error = 'Не подходит длина логина'
        elif len(set(self.lineEditPassword1.text()) &
                 set(string.ascii_letters)) == 0:
            error = 'Нету букв в пароле'
        elif len(set(self.lineEditPassword1.text()) & set(string.digits)) == 0:
            error = 'Нету цифр в пароле'
        elif len(set(self.lineEditPassword1.text()) - set(
                string.printable)) > 0:
            error = 'Недопустимые символы в пароле'
        elif (len(self.lineEditPassword1.text()) < 5) or (len(
                self.lineEditPassword1.text()) > 25):
            error = 'Не подходит длина пароля'
        elif self.lineEditPassword1.text() != self.lineEditPassword2.text():
            error = 'Не совпадают пароли'
        elif (len(self.securityQuestion.currentText()) < 5) or (len(
                self.securityQuestion.currentText()) > 50):
            error = 'Не подходит длина вопроса'
        elif (len(self.lineEditQuestion.text()) < 5) or (len(
                self.lineEditQuestion.text()) > 25):
            error = 'Не подходит длина ответа'
        elif self.lineEditLogin.text() in LoginsData:
            error = 'Логин уже занят'

        if error:
            QMessageBox.critical(self, 'Ошибка', error, QMessageBox.Ok)
        else:
            QMessageBox.information(self, 'Регистрация закончена',
                                    'Поздравляю, регистрация прошла успешно!',
                                    QMessageBox.Ok)

            self.cursor.executemany('INSERT INTO Users(Login, Password, '
                                    'SecurityQuestion, AnswerQuestion) '
                                    'VALUES(?, ?, ?, ?)',
                                    [(self.lineEditLogin.text(),
                                      self.lineEditPassword1.text(),
                                      self.securityQuestion.currentText(),
                                      self.lineEditQuestion.text())])
            self.connection.commit()

            self.close()


class ForgotPassword(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.connection = sqlite3.connect('UsersData.db')
        self.cursor = self.connection.cursor()

        self.setFixedSize(700, 400)
        self.center()
        self.setWindowTitle('Восстановление пароля')

        self.gridLayoutWidget = QGridLayout()
        self.gridLayoutWidget.setSpacing(10)
        self.gridLayoutWidget.setContentsMargins(100, 100, 100, 100)
        self.setLayout(self.gridLayoutWidget)

        self.labelLogin = QLabel(self)
        self.labelLogin.setText('Логин для\nвосстановления')
        self.gridLayoutWidget.addWidget(self.labelLogin, 0, 0)

        self.lineEditLogin = QLineEdit(self)
        self.lineEditLogin.setFixedSize(300, 30)
        self.gridLayoutWidget.addWidget(self.lineEditLogin, 0, 1, 1, 2)

        self.pushButtonTrue = QPushButton(self)
        self.pushButtonTrue.setFixedSize(150, 50)
        self.pushButtonTrue.setText('Восстановить')
        self.pushButtonTrue.clicked.connect(self.Recover1)
        self.gridLayoutWidget.addWidget(self.pushButtonTrue, 1, 1)

        self.pushButtonFalse = QPushButton(self)
        self.pushButtonFalse.setFixedSize(150, 50)
        self.pushButtonFalse.setText('Отмена')
        self.pushButtonFalse.clicked.connect(self.close)
        self.gridLayoutWidget.addWidget(self.pushButtonFalse, 1, 2)

        self.show()

    def Recover1(self):
        LoginsData = self.cursor.execute('SELECT Login FROM Users').fetchall()
        LoginsData = list(map(lambda x: x[0], LoginsData))

        if self.lineEditLogin.text() in LoginsData:
            self.login = self.lineEditLogin.text()

            self.labelLogin.close()
            self.lineEditLogin.close()
            self.pushButtonTrue.close()
            self.pushButtonFalse.close()

            self.data = self.cursor.execute(f'SELECT SecurityQuestion, '
                                            f'AnswerQuestion FROM Users '
                                            f'WHERE Login = \'{self.login}\''
                                            ).fetchone()

            self.labelQuestion1 = QLabel(self)
            self.labelQuestion1.setText('Контрольный\nвопрос')
            self.gridLayoutWidget.addWidget(self.labelQuestion1, 0, 0)

            self.labelQuestion2 = QLabel(self)
            font = QFont()
            font.setPointSize(15)
            self.labelQuestion2.setFont(font)
            self.labelQuestion2.setText(self.data[0][:len(self.data[0])//2] +
                                        '\n' +
                                        self.data[0][len(self.data[0])//2:])
            self.gridLayoutWidget.addWidget(self.labelQuestion2, 0, 1, 1, 2)

            self.labelAnswer = QLabel(self)
            self.labelAnswer.setText('Ответ')
            self.gridLayoutWidget.addWidget(self.labelAnswer, 1, 0)

            self.lineEditAnswer = QLineEdit(self)
            self.lineEditAnswer.setFixedSize(300, 30)
            self.lineEditAnswer.setToolTip('Введите ответ')
            self.gridLayoutWidget.addWidget(self.lineEditAnswer, 1, 1, 1, 2)

            self.pushButtonTrue = QPushButton(self)
            self.pushButtonTrue.setFixedSize(150, 50)
            self.pushButtonTrue.setText('Восстановить')
            self.pushButtonTrue.clicked.connect(self.Recover2)
            self.gridLayoutWidget.addWidget(self.pushButtonTrue, 2, 1)

            self.pushButtonFalse = QPushButton(self)
            self.pushButtonFalse.setFixedSize(150, 50)
            self.pushButtonFalse.setText('Отмена')
            self.pushButtonFalse.clicked.connect(self.close)
            self.gridLayoutWidget.addWidget(self.pushButtonFalse, 2, 2)
        else:
            QMessageBox.critical(self, 'Ошибка',
                                 'Пользователя с таким логином не существует',
                                 QMessageBox.Ok)

    def Recover2(self):
        if self.lineEditAnswer.text() == self.data[1]:
            self.Recover3()
        else:
            QMessageBox.critical(self, 'Ошибка', 'Ответ не совпадает',
                                 QMessageBox.Ok)

    def Recover3(self):
        self.labelQuestion1.close()
        self.labelQuestion2.close()
        self.labelAnswer.close()
        self.lineEditAnswer.close()
        self.pushButtonTrue.close()
        self.pushButtonFalse.close()

        self.labelPassword1 = QLabel(self)
        self.labelPassword1.setText('Новый пароль')
        self.gridLayoutWidget.addWidget(self.labelPassword1, 0, 0)

        self.labelPassword2 = QLabel(self)
        self.labelPassword2.setText('Повторите\nновый пароль')
        self.gridLayoutWidget.addWidget(self.labelPassword2, 1, 0)

        self.lineEditPassword1 = QLineEdit(self)
        self.lineEditPassword1.setFixedSize(350, 30)
        self.gridLayoutWidget.addWidget(self.lineEditPassword1, 0, 1, 1, 2)

        self.lineEditPassword2 = QLineEdit(self)
        self.lineEditPassword2.setFixedSize(350, 30)
        self.gridLayoutWidget.addWidget(self.lineEditPassword2, 1, 1, 1, 2)

        self.pushButtonTrue = QPushButton(self)
        self.pushButtonTrue.setFixedSize(175, 50)
        self.pushButtonTrue.setText('Сменить пароль')
        self.pushButtonTrue.clicked.connect(self.Recover4)
        self.gridLayoutWidget.addWidget(self.pushButtonTrue, 2, 1)

        self.pushButtonFalse = QPushButton(self)
        self.pushButtonFalse.setFixedSize(175, 50)
        self.pushButtonFalse.setText('Отмена')
        self.pushButtonFalse.clicked.connect(self.close)
        self.gridLayoutWidget.addWidget(self.pushButtonFalse, 2, 2)

    def Recover4(self):
        error = ''
        if len(set(self.lineEditPassword1.text()) &
               set(string.ascii_letters)) == 0:
            error = 'Нету букв в пароле'
        elif len(set(self.lineEditPassword1.text()) & set(string.digits)) == 0:
            error = 'Нету цифр в пароле'
        elif len(set(self.lineEditPassword1.text()) - set(
                string.printable)) > 0:
            error = 'Недопустимые символы в пароле'
        elif (len(self.lineEditPassword1.text()) < 5) or (len(
                self.lineEditPassword1.text()) > 25):
            error = 'Не подходит длина пароля'
        elif self.lineEditPassword1.text() != self.lineEditPassword2.text():
            error = 'Не совпадают пароли'
        if error:
            QMessageBox.critical(self, 'Ошибка', error, QMessageBox.Ok)
        else:
            QMessageBox.information(self, 'Пароль изменён',
                                    'Поздравляю, замена пароля '
                                    'прошла успешно!',
                                    QMessageBox.Ok)
            self.cursor.execute(f"UPDATE Users SET Password = "
                                f"\'{self.lineEditPassword1.text()}\' "
                                f"WHERE Login = \'{self.login}\'")
            self.connection.commit()

            self.close()


if __name__ == '__main__':
    pass
    app = QApplication(sys.argv)
    ex = Authentication()
    sys.exit(app.exec_())
