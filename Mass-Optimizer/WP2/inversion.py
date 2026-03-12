with open('l188tip.dat', 'r') as f: lines = f.readlines()
with open('l188tipinverted.dat', 'w') as f: f.writelines([lines[0]] + lines[1:][::-1])
