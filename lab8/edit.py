import psycopg2
import sys

from PyQt5.QtWidgets import (QApplication, QWidget,
                             QTabWidget, QAbstractScrollArea,
                             QVBoxLayout, QHBoxLayout,
                             QTableWidget, QGroupBox,
                             QTableWidgetItem, QPushButton, QMessageBox)

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self._connect_to_db()

        self.setWindowTitle("Shedule")
        self.setGeometry(360, 250, 1330, 615)

        self.vbox = QVBoxLayout(self)

        self.tabs = QTabWidget(self)
        self.vbox.addWidget(self.tabs)

        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(lambda _: self._update())
        self.updatebtn_lay = QHBoxLayout()
        self.vbox.addLayout(self.updatebtn_lay)
        self.updatebtn_lay.addWidget(self.update_button)

        self._create_shedule_tab()
        self._create_teachers_tab()
        self._create_subjects_tab()

    def _connect_to_db(self):
        self.conn = psycopg2.connect(database="bot_db",
                                     user="postgres",
                                     password="05062004liza",
                                     host="localhost",
                                     port="5432")

        self.cursor = self.conn.cursor()

    def _create_shedule_tab(self):
        self.shedule_tab = QWidget()
        self.tabs.addTab(self.shedule_tab, "Расписание")
        days = [
            'Понедельник',
            'Вторник',
            'Среда',
            'Четверг',
            'Пятница',
            'Суббота']

        day_tab = QTabWidget(self)
        weekdays = {'Понедельник': 1, 'Вторник': 2, 'Среда': 3, 'Четверг': 4, 'Пятница': 5, 'Суббота': 6}
        for i in days:
            day_tab.addTab(self._create_day_table(weekdays[i]), i)
        day_tab_layout = QVBoxLayout()
        day_tab_layout.addWidget(day_tab)
        self.shedule_tab.setLayout(day_tab_layout)

    def _create_day_table(self, day):
        table = QTableWidget()
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels(
            ["id", "Неделя", "День", "Предмет", "Аудитория", "Время", "Препод", "", ""])
        self._update_day_table(table, day)
        return table

    def _update_day_table(self, table, day):
        self.cursor.execute(f"SELECT * FROM timetable join subject on"
                            f" timetable.subject = subject.id "
                            f"JOIN teacher on timetable.teacher = teacher.id WHERE day={day} "
                            f"ORDER BY timetable.id")
        records = list(self.cursor.fetchall())
        table.setRowCount(len(records) + 1)
        weekdays = {1: 'Понедельник', 2: 'Вторник', 3: 'Среда', 4: 'Четверг', 5: 'Пятница', 6: 'Суббота'}
        for i, r in enumerate(records):
            r = list(r)
            editButton = QPushButton("Edit")
            delButton = QPushButton("Delete")
            table.setItem(i, 0,
                          QTableWidgetItem(str(r[0])))
            table.setItem(i, 1,
                          QTableWidgetItem(str(r[1])))
            table.setItem(i, 2,
                          QTableWidgetItem(str(weekdays[r[2]])))
            table.setItem(i, 3,
                          QTableWidgetItem(str(r[8])))
            table.setItem(i, 4,
                          QTableWidgetItem(str(r[4])))
            table.setItem(i, 5,
                          QTableWidgetItem(str(r[5])))
            table.setItem(i, 6,
                          QTableWidgetItem(str(r[10])))
            table.setCellWidget(i, 7, editButton)
            table.setCellWidget(i, 8, delButton)

            editButton.clicked.connect(
                lambda _, rowNum=i, table=table: self._change_from_timetable(rowNum, table))
            delButton.clicked.connect(lambda _, rowNum=i, table=table: self._delete_from_timetable(rowNum, table))

        addButton = QPushButton("Add")
        addButton.clicked.connect(lambda _, rowNum=len(records), table=table: self._add_row_timetable(rowNum, table))
        table.setCellWidget(len(records), 7, addButton)
        table.resizeRowsToContents()

    def _change_from_timetable(self, rowNum, table):
        row = list()
        for i in range(table.columnCount() - 2):
            try:
                row.append(table.item(rowNum, i).text())
            except:
                row.append(None)
        print(row)
        weekdays = {'Понедельник': 1, 'Вторник': 2, 'Среда': 3, 'Четверг': 4, 'Пятница': 5, 'Суббота': 6}
        row[2] = weekdays[row[2]]
        try:
            self.cursor.execute("select id from subject where name=%s", (row[3],))
            subject = self.cursor.fetchone()
            row[3] = subject[0]
            self.cursor.execute("select id from teacher where full_name=%s", (row[6],))
            teacher = self.cursor.fetchone()
            row[6] = teacher[0]
            row.append(row[0])
            row = row[1:]
            print(row)
            self.cursor.execute(
                "update timetable set week=%s, day=%s, subject=%s, room_numb=%s, start_time=%s, teacher=%s "
                "where timetable.id=%s", tuple(row))
            self.conn.commit()
        except Exception as e:
            QMessageBox.about(self, "Error", str(e))
            self._connect_to_db()

    def _delete_from_timetable(self, rowNum, table):
        try:
            weekdays = {'Понедельник': 1, 'Вторник': 2, 'Среда': 3, 'Четверг': 4, 'Пятница': 5, 'Суббота': 6}
            id = table.item(rowNum, 0).text()
            day = weekdays[table.item(rowNum, 2).text()]
            self.cursor.execute("delete from timetable where timetable.id=%s", (id,))
            self.conn.commit()
            table.setRowCount(0)
            self._update_day_table(table, day)
        except Exception as e:
            QMessageBox.about(self, "Error", str(e))
            self._connect_to_db()

    def _add_row_timetable(self, rowNum, table):
        row = list()
        for i in range(1, table.columnCount() - 2):
            try:
                row.append(table.item(rowNum, i).text())
            except:
                row.append(None)
        try:
            self.cursor.execute("select subject.id from subject where name=%s", (row[2],))
            subject = self.cursor.fetchone()
            row[2] = subject[0]
            if row[5] is None:
                row[5] = ''
            if row[3] is None:
                row[3] = ''
            self.cursor.execute("select teacher.id from teacher where full_name=%s", (row[5],))
            teacher = self.cursor.fetchone()
            row[5] = teacher[0]
            weekdays = {'Понедельник': 1, 'Вторник': 2, 'Среда': 3, 'Четверг': 4, 'Пятница': 5, 'Суббота': 6}
            row[1] = weekdays[row[1]]
            print(row)
            self.cursor.execute(
                "insert into timetable (week, day, subject, room_numb, start_time, teacher) values(%s, %s, %s, %s, %s, %s)",
                (tuple(row)))
            self.conn.commit()
            table.setRowCount(0)
            self._update_day_table(table, row[1])
        except Exception as e:
            print(e)
            QMessageBox.about(self, "Error", str(e))
            self._connect_to_db()

    def _create_teachers_tab(self):
        self.teachers = QWidget()
        self.tabs.addTab(self.teachers, "Преподаватели")
        table = QTableWidget(self)
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["id", "Имя", "Предмет", "", ""])

        teachers_tab_layout = QVBoxLayout()
        teachers_tab_layout.addWidget(table)

        self._update_teachers_tab(table)
        self.teachers.setLayout(teachers_tab_layout)

    def _update_teachers_tab(self, table):
        self.cursor.execute(f"SELECT * FROM teacher join subject on teacher.subject=subject.id"
                            f" ORDER BY teacher.id")
        records = list(self.cursor.fetchall())
        table.setRowCount(len(records) + 1)

        for i, r in enumerate(records):
            r = list(r)
            editButton = QPushButton("Edit")
            delButton = QPushButton("Delete")
            table.setItem(i, 0,
                          QTableWidgetItem(str(r[0])))
            table.setItem(i, 1,
                          QTableWidgetItem(str(r[1])))
            table.setItem(i, 2,
                          QTableWidgetItem(str(r[4])))
            table.setCellWidget(i, 3, editButton)
            table.setCellWidget(i, 4, delButton)

            editButton.clicked.connect(
                lambda _, rowNum=i, tabl=table: self._change_from_teacher(rowNum, tabl))
            delButton.clicked.connect(
                lambda _, rowNum=i, tabl=table:
                self._delete_from_teacher(rowNum, table))
        addButton = QPushButton("Add")
        addButton.clicked.connect(
            lambda _, rowNum=len(records), table=table: self._add_row_teacher(rowNum, table))
        table.setCellWidget(len(records), 3, addButton)
        table.resizeRowsToContents()

    def _change_from_teacher(self, rowNum, table):
        row = list()

        for i in range(table.columnCount() - 2):
            try:
                row.append(table.item(rowNum, i).text())
            except:
                row.append(None)
        try:
            self.cursor.execute("select subject.id from subject where name=%s", (row[2],))
            subject = self.cursor.fetchone()
            row[2] = subject[0]
            row.append(row[0])
            row = row[1:]
            self.cursor.execute("update teacher set full_name=%s, subject=%s where teacher.id=%s", tuple(row))
            self.conn.commit()
        except Exception as e:
            QMessageBox.about(self, "Error", str(e))
            self._connect_to_db()

    def _delete_from_teacher(self, rowNum, table):
        try:
            id = table.item(rowNum, 0).text()
            self.cursor.execute("delete from timetable where teacher=%s", (id,))
            self.cursor.execute("delete from teacher where teacher.id=%s", (id,))
            self.conn.commit()
            table.setRowCount(0)
            self._update_teachers_tab(table)
        except Exception as e:
            QMessageBox.about(self, "Error", str(e))
            self._connect_to_db()

    def _add_row_teacher(self, rowNum, table):
        row = list()
        for i in range(1, table.columnCount() - 2):
            try:
                row.append(table.item(rowNum, i).text())
            except:
                row.append(None)
        self.cursor.execute("select subject.id from subject where name=%s", (row[1],))
        subject = self.cursor.fetchone()
        row[1] = subject[0]
        try:
            self.cursor.execute(
                "insert into teacher (full_name, subject) values(%s, %s)",
                (tuple(row)))
            self.conn.commit()
            table.setRowCount(0)
            self._update_teachers_tab(table)
        except Exception as e:
            print(e)
            QMessageBox.about(self, "Error", str(e))
            self._connect_to_db()

    def _create_subjects_tab(self):
        self.subjects = QWidget()
        self.tabs.addTab(self.subjects, "Предметы")
        table = QTableWidget(self)
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["id_subject", "Предмет", "", ""])

        subjects_tab_layout = QVBoxLayout()
        subjects_tab_layout.addWidget(table)

        self._update_subjects_tab(table)
        self.subjects.setLayout(subjects_tab_layout)

    def _update_subjects_tab(self, table):
        self.cursor.execute(f"SELECT * FROM subject ORDER BY subject.id")
        records = list(self.cursor.fetchall())
        table.setRowCount(len(records) + 1)
        for i, r in enumerate(records):
            r = list(r)
            editButton = QPushButton("Edit")
            delButton = QPushButton("Delete")
            table.setItem(i, 0,
                          QTableWidgetItem(str(r[0])))
            table.setItem(i, 1,
                          QTableWidgetItem(str(r[1])))
            table.setCellWidget(i, 2, editButton)
            table.setCellWidget(i, 3, delButton)

            editButton.clicked.connect(
                lambda _, rowNum=i, table=table: self._change_from_subjects(rowNum, table))
            delButton.clicked.connect(
                lambda _, rowNum=i, table=table:
                self._delete_from_subjects(rowNum, table))

        addButton = QPushButton("Add")
        addButton.clicked.connect(
            lambda _, rowNum=len(records), table=table: self._add_row_subject(rowNum, table))
        table.setCellWidget(len(records), 2, addButton)
        table.resizeRowsToContents()

    def _change_from_subjects(self, rowNum, table):
        row = list()

        for i in range(table.columnCount() - 2):
            try:
                row.append(table.item(rowNum, i).text())
            except:
                row.append(None)
        try:
            row.append(row[0])
            row = row[1:]
            self.cursor.execute("update subject set name=%s where subject.id=%s", tuple(row))
            self.conn.commit()
        except Exception as e:
            QMessageBox.about(self, "Error", str(e))
            self._connect_to_db()

    def _delete_from_subjects(self, rowNum, table):
        try:
            id = table.item(rowNum, 0).text()
            self.cursor.execute("delete from timetable where subject=%s", (id,))
            self.cursor.execute("delete from teacher where subject=%s", (id,))
            self.cursor.execute("delete from subject where subject.id=%s", (id,))
            self.conn.commit()
            table.setRowCount(0)
            self._update_subjects_tab(table)
        except Exception as e:
            QMessageBox.about(self, "Error", str(e))
            self._connect_to_db()

    def _add_row_subject(self, rowNum, table):
        subject = table.item(rowNum, 1).text()
        try:
            self.cursor.execute(
                "insert into subject (name) values(%s)",
                (subject,))
            self.conn.commit()
            table.setRowCount(0)
            self._update_subjects_tab(table)
        except Exception as e:
            print(e)
            QMessageBox.about(self, "Error", str(e))
            self._connect_to_db()

    def _update(self):
        self.tabs.removeTab(0)
        self.tabs.removeTab(0)
        self.tabs.removeTab(0)
        self._create_shedule_tab()
        self._create_teachers_tab()
        self._create_subjects_tab()


app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec_())
