from dataLoader import makeKey

strOps = ["contains", "startsWith", "endsWith", "equals", "notContains"]
numOps = ["=", "!=", ">", "<", ">=", "<="]

def check(cell, op, val):
    # both in key form
    if op == "contains":
        return val in cell
    if op == "notContains":
        return val not in cell
    if op == "startsWith":
        return cell.startswith(val)
    if op == "endsWith":
        return cell.endswith(val)
    if op == "equals" or op == "=":
        return cell == val
    if op == "!=":
        return cell != val
    if op == ">":
        return cell > val
    if op == "<":
        return cell < val
    if op == ">=":
        return cell >= val
    if op == "<=":
        return cell <= val
    return False

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


def matchOne(row, cond, kinds):
    # col, op, val, neg
    col, op, val, neg = cond
    ok = check(makeKey(row[col], kinds[col]), op, val)
    if neg:
        return not ok
    return ok


def matchRow(row, conds, joins, kinds):
    # AND before OR
    total = False
    grp = matchOne(row, conds[0], kinds)
    for i in range(1, len(conds)):
        m = matchOne(row, conds[i], kinds)
        if joins[i - 1] == "AND":
            grp = grp and m
        else:
            total = total or grp
            grp = m
    return total or grp


def compFilter(rows, conds, joins, kinds):
    if not conds:
        return list(rows)
    out = []
    for r in rows:
        if matchRow(r, conds, joins, kinds):
            out.append(r)
    return out