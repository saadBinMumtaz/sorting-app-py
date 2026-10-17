from PyQt5.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem, QAbstractItemView,
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QComboBox,
    QCheckBox, QPushButton, QLabel, QApplication
)
from PyQt5.QtGui import QColor
from dataLoader import loadData
from sortAlgos import algoNames, algoInfo, runSort, whyNot

state = {}
ui = {}


def fillTable(rows, sortCol=-1):
    table = ui["table"]
    table.setUpdatesEnabled(False)  # faster while filling
    table.clearContents()
    table.setRowCount(len(rows))

    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            item = QTableWidgetItem(str(value))

            if j == sortCol:
                item.setBackground(QColor("#2a2a3d"))

            table.setItem(i, j, item)

    table.setUpdatesEnabled(True)


def buildWindow():
    cols, kinds, rows = loadData("data/spotify_songs.csv")

    state["cols"] = cols
    state["kinds"] = kinds
    state["full"] = rows
    state["shown"] = rows
    state["algoFor"] = {}

    win = QMainWindow()
    win.setWindowTitle("Data Sorter")
    win.resize(1300, 750)
    ui["win"] = win

    table = QTableWidget()
    table.setColumnCount(len(cols))
    table.setHorizontalHeaderLabels(cols)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.setAlternatingRowColors(True)
    ui["table"] = table

    tabs = QTabWidget()
    tabs.addTab(buildSortTab(), "Sort")
    ui["tabs"] = tabs

    layout = QVBoxLayout()
    layout.addWidget(tabs)

    bar = QHBoxLayout()
    bar.addWidget(QLabel("Sort scope:"))

    scopeBox = QComboBox()
    scopeBox.addItems(["Full dataset", "Filtered results"])
    ui["scopeBox"] = scopeBox
    bar.addWidget(scopeBox)

    layout.addLayout(bar)
    layout.addWidget(table)

    root = QWidget()
    root.setLayout(layout)
    win.setCentralWidget(root)

    table.horizontalHeader().sectionClicked.connect(
        ui["colBox"].setCurrentIndex
    )

    refresh(rows)
    return win


def status(text):
    ui["win"].statusBar().showMessage(text)


def buildSortTab():
    tab = QWidget()
    layout = QHBoxLayout(tab)

    colBox = QComboBox()
    colBox.addItems(state["cols"])

    algoBox = QComboBox()
    algoBox.addItems(algoNames)

    descChk = QCheckBox("Descending")
    sortBtn = QPushButton("Sort")
    benchBtn = QPushButton("Benchmark")

    infoLbl = QLabel()
    resLbl = QLabel("Time: - | Comparisons: - | Swaps: -")

    ui["colBox"] = colBox
    ui["algoBox"] = algoBox
    ui["descChk"] = descChk
    ui["sortBtn"] = sortBtn
    ui["benchBtn"] = benchBtn
    ui["infoLbl"] = infoLbl
    ui["resLbl"] = resLbl

    layout.addWidget(QLabel("Column"))
    layout.addWidget(colBox)
    layout.addWidget(QLabel("Algorithm"))
    layout.addWidget(algoBox)
    layout.addWidget(descChk)
    layout.addWidget(sortBtn)
    layout.addWidget(benchBtn)
    layout.addWidget(infoLbl)
    layout.addWidget(resLbl)

    colBox.currentIndexChanged.connect(onColChange)
    algoBox.currentTextChanged.connect(onAlgoChange)
    sortBtn.clicked.connect(doSort)

    onAlgoChange(algoBox.currentText())
    return tab


def onAlgoChange(name):
    info = algoInfo[name]
    ui["infoLbl"].setText(info[0] + " | " + info[1])

    col = ui["colBox"].currentIndex()
    state["algoFor"][col] = name


def onColChange(col):
    if col in state["algoFor"]:
        ui["algoBox"].setCurrentText(state["algoFor"][col])


def refresh(rows, sortCol=-1):
    state["shown"] = rows
    fillTable(rows, sortCol)
    status(f"Showing {len(rows):,} of {len(state['full']):,} rows")


def sourceRows():
    if ui["scopeBox"].currentIndex() == 0:
        return state["full"]

    return state["shown"]


def doSort():
    col = ui["colBox"].currentIndex()
    name = ui["algoBox"].currentText()
    desc = ui["descChk"].isChecked()
    src = sourceRows()
    kind = state["kinds"][col]

    why = whyNot(name, src, col, kind)
    if why != "":
        status(name + ": " + why)
        return

    status("Sorting with " + name + " ... please wait")
    QApplication.processEvents()  # shows the message before the sort starts

    sortDone(runSort(src, col, kind, name, desc), col)


def sortDone(result, col):
    rows, ms, comparisons, swaps = result

    refresh(rows, col)

    ui["resLbl"].setText(
        f"Time: {ms:.2f} ms | "
        f"Comparisons: {comparisons:,} | Swaps: {swaps:,}"
    )