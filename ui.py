import time
from PyQt5.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem, QAbstractItemView,
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QComboBox,
    QCheckBox, QPushButton, QLabel, QLineEdit, QDialog, QApplication
)
from PyQt5.QtGui import QColor
from dataLoader import loadData, toKey
from sortAlgos import algoNames, algoInfo, runSort, whyNot, multiSort
from searchAlgos import strOps, numOps, columnValues, linearSearch, binarySearch, jumpSearch, compFilter

qss = """
QWidget { background-color: #1e1e2e; color: #cdd6f4; font-size: 13px; }
QPushButton { background-color: #89b4fa; color: #1e1e2e; border: none;
              border-radius: 6px; padding: 6px 14px; font-weight: bold; }
QPushButton:hover { background-color: #b4befe; }
QPushButton:disabled { background-color: #45475a; color: #7f849c; }
QPushButton#go { background-color: #a6e3a1; }
QPushButton#go:hover { background-color: #94e2d5; }
QLineEdit, QComboBox, QSpinBox { background-color: #313244; border: 1px solid #45475a;
                                 border-radius: 4px; padding: 4px; }
QTableView { background-color: #181825; alternate-background-color: #1e1e2e;
             gridline-color: #313244; selection-background-color: #89b4fa;
             selection-color: #1e1e2e; }
QHeaderView::section { background-color: #313244; padding: 6px; border: none; }
QTabBar::tab { background: #313244; padding: 8px 16px; }
QTabBar::tab:selected { background: #89b4fa; color: #1e1e2e; }
"""

benchRows = 3000
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


def showBenchmark(result, colName, n, parent):
    dlg = QDialog(parent)
    dlg.setWindowTitle(f"Benchmark: {colName} ({n:,} rows)")
    dlg.resize(820, 380)

    layout = QVBoxLayout(dlg)

    table = QTableWidget(len(result), 6)
    table.setHorizontalHeaderLabels(
        ["Algorithm", "Complexity", "Stable", "Time (ms)", "Comparisons", "Swaps"]
    )

    for i, row in enumerate(result):
        for j, value in enumerate(row):
            table.setItem(i, j, QTableWidgetItem(str(value)))

    table.resizeColumnsToContents()
    layout.addWidget(table)
    dlg.exec()


def buildWindow():
    cols, kinds, rows = loadData("data/spotify_songs.csv")

    state["cols"] = cols
    state["kinds"] = kinds
    state["full"] = rows
    state["shown"] = rows
    state["algoFor"] = {}

    win = QMainWindow()
    win.setStyleSheet(qss)
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
    tabs.addTab(buildMultiTab(), "Multi-Sort")
    tabs.addTab(buildSearchTab(), "Search")
    tabs.addTab(buildCompTab(), "Filters (AND/OR/NOT)")
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

    showRows(rows)
    return win


def status(text):
    ui["win"].statusBar().showMessage(text)


def showRows(rows, sortCol=-1):
    state["shown"] = rows
    fillTable(rows, sortCol)
    status(f"Showing {len(rows):,} of {len(state['full']):,} rows")


refresh = showRows


def sourceRows():
    if ui["scopeBox"].currentIndex() == 0:
        return state["full"]
    return state["shown"]


def buildSortTab():
    tab = QWidget()
    layout = QHBoxLayout(tab)

    colBox = QComboBox()
    colBox.addItems(state["cols"])

    algoBox = QComboBox()
    algoBox.addItems(algoNames)

    descChk = QCheckBox("Descending")
    sortBtn = QPushButton("Sort")
    sortBtn.setObjectName("go")
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
    benchBtn.clicked.connect(doBench)

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


def sortDone(result, col=-1):
    rows, ms, comparisons, swaps = result

    showRows(rows, col)

    ui["resLbl"].setText(
        f"Time: {ms:.2f} ms | "
        f"Comparisons: {comparisons:,} | Swaps: {swaps:,}"
    )


