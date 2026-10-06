import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")

with app.setup(hide_code=True):
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import altair

    from typing import NamedTuple
    import argparse
    from pathlib import Path


    import kagglehub
    from kagglehub import KaggleDatasetAdapter

    import lib.viz as viz


@app.cell
def _():
    # Parse command line arguments
    _parser = argparse.ArgumentParser(description='Presidential Election Scenarios Analysis')
    _parser.add_argument(
        '-o', '--output',
        default="./.data/presidential_values/",
        type=str,
        help='Output directory for results')
    _args = _parser.parse_args()
    output_dir = Path(_args.output)
    return (output_dir,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Presidential Election Scenarios
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Our goal is calculate the three "values of a vote":

    **V1**. Apportionment Value

    $$
    \text{AV}(x) = \frac{e_{s(x)} / E}{n_{s(x)} / N}
    $$

    As a characterization of apportionment itself, $n_s$ should be the apportionment population (AP).

    As a characterization of the value of a vote it could use voting-eligible population (VEP) (which would make it a "potential" value of a vote, ex ante) or voting population (VP) (which would make it an ex post "actual" value of a vote). In these cases the meaning is a bit different, but we won't think about that for now.

    We'll calculate all four as columns `av_ap`, `av_vap`, `av_vep`, and `av_vp`.

    **V2**. Pivotality Value

    $$
    \text{PV}(x) = \frac{ e_{s(x)} \sqrt{n_{s(x)}} / \sum_s e_s \sqrt{n_s}}{n_s / N}
    $$

    In this measure $n_s$ and $N$ should probably be VEP, as only potential voters have a chance of being "pivotal" at all. VAP is quite similar and more available, so we'll also use this.

    VP might be fine too, but has the usual downside of being causally downstream of the voting system itself; the (already suspect) hypothesis of a "uniform distribution" over outcomes is even less plausible as a distribution over the results of the votes actually cast.

    **V3**. Wasted Vote Value

    $$
    \begin{align}
    \text{WVV}(x) = \frac{e_{s(x)} / E}{R_{v(x)}(s(x)) / N} && && \text{(winners only)}
    \end{align}
    $$

    Here $N$ should be the total votes cast. We could extend this to the rest of VEP by valuing votes which weren't cast at all at zero.


    TODO: probably don't ship WVV in this form; the losers getting 0 value feels bad. It works for electoral college but not nationally.

    ----


    ...as well as their corresponding measures (MAD, Var, H)...


    ... for each of 5 presidential election scenarios:


    **P1**. A national general election.


    **P2**. Simplified present day (winner-take-all in all states)

    **P3**. The present day: winner-takes-all electors in all states but Maine and Nebraska.

    **P4**. Assigning electors by districts, and the two senate electors to the winners of the states as whole. (I.e. what Maine/Nebraska do but nationwide)

    **P5**. Assigning state electors, including senate electors, to candidates in proportion to vote share in each state.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Each scenario outputs its value along a dimension which is a product of:
    - a spatial granularity: nationally, by state, or by district
      - TODO: we ought to do this with and without U.S. territories.
    - a party line: either uniform, or split D/R
      - TODO: support abstentions
      - TODO: support third parties and "other"

    There are some limitations to the data set.
    - VAP/VEP are not currently supported pre-1980
      - TODO: we can probably get census data for VAP for all years. Not sure it would be consistent with UF though.
    - VEP is not supported at the district level at all.
    - district granularity is only supported after 2012
      - TODO: we can probably support populations going back much further, but electoral results are harder.
    """)
    return


@app.cell(hide_code=True)
def _():
    data_national = kagglehub.dataset_load(
      KaggleDatasetAdapter.PANDAS,
      "samkritch/u-s-presidential-elections-by-state-1976-2024",
      'pres_1976_2024.csv',
    )

    _data_2028 = data_national[data_national['year'] == 2024].copy()
    _data_2028['year'] = 2028

    # for forward-compat maybe should keep-by-name rather than remove-by-name

    # Set vote-related and VAP/VEP columns to NaN
    _vote_columns = [
        'vap_estimate', 'vep_estimate',
        'votes_total', 'votes_democrat', 'votes_other', 'votes_republican',
        'electors_democrat', 'electors_republican', 'electors_other'
    ]
    for _col in _vote_columns:
        _data_2028[_col] = np.nan

    _election_columns = ['winning_party', 'winning_party_popular', 'candidate_democrat', 'candidate_republican']

    for _col in _election_columns:
        _data_2028[_col] = None

    data_national = pd.concat([data_national, _data_2028], ignore_index=True)

    mo.output.append(mo.md("## National Dataset"))
    mo.output.append(data_national )
    return (data_national,)


@app.cell(hide_code=True)
def _():
    data_state = kagglehub.dataset_load(
      KaggleDatasetAdapter.PANDAS,
      "samkritch/u-s-presidential-elections-by-state-1976-2024",
      'pres_by_state_1976_2024.csv',
    )

    _nansum = lambda x: x.sum(min_count=1)
    national_totals = data_state.groupby('year').agg({
        'electors': _nansum,
        'apportionment_population': _nansum,
        'vap_estimate': _nansum,
        'vep_estimate': _nansum,
        'votes_total': _nansum,
    }).rename(columns={
        'electors': 'national_electors',
        'apportionment_population': 'national_apportionment_population',
        'vap_estimate': 'national_vap_estimate',
        'vep_estimate': 'national_vep_estimate',
        'votes_total': 'national_votes_total'
    })


    # Merge national totals back to dataframe
    data_state = data_state.merge(national_totals, left_on='year', right_index=True)
    data_state = data_state.rename(columns={
        'electors': 'state_electors',
        'apportionment_population': 'state_apportionment_population',
        'vap_estimate': 'state_vap_estimate',
        'vep_estimate': 'state_vep_estimate',
        'votes_total': 'state_votes_total'
    })



    _data_2028 = data_state[data_state['year'] == 2024].copy()
    _data_2028['year'] = 2028

    # for forward-compat maybe should keep-by-name rather than remove-by-name

    # Set vote-related and VAP/VEP columns to NaN
    _vote_columns = [
        'state_vap_estimate', 'state_vep_estimate', 'national_vap_estimate', 'national_vep_estimate',
        'state_votes_total', 'votes_democrat', 'votes_other', 'votes_republican', 'national_votes_total',
        'electors_democrat', 'electors_republican', 'electors_other'
    ]
    for _col in _vote_columns:
        _data_2028[_col] = np.nan

    _election_columns = ['winning_party']

    for _col in _election_columns:
        _data_2028[_col] = None

    data_state = pd.concat([data_state, _data_2028], ignore_index=True)

    mo.output.append(mo.md("## State Dataset"))
    mo.output.append(data_state )
    return data_state, national_totals


@app.cell(hide_code=True)
def _(data_state, national_totals):
    data_district: pd.DataFrame = kagglehub.dataset_load(
      KaggleDatasetAdapter.PANDAS,
      "samkritch/u-s-presidential-elections-by-state-1976-2024",
      'pres_by_district_2012_2024.csv',
    )

    # todo: support third parties
    data_district['winning_party'] = data_district.apply(lambda row: "democrat" if row["votes_democrat"] > row["votes_republican"] else "republican", axis=1)

    data_district = data_district.merge(national_totals, left_on='year', right_index=True)
    state_totals: pd.DataFrame = data_state[['year', 'state', 'state_electors', 'state_apportionment_population', 
                                             'state_vep_estimate', 'state_vap_estimate', 'votes_democrat', 
                                             'votes_republican', 'winning_party', 'state_votes_total']].copy()

    state_totals = state_totals.rename(columns={
        'votes_total': 'state_votes_total',
        'votes_democrat': 'state_votes_democrat',
        'votes_republican': 'state_votes_republican',
        'winning_party': 'state_winning_party'
    })

    data_district = data_district.merge(state_totals, on=['year', 'state'])
    # Until upstream is fixed
    data_district = data_district.rename(columns={'apportionment_voting_age_population': 'apportionment_vap'})





    _data_2028 = data_district[data_district['year'] == 2024].copy()
    _data_2028['year'] = 2028

    # for forward-compat maybe should keep-by-name rather than remove-by-name

    # Set vote-related and VAP/VEP columns to NaN
    _vote_columns = [
        'state_vap_estimate', 'state_vep_estimate', 'national_vap_estimate', 'national_vep_estimate',
        'votes_total', 'votes_democrat', 'votes_other', 'votes_republican', 'state_votes_total', 'national_votes_total',
        'state_votes_democrat', 'state_votes_republican', # 'state_votes_other'? 
        'electors_democrat', 'electors_republican', 'electors_other'
    ]
    for _col in _vote_columns:
        _data_2028[_col] = np.nan

    _election_columns = ['winning_party', 'state_winning_party']

    for _col in _election_columns:
        _data_2028[_col] = None

    data_district = pd.concat([data_district, _data_2028], ignore_index=True)


    mo.output.append(mo.md("## District Dataset"))
    mo.output.append(data_district)
    return (data_district,)


@app.cell(hide_code=True)
def _():
    class PopCols(NamedTuple):
        n: str | None
        s: str | None
        d: str | None


    population_cols = {
        'ap': PopCols("national_apportionment_population", "state_apportionment_population", "apportionment_population"),
        'vap': PopCols("national_vap_estimate", "state_vap_estimate", "apportionment_vap"),
        'vep': PopCols("national_vep_estimate", "state_vep_estimate", None),
        'vp': PopCols("national_votes_total", "state_votes_total", "votes_total"),
    }
    return PopCols, population_cols


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## P1: General Election

    For this we can use the national dataset only.

    The only question is whether we consider national election votes to be "wasted" in the same way state votes are. For most purposes I would say they are *not*, but I'll calculate the appropriate WVVs as if they were.
    """)
    return


