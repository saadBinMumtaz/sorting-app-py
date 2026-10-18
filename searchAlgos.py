from dataLoader import makeKey
from filters import check

def columnValues(rows, col, kind):
    # just the values of one column (text in lowercase)
    values = []
    for r in rows:
        values.append(makeKey(r[col], kind))
    return values

def linearSearch(values, op, val):
    # any operator. Returns the positions of the matches
    found = []
    for i in range(len(values)):
        if check(values[i], op, val):
            found.append(i)
    return found

def binarySearch(values, val):
    # values must be sorted
    lo = 0
    hi = len(values)
    while lo < hi:
        mid = (lo + hi) // 2
        if values[mid] < val:
            lo = mid + 1
        else:
            hi = mid
    found = []
    while lo < len(values) and values[lo] == val:
        found.append(lo)
        lo += 1
    return found

def jumpSearch(values, val):
    # values must be sorted
    n = len(values)
    if n == 0:
        return []
    step = max(1, int(n ** 0.5))
    prev = 0
    cur = step
    while prev < n and values[min(cur, n) - 1] < val:
        prev = cur
        cur += step
    found = []
    i = prev
    while i < n and values[i] <= val:
        if values[i] == val:
            found.append(i)
        i += 1
    return found