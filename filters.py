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