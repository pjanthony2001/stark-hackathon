import numpy as np


# +
def computational_trace_1(x0:np.ndarray, A:np.ndarray, T:int)->np.ndarray:
    # For relationships x_{i+1}=A x_i
    # x0 is a vector, A is a matrix, T is the number of iterations
    w=len(x0)
    xi=x0
    Matrix=np.zeros((T,w))
    for i in range(T):
        Matrix[i]=xi
        xi=np.dot(A,xi)
    return Matrix

def computational_trace_2(x0:np.ndarray, M:np.ndarray, T:int)->np.ndarray:
    # For relationships x_{i+1}=SUM(A_j (x_i)^j)
    # x0 is a vector, M is a list of matrix, T is the number of iterations
    w=len(x0)
    n=len(M)
    xi=x0
    Matrix=np.zeros((T,w))
    for i in range(T):
        Matrix[i]=xi
        x=np.zeros(w)
        for j in range(n):
            A=M[j]
            x=x+np.dot(A,(xi**j))
        xi=x
    return Matrix

def polynome_j_degree1(j:int, x:np.ndarray, y:np.ndarray, A:np.ndarray)->float:
    return y[j]-np.dot(A[j],x)

def polynome_j(j:int, x:np.ndarray, y:np.ndarray, M:np.ndarray)->float:
    n=len(M)
    P=y[j]
    for i in range(n):
        A=M[i]
        Aj=A[j]
        P=P-np.dot(Aj,(x**i))
    return P
# -


