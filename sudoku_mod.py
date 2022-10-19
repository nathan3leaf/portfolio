import math
import PyQt5
from PyQt5 import QtWidgets, QtCore
import os
import random
import pandas
import sudoku_ui
import sys
import threading
import time

def catch_exceptions(t, val, tb):
	PyQt5.QtWidgets.QMessageBox.critical(None, "An exception was raised: ", "Exception Type: {}".format(t))
	old_hook(t, val, tb)

old_hook = sys.excepthook
sys.excepthook = catch_exceptions

def startThread(functionName, *args, **kwargs):
	print(args)
	if len(args) == 0:
		t = threading.Thread(target=functionName)
	else:
		try:
			t = threading.Thread(target=functionName, args=args, kwargs=kwargs)
		except:
			try:
				if args is None:
					t = threading.Thread(target=functionName, kwargs=kwargs)
			except:
				t = threading.Thread(target=functionName)
	t.daemon = True
	t.start()

class BuildGame:
	def __init__(self):
		valueOptions = [1,2,3,4,5,6,7,8,9]
		BuildGame.row_sums = [1,3,6,10,15,21,28,36,45]
		blank_table = [[0,0,0] * 3] * 9
		print("blank_table: ", blank_table)
		game_board = pandas.DataFrame(blank_table)

		# Randomly place each value in each quadrant
		for i, sum_total in zip(valueOptions, self.row_sums):
			game_board = self.place(i, game_board, sum_total)
		print("game_board: ", game_board)
		self.game_board = game_board

	@staticmethod
	def place(i: "The value being placed", game_board: "The current game board structure", sum_total: "The sum that each row and column should add up to", r=0, c=0, placed=0):
		i_value = i
		build_error = False
		tries = 0
		last_resort = False
		tracking = 0

		while placed != 9:
			base = [[0 + (3 * r), 1 + (3 * r), 2 + (3 * r)], [0 + (3 * c), 1 + (3 * c), 2 + (3 * c)]]
			possible_cells = [[x, y] for x in base[0] for y in base[1]]
			y, x = random.choice(possible_cells)

			if game_board.loc[y, x] == 0:
				match_found = False

				while match_found is False:
					if game_board.loc[y, x] == 0 and game_board.loc[y].sum() + i_value == sum_total and game_board.loc[:, x].sum() + i_value == sum_total and i_value not in BuildGame.surrounding_nine(y, x, game_board):
						game_board.loc[y, x] = i_value
						match_found = True
						build_error = False
						placed += 1

						if c == 0:
							if r < 2:
								r += 1
							elif r == 2:
								r = 0
								c += 1
						elif c > 0:
							if r < 2:
								r += 1
							elif r == 2:
								r = 0
								c += 1
							elif c == 2:
								r += 1
					else:
						try:
							possible_cells.remove([y, x])

							if len(possible_cells) > 0:
								y, x = random.choice(possible_cells)
							else:
								# Remove all i's from board and try again
								tries += 1

								for _n in game_board.index:
									for _col in game_board.columns:
										if game_board.loc[_n, _col] == i_value:
											game_board.loc[_n, _col] = 0
								r = 0
								c = 0
								placed = 0

								if tries > 50:
									if i_value > 1:
										i_value -= 1
									for _n in game_board.index:
										for _col in game_board.columns:
											if last_resort is True:
												if game_board.loc[_n, _col] == i_value or game_board.loc[_n, _col] == i_value - 1:
													game_board.loc[_n, _col] = 0
											else:
												if game_board.loc[_n, _col] == i_value:
													game_board.loc[_n, _col] = 0
									if last_resort is True:
										i_value -= 1

									while i_value != i:
										game_board = BuildGame.place(i_value, game_board, BuildGame.row_sums[i_value - 1])
										i_value += 1
										tracking += 1

										if tracking > 5:
											last_resort = True
											tracking = 0
										else:
											last_resort = False
								else:
									break

						except Exception as e:
							print(e)
							r = 0
							c = 0
							placed = 0
							tries = 0
							match_found = True
							print("Resetting...")

			if build_error is True:
				print("Problem")
				break

		return game_board

	@staticmethod
	def surrounding_nine(r, c, game_board):
		scan = BuildGame.get_indicies(BuildGame.quadrant_selection(r, c))
		rows = scan[0]
		cols = scan[1]
		# print("surrounding nine: ", [game_board.loc[r, c] for r in rows for c in cols])
		return [game_board.loc[r, c] for r in rows for c in cols]

	@staticmethod
	def quadrant_selection(r, c):
		# print("r, c: ", r, c)
		if r in range(0, 3):
			quad_y = 0
		elif r in range(3, 6):
			quad_y = 3
		elif r in range(6, 9):
			quad_y = 6

		if c in range(0, 3):
			quad_x = 0
		elif c in range(3, 6):
			quad_x = 3
		elif c in range(6, 9):
			quad_x = 6

		# print("[quad_y, quad_x]: ", [quad_y, quad_x])
		return [quad_y, quad_x]

	@staticmethod
	def get_indicies(block_number):
		# print("block_number: ", block_number)
		y, x = block_number
		# print("y, x: ", y, x)

		if y == 0 and x == 0:
			return [[0,1,2], [0,1,2]]
		elif y == 0 and x == 3:
			return [[0,1,2], [3,4,5]]
		elif y == 0 and x == 6:
			return [[0,1,2], [6,7,8]]
		elif y == 3 and x == 0:
			return [[3,4,5], [0,1,2]]
		elif y == 3 and x == 3:
			return [[3,4,5], [3,4,5]]
		elif y == 3 and x == 6:
			return [[3,4,5], [6,7,8]]
		elif y == 6 and x == 0:
			return [[6,7,8], [0,1,2]]
		elif y == 6 and x == 3:
			return [[6,7,8], [3,4,5]]
		elif y == 6 and x == 6:
			return [[6,7,8], [6,7,8]]

