import random


class MatrixClass:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.matrix = self.random_matrix()

    def random_matrix(self):
        matrix = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                row.append(random.randint(-10, 10))
            matrix.append(row)
        return matrix


    def display_matrix(self):
        for row in self.matrix:
            for num in row:
                print(f"{num:4}", end="")
            print()


    def var3(self):
        zeroElemCols = 0
        for j in range(self.cols):
            for i in range(self.rows):
                if self.matrix[i][j] == 0:
                    zeroElemCols += 1
                    break

        maxRepeat = 0
        maxRepeatRow = -1
        for i in range(self.rows):
            currentRepeat = 1
            maxInRow = 1
            for j in range(1, self.cols):
                if self.matrix[i][j] == self.matrix[i][j - 1]:
                    currentRepeat += 1
                else:
                    currentRepeat = 1
                maxInRow = max(maxInRow, currentRepeat)
            if maxInRow > maxRepeat:
                maxRepeat = maxInRow
                maxRepeatRow = i

        return zeroElemCols, maxRepeatRow

    def var15(self):
        firstZeroElemCols = -1
        for j in range(self.cols):
            for i in range(self.rows):
                if self.matrix[i][j] == 0:
                    firstZeroElemCols = j
                    break
            if firstZeroElemCols != -1:
                break

        rowsSums = []
        for i in range(self.rows):
            negativeSum = sum(x for x in self.matrix[i] if x < 0 and x % 2 == 0)
            rowsSums.append((negativeSum, self.matrix[i]))

        rowsSums.sort()
        return firstZeroElemCols, rowsSums

    def var5(self):
        allSum = 0
        for j in range(self.cols):
            positiveSum = 0
            isPositive = True
            for i in range(self.rows):
                if self.matrix[i][j] < 0:
                    isPositive = False
                    break
                else:
                    positiveSum += self.matrix[i][j]
            if isPositive:
                allSum += positiveSum

        diaganalSum = {}
        for i in range(self.rows):
            for j in range(self.cols):
                diaganalIndex = i + j
                diaganalSum[diaganalIndex] = diaganalSum.get(diaganalIndex, 0) + abs(self.matrix[i][j])

        return allSum, min(diaganalSum.values())



rows = int(input('Enter numbers of rows: '))
cols = int(input('Enter numbers of cols: '))

randMatix = MatrixClass(rows, cols)
randMatix.display_matrix()

option = int(input('Choose the variant (3, 15, 5): '))

match option:
    case 3:
        result1, result2 = randMatix.var3()
        print(f"Number of columns containing at least one null element: {result1}. "
              f"The number of the row containing the longest series of identical elements: {result2}")
    case 15:
        result3, result4 = randMatix.var15()
        print(f"Determine the number of the first column containing at least one zero element: {result3}.  "
              f"Rearranging the rows of a given matrix, arrange them in descending order of characteristics: {result4}.")
        for _, row in result4:
            print(row)
    case 5:
        result5, result6 = randMatix.var5()
        print(f"The sum of the elements in those columns that do not contain negative elements: {result5}. "
              f"Minimum among the sums of the moduli of the elements of the diagonals parallel to the secondary diagonal of the matrix: {result6}.")
    case _:
        print('Wrong')
