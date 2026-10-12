import matplotlib.pyplot as plt

x = [10, 20, 30, 40]
y = [100, 200, 300, 400]

plt.figure(figsize=(6, 4))
plt.plot(x, y, marker="o", color="#8c1d40", linewidth=2)
plt.title("Line Plot")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.grid(True)
plt.tight_layout()
plt.show()

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.savefig('plot.png', dpi=150, bbox_inches='tight', facecolor='white')
