import numpy as np
import matplotlib.pyplot as plt

clean = np.fromfile("WP2/clean.dat").reshape(-1, 3)[:, :2]
slot = np.fromfile("WP2/slot.dat").reshape(-1, 3)[:, :2]
fowler = np.fromfile("WP2/fowler.dat").reshape(-1, 3)[:, :2]

plt.plot(clean[:, 0], clean[:, 1])
plt.plot(slot[:, 0], slot[:, 1])
plt.plot(fowler[:, 0], fowler[:, 1])
plt.legend(['Clean', 'Slot', 'Fowler'])
plt.grid(True, which='both', linewidth=0.5)
plt.minorticks_on()
plt.grid(True, which='minor', linestyle=':', linewidth=0.3)
ax = plt.gca()
ax.set_xlim(left=-10)
ax.spines['left'].set_color('black')
ax.spines['left'].set_linewidth(1)
ax.yaxis.set_ticks_position('left')
ax.yaxis.set_label_position('left')
ax.axvline(x=-10, color='black', linewidth=1)

ax.set_ylim(bottom=0)

plt.xlabel("Angle of attack (degrees)")
plt.ylabel('$C_{L}$ (-)')

plt.title("Lift coefficient vs angle of attack for different wing configurations")

plt.savefig("cl_vs_alpha.png", dpi=300)

plt.show()

