import numpy as np
import matplotlib.pyplot as plt

np.random.seed(1)
x = np.random.rand(50)
y = np.random.rand(50)

plt.figure(figsize=(6, 4))
plt.scatter(x, y, s=70, c="#0f766e", alpha=0.75, edgecolors="white")
plt.title("Scatter Plot")
plt.xlabel("X")
plt.ylabel("Y")
plt.tight_layout()
plt.show()

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.savefig('plot.png', dpi=150, bbox_inches='tight', facecolor='white')