@app.cell(hide_code=True)
def _(data_national):
    data_p1 = data_national.copy()

    for _p in ['ap', 'vap', 'vep', 'vp']:
        data_p1[f'av_{_p}'] = 1

    for _p in ['vap', 'vep', 'vp']:
        data_p1[f'pv_{_p}'] = 1

    # Do we treat this as "1" because there's no states to "waste" votes?
    # data_p1['wvv'] = 1

    data_p1['wvv_vp'] = data_p1.apply(
        lambda row: np.nan if pd.isna(row['winning_party'])
        else row['votes_total'] / row[f"votes_{row['winning_party']}"],
        axis=1
    )



    data_p1.head(3)
    return (data_p1,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## P2: Simplified Electoral College

    P2 is fairly simple and can be computed directly from state-level data.
    """)
    return


@app.cell(hide_code=True)
def _(PopCols, data_state, population_cols):
    data_p2 = data_state.copy()

    # Undo the real assignment of ME/NE electors
    data_p2['electors_democrat'] = data_p2['state_electors'].where(data_p2['votes_democrat'] >= data_p2['votes_republican'], 0)
    data_p2['electors_republican'] = data_p2['state_electors'].where(data_p2['votes_democrat'] < data_p2['votes_republican'], 0)

    # Calcualtes PV(x) = (N * e_s / sqrt(n_s)) / (sum of e_s * sqrt(n_s) for all s)
    def calculate_pv(group, pcols: PopCols):
        # Calculate the denominator: sum of e_s * sqrt(n_s) for all states
        denominator = (
            group["state_electors"] * np.sqrt(group[pcols.s])
        ).sum()

        # Calculate PV for each state
        pv_values = (
            group[pcols.n]
            * group["state_electors"]
            / np.sqrt(group[pcols.s])
        ) / denominator
        return pv_values

    for _p in ['ap', 'vap', 'vep', 'vp']:
        _pcols = population_cols[_p]
        # Assign AV
        data_p2[f"av_{_p}"] = (data_p2['state_electors'] / data_p2['national_electors']) / (data_p2[_pcols.s] / data_p2[_pcols.n])

    # AP doesn't make sense for PV
    for _p in ['vap', 'vep', 'vp']:
        _pcols = population_cols[_p]
        # Assign PV
        data_p2[f"pv_{_p}"] = data_p2.groupby("year").apply(calculate_pv, pcols=_pcols).reset_index(drop=True)


    data_p2["wvv_vp"] = data_p2.apply(
        lambda row: np.nan if pd.isna(row["winning_party"])
        else (row["state_electors"] * row["national_votes_total"])
        / (row["national_electors"] * row[f"votes_{row['winning_party']}"]),
        axis=1,
    )
    data_p2
    return (data_p2,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## P3: Actual Electoral College

    Today, both Maine and Nebraska assign their 2 "Senate" electors to the winner of the state election, but assign their "House" electors to the popular-vote winner in each congressional district.

    Maine has assigned its district electors by district for all the years in our data, while Nebraska adopted the system in 1992. Maine split its electors in 2016 and 2020. Nebraska in 2008 and 2020.

    How then should we handle our value functions?
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    First, we need a new schema for our table, which will also be applicable to P4. We will have one row per congressional district rather than per state. At the P3 level, the P2 measures can be copied to every district for all states but ME and NE.

    For AV: each district receives its share of the Senate electors, plus its house elector. Here $e_s$ represents only the 2 Senate electors for states which split:

    $$
    \text{AV}(x) = \frac{e_{s(x)}/E}{n_{s(x)} / N} + \frac{e_{d(x)}/E}{n_{d(x)} / N}
    $$

    For PV: recall that the original PV formula could be written as:

    $$
    \begin{align}
    \text{PV}(x) &= \frac{1}{\sqrt{n_{s(x)}}}\frac{ e_{s(x)}}{\sum_s e_s \sqrt{n_s}} N
    \end{align}
    $$

    For ME and NE, we should separately treat the pivotality of the state, associated with the two state electors, from that of the districts. For these districts:

    $$
    \begin{align}
    \text{PV}(x) &= \frac{1}{\sqrt{n_{s(x)}}}\frac{ e_{s(x)} }{Z} N + \frac{1}{\sqrt{n_{d(x)}}}\frac{ e_{d(x)} }{Z} N
    \end{align}
    $$

    where $Z$ is the normalization constant:

    $$
    Z = \sum_s e_s \sqrt{n_s} + \sum_d e_d \sqrt{n_d}
    $$

    For WVV, we again separate the Senate and House electors into separate terms, for the winners only:

    $$
    \text{WVV}(x) = \frac{e_{s(x)} / E}{r_{v(x)}(s(x)) / N} + \frac{e_{d(x)} / E}{r_{v(x)}(d(x)) / N}
    $$

    and use VP.
    """)
    return


