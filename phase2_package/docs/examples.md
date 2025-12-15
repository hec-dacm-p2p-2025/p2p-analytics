# Examples

This page provides practical workflow using `p2p_analytics`.

--- 
## Example 1 - Spread dynamics over time

```python
import matplotlib.pyplot as plt
from p2p_analytics import p2p_spread

spread = p2p_spread("ARS", by="day", root=PHASE1_ROOT)

plt.plot(spread["date"], spread["spread_abs"])
plt.title("ARS Daily BUY–SELL Spread")
plt.ylabel("Spread (ARS)")
plt.xlabel("Date")
plt.show()
```

---
## Example 2 - Multi-currency comparison
```python
from p2p_analytics import fiat_comparison

fx = fiat_comparison(["ARS", "BOB", "MXN"], root=PHASE1_ROOT)
print(fx.head())
```

---
## Example 3 - Exporting to Power BI
```python
from p2p_analytics import p2p_summary

summary = p2p_summary("ARS", root=PHASE1_ROOT)

summary.to_parquet("exports/summary_ARS.parquet", index=False)
summary.to_csv("exports/summary_ARS.csv", index=False)
```