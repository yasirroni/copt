# Capacity Outage Probability Table (COPT) Maker

Fast Capacity Outage Probability Table (COPT) generator powered by `NumPy`.

## App in Binder

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/yasirroni/copt/HEAD?urlpath=voila%2Frender%2Fnotebooks%2Fapp.ipynb)

## Notebook in Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yasirroni/copt/blob/main/notebooks/app.ipynb)

## Feature

1. Calculate Loss of Load Probability (COPT).

1. Calculate Expected Energy Not Served (EENS).

1. Calculate Load Shedding Cost.

## Psuedocode

Program structure:

```plaintext
Forced Outage Data
└── Individual Generator Capacity Outage Probability Table
    └── Combined Capacity Outage Probability Table
        ├── Loss of Load Probability
        │   └── Loss Of Load Expectation
        └────── Expected Energy Not Served
                └── Expected Unserved Energy Cost
```

Step by step pseudocode

```python
# Individual Generator Capacity Outage Probability Table
i = 1
for i in generatorNumbers:
    tables[i] = [capacity[i], [0, 1 - outage_rate[i]]]
    i = i + 1

# Combined Capacity Outage Probability Table
for table in tables:
    COPT = [
        (COPT_capacities + table_capacity)
        (COPT_probabilities * table_probability)
    ]
COPT_cumulativeProbabilities = sum(COPT_probabilities)

# Loss of Load Probability
LOLP = COPT_cumulativeProbabilities(
    min(
        where(
            capacity < demand
            )
        )
)

# Loss Of Load Expectation
LOLE = LOLP * 365

# Expected Energy Not Served
for demand in demands:
EENS = sum(
    COPT_probabilities * (COPT_capacities < demand) * (demand - COPT_capacities)
)

# Expected Unserved Energy Cost
cost = EENS * VOLL
```

## Contributing

1. We use [`nb-clean`](https://github.com/srstevenson/nb-clean) to clean notebooks metadata. It should not be added as filter since Colab metadata will be added later.

    ```shell
    pip install nb-clean
    nb-clean clean notebooks/app.ipynb --preserve-cell-outputs --preserve-cell-metadata
    ```

1. To better support colab, add below metadata (after clean) to hide cell in colab (only on the UI cell):

    ```shell
       "metadata": {
        "cellView": "form",
        "colab": {}
       },
    ```
