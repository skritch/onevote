import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import altair

    import kagglehub
    from kagglehub import KaggleDatasetAdapter

    import viz


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Counterfactual Scenarios
    """)
    return


@app.cell
def _():
    population_cols = {
        'ap': ("national_population", "state_population", "district_census_population"),
        'vap': ("national_vap_estimate", "state_vap_estimate", "district_census_vap"),
        'vep': ("national_vep_estimate", "state_vep_estimate", None),
        'vp': ("national_votes_total", "state_votes_total", "votes_total"),
    }
    return (population_cols,)


@app.cell(hide_code=True)
def _():
    # Load the latest version
    data_state = kagglehub.dataset_load(
      KaggleDatasetAdapter.PANDAS,
      "samkritch/u-s-presidential-elections-by-state-1976-2024",
      'pres_by_state_1976_2024.csv',
    )

    national_totals = data_state.groupby('year').agg({
        'state_electors': 'sum',
        'state_population': 'sum',
        'state_vap_estimate': 'sum',
        'state_vep_estimate': 'sum',
        'votes_total': 'sum'
    }).rename(columns={
        'state_electors': 'national_electors',
        'state_population': 'national_population',
        'state_vap_estimate': 'national_vap_estimate',
        'state_vep_estimate': 'national_vep_estimate',
        'votes_total': 'national_votes_total'
    })


    # Merge national totals back to dataframe
    data_state = data_state.merge(national_totals, left_on='year', right_index=True)

    data_state.head(2)
    return data_state, national_totals


@app.cell
def _():
    data_national = kagglehub.dataset_load(
      KaggleDatasetAdapter.PANDAS,
      "samkritch/u-s-presidential-elections-by-state-1976-2024",
      'pres_1976_2024.csv',
    )
    data_national.head(1)
    return (data_national,)


@app.cell
def _(data_state, national_totals):
    data_district: pd.DataFrame = kagglehub.dataset_load(
      KaggleDatasetAdapter.PANDAS,
      "samkritch/u-s-presidential-elections-by-state-1976-2024",
      'pres_by_district_2012_2024.csv',
    )
    # temp until I update upstream
    data_district['state'] = data_district['state'].str.upper()

    data_district = data_district.merge(national_totals, left_on='year', right_index=True)


    state_totals: pd.DataFrame = data_state[['year', 'state', 'state_electors', 'state_population', 
                                             'state_vep_estimate', 'state_vap_estimate', 'votes_democrat', 
                                             'votes_republican', 'winning_party', 'votes_total']].copy()

    state_totals = state_totals.rename(columns={
        'votes_total': 'state_votes_total',
        'votes_democrat': 'state_votes_democrat',
        'votes_republican': 'state_votes_republican',
        'winning_party': 'state_winning_party'
    })

    data_district = data_district.merge(state_totals, on=['year', 'state'])

    data_district.head(1)
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
    \text{WVV}(x) = \frac{e_{s(x)} / E}{R_{v(x), s(x)} / N} && && \text{(winners only)}
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
    ### P1: General Election

    For this we can use the national dataset only.

    The only question is whether we consider national election votes to be "wasted" in the same way state votes are. For most purposes I would say they are *not*, but I'll calculate the appropriate WVVs as if they were.
    """)
    return


