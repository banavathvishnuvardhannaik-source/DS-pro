import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

np.random.seed(5)
data = np.random.randn(200)

sns.boxplot(x=data, color="#c9a227")
plt.title("Box Plot")
plt.tight_layout()
plt.show()

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.savefig('plot.png', dpi=150, bbox_inches='tight', facecolor='white')
