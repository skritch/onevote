import marimo

__generated_with = "0.19.6"
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

    import viz



@app.cell
def _():
    # Parse command line arguments
    _parser = argparse.ArgumentParser(description='Presidential Election Scenarios Analysis')
    _parser.add_argument(
        '--output-dir',
        default="./.data/presidential_values/",
        type=str, 
        help='Output file path for results')
    _args = _parser.parse_args()
    output_dir = Path(_args.output_dir)
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
    This notebook calculates various "value functions" for various presidential election scenarios.
    - 3 values (AV, PV, WVV)
    - with AV, PV implemented for 4 definitions of "population" (AP, VAP, VEP, VP)
    - times 4 (currently) scenarios (P1=general election, P2=simplified electoral college, etc.)

    The resulting dataframes are inputs to the OneVote webapp.

    Each scenario outputs its value along a dimension which is a product of:
    - a spatial granularity: nationally, by state, or by district
      - TODO: we ought to do this with and without U.S. territories.
    - a party line: either uniform, or split D/R
      - TODO: support abstentions
      - TODO: support third parties and "other"

    There are some limitations:
    - VAP/VEP are not currently supported 1980
      - TODO: we can probably get census data for VAP for all years. Not sure it would be consistent with UF though.
    - VEP is not supported districts at all
    - district granularity is only supported after 2012
      - TODO: we can probably support populations going back much further, but electoral results are harder.


    I anticipate the frontend will want to do both of:
    - compare values for the same scenario
    - compare scenarios for the same values
    - compare across years for the same scenarios and values

    so no grouping by "values", "scenarios", or "years" is particularly preferable over the others.  Currently, for simplicity, I'm going to group by scenario, as the scenarios each produce values along different dimensions, and we don't have a correct district dimension pre-2012.
    - Later we may prefer dict-of-JSONs
    - Later we may be want to split this by scenario or by value.

    TODO: where to output measures? In separate files? One big file?
    """)
    return


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
    data_national = kagglehub.dataset_load(
      KaggleDatasetAdapter.PANDAS,
      "samkritch/u-s-presidential-elections-by-state-1976-2024",
      'pres_1976_2024.csv',
    )
    # data_national 
    return (data_national,)


@app.cell(hide_code=True)
def _():
    data_state = kagglehub.dataset_load(
      KaggleDatasetAdapter.PANDAS,
      "samkritch/u-s-presidential-elections-by-state-1976-2024",
      'pres_by_state_1976_2024.csv',
    )

    national_totals = data_state.groupby('year').agg({
        'electors': 'sum',
        'apportionment_population': 'sum',
        'vap_estimate': 'sum',
        'vep_estimate': 'sum',
        'votes_total': 'sum'
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

    # data_state
    return data_state, national_totals


@app.cell(hide_code=True)
def _(data_state, national_totals):
    data_district: pd.DataFrame = kagglehub.dataset_load(
      KaggleDatasetAdapter.PANDAS,
      "samkritch/u-s-presidential-elections-by-state-1976-2024",
      'pres_by_district_2012_2024.csv',
    )
    # temp until I update upstream
    data_district['state'] = data_district['state'].str.upper()
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

    # data_district
    return (data_district,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Presidential Election Scenarios

    Our goal is calculate the three values:

    **V1**. Apportionment Value

    $$
    \text{AV}(x) = \frac{e_{s(x)} / E}{n_{s(x)} / N}
    $$

    As a measure of apportionment, $n_s$ should be the apportionment population (AP). As a measure of the value of a vote it would use voting-eligible population (VEP) (which would make it a "potential" value of a vote, ex ante) or voting population (VP) (which would make it an ex post "actual" value of a vote).

    We'll calculate all *four* as `av_ap`, `av_vap`, `av_vep`, and `av_vp`.
    - currently have no VAP/VEP for 1976
    - no VEP at district-level

    **V2**. Pivotality Value

    $$
    \text{PV}(x) = \frac{ e_{s(x)} \sqrt{n_{s(x)}} / \sum_s e_s \sqrt{n_s}}{n_s / N}
    $$

    In this measure $n_s$ and $N$ should probably be VEP, as only potential voters have a chance of being "pivotal" at all. VP might be fine too, but has the usual downside of being causally downstream of the voting system itself; the (already suspect) hypothesis of a "uniform distribution" over outcomes is even less plausible as a distribution over the results of the votes actually cast.

    **V3**. Wasted Vote Value

    $$
    \begin{align}
    \text{WVV}(x) = \frac{e_{s(x)} / E}{r_{s(x), v(x)} / N} && && \text{(winners only)}
    \end{align}
    $$

    Here $N$ should be the total votes cast. We could extend this to the rest of VEP by valuing votes which weren't cast at all at zero.

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

    # Or do we assign value=0 to the losers nationally?
    data_p1['wvv_democrat'] = data_p1.apply(
        lambda row: (row['votes_total'] / row['votes_democrat'])
        if row['winning_party'] == 'democrat'
        else 0,
        axis=1
    )
    data_p1['wvv_republican'] = data_p1.apply(
        lambda row: (row['votes_total'] / row['votes_republican'])
        if row['winning_party'] == 'republican'
        else 0,
        axis=1
    )
    data_p1["wvv_other"] = 0
    data_p1.tail(1)
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

    # Calcualtes PV(x) = (N * e_s / sqrt(n_s)) / (sum of e_s * sqrt(n_s) for all s)
    # Using 
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

    # AP doesn't make sense for P
    for _p in ['vap', 'vep', 'vp']:
        _pcols = population_cols[_p]
        # Assign PV
        data_p2[f"pv_{_p}"] = data_p2.groupby("year").apply(calculate_pv, pcols=_pcols).reset_index(drop=True)


    data_p2["wvv_democrat"] = data_p2.apply(
        lambda row: (row["state_electors"] * row["national_votes_total"])
        / (row["national_electors"] * row["votes_democrat"])
        if row["winning_party"] == "democrat"
        else 0,
        axis=1,
    )
    data_p2["wvv_republican"] = data_p2.apply(
        lambda row: (row["state_electors"] * row["national_votes_total"])
        / (row["national_electors"] * row["votes_republican"])
        if row["winning_party"] == "republican"
        else 0,
        axis=1,
    )
    data_p2["wvv_other"] = 0
    data_p2.tail(1)
    return (data_p2,)


@app.cell(hide_code=True)
def _(data_p2):
    year_dropdown = mo.ui.dropdown.from_series(data_p2.year, value=2024, label="Choose a year: ")
    state1_dropdown = mo.ui.dropdown.from_series(data_p2.state, value="NEW YORK", label="Choose a state: ")
    state2_dropdown = mo.ui.dropdown.from_series(data_p2.state, value="OHIO", label="Choose a state: ")

    year_dropdown, state1_dropdown, state2_dropdown
    return state1_dropdown, state2_dropdown, year_dropdown


@app.cell(hide_code=True)
def _(data_p2, state1_dropdown, state2_dropdown, year_dropdown):
    # Filter data for selected year and states
    year_data = data_p2[data_p2.year == year_dropdown.value]
    state1_data = year_data[year_data.state == state1_dropdown.value].iloc[0]
    state2_data = year_data[year_data.state == state2_dropdown.value].iloc[0]

    # Prepare data for visualization
    _values = ['av_ap', 'av_vap', 'av_vep', 'av_vp',  'pv_vap', 'pv_vep', 'pv_vp', 'wvv_democrat', 'wvv_republican']
    state1_values = [state1_data[_v] for _v in _values]
    state2_values = [state2_data[_v] for _v in _values]

    # Create combined dataset
    chart_data = []
    for i, _v in enumerate(_values):
        chart_data.append({
            'name': _v,
            'value': state1_values[i],
            'state': state1_dropdown.value,
        })
        chart_data.append({
            'name': _v,
            'value': state2_values[i],
            'state': state2_dropdown.value,
        })

    chart_df = pd.DataFrame(chart_data)

    # Create the chart with state facets
    chart = altair.Chart(chart_df).mark_bar().encode(
        x=altair.X('name:O', title='Metric', axis=altair.Axis(labelAngle=-45)),
        y=altair.Y('value:Q', title='Value', scale=altair.Scale(zero=False)),
        column=altair.Column('state:N', title='State'),
        tooltip=['name:O', 'value:Q', 'state:N', 'category:O']
    ).resolve_scale(
        y='shared'
    ).properties(
        width=180,
        height=300,
        title=f'P2 Value Comparison ({year_dropdown.value})'
    )

    chart
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## P3

    Today, both Maine and Nebraska assign their 2 "Senate" electors to the winner of the state election, but assign their "House" electors to the popular-vote winner in each congressional district.

    Maine has assigned its district electors by district for all the years in our data, while Nebraska adopted the system in 1992. Maine split its electors in 2016 and 2020. Nebraska in 2008 and 2020.

    How then should we handle our value functions?

    ---

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
    \text{WVV}(x) = \frac{e_{s(x)} / E}{r_{s(x), v(x)} / N} + \frac{e_{d(x)} / E}{r_{d(x), v(x)} / N}
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
        state_const = (
            ((row['state_electors'] if not row['_is_split'] else 2) * row[p.n])
             / (row['national_electors'])
        )
        state_part = (state_const / sd, 0) if sw == 'democrat' else (0, state_const / sr)
        if not row['_is_split']:
            return state_part
        district_const = (
            (row[p.n]) / (row['national_electors'])
        )
        if row['winning_party'] == 'democrat':
            return (state_part[0] + district_const / row['votes_democrat'], state_part[1])
        else:
            return (state_part[0], state_part[1] + district_const / row['votes_republican'])
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
    data_p3[['wvv_democrat', 'wvv_republican']] = data_p3.apply(wvv_for_district, p=population_cols['vp'], axis=1, result_type='expand')
    data_p3["wvv_other"] = 0.0


    data_p3.tail(1)
    return (data_p3,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## P4

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
    data_p4[['wvv_democrat', 'wvv_republican']] = data_p4.apply(wvv_for_district, p=population_cols['vep'], axis=1, result_type='expand')
    data_p4["wvv_other"] = 0.0

    data_p4.tail(1)
    return (data_p4,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    AV and PV should not vary within a state for AP, because the districts are mostly equally sized. VAP, VEP should vay a bit more, with VP the most, but VP is the least reliable.

    The main reason for these is to compare to P2/P3, and for WVV-type measures which do depend on the particular district.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## P5

    Here we assign the current number of electors, at the state level, in proportion to the popular vote. We'll include third parties, why not, but will pretend all "other" votes comprise a single party for now.

    Suppose the vote percent of a party is $p_s$. We assign $\lfloor p_s e_s \rfloor$ electors to each party. Assuming no abstentions, the remaining electors are at most one less than the number of parties. Assign them to the largest remainders in descending order.

    E.g. 7 electors, 60% -> $\frac{0.6}{1/7} = 4.2$ means 4 go to D. $\frac{0.4}{1/7} = 2.8$ means 2 goes to R. The last elector goes to D.

    Now, how do we calculate values?

    **AV**

    This should be unchanged.

    (Could we compute another version of with the exact elector count $\frac{e_{s, v} / E}{r_{s, v} / N_{VP}}$. (This would basically be WVV... feels a little odd.)

    **PV**

    My immediate thought is to assign one elector to each $\frac{n_s}{e_s}$ of population, but these are not WTA, they "fill up all the way" before spilling over to the next elector.

    Instead, in keeping with the original formulation, we need to consider the full $2^{n_s}$ space of state outcomes, then count the number in which voter $x \in s$ is pivotal. Well, the popular outcome is going to be the same $\approx \sqrt{n_s}$-wide normal-ish distribution as before, which is extremely peaked compared to the spacing of the elector seats $\frac{n_s}{e_s} \approx 800\text{k}$. Only the final elector (with odd $e_s$) or the final two electors (with even $e_s$) flip at all—and these flip with the same $\frac{1}{\sqrt{n_s}}$ scaling as before.

    The different is that both parties automatically split up the remaining electors with near-certainty. Only one/two electors per state has any chance to change hands—in fact, if the elector counts are even, they will effectively always split, where when they're odd there's a pivotality chance for the single contested seat.

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

    We just do $\frac{e_{s, v} / E}{r_{s, v} / N}$ for both sides. Easy.

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


    # WVV. Quite simple. 
    for party in ['democrat', 'republican', 'other']:
        data_p5[f"wvv_{party}"] = data_p5.apply(
            lambda row: (row[f"electors_{party}"] * row["national_votes_total"])
                / (row["national_electors"] * row[f"votes_{party}"])
            if row[f"electors_{party}"] > 0 else 0,
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
def _(data_p1, data_p2, data_p3, data_p4, data_p5, output_dir):
    # There's a lot of columns we don't need in frontend... remove?

    output_dir.mkdir(exist_ok=True)
    data_p1.to_csv(output_dir / 'p1.csv') 
    data_p2.to_csv(output_dir / 'p2.csv')
    data_p3.to_csv(output_dir / 'p3.csv')
    data_p4.to_csv(output_dir / 'p4.csv')
    data_p5.to_csv(output_dir / 'p5.csv')
    return


if __name__ == "__main__":
    app.run()
