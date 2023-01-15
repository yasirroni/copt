# Capacity Outage Probability Table (COPT) Maker

Fast Capacity Outage Probability Table (COPT) generator powered by `NumPy`.

## Notebooks

All notebooks are available in Colab.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yasirroni/copt).

## Feature

1. Calculate Loss of Load Probability (COPT).

    [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yasirroni/copt/blob/main/notebooks/app_copt.ipynb)

1. Calculate Expected Unserved Energy Cost (EUNC).

    [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yasirroni/copt/blob/main/notebooks/app_eunc.ipynb)

1. Calculate Capacity Credit (CC).

    [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yasirroni/copt/blob/main/notebooks/app_cc.ipynb)

## Program structure

Program structure:

```plaintext
Forced Outage Data
└── Individual Generator Capacity Outage Probability Table
    └── Combined Capacity Outage Probability Table
        ├── Loss of Load Probability
        │   └── Loss Of Load Expectation
        └────── Expected Energy Not Served
                ├── Expected Unserved Energy Cost
                └── Capacity Credit
```

## Contributing

1. We use [`nb-clean`](https://github.com/srstevenson/nb-clean) to clean notebook metadata. It should not be added as a filter since Colab metadata will be added later.

    ```shell
    pip install nb-clean
    nb-clean clean notebooks/app_cc.ipynb -m cellView -M
    nb-clean clean notebooks/app_copt.ipynb -m cellView -M
    nb-clean clean notebooks/app_eunc.ipynb -m cellView -M
    ```

    > **Warning**
    >
    > The `-M` arguments only available in [this PR](https://github.com/srstevenson/nb-clean/pull/169)

1. To better support Google Colab, add below cell metadata to hide the cell (only on the UI cell):

    ```shell
       "metadata": {
        "cellView": "form",
       },
    ```

1. Autofix using pre-commit (optional):

    To run on all files

    ```shell
    pre-commit run --all-files
    ```

    To run on `notebooks`:

    ```shell
    pre-commit run --files notebooks/app_cc.ipynb
    pre-commit run --files notebooks/app_copt.ipynb
    pre-commit run --files notebooks/app_eunc.ipynb
    ```

## TODOs

1. Download templates

1. Publish package
