import random


def randomMtr(rows, cols):
    matrix = []
    for i in range(rows):
        row = []

        for j in range(cols):
            row.append(random.randint(-10, 10))

        matrix.append(row)

    return (matrix)


def var3(matrix):
    zeroElemCols = 0
    cols = len(matrix[0])
    rows = len(matrix)

    for j in range(cols):
        for i in range(rows):
            if matrix[i][j] == 0:
                zeroElemCols += 1
                break

    maxRepeat = 0
    maxRepeatRow = -1

    for i in range(rows):
        currentRepeat = 1
        maxInRow = 1

        for j in range(1, len(matrix[i])):
            if matrix[i][j] == matrix[i][j - 1]:
                currentRepeat += 1
            else:
                currentRepeat = 1

            maxInRow = max(maxInRow, currentRepeat)

        if maxInRow > maxRepeat:
            maxRepeat = maxInRow
            maxRepeatRow = i

    return zeroElemCols, maxRepeatRow


def var15(matrix):
    firstZeroElemCols = -1
    cols = len(matrix[0])
    rows = len(matrix)

    for j in range(cols):
        for i in range(rows):
            if matrix[i][j] == 0:
                firstZeroElemCols = j
                break

        if firstZeroElemCols != -1:
            break

    rowsSums = []

    for i in range(rows):
        negativeSum = 0

        for j in range(cols):
            if matrix[i][j] < 0 and matrix[i][j] % 2 == 0:
                negativeSum += matrix[i][j]

        rowsSums.append((negativeSum, matrix[i]))

    rowsSums.sort()


    return firstZeroElemCols, rowsSums


def var5(matrix):
    cols = len(matrix[0])
    rows = len(matrix)
    allSum = 0

    for j in range(cols):
        positiveSum = 0
        isPositive = True

        for i in range(rows):
            if matrix[i][j] < 0:
                isPositive = False
                break
            else:
                positiveSum += matrix[i][j]

        if isPositive:
            allSum += positiveSum

    diaganalSum = {}

    for i in range(rows):
        for j in range(rows):
            diaganalIndex = i + j

            if diaganalIndex not in diaganalSum:
                diaganalSum[diaganalIndex] = 0
            diaganalSum[diaganalIndex] += abs(matrix[i][j])

    return allSum, min(diaganalSum.values())



rows = int(input('Enter numbers of rows: '))
cols = int(input('Enter numbers of cols: '))

matrix = randomMtr(rows, cols)

for row in matrix:
    for num in row:
        print(f"{num:4}", end="")
    print()

option = int(input('Choose the variant (3, 15, 5): '))

match option:
    case 3:
        result1, result2 = var3(matrix)
        print(f"Number of columns containing at least one null element: {result1}. "
              f"The number of the row containing the longest series of identical elements: {result2}")
    case 15:
        result3, result4 = var15(matrix)
        print(f"Determine the number of the first column containing at least one zero element: {result3}.  "
              f"Rearranging the rows of a given matrix, arrange them in descending order of characteristics: {result4}.")
    case 5:
        result5, result6 = var5(matrix)
        print(f"The sum of the elements in those columns that do not contain negative elements: {result5}. "
              f"Minimum among the sums of the moduli of the elements of the diagonals parallel to the secondary diagonal of the matrix: {result6}.")
    case _:
        print('Wrong')