class BuildUI(PyQt5.QtWidgets.QMainWindow, sudoku_ui.Ui_sudoku_game):
	process_start = PyQt5.QtCore.pyqtSignal()
	process_finished = PyQt5.QtCore.pyqtSignal()
	start_game_timer = PyQt5.QtCore.pyqtSignal()
	kill_timer = PyQt5.QtCore.pyqtSignal()

	def __init__(self):
		super(BuildUI, self).__init__()
		self.setupUi(self)
		self.center()
		self.easy_mode = 45
		self.medium_mode = 40
		self.hard_mode = 35
		self.stupes_mode = 30
		self.user_available_cells = []
		self.user_entries = []
		self.start_easy_game.triggered.connect(lambda: self.setup_game(self.easy_mode))
		self.start_medium_game.triggered.connect(lambda: self.setup_game(self.medium_mode))
		self.start_hard_game.triggered.connect(lambda: self.setup_game(self.hard_mode))
		self.start_stupes_game.triggered.connect(lambda: self.setup_game(self.stupes_mode))
		self.start_custom_game.clicked.connect(lambda: self.setup_game(81 - self.custom_hidden.value()))
		self.undo.clicked.connect(self.undo_last_entry)
		widgetList = self.findChildren(PyQt5.QtWidgets.QPushButton)

		for widget in widgetList:
			for char in widget.objectName():
				try:
					i = int(char)
					widget.clicked.connect(self.enter_value)
					break
				except:
					pass

		self.check_errors.clicked.connect(self.check_errors_on_board)
		self.reset_game.clicked.connect(self.reset)
		self.sudoku_table.cellClicked.connect(self.cell_activated)
		self.sudoku_table.cellChanged.connect(self.verify_user_input)

	def center(self):
		frameGm = self.frameGeometry()
		screen = PyQt5.QtWidgets.QApplication.desktop().screenNumber(PyQt5.QtWidgets.QApplication.desktop().cursor().pos())
		centerPoint = PyQt5.QtWidgets.QApplication.desktop().screenGeometry(screen).center()
		frameGm.moveCenter(centerPoint)
		self.move(frameGm.topLeft())

	def enter_value(self):
		button_name = self.sender()
		for char in button_name.objectName():
			try:
				i = int(char)
				break
			except:
				pass
		try:
			cell_value = self.sudoku_table.item(self.selected_row, self.selected_column).text()
			if cell_value == '':
				cell_item = PyQt5.QtWidgets.QTableWidgetItem()
				cell_item.setText('%s' % i)
				cell_item.setTextAlignment(PyQt5.QtCore.Qt.AlignCenter | PyQt5.QtCore.Qt.AlignVCenter)
				self.sudoku_table.setItem(self.selected_row, self.selected_column, cell_item)
			elif [self.selected_row, self.selected_column] in self.user_available_cells:
				cell_item = PyQt5.QtWidgets.QTableWidgetItem()
				cell_item.setText('%s' % i)
				cell_item.setTextAlignment(PyQt5.QtCore.Qt.AlignCenter | PyQt5.QtCore.Qt.AlignVCenter)
				self.sudoku_table.setItem(self.selected_row, self.selected_column, cell_item)

		except Exception as e:
			cell_item = PyQt5.QtWidgets.QTableWidgetItem()
			cell_item.setText('%s' % i)
			cell_item.setTextAlignment(PyQt5.QtCore.Qt.AlignCenter | PyQt5.QtCore.Qt.AlignVCenter)
			self.sudoku_table.setItem(self.selected_row, self.selected_column, cell_item)

	def check_errors_on_board(self, errors=0):
		for r in range(self.sudoku_table.rowCount()):
			for c in range(self.sudoku_table.columnCount()):
				if str(self.sudoku_table.item(r, c).text()) != str(self.game.game_board.loc[r, c]):
					errors += 1

		if errors > 0:
			SUDOKU.UI.errors_display.setText('%s' % errors)

		elif errors == 0:
			SUDOKU.UI.errors_display.setText('%s' % errors)
			SUDOKU.UI.kill_timer.emit()
			SUDOKU.dialog_window_msg = "SOLVED!!\nNICE JOB!!"
			SUDOKU.UI.process_start.emit()

	def reset(self):
		self.sudoku_table.blockSignals(True)

		for coords in self.user_available_cells:
			cell_item = PyQt5.QtWidgets.QTableWidgetItem()
			cell_item.setText('')
			cell_item.setTextAlignment(PyQt5.QtCore.Qt.AlignCenter | PyQt5.QtCore.Qt.AlignVCenter)
			self.sudoku_table.setItem(coords[0], coords[1], cell_item)
		self.sudoku_table.blockSignals(False)

	def cell_activated(self, r, c):
		self.selected_row = r
		self.selected_column = c

	def verify_user_input(self, r, c):
		if self.sudoku_table.item(r, c).text() != self.game.game_board.loc[r, c]:
			if [r, c] not in self.user_available_cells:
				cell_item = PyQt5.QtWidgets.QTableWidgetItem()
				cell_item.setText('%s' % self.game.game_board.loc[r, c])
				cell_item.setTextAlignment(PyQt5.QtCore.Qt.AlignCenter | PyQt5.QtCore.Qt.AlignVCenter)
				self.sudoku_table.blockSignals(True)
				self.sudoku_table.setItem(r, c, cell_item)
				self.sudoku_table.blockSignals(False)

		self.user_entries.append([r, c])

	def undo_last_entry(self):
		try:
			coords = self.user_entries[-1]
			self.user_entries = self.user_entries[:len(self.user_entries)-1]
			cell_item = PyQt5.QtWidgets.QTableWidgetItem()
			cell_item.setText('')
			cell_item.setTextAlignment(PyQt5.QtCore.Qt.AlignCenter | PyQt5.QtCore.Qt.AlignVCenter)
			self.sudoku_table.blockSignals(True)
			self.sudoku_table.setItem(coords[0], coords[1], cell_item)
			self.sudoku_table.blockSignals(False)
		except:
			print("Couldn't undo")

	def setup_game(self, shown_count):
		def create_game_board():
			SUDOKU.UI.kill_timer.emit()
			SUDOKU.dialog_window_msg = "CREATING GAME BOARD, \nWHICH IS SOMETIMES TOUGH.."
			SUDOKU.UI.process_start.emit()
			self.game = BuildGame()
			self.user_entries = []
			shown_per_quadrant = int(round((81 - (81 - shown_count)) / 9, 0))
			shown = set()

			for x in range(9):
				for i in [random.randrange(1 + (x * 9), 1 + ((x + 1) * 9), 1) for _ in range(shown_per_quadrant)]:
					shown.add(i)

			while len(shown) < shown_count:
				x = random.randrange(1, 81, 1)
				shown.add(x)

			i = 1

			for r in self.game.game_board.index:
				for c in self.game.game_board.columns:
					if i not in shown:
						cell_item = PyQt5.QtWidgets.QTableWidgetItem()
						cell_item.setText('')
						cell_item.setTextAlignment(PyQt5.QtCore.Qt.AlignCenter|PyQt5.QtCore.Qt.AlignVCenter)
						self.sudoku_table.setItem(r, c, cell_item)
						self.user_available_cells.append([r, c])
					else:
						cell_item = PyQt5.QtWidgets.QTableWidgetItem()
						cell_item.setText('%s' % self.game.game_board.loc[r, c])
						cell_item.setTextAlignment(PyQt5.QtCore.Qt.AlignCenter | PyQt5.QtCore.Qt.AlignVCenter)
						self.sudoku_table.setItem(r, c, cell_item)
					i += 1

			SUDOKU.UI.process_finished.emit()
			SUDOKU.UI.start_game_timer.emit()
		startThread(create_game_board)

