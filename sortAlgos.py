import sys
import time
from dataLoader import makeKey

sys.setrecursionlimit(100000)  # quick sort and merge sort recurse

cmp = 0  # compare count
swp = 0  # swap count

def bubbleSort(a):
    global cmp, swp
    n = len(a)
    for i in range(n):
        for j in range(n - i - 1):
            cmp += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swp += 1
    return a

def selectionSort(a):
    global cmp, swp
    n = len(a)
    for i in range(n):
        minIndex = i
        for j in range(i + 1, n):
            cmp += 1
            if a[j] < a[minIndex]:
                minIndex = j
        if minIndex != i:
            a[i], a[minIndex] = a[minIndex], a[i]
            swp += 1
    return a

def insertionSort(a):
    global cmp, swp
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            cmp += 1
            a[j + 1] = a[j]  # shift = swap
            swp += 1
            j -= 1
        a[j + 1] = key
    return a

def mergeSort(a):
    global cmp, swp
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = mergeSort(a[:mid])
    right = mergeSort(a[mid:])
    result = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        cmp += 1
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
        swp += 1  # placement = swap
    swp += (len(left) - i) + (len(right) - j)
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def partition(a, p, r):
    global cmp, swp

    pivot = a[p]
    i = p

    for j in range(p + 1, r + 1):
        cmp += 1

        if a[j] <= pivot:
            i += 1
            a[i], a[j] = a[j], a[i]
            swp += 1

    a[p], a[i] = a[i], a[p]
    swp += 1

    return i


def quickSort(a, p, r):
    if p < r:
        q = partition(a, p, r)
        quickSort(a, p, q - 1)
        quickSort(a, q + 1, r)

    return a

def heapify(a, n, i):
    global cmp, swp

    largest = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n:
        cmp += 1
        if a[left] > a[largest]:
            largest = left

    if right < n:
        cmp += 1
        if a[right] > a[largest]:
            largest = right

    if largest != i:
        a[i], a[largest] = a[largest], a[i]
        swp += 1
        heapify(a, n, largest)


def heapSort(a):
    global cmp, swp
    n = len(a)

    for i in range(n // 2 - 1, -1, -1):
        heapify(a, n, i)

    for i in range(n - 1, 0, -1):
        a[0], a[i] = a[i], a[0]
        swp += 1
        heapify(a, i, 0)

    return a

def shellSort(a):
    global cmp, swp
    n = len(a)
    gap = n // 2

    while gap > 0:
        for i in range(gap, n):
            temp = a[i]
            j = i

            while j >= gap:
                cmp += 1

                if a[j - gap] <= temp:
                    break

                a[j] = a[j - gap]
                swp += 1
                j -= gap

            a[j] = temp

        gap //= 2

    return a

def countingSort(arr):
    global cmp, swp

    lo = min(arr)
    hi = max(arr)
    count = [0] * (hi - lo + 1)
    output = [0] * len(arr)

    for x in arr:
        count[x - lo] += 1

    for i in range(1, len(count)):
        count[i] += count[i - 1]

    for x in reversed(arr):
        count[x - lo] -= 1
        output[count[x - lo]] = x
        swp += 1

    return output

def countSortByDigit(arr, exp):
    global cmp, swp

    count = [0] * 10
    output = [0] * len(arr)

    for x in arr:
        digit = (x // exp) % 10
        count[digit] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    for x in reversed(arr):
        digit = (x // exp) % 10
        count[digit] -= 1
        output[count[digit]] = x
        swp += 1

    return output


def radixSort(arr):
    global cmp, swp

    exp = 1
    biggest = max(arr)

    while biggest // exp > 0:
        arr = countSortByDigit(arr, exp)
        exp *= 10

    return arr

def bucketSort(arr):
    global cmp, swp

    n = len(arr)
    buckets = [[] for i in range(n)]

    for x in arr:
        buckets[int(n * x)].append(x)

    for b in buckets:
        insertionSort(b)

    result = []

    for b in buckets:
        result.extend(b)

    return result

def multiSort(rows, levels, kinds, name="Merge Sort"):
 
    tms = 0
    tc = 0
    ts = 0
    for col, desc in reversed(levels):
        rows, ms, c, s = runSort(rows, col, kinds[col], name, desc)
        tms += ms
        tc += c
        ts += s
    return rows, tms, tc, ts

algoNames = ["Bubble Sort", "Selection Sort", "Insertion Sort", "Merge Sort", "Quick Sort",
             "Heap Sort", "Shell Sort", "Counting Sort", "Radix Sort", "Bucket Sort"]

algoFuncs = {
    "Bubble Sort": bubbleSort,
    "Selection Sort": selectionSort,
    "Insertion Sort": insertionSort,
    "Merge Sort": mergeSort,
    "Quick Sort": quickSort,
    "Heap Sort": heapSort,
    "Shell Sort": shellSort,
    "Counting Sort": countingSort,
    "Radix Sort": radixSort,
    "Bucket Sort": bucketSort,
}

# complexity, stable
algoInfo = {
    "Bubble Sort": ["O(n²)", "Stable"],
    "Selection Sort": ["O(n²)", "Unstable"],
    "Insertion Sort": ["O(n²)", "Stable"],
    "Merge Sort": ["O(n log n)", "Stable"],
    "Quick Sort": ["O(n log n) avg, O(n²) worst", "Unstable"],
    "Heap Sort": ["O(n log n)", "Unstable"],
    "Shell Sort": ["O(n²) worst", "Unstable"],
    "Counting Sort": ["O(n + k)", "Stable"],
    "Radix Sort": ["O(d · (n + b))", "Stable"],
    "Bucket Sort": ["O(n + k) avg, O(n²) worst", "Stable"],
}

def whyNot(name, rows, col, kind):
    if len(rows) == 0:
        return ""

    if name == "Counting Sort" or name == "Radix Sort" or name == "Bucket Sort":
        if kind != "num":
            return "needs a number column"

    if name == "Counting Sort" or name == "Radix Sort":
        vals = [r[col] for r in rows]

        for v in vals:
            if v != int(v):
                return "needs whole numbers"

        if name == "Radix Sort" and min(vals) < 0:
            return "needs numbers 0 or more"

        if name == "Counting Sort" and max(vals) - min(vals) > 5000000:
            return "value range is too big"

    return ""


def runSort(rows, col, kind, name, desc=False):
    global cmp, swp

    cmp = 0
    swp = 0

    if len(rows) == 0:
        return [], 0, 0, 0

    keys = []
    waiting = {}

    for r in rows:
        k = makeKey(r[col], kind)
        keys.append(k)

        if k not in waiting:
            waiting[k] = []

        waiting[k].append(r)

    start = time.perf_counter()

    if name == "Quick Sort":
        keys = quickSort(keys, 0, len(keys) - 1)
    elif name == "Counting Sort":
        keys = countingSort([int(k) for k in keys])
    elif name == "Radix Sort":
        keys = radixSort([int(k) for k in keys])
    elif name == "Bucket Sort":
        lo = min(keys)
        span = max(keys) - lo
        if span == 0:
            span = 1
        back = {}
        scaled = []
        for k in keys:
            x = (k - lo) / (span * 1.000001)  # between 0 and 1, as bucketSort needs
            scaled.append(x)
            back[x] = k
        keys = []
        for x in bucketSort(scaled):
            keys.append(back[x])
    else:
        keys = algoFuncs[name](keys)

    ms = (time.perf_counter() - start) * 1000

    if desc:
        keys.reverse()

    out = []

    for k in keys:
        out.append(waiting[k].pop(0))

    return out, ms, cmp, swp