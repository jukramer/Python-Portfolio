import numpy as np

N = 4

a=np.arange(N)[None, :]
b=np.arange(N)[:, None]

# print((a-b))
# print(idx:=(a-b)%N)
# print('\n\n\n')

a = np.array([[1,2,3],
              [4,5,6]])

b = np.array([[[1,2,3],
               [1,2,3]],
              [[4,5,6],
               [1,2,3]]])


print(a[::-1,:])