@app.cell(hide_code=True)
def _(PopCols):
    # Functions for P3/P4

    def av_for_district(row, p: PopCols):
        state_part = (
            ((row['state_electors'] if not row['_is_split'] else 2) * row[p.n])
             / (row[p.s] * row['national_electors'])
        )
        if not row['_is_split']:
            return state_part
        district_part = (
            (row[p.n]) / (row[p.d] * row['national_electors'])
        )
        return state_part + district_part


    def pv_for_district(row, p: PopCols):
        state_part = (
            ((row['state_electors'] if not row['_is_split'] else 2) * row[p.n])
             / (np.sqrt(row[p.s]) * row['pv_denominator'])
        )
        if not row['_is_split']:
            return state_part
        district_part = (
            (row[p.n]) / (np.sqrt(row[p.s]) * row['pv_denominator'])
        )
        return state_part + district_part

    def wvv_for_district(row, p: PopCols):
        sd, sr, sw = row['state_votes_democrat'], row['state_votes_republican'], row['state_winning_party']
        if pd.isna(sw):
            return np.nan
        state_const = (
            ((row['state_electors'] if not row['_is_split'] else 2) * row[p.n])
             / (row['national_electors'])
        )
        state_val = state_const / sd if sw == 'democrat' else state_const / sr
        if not row['_is_split']:
            return state_val
        dw = row['winning_party']
        district_const = row[p.n] / row['national_electors']
        dv = row['votes_democrat'] if dw == 'democrat' else row['votes_republican']
        # state senate electors go to sw; district elector goes to dw
        return (state_val if dw == sw else 0) + district_const / dv

    return av_for_district, pv_for_district, wvv_for_district