@app.cell(hide_code=True)
def _(data_national):
    data_p1 = data_national.copy()

    data_p1['av_ap'] = 1
    data_p1['av_vap'] = 1
    data_p1['av_vep'] = 1
    data_p1['av_vp'] = 1
    data_p1['pv'] = 1

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
    data_p1
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### P2: Simplified Electoral College

    P2 is fairly simple and can be computed directly from state-level data.
    """)
    return


@app.cell(hide_code=True)
def _(data_state):
    data_p2 = data_state.copy()
    data_p2["av_ap"] = (data_p2['state_electors'] / data_p2['national_electors']) / (data_p2['state_population'] / data_p2['national_population'])
    data_p2["av_vap"] = (data_p2['state_electors'] / data_p2['national_electors']) / (data_p2['state_vap_estimate'] / data_p2['national_vap_estimate'])
    data_p2["av_vep"] = (data_p2['state_electors'] / data_p2['national_electors']) / (data_p2['state_vep_estimate'] / data_p2['national_vep_estimate'])
    data_p2["av_vp"] = (data_p2['state_electors'] / data_p2['national_electors']) / (data_p2['votes_total'] / data_p2['national_votes_total'])

    # Calcualtes PV(x) = (N * e_s / sqrt(n_s)) / (sum of e_s * sqrt(n_s) for all s)
    # Using 
    def calculate_pv(group, p='vep'):

        p_cols = {
            'ap': ("state_population", "national_population"),
            'vap': ("state_vap_estimate", "national_vap_estimate"),
            'vep': ("state_vep_estimate", "national_vep_estimate"),
            'vp': ("votes_total", "national_votes_total"),
        }

        # Calculate the denominator: sum of e_s * sqrt(n_s) for all states
        denominator = (
            group["state_electors"] * np.sqrt(group[p_cols[p][0]])
        ).sum()

        # Calculate PV for each state
        pv_values = (
            group[p_cols[p][1]]
            * group["state_electors"]
            / np.sqrt(group[p_cols[p][0]])
        ) / denominator
        return pv_values

    # Assign PV
    data_p2["pv_ap"] = data_p2.groupby("year").apply(calculate_pv, p='ap').reset_index(drop=True)
    data_p2["pv_vap"] = data_p2.groupby("year").apply(calculate_pv, p='vap').reset_index(drop=True)
    data_p2["pv_vep"] = data_p2.groupby("year").apply(calculate_pv, p='vep').reset_index(drop=True)
    data_p2["pv_vp"] = data_p2.groupby("year").apply(calculate_pv, p='vp').reset_index(drop=True)

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
    data_p2
    return (data_p2,)


@app.cell
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
    metrics = ['av_ap', 'av_vap', 'av_vep', 'av_vp', 'pv_ap', 'pv_vap', 'pv_vep', 'pv_vp', 'wvv_democrat', 'wvv_republican']

    state1_values = [state1_data[metric] for metric in metrics]
    state2_values = [state2_data[metric] for metric in metrics]

    # Create combined dataset
    chart_data = []
    for i, metric in enumerate(metrics):
        chart_data.append({
            'metric': metric,
            'value': state1_values[i],
            'state': state1_dropdown.value,
        })
        chart_data.append({
            'metric': metric,
            'value': state2_values[i],
            'state': state2_dropdown.value,
        })

    chart_df = pd.DataFrame(chart_data)

    # Create the chart with state facets
    chart = altair.Chart(chart_df).mark_bar().encode(
        x=altair.X('metric:O', title='Metric', axis=altair.Axis(labelAngle=-45)),
        y=altair.Y('value:Q', title='Value', scale=altair.Scale(zero=False)),
        column=altair.Column('state:N', title='State'),
        tooltip=['metric:O', 'value:Q', 'state:N', 'category:O']
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
    ### P3

    Today, both Maine and Nebraska assign their 2 "Senate" electors to the winner of the state election, but assign their "House" electors to the popular-vote winner in each congressional district.

    Maine has assigned its district electors by district for all the years in our data, while Nebraska adopted the system in 1992. Maine split its electors in 2016 and 2020. Nebraska in 2008 and 2020.

    How then should we handle our value functions?

    ---

    First, we need a new schema for our table, which will also be applicable to P4. We will have one row per congressional district rather than per state. At the P3 level, the P2 measures can be copied to every district for all states but ME and NE.

    For AV: each district receives its share of the Senate electors, plus its house elector. Here $e_s$ represents only the Senate electors:

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
    \text{WVV}(x) = \frac{e_{s(x)} / E}{R_{v(x), s(x)} / N} + \frac{e_{d(x)} / E}{R_{v(x), d(x)} / N}
    $$

    and use VP.
    """)
    return


