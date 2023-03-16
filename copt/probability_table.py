# @title
import glob
import itertools
import numpy as np
import pandas as pd
from numba import jit

# @title
COPT_COLUMNS = ['Combined Capacity',
                'Individual Probability',
                'Cumulative Probability',
                ]

NUMPY_ZERO = np.float64(0)

IDX_CAP = 0
IDX_INP = 1
IDX_CMP = 2

# copt
# @jit(nopython=True)
def get_copt(
        capacities,
        outage_rates,
        status,
        row_threshold=100,
        min_cum_prob=0.0001,
        row_reduced_to=50,
        max_cap=100,
        merge_insignificant=False,
        merge_resample=False,
        merge_tail=False,
        merge_head=False,
        ):

    # filter only available generator
    # TODO: sort based on frequency of capacities, not capacities size
    generator_list = [[cap, 1 - out]
                      for cap, out, stat
                      in sorted(zip(capacities, outage_rates, status), reverse=True)
                      if stat]

    # make tables for each generator
    # TODO: Tables already support derating, input data should also support it
    # from excel
    tables = [np.array([generator, [0, 1 - generator[1]]])
              for generator in generator_list]

    table = tables[0].copy()  # copy to avoid modifying data
    for table_ in tables[1:]:
        # combine tables
        table = _combine_tables(table, table_)

        # combine duplicate
        table = np.array([[k, sum([x[1] for x in list(g)])]
                          for k, g in itertools.groupby(table, lambda x:x[0])])

        if np.any(table[:,IDX_INP] < 0):
            print('a')

        # TODO: support remove individual probability that is too small 

        # merge head
        if merge_head:
            if len(table) > row_threshold:
                table = _merge_head(table, max_cap)

        if merge_insignificant:
            if len(table) > row_threshold:
                table = _merge_insignificant(table, min_cum_prob)

        # merge resample
        if merge_resample:
            if len(table) > row_threshold:
                table = _merge_resample(table, row_reduced_to)

        # merge tail
        if merge_tail:
            if len(table) > row_threshold:
                table = _merge_tail(table, row_threshold)

    table = np.hstack((table,
                       # Cumulative Probability
                       np.atleast_2d(np.cumsum(table[::-1, IDX_INP])[::-1]).T,
                       # # Reversed Cumulative Probability
                       # np.atleast_2d(np.cumsum(table[:, IDX_INP])).T,
                       ))

    return table


@jit(nopython=True)
def _combine_tables(table, table_):
    # TODO:
    # Compare between:
    #   1. flatten + transpose
    #   2. np.array([table[:, 0]]).T
    table = np.hstack((
        (
            np.expand_dims(table[:, IDX_CAP], axis=1) + table_[:, IDX_CAP]
        ).reshape(-1, 1),  # sum capacity
        (
            np.expand_dims(table[:, IDX_INP], axis=1) * table_[:, IDX_INP]
        ).reshape(-1, 1),  # multiply probability
    ))

    # sort table
    table = table[(-table[:, IDX_CAP]).argsort(), :]
    return table


# @jit(nopython=True)
def _merge_head(table, max_cap):
    mask = table[:, IDX_CAP] < max_cap
    table = np.vstack((
        [table[0, IDX_CAP], table[~mask, IDX_INP].sum()],
        table[table[:, IDX_CAP] < max_cap]
    ))
    return table


# @jit(nopython=True)
def _merge_insignificant(table, min_cum_prob, round_strategy='updown'):
    # merge insignificant
    cum_prob = np.cumsum(table[::-1, IDX_INP])[::-1]
    mask_insignificant = cum_prob < min_cum_prob
    # mask_insignificant[-1] = False  # avoid divide by zeros due to CAP == 0
    if mask_insignificant.sum() > 1:
        # NOTE:
        # ROUNDUP: More accurate but reduce EENS
        # ROUNDDOWN: Not accurate and will amplify EENS
        # ROUNDUPDOWN: Not accurate, increase EENS, but better than ROUNDDOWN
        
        if round_strategy == 'updown':
            # round up down approach
            removed_cap = table[mask_insignificant, IDX_CAP]
            removed_inp = table[mask_insignificant, IDX_INP]

            weight_to_top = (removed_cap
                            / table[~mask_insignificant, IDX_CAP][-1])
            zero_inp = (
                table[-1, IDX_INP]  # zero_inp
                + np.sum(removed_inp * (1 - weight_to_top))
            )
            table = table[~mask_insignificant, :]  # cut
            table[-1, IDX_INP] = (
                table[-1, IDX_INP]  # top_inp
                + np.sum(removed_inp * weight_to_top)
            )
            table = np.vstack((
                table,
                np.array([[NUMPY_ZERO, zero_inp]])
            ))
        
        elif round_strategy == 'up':
            # round up approach
            table = table[~mask_insignificant, :]  # cut
            table[-1, IDX_INP] = 1 - table[:-1, IDX_INP].sum()  # replace

        elif round_strategy == 'down':
            # round down approach
            table = np.vstack((
                table[~mask_insignificant, :],  # cut
                np.array([[NUMPY_ZERO, table[mask_insignificant, 1].sum()]])
            ))

    return table


