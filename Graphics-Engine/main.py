def foo(a):
    a *= 2
    if a < 2000:
        print(foo(a))
        
    return a
    
foo(2)