@app.cell(hide_code=True)
def _(
    av_for_district,
    data_district: pd.DataFrame,
    population_cols,
    pv_for_district,
    wvv_for_district,
):
    data_p3 = data_district.copy()

    _is_split_state_district = (data_p3['state'] == 'MAINE') | ((data_p3['state'] == 'NEBRASKA') & (data_p3['year'] >= 1992))
    data_p3['_is_split'] = _is_split_state_district

    # No VEP at district level.
    for _p in ['ap', 'vap', 'vp']:
        _pcols = population_cols[_p]

        # AV
        _av_col = f'av_{_p}'
        data_p3[_av_col] = 0.0
        data_p3[_av_col] = data_p3.apply(av_for_district, p=_pcols, axis=1, )

    # No AP, doesn't make sense for p.
    for _p in ['vap', 'vp']:
        _pcols = population_cols[_p]
        # PV
        _pv_col = f'pv_{_p}'

        # Build the denominator of PV
        _state_electors = pd.concat([
            (data_district[~_is_split_state_district]
                .groupby(["state", "year"])
                .size() + 2
            )
            , (data_district[_is_split_state_district]
                .groupby(["state", "year"])
                .size().map(lambda _: 2)
            )
        ])
        _sqrt_state_pops = np.sqrt(data_district.groupby(["state", "year"])[_pcols.d].sum())
        _z_state = ((_state_electors * _sqrt_state_pops)
            .reset_index(level=0, drop=True) # Drop state
            .groupby("year")
            .sum()
       )
        _z_district = (np.sqrt(data_p3.loc[_is_split_state_district, _pcols.d])
            .groupby(data_p3.loc[_is_split_state_district, "year"])
            .sum()
        )
        _z = _z_state + _z_district

        data_p3['pv_denominator'] = data_p3['year'].map(_z)
        data_p3[_pv_col] = 0.0
        data_p3[_pv_col] = data_p3.apply(pv_for_district, p=_pcols, axis=1)


    # WVV
    data_p3['wvv_vp'] = data_p3.apply(wvv_for_district, p=population_cols['vp'], axis=1)


    data_p3
    return (data_p3,)


