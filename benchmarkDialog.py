from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem


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