import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame({
    "category": ["A", "B", "C"],
    "values": [100, 200, 215],
})

df.plot(kind="bar", x="category", y="values",
        color="#c9a227", legend=False)
plt.title("Bar Plot")
plt.ylabel("Value")
plt.tight_layout()
plt.show()

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.savefig('plot.png', dpi=150, bbox_inches='tight', facecolor='white')