@app.cell
def _(data_p2, data_p3, data_state):
    # Build state-level data for p3
    # For split states values we need to use p3 aggs
    # For electors we need to use data_state directly, since p2 undoes ME/NE
    # For everything else we can use p2

    _dim_cols = ['year', 'state_po']
    _elector_cols = ['electors_democrat', 'electors_republican', 'electors_other']
    _val_cols = [
        'av_ap', 'av_vap', 'av_vp', 'pv_vap', 'pv_vp', 
        # 'wvv_vp' # disabling this at state level, not sure how it should be defined.
    ]

    _not_split_p2 = ~((data_p2['state'] == 'MAINE') | ((data_p2['state'] == 'NEBRASKA') & (data_p2['year'] >= 1992)))
    _not_in_district_data = data_p2['year'] < 2012
    _non_split_state_values = data_p2[_not_split_p2 | _not_in_district_data][_dim_cols + _val_cols]
    _split_state_values = data_p3[data_p3['_is_split']].groupby(_dim_cols)[_val_cols].mean().reset_index()
    _state_values = pd.concat([_non_split_state_values, _split_state_values], ignore_index=True).set_index(_dim_cols, drop=True)
    _state_electors  = data_state[_dim_cols +_elector_cols].set_index(_dim_cols, drop=True)
    data_p3_state = pd.concat([_state_values, _state_electors], axis=1).reset_index()
    data_p3_state
    return (data_p3_state,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## P4: Electors by Districts

    Like P3, but we apply the same logic to every state, so it's simpler.
    """)
    return


@app.cell(hide_code=True)
def _(
    av_for_district,
    data_district: pd.DataFrame,
    population_cols,
    pv_for_district,
    wvv_for_district,
):
    data_p4 = data_district.copy()
    data_p4['_is_split'] = True

    # Set P4 elector values
    # These are only the house electors; we'll add senate electors to our state aggs.
    # For D.C., we consider one of its 3 electors to be a "House" elector.
    data_p4['electors'] = 1  
    data_p4['electors_democrat'] = (data_p4['votes_democrat'] > data_p4['votes_republican']).astype(int)
    data_p4['electors_republican'] = (data_p4['votes_democrat'] < data_p4['votes_republican']).astype(int)


    for _p in ['ap', 'vap', 'vp']:
        _pcols = population_cols[_p]

        # AV
        _av_col = f'av_{_p}'
        data_p4[_av_col] = data_p4.apply(av_for_district, axis=1, p=_pcols)

        # PV
        _pv_col = f'pv_{_p}'
        # Denominator for PV calculations
        _state_electors = (data_district
            .groupby(["state", "year"])
            .size().map(lambda _: 2)
        )
        _sqrt_state_pops = np.sqrt(data_district.groupby(["state", "year"])[_pcols.d].sum())
        _z_state = ((_state_electors * _sqrt_state_pops)
            .reset_index(level=0, drop=True) # Drop state
            .groupby("year")
            .sum()
        )
        _z_district = (np.sqrt(data_district[_pcols.d])
            .groupby(data_district["year"])
            .sum()
        )
        _z = _z_state + _z_district

        data_p4['pv_denominator'] = data_p4['year'].map(_z)
        data_p4[_pv_col] = data_p4.apply(pv_for_district, p=_pcols, axis=1)


    # WVV
    data_p4['wvv_vp'] = data_p4.apply(wvv_for_district, p=population_cols['vep'], axis=1)
    data_p4
    return (data_p4,)


@app.cell
def _(data_p4):
    # build state-level data for p4

    _dim_cols = ['year', 'state_po']
    _elector_cols = ['electors_democrat', 'electors_republican', 'electors_other']
    _val_cols = [
        'av_ap', 'av_vap', 'av_vp', 'pv_vap', 'pv_vp', 
        # 'wvv_vp'  # disabling this at state level, not sure how it should be defined.
    ]

    # Easiest 
    _value_means = data_p4.groupby(_dim_cols)[_val_cols].mean()
    _elector_sums = data_p4.groupby(_dim_cols)[_elector_cols].sum(min_count=1)

    # Add senate electors. Easiest to compute these from the same dataset.
    _state_votes = data_p4.groupby(_dim_cols)[['state_votes_democrat', 'state_votes_republican']].max()
    _state_d = (_state_votes['state_votes_democrat'] >= _state_votes['state_votes_republican']).apply(lambda b: 2 if b else 0)
    _state_r = (_state_votes['state_votes_democrat'] < _state_votes['state_votes_republican']).apply(lambda b: 2 if b else 0)
    _elector_sums['electors_democrat'] = _elector_sums['electors_democrat'] + _state_d
    _elector_sums['electors_republican'] = _elector_sums['electors_republican'] + _state_r

    data_p4_state = pd.concat([_value_means, _elector_sums], axis=1).reset_index()


    data_p4_state

    return (data_p4_state,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    AV and PV should not vary within a state for AP, because the districts are mostly equally sized. VAP, VEP should vary a bit more, with VP the most, but VP is the least reliable.

    The main reason for these is to compare to P2/P3, and for WVV-type measures which do depend on the particular district.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## P5: Party-Proportional Electors

    Here we assign the current number of electors, at the state level, in proportion to the popular vote. We'll include third parties, why not, but will pretend all "other" votes comprise a single party for now.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Suppose the vote percent of a party is $p_s$. We assign $\lfloor p_s e_s \rfloor$ electors to each party. Assuming no abstentions, the remaining electors are at most one less than the number of parties. Assign them to the largest remainders in descending order.

    E.g. 7 electors, 60% vote Democrat. Then $\frac{0.6}{1/7} = 4.2$ means 4 go to D, and $\frac{0.4}{1/7} = 2.8$ means 2 goes to R. The last elector goes to D.

    Now, how do we calculate values?

    **AV**

    This should be unchanged.

    (Could we compute another version of this with the exact elector count $\frac{e_p(s) / E}{R_p(s) / N_{VP}}$? This would basically be WVV... feels a little odd.)

    **PV**

    TODO: this feels confused. Surely we need to choose a normal centered on something other than 50% of the votes.

    My immediate thought is to assign one elector to each $\frac{n_s}{e_s}$ of population, but these are not WTA, they "fill up all the way" before spilling over to the next elector.

    Instead, in keeping with the original formulation, we need to consider the full $2^{n_s}$ space of state outcomes, then count the number in which voter $x \in s$ is pivotal. Well, the popular outcome is going to be the same $\approx \sqrt{n_s}$-wide normal-ish distribution as before, which is extremely peaked compared to the spacing of the elector seats $\frac{n_s}{e_s} \approx 800\text{k}$. Only the final elector (with odd $e_s$) or the final two electors (with even $e_s$) flip at all—and these flip with the same $\frac{1}{\sqrt{n_s}}$ scaling as before.

    The difference is that both parties automatically split up the remaining electors with near-certainty. Only one/two electors per state has any chance to change hands—in fact, if the elector counts are even, they will effectively always split, where when they're odd there's a pivotality chance for the single contested seat.

    By a strict pivotality calculation where therefore have (for odd $e_s$):

    $$
    \begin{align}
    P[x \text{ is pivotal}] &= (P[x \text{ flips elector 1}] + P[x \text{ flips elector 2}] + \ldots + P[x \text{ flips elector } e_s]) \cdot \frac{1}{\Vert \mathbf{e} \Vert} \\
      &\approx (0 + \ldots + P[x \text{ flips elector } \frac{e_s}{2}] + \ldots + 0) \cdot \frac{1}{\Vert \mathbf{e} \Vert} \\
      &\propto \frac{1_{e_{s(x)} \text{ odd}}}{\sqrt{n_s}}\\
    \text{PV}(x) &= \frac{1_{e_{s(x)} \text{ odd}}}{\sqrt{n_s}} \cdot \frac{N}{\sum_{s \mid  e_{s} \text{ odd}} \sqrt{n_s}}
    \end{align}
    $$

    N here could be VEP, VAP, or VP.

    At least in this simplified view, we get a PV which does not depend on state elector counts at all.

    But should there be some contribution from all the other electors that each population member grants "for free"? Should these be included in the denominator $\Vert \mathbf{e} \Vert$? Well, it divides out anyway.

    Apparently the "uniform distribution" of PV is not very sensible for this scenario. (It also precludes third parties.)

    **WVV**

    We just do $\frac{e_p(s) / E}{R_p(s) / N}$ for each party. Easy.

    Note that, for a given party, this will drop as votes increase, and then spike each time a new elector is acquired. Somewhat pathological (but not really moreso than WVV ever is, I suppose.)
    """)
    return