def doBench():
    col = ui["colBox"].currentIndex()
    kind = state["kinds"][col]
    rows = sourceRows()[:benchRows]

    result = []

    for name in algoNames:
        info = algoInfo[name]

        status("Running " + name + " ...")
        QApplication.processEvents()

        why = whyNot(name, rows, col, kind)

        if why != "":
            result.append([name, info[0], info[1], "N/A: " + why, "-", "-"])
        else:
            out, ms, c, s = runSort(rows, col, kind, name)
            result.append([name, info[0], info[1], f"{ms:.2f}", f"{c:,}", f"{s:,}"])

    status("Benchmark finished")
    showBenchmark(result, state["cols"][col], len(rows), ui["win"])


def buildMultiTab():
    tab = QWidget()
    lay = QHBoxLayout(tab)
    ui["lvls"] = []
    for i in range(3):
        cb = QComboBox()
        cb.addItems(["(none)"] + state["cols"])
        ob = QComboBox()
        ob.addItems(["Ascending", "Descending"])
        lay.addWidget(QLabel(f"Level {i + 1}"))
        lay.addWidget(cb)
        lay.addWidget(ob)
        ui["lvls"].append([cb, ob])
    mAlgo = QComboBox()
    mAlgo.addItems(algoNames)
    mAlgo.setCurrentText("Merge Sort")
    mBtn = QPushButton("Multi-Sort")
    mBtn.clicked.connect(doMulti)
    ui["mAlgo"] = mAlgo
    lay.addWidget(mAlgo)
    lay.addWidget(mBtn)
    return tab


def doMulti():
    lv = []
    for pair in ui["lvls"]:
        cb = pair[0]
        ob = pair[1]
        if cb.currentIndex() > 0:
            lv.append((cb.currentIndex() - 1, ob.currentIndex() == 1))
    if len(lv) == 0:
        status("Pick at least one level")
        return
    rows = sourceRows()
    name = ui["mAlgo"].currentText()
    for col, desc in lv:
        why = whyNot(name, rows, col, state["kinds"][col])
        if why != "":
            status(f"{name} can't sort {state['cols'][col]}: {why}")
            return
    status("Sorting ... please wait")
    QApplication.processEvents()
    sortDone(multiSort(rows, lv, state["kinds"], name))


def buildSearchTab():
    tab = QWidget()
    lay = QHBoxLayout(tab)

    sCol = QComboBox()
    sCol.addItems(state["cols"])

    sOp = QComboBox()

    sVal = QLineEdit()
    sVal.setPlaceholderText("value")

    sAlgo = QComboBox()
    sAlgo.addItems(["Linear Search", "Binary Search", "Jump Search"])

    sBtn = QPushButton("Search")
    rBtn = QPushButton("Reset")

    ui["sCol"] = sCol
    ui["sOp"] = sOp
    ui["sVal"] = sVal
    ui["sAlgo"] = sAlgo

    for w in (QLabel("Column"), sCol, sOp, sVal, QLabel("Algorithm"), sAlgo, sBtn, rBtn):
        lay.addWidget(w)

    sCol.currentIndexChanged.connect(fillOps)
    sOp.currentTextChanged.connect(checkAlgo)
    sBtn.clicked.connect(doSearch)
    rBtn.clicked.connect(doReset)

    fillOps()
    return tab


def fillOps():
    ui["sOp"].clear()
    if state["kinds"][ui["sCol"].currentIndex()] == "str":
        ui["sOp"].addItems(strOps)
    else:
        ui["sOp"].addItems(numOps)


def checkAlgo():
    isExact = ui["sOp"].currentText() in ("equals", "=")
    ui["sAlgo"].setEnabled(isExact)  # only exact match can use binary or jump search


