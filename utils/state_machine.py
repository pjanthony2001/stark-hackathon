# # 

from utils.matrix import Matrix
from utils.field import Field, Fieldelement


class State_machine:
    def computational_trace_1(x0:'Matrix', A:'Matrix', T:int, F:'Field')->'Matrix':
        # For relationships x_{i+1}=A x_i
        # x0 is a vector, A is a matrix, T is the number of iterations
        w=len(x0.values)
        xi=x0
        zero=Fieldelement(F,0)
        liste_de_zeros=[zero]*(T*w)
        matrix=Matrix(T,w,liste)
        for i in range(T):
            for j in range(w):
                matrix.matrix[i][j]=xi.values[j]
                matrix.values[i*w+j]=xi.values[j]
            xi=A.dot(xi)
        return matrix

    def polynome_j_degree1(j:'int', x:'Matrix', y:'Matrix', A:'Matrix')->'float':
        Aj=Matrix(1,A.columns,A.matrix[j])
        return y.values[j]-Aj.dot(x)

    def computational_trace_2(x0:'Matrix', M:'list[Matrix]', T:'int',F:'field')->'Matrix':
        # For relationships x_{i+1}=SUM(A_j (x_i)^j)
        # x0 is a vector, M is a list of matrix, T is the number of iterations
        w=len(x0.values)
        n=len(M)
        xi=x0
        zero=Fieldelement(F,0)
        liste=[zero]*(T*w)
        matrix=Matrix(T,w,liste)
        for i in range(T):
            for j in range(w):
                matrix.matrix[i][j]=xi[j]
                matrix.values[w*i+j]=xi[j]
            x=Matrix(w,1,[zero]*w)
            for k in range(n):
                A=M[k]
                xi_power_j=Matrix(w,1,[(xi.values[s])**j for s in range(w)])
                x=x+A.dot(xi_power_j)
            xi=x
        return matrix

    def polynome_j(j:'int', x:'Matrix', y:'Matrix', M:'list[Matrix]')->'float':
        n=len(M)
        P=y.values[j]
        for i in range(n):
            A=M[i]
            Aj=Matrix(1,len(A.matrix[j]),A.matrix[j])
            x_power_i=Matrix(len(x.values),1,[x.values[k]**i for k in range(len(x.values))])
            P=P-Aj.dot(x_power_i)
        return P




