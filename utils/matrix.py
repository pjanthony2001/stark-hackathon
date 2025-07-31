from utils.field import Field, FieldElement

class Matrix():
    
    def __init__(self, m: int, n: int, values: list[FieldElement]):
        assert len(values) == m * n
        assert FieldElement.field_eq(values)

        self.dimensions = (m, n)
        self.rows = m
        self.columns = n
        self.matrix = [[values[i * n + j] for j in range(n)] for i in range(m)]
        self.values = values
    
    def __str__(self):
        return "[" + "".join([f"{row},\n" for row in self.matrix[:-1]] + [f"{self.matrix[-1]}"]) + "]"
 
    def __add__(self, right: 'Matrix'):
        assert self.dimensions == right.dimensions

        m, n = self.dimensions
        return Matrix(m, n, [self.values[i] + right.values[i] for i in range(m * n)])
    
    def dot(self, right: 'Matrix'):
        assert self.columns == right.rows
        
        n = self.columns
        values = [FieldElement(Field.main(),0)] * (self.rows * right.columns)
        
        for i in range(self.rows):
            for j in range(right.columns):
                sum = FieldElement(Field.main(),0)
                for k in range(n):
                    print(type(self.matrix[i][k]))
                    sum = sum + self.matrix[i][k] * right.matrix[k][j]
                values[i * right.columns + j] = sum
        return Matrix(self.rows, right.columns, values)

    def __rmul__(self, scalar: FieldElement):
        values = [scalar * x for x in self.values]
        return Matrix(self.rows, self.columns, values)

    def __sub__(self, right: 'Matrix'):
        assert self.dimensions == right.dimensions
        return self.__add__(right.__rmul__( FieldElement(Field.main(),-1) ))

    def transpose(self):
        values = []
        for j in range(self.columns):
            for i in range(self.rows):
                values.append( self.values[i * self.columns + j] )
        return Matrix(self.columns, self.rows, values)
    
    def is_square(self):
        return self.rows == self.columns
    
    
class Vector(Matrix):
    
    def __init__(self, m: int, values: list[FieldElement]):
        assert len(values) == m
        super().__init__(m, 1, values)
    
    def __str__(self):
        return "[" + "".join([f"{row[0]}," for row in self.matrix[:-1]] + [f"{self.matrix[-1][0]}"]) + "]"
    
    def __mul__(self, scalar: FieldElement):
        return Vector(self.rows, [scalar * x for x in self.values])