class MsgBox(object):
	def setupUi(self, display_msg):
		display_msg.setObjectName("display_msg")
		display_msg.resize(234, 89)
		self.labelProcessStatus = QtWidgets.QLabel(display_msg)
		self.labelProcessStatus.setGeometry(QtCore.QRect(10, 15, 221, 51))
		self.labelProcessStatus.setAlignment(QtCore.Qt.AlignCenter)
		self.labelProcessStatus.setWordWrap(True)
		self.labelProcessStatus.setObjectName("labelProcessStatus")
		QtCore.QMetaObject.connectSlotsByName(display_msg)
		self.retranslateUi(display_msg)
		QtCore.QMetaObject.connectSlotsByName(display_msg)

	def retranslateUi(self, display_msg):
		_translate = QtCore.QCoreApplication.translate
		display_msg.setWindowTitle(_translate("display_msg", "PLEASE WAIT"))
		self.labelProcessStatus.setText(_translate("display_msg", "CREATING GAME BOARD, \nWHICH IS SOMETIMES TOUGH.."))

class MsgPrompt(PyQt5.QtWidgets.QDialog, MsgBox):
	app = PyQt5.QtWidgets.QApplication(sys.argv)

	def __init__(self):
		super(MsgPrompt, self).__init__()
		self.setupUi(self)

	def show_dialog_box(self):
		self.labelProcessStatus.setText('%s' % (SUDOKU.dialog_window_msg))
		super(MsgPrompt, self).exec_()

	def hide_dialog_box(self):
		self.close()

