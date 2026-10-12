import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

np.random.seed(42)
data = np.random.randn(1000)

sns.histplot(data, kde=True, color="#8c1d40")
plt.title("Histogram & Density")
plt.tight_layout()
plt.show()

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.savefig('plot.png', dpi=150, bbox_inches='tight', facecolor='white')