# @jit(nopython=True)
def _merge_resample(table, row_reduced_to):
    group_size = (len(table) - 2) // row_reduced_to  # -2 for head and tail
    reduced_row = (group_size * row_reduced_to) + 1

    head = np.atleast_2d(table[:-reduced_row, :])
    tail = np.atleast_2d(table[-1, :])

    # using resampled tail strategy, except zeros
    removed_cap = table[-reduced_row:-1, IDX_CAP].reshape(row_reduced_to, -1)
    removed_inp = table[-reduced_row:-1, IDX_INP].reshape(row_reduced_to, -1)
    
    # NOTE:
    #   arr[start:stop:step]

    resampled_cap = np.atleast_2d(
        np.concatenate((removed_cap[:, 0], tail[:, IDX_CAP]))
    ).T


    distance_top = ((resampled_cap[:-1] - removed_cap)
                    / -np.diff(resampled_cap, axis=0))

    distance_bot = 1 - distance_top

    resampled_inp = np.zeros(len(removed_cap) + 1)
    resampled_inp[:-1] = np.sum(removed_inp * distance_bot, axis=1)  # top, distance_bot
    resampled_inp[1:] = resampled_inp[1:] + np.sum(removed_inp * distance_top, axis=1)  # bot, distance_top
    resampled_inp[-1] = resampled_inp[-1] + tail[-1, IDX_INP]  # add tail inp
    resampled_inp = np.atleast_2d(resampled_inp).T  # transpose

    resampled_tab = np.hstack((resampled_cap, resampled_inp))
    table = np.vstack((head, resampled_tab))
    return table



def _merge_tail(table, row_threshold):
    removed_cap = table[row_threshold:-1, IDX_CAP]
    removed_inp = table[row_threshold:-1, IDX_INP]

    weight_to_top = (removed_cap
                     / table[row_threshold - 1, IDX_CAP])
    zero_inp = (
        table[-1, IDX_INP]  # zero_inp
        + np.sum(removed_inp * (1 - weight_to_top))
    )

    table = table[:row_threshold]  # cut

    table[-1, IDX_INP] = (
        table[-1, IDX_INP]  # top_inp
        + np.sum(removed_inp * weight_to_top)
    )

    table = np.vstack((
        table,
        np.array([[NUMPY_ZERO, zero_inp]])
    ))

    return table

# # lolp
# @jit(nopython=True)  # disabled for now because it cause crash in big array
def get_lolp(capacity, cumulative_probability, demand):
    """
    format:
        capacity (descend)
        cumulative_probability(descend)
    """
    # NOTE: Lowest COPT table < lowest demand cause error
    try:
        idx = np.where(capacity < demand)[0][0]
    except Exception:  # IndexError
        idx = -1
    return cumulative_probability[idx]


# # eens
# @jit(nopython=True)  # disabled for now because it cause crash in big array
def get_eens(capacity, individual_probability, demand):
    """
    format:
        capacity
        individual_probability
    """
    return sum(individual_probability
               * (capacity < demand)
               * (demand - capacity))


# @jit(nopython=True)  # disabled for now because it cause crash in big array
def find_delta_load_eens(lb, ub, table, net_loads, eens, tol=0.0001):
    # lb_0 = 0
    # ub_0 = max(sun)
    # delta_load_0 = max(sun) / 2
    eens_delta_load = np.inf
    while abs(eens_delta_load - eens) > tol:
        delta_load = (lb + ub) * 0.5
        eens_delta_load = sum([get_eens(table[:, IDX_CAP], table[:, IDX_INP], net_load)
                               for net_load in net_loads + delta_load])
        if eens_delta_load > eens:
            ub = delta_load
        else:
            lb = delta_load
    return delta_load, eens_delta_load

# @jit(nopython=True)  # disabled for now because it cause crash in big array
def find_delta_load_lole(lb, ub, table, net_loads, lole, tol=0.0001):
    # lb_0 = 0
    # ub_0 = max(sun)
    # delta_load_0 = max(sun) / 2
    lole_delta_load = np.inf
    while abs(lole_delta_load - lole) > tol and abs(ub - lb) > tol:
        delta_load = (lb + ub) * 0.5
        lole_delta_load = sum([get_lolp(table[:, IDX_CAP], table[:, IDX_CMP], net_load)
                               for net_load in net_loads + delta_load])
        if lole_delta_load > lole:
            ub = delta_load
        else:
            lb = delta_load
    return delta_load, lole_delta_load
