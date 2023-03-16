# %%
import numpy as np

from copt import get_copt, _merge_resample, _merge_head


decimal_places = 1
np.set_printoptions(precision=decimal_places, suppress=True)

# %%
def test_merge_resample():
    # %%
    table_inp = np.array([
        [255, 0.8041],  # 1.0000
        [230, 0.0081],  # 0.1959
        [205, 0.0423],  # 0.1878
        [180, 0.0004],  # 0.1455
        [175, 0.0423],  # 0.1451
        [155, 0.0893],  # 0.1028
        [150, 0.0004],  # 0.0135
        [130, 0.0009],  # 0.0131
        [125, 0.0022],  # 0.0122
        [105, 0.0047],  # 0.0100
        [100, 0.0000],  # 0.0053
        [ 80, 0.0000],  # 0.0053
        [ 75, 0.0047],  # 0.0053
        [ 50, 0.0000],  # 0.0006
        [ 25, 0.0002],  # 0.0006
        [  0, 0.0004],  # 0.0004
    ])

    table_out = _merge_resample(table_inp, row_reduced_to=5)
    assert table_out[:,1].sum() == table_inp[:,1].sum()


# %%
def test_merge_head():
    # %%
    table_inp = np.array([
        [255, 0.8041],  # 1.0000
        [230, 0.0081],  # 0.1959
        [205, 0.0423],  # 0.1878
        [180, 0.0004],  # 0.1455
        [175, 0.0423],  # 0.1451
        [155, 0.0893],  # 0.1028
        [150, 0.0004],  # 0.0135
        [130, 0.0009],  # 0.0131
        [125, 0.0022],  # 0.0122
        [105, 0.0047],  # 0.0100
        [100, 0.0000],  # 0.0053
        [ 80, 0.0000],  # 0.0053
        [ 75, 0.0047],  # 0.0053
        [ 50, 0.0000],  # 0.0006
        [ 25, 0.0002],  # 0.0006
        [  0, 0.0004],  # 0.0004
    ])

    table_out = _merge_head(table_inp, max_cap=150)
    assert table_out[:,1].sum() == table_inp[:,1].sum()


# %%
def test_get_copt():
    # %%
    capacities = [100, 80, 25, 50]
    outage_rates = [0.10, 0.05, 0.01, 0.05]
    status = [1, 1, 1, 1]
    table = get_copt(capacities, outage_rates, status)
    print(table)

# %%