@app.cell(hide_code=True)
def _(data_district: pd.DataFrame, data_state, population_cols):
    data_p3 = data_district.copy()


    _is_split_state = (data_state['state'] == 'MAINE') | ((data_state['state'] == 'NEBRASKA') & (data_state['year'] >= 1992))
    data_p3['_is_split'] = (data_p3['state'] == 'MAINE') | ((data_p3['state'] == 'NEBRASKA') & (data_p3['year'] >= 1992))

    def av_for_district(row, p: str):
        state_part = (
            ((row['state_electors'] if not row['_is_split'] else 2) * row[population_cols[p][0]])
             / (row[population_cols[p][1]] * row['national_electors'])
        )
        if not row['_is_split']:
            return state_part
        district_part = (
            (row[population_cols[p][0]]) / (row[population_cols[p][2]] * row['national_electors'])
        )
        return state_part + district_part

    
    def pv_for_district(row, p: str):
        state_part = (
            ((row['state_electors'] if not row['_is_split'] else 2) * row[population_cols[p][0]])
             / (np.sqrt(row[population_cols[p][1]]) * row['pv_denominator'])
        )
        if not row['_is_split']:
            return state_part
        district_part = (
            (row[population_cols[p][0]]) / (np.sqrt(row[population_cols[p][1]]) * row['pv_denominator'])
        )
        return state_part + district_part

    def wvv_for_district(row, p: str):
        sd, sr, sw = row['state_votes_democrat'], row['state_votes_republican'], row['state_winning_party']
        state_const = (
            ((row['state_electors'] if not row['_is_split'] else 2) * row[population_cols[p][0]])
             / (row['national_electors'])
        )
        state_part = (state_const / sd, 0) if sw == 'democrat' else (0, state_const / sr)
        if not row['_is_split']:
            return state_part
        district_const = (
            (row[population_cols[p][0]]) / (row['national_electors'])
        )
        if row['winning_party'] == 'democrat':
            return (state_part[0] + district_const / row['votes_democrat'], state_part[1])
        else:
            return (state_part[0], state_part[1] + district_const / row['votes_republican'])

    for _p in ['ap', 'vap', 'vep', 'vp']:
        (_n_pop, _s_pop, _d_pop) = population_cols[_p]

        # AV
        _av_col = f'av_{_p}'
        data_p3[_av_col] = 0.0
        data_p3[_av_col] = data_p3.apply(av_for_district, p=_p, axis=1, )

        # PV
        _pv_col = f'pv_{_p}'
    
        # Denominator for PV calculations
        _z_by_year = (
            (data_state.loc[~_is_split_state, 'state_electors'] * np.sqrt(data_state.loc[~_is_split_state, _s_pop])).groupby(data_state.loc[~_is_split_state, "year"]).sum()
            + 
            (2 * np.sqrt(data_state.loc[_is_split_state, _s_pop])).groupby(data_state.loc[_is_split_state, "year"]).sum()
            + (np.sqrt(data_p3[_d_pop])).groupby(data_p3["year"]).sum()
        )
        data_p3['pv_denominator'] = data_p3['year'].map(_z_by_year)
        data_p3[_pv_col] = 0.0
        data_p3[_pv_col] = data_p3.apply(pv_for_district, p=_p, axis=1)


    # WVV
    data_p3[['wvv_democrat', 'wvv_republican']] = data_p3.apply(wvv_for_district, axis=1, result_type='expand')
    data_p3["wvv_other"] = 0.0


    data_p3
    return av_for_district, pv_for_district, wvv_for_district


@app.cell(hide_code=True)
def _(
    av_for_district,
    data_district: pd.DataFrame,
    data_p2,
    population_cols,
    pv_for_district,
    wvv_for_district,
):
    data_p4 = data_district.copy()
    data_p4['_is_split'] = True

    for _p in ['ap', 'vap', 'vp']:
        # AV
        _av_col = f'av_{_p}'
        data_p4[_av_col] = 0.0
        data_p4[_av_col] = data_p4.apply(av_for_district, axis=1, p=_p)

        # PV
        _pv_col = f'pv_{_p}'
        # Denominator for PV calculations
        _z_by_year = (
            (2 * np.sqrt(data_p2[population_cols[_p][1]])).groupby(data_p2["year"]).sum()
            + (np.sqrt(data_p4[population_cols[_p][2]])).groupby(data_p4["year"]).sum()
        )
        data_p4['pv_denominator'] = data_p4['year'].map(_z_by_year)
        data_p4[_pv_col] = 0.0
        data_p4[_pv_col] = data_p4.apply(pv_for_district, p=_p, axis=1)


    # WVV
    data_p4[['wvv_democrat', 'wvv_republican']] = data_p4.apply(wvv_for_district, axis=1, result_type='expand')
    data_p4["wvv_other"] = 0.0

    data_p4
    return


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
    ### P5

    Here we assign the current number of electors, at the state level, in proportion to the popular vote.

    For now I'll ignore third parties and abstentions.

    Mathematically, suppose the vote percent D is $p_s$ and there are $k_s$ electors. Each elector is worth $\frac{1}{e_s}$. We assign $\lfloor \frac{p_s}{1/e_s} \rfloor$ electors to D and $\lfloor \frac{1- p_s}{1/e_s} \rfloor$ to R.

    E.g. 7 electors, 60% -> $\frac{0.6}{1/7} = 4.2$ means 4 go to D. $\frac{0.4}{1/7} = 2.8$ means 2 goes to R. Then we'll assign the winner to the popular winner, here D. (Another option would be to assign it to the larger remainder.)

    (There can be at most one left over.)

    That is:

    $$
    e_{s, v} = \left\lfloor \frac{R_{v, s}}{n_s} e_s \right\rfloor + 1_{R_{v, s} > n_s}
    $$

    (This expression does not count for the case where $\frac{R_{v, s}}{n_s} e_s$ is an integer exactly, in which case nothing should be added.)

    Now, how do we calculate metrics?

    AV should be unchanged, but we could compute another version of it using exact elector count $\frac{e_{s, v} / E}{R_{v, s} / N_{VP}}$.

    (Is there another verison where we assign one elector to each $\frac{n_s}{e_s}$? Well, this gives the same expression...)

    PV: My immediate idea is to assign one elector to each $\frac{n_s}{e_s}$ of population, but these are not WTA, they "fill up all the way" before spilling over to the next elector.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
