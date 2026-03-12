with open('WP2/Airfoils/ms313.dat', 'r') as f: lines = f.readlines()
with open('WP2/Airfoils/ms313_inverted.dat', 'w') as f: f.writelines([lines[0]] + lines[1:][::-1])