@app.function(hide_code=True)
def calc_electors_party_proportional(row):
    """
    Calculates the electors assigned to each party.

    Last 1/2 electors are assigned to the largest remainder.

    Currently treats all third parties as a single one, which is obviously wrong.
    """
    if pd.isna(row['state_votes_total']):
        return (np.nan, np.nan, np.nan)
    quota = row['state_votes_total'] / row['state_electors']
    d = np.floor(row['votes_democrat'] / quota)
    r = np.floor(row['votes_republican'] / quota)
    # Assume a single 3p
    o = np.floor(row['votes_other'] / quota)

    # remaining electors to allocate (should be 1 if e_s odd, 2 if e_s even, but third party might complicate that)
    e_rem = row['state_electors'] - (d + r + o)

    # party remainders
    d_rem = row['votes_democrat'] - d * quota
    r_rem = row['votes_republican'] - r * quota
    o_rem = row['votes_other'] - o * quota

    if e_rem == 0:
        return (d, r, o)
    if e_rem == 1:
        if d_rem == max(d_rem, r_rem, o_rem): return (d + 1, r, o)
        if r_rem == max(d_rem, r_rem, o_rem): return (d, r + 1, o)
        if o_rem == max(d_rem, r_rem, o_rem): return (d, r, o + 1)
    if e_rem == 2:
        if o_rem == min(d_rem, r_rem, o_rem): return (d + 1, r + 1, o)
        if d_rem == min(d_rem, r_rem, o_rem): return (d, r + 1, o + 1)
        if r_rem == min(d_rem, r_rem, o_rem): return (d + 1, r, o + 1)
    raise Exception(f"Unexpected: {row['state']} | {row['year']} | {(d, r, o)} + remainder {e_rem}?")