class Timer(object):
	app = PyQt5.QtWidgets.QApplication(sys.argv)

	def __init__(self):
		super(Timer, self).__init__()

	def start_timer(self):
		print("Starting timer...")
		Timer.timer = QtCore.QTimer()
		Timer.time = QtCore.QTime(0, 0, 0)
		Timer.timer.timeout.connect(self.tick)
		Timer.timer.start(1000)
		Timer.app.exec_()

	def tick(self):
		Timer.time = Timer.time.addSecs(1)
		self.update_UI('%s' % Timer.time.toString("hh:mm:ss"))

	def update_UI(self, text_string):
		# print(text_string)
		SUDOKU.UI.timer_display.setText('%s' % text_string)

	def end_timer(self):
		try:
			print('%s' % Timer.time.toString("hh:mm:ss"))
			SUDOKU.UI.timer_display.setText('%s' % Timer.time.toString("hh:mm:ss"))
			Timer.timer.stop()
		except:
			pass

class SUDOKU(object):
	def __init__(self):
		SUDOKU.app = PyQt5.QtWidgets.QApplication(sys.argv)
		SUDOKU.UI = BuildUI()
		SUDOKU.dialog_box = MsgPrompt()
		SUDOKU.timer = Timer()
		SUDOKU.UI.start_game_timer.connect(SUDOKU.timer.start_timer)
		SUDOKU.UI.kill_timer.connect(SUDOKU.timer.end_timer)
		SUDOKU.UI.process_start.connect(SUDOKU.dialog_box.show_dialog_box)
		SUDOKU.UI.process_finished.connect(SUDOKU.dialog_box.hide_dialog_box)
		SUDOKU.UI.show()
		SUDOKU.app.exec_()

def main():
	SUDOKU()

if __name__ == '__main__':
	main()