def doSearch():
    col = ui["sCol"].currentIndex()
    kind = state["kinds"][col]
    op = ui["sOp"].currentText()
    name = ui["sAlgo"].currentText()

    try:
        val = toKey(ui["sVal"].text(), kind)
    except ValueError:
        status("Please enter a valid number")
        return

    isExact = op in ("equals", "=")
    rows = state["full"]

    if isExact and name != "Linear Search":
        rows = runSort(rows, col, kind, "Merge Sort")[0]  # binary and jump need sorted rows (not timed)

    if not isExact:
        name = "Linear Search"

    values = columnValues(rows, col, kind)  # just this column (not timed)

    start = time.perf_counter()
    if name == "Binary Search":
        spots = binarySearch(values, val)
    elif name == "Jump Search":
        spots = jumpSearch(values, val)
    else:
        spots = linearSearch(values, op, val)
    ms = (time.perf_counter() - start) * 1000

    res = []
    for i in spots:
        res.append(rows[i])  # the rows at those positions

    showRows(res)
    ui["resLbl"].setText(f"{len(res):,} found in {ms:.3f} ms ({name})")
    status(f"{len(res):,} found in {ms:.3f} ms ({name})")


def doReset():
    showRows(state["full"])


def makeCondRow(cols, kinds, first):
    widget = QWidget()
    lay = QHBoxLayout(widget)
    lay.setContentsMargins(0, 0, 0, 0)
    join = QComboBox()
    join.addItems(["AND", "OR"])
    join.setVisible(not first)  # no join on first
    neg = QCheckBox("NOT")
    colBox = QComboBox()
    colBox.addItems(cols)
    opBox = QComboBox()
    valBox = QLineEdit()
    for w in (join, neg, colBox, opBox, valBox):
        lay.addWidget(w)

    def fillOps():
        opBox.clear()
        if kinds[colBox.currentIndex()] == "str":
            opBox.addItems(strOps)
        else:
            opBox.addItems(numOps)

    colBox.currentIndexChanged.connect(fillOps)
    fillOps()
    return {"widget": widget, "join": join, "neg": neg, "col": colBox,
            "op": opBox, "val": valBox, "kinds": kinds}


def getCond(row):
    c = row["col"].currentIndex()
    val = toKey(row["val"].text(), row["kinds"][c])  # may raise ValueError
    return (c, row["op"].currentText(), val, row["neg"].isChecked())


def buildCompTab():
    tab = QWidget()
    lay = QVBoxLayout(tab)
    rowBox = QVBoxLayout()
    ui["rowBox"] = rowBox
    lay.addLayout(rowBox)
    ui["conds"] = []
    addCond()
    btns = QHBoxLayout()
    addBtn = QPushButton("+ Add condition")
    delBtn = QPushButton("- Remove last")
    fBtn = QPushButton("Apply filter")
    fResetBtn = QPushButton("Reset")
    for b in (addBtn, delBtn, fBtn, fResetBtn):
        btns.addWidget(b)
    lay.addLayout(btns)
    addBtn.clicked.connect(addCond)
    delBtn.clicked.connect(delCond)
    fBtn.clicked.connect(doComp)
    fResetBtn.clicked.connect(doReset)
    return tab


def addCond():
    first = len(ui["conds"]) == 0
    row = makeCondRow(state["cols"], state["kinds"], first)
    ui["conds"].append(row)
    ui["rowBox"].addWidget(row["widget"])


def delCond():
    if len(ui["conds"]) > 1:
        row = ui["conds"].pop()
        row["widget"].setParent(None)


def doComp():
    conds = []
    try:
        for row in ui["conds"]:
            conds.append(getCond(row))
    except ValueError:
        status("A number column needs a valid number")
        return
    joins = []
    for row in ui["conds"][1:]:
        joins.append(row["join"].currentText())
    t0 = time.perf_counter()
    res = compFilter(state["full"], conds, joins, state["kinds"])
    ms = (time.perf_counter() - t0) * 1000
    showRows(res)
    ui["resLbl"].setText(f"{len(res):,} found in {ms:.2f} ms (composite filter)")
    status(f"{len(res):,} found in {ms:.2f} ms (composite filter)")