@app.cell(hide_code=True)
def _(data_state, population_cols):
    data_p5 = data_state.copy()

    data_p5[['electors_democrat', 'electors_republican', 'electors_other']] = (
        data_p5.apply(calc_electors_party_proportional, axis=1, result_type='expand')
    )

    for _p, _pcols in population_cols.items():
        # Assign AV
        data_p5[f"av_{_p}"] = (data_p5['state_electors'] / data_p5['national_electors']) / (data_p5[_pcols.s] / data_p5[_pcols.n])

        # Assign PV
        # data_p5[f"pv_{_p}"] = data_p2.groupby("year").apply(calculate_pv, pcols=_pcols).reset_index(drop=True)


    # WVV: value for the state's popular vote winner.
    data_p5['wvv_vp'] = data_p5.apply(
        lambda row: np.nan if pd.isna(row['winning_party'])
        else (row[f"electors_{row['winning_party']}"] * row['national_votes_total'])
            / (row['national_electors'] * row[f"votes_{row['winning_party']}"]),
        axis=1,
    )

    data_p5
    return (data_p5,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Output
    """)
    return


@app.cell
def _(
    data_p1,
    data_p2,
    data_p3,
    data_p3_state,
    data_p4,
    data_p4_state,
    data_p5,
    output_dir,
):
    import json, math

    def _clean(v):
        if isinstance(v, np.integer): return int(v)
        if isinstance(v, (np.floating, float)):
            if isinstance(v, np.floating) and np.isnan(v): return None
            if isinstance(v, float) and math.isnan(v): return None
            rounded = round(float(v), 3)
            return int(rounded) if rounded == int(rounded) else rounded
        return v

    def _key(v):
        try:
            f = float(v)
            return str(int(f)) if f.is_integer() else str(f)
        except (TypeError, ValueError):
            return str(v)

    def _to_nested(df, keys, value_cols):
        cols = [c for c in value_cols if c in df.columns]
        df = df[keys + cols].copy()
        if len(keys) == 1:
            return {_key(row[keys[0]]): {c: _clean(row[c]) for c in cols} for _, row in df.iterrows()}
        result = {}
        for k, g in df.groupby(keys[0]):
            result[_key(k)] = _to_nested(g, keys[1:], cols)
        return result

    _value_cols = ['av_ap', 'av_vap', 'av_vep', 'av_vp', 'pv_ap', 'pv_vap', 'pv_vep', 'pv_vp', 'wvv_vp']
    _elector_cols = ['electors_democrat', 'electors_republican', 'electors_other']
    _output_cols = _value_cols + _elector_cols

    output_dir.mkdir(parents=True, exist_ok=True)


    _outputs = [
        ('p1.json', data_p1, ['year']),
        ('p2.json', data_p2, ['year', 'state_po']),
        ('p3.json', data_p3, ['year', 'state_po', 'district_code']),
        ('p3_state.json', data_p3_state, ['year', 'state_po']),
        ('p4.json', data_p4, ['year', 'state_po', 'district_code']),
        ('p4_state.json', data_p4_state, ['year', 'state_po']),
        ('p5.json', data_p5, ['year', 'state_po'])
    ]

    for (_name, _df, _levels) in _outputs:
        _output = _to_nested(_df, _levels, _output_cols)
        (output_dir / _name).write_text(json.dumps(_output, indent=2))



    print(f"Wrote {len(_outputs)} files to {output_dir}...")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ---

    The resulting dataframes are inputs to the OneVote webapp. The frontend will want to do all of the following:
    - compare values for the same scenario, e.g. **V1** vs **V2** given **P1**
    - compare scenarios for the same value, e.g. **P1** v2 **P2** given **V1**.
    - compare across years for the same scenarios and values.
    - compare between states, districts, and parties for the same scenarios and values.

    Therefore no grouping by "values", "scenarios", or "years" will be particularly preferable over the others.  Currently, for simplicity, I'm going to group by scenario, as the scenarios each produce values along different dimensions, and we don't have a correct district dimension pre-2012.
    - Later we may prefer dict-of-JSONs
    - Later we may be want to split this by scenario or by value.

    TODO: where to output measures? In separate files? One big file?

    TODO: calculate measures, output those two.
    """)
    return


if __name__ == "__main__":
    app.run()
