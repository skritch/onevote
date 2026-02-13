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
        'ap': ("national_apportionment_population", "state_apportionment_population", "apportionment_population"),
        'vap': ("national_vap_estimate", "state_vap_estimate", "apportionment_voting_age_population"),
        'vep': ("national_vep_estimate", "state_vep_estimate", None),
        'vp': ("national_votes_total", "state_votes_total", "votes_total"),
    }
    return (population_cols,)


@app.cell
def _():
    data_national = kagglehub.dataset_load(
      KaggleDatasetAdapter.PANDAS,
      "samkritch/u-s-presidential-elections-by-state-1976-2024",
      'pres_1976_2024.csv',
    )
    data_national.head(1)
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

    data_state.head(2)
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
def _(data_state, population_cols):
    data_p2 = data_state.copy()

    # Calcualtes PV(x) = (N * e_s / sqrt(n_s)) / (sum of e_s * sqrt(n_s) for all s)
    # Using 
    def calculate_pv(group, p='vep'):
        # Calculate the denominator: sum of e_s * sqrt(n_s) for all states
        denominator = (
            group["state_electors"] * np.sqrt(group[population_cols[p][1]])
        ).sum()

        # Calculate PV for each state
        pv_values = (
            group[population_cols[p][0]]
            * group["state_electors"]
            / np.sqrt(group[population_cols[p][1]])
        ) / denominator
        return pv_values

    for _p, (_n, _s, _d) in population_cols.items():
        # Assign AV
        data_p2[f"av_{_p}"] = (data_p2['state_electors'] / data_p2['national_electors']) / (data_p2[_s] / data_p2[_n])
        # Assign PV
        data_p2[f"pv_{_p}"] = data_p2.groupby("year").apply(calculate_pv, p=_p).reset_index(drop=True)
    

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
    \text{WVV}(x) = \frac{e_{s(x)} / E}{R_{v(x), s(x)} / N} + \frac{e_{d(x)} / E}{R_{v(x), d(x)} / N}
    $$

    and use VP.
    """)
    return


@app.cell(hide_code=True)
def _(population_cols):
    # Functions for P3/P4

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

    # No VEP because we can't use it at the district level (though VAP would probably be fine)
    for _p in ['ap', 'vap', 'vp']:
        (_n_pop, _s_pop, _d_pop) = population_cols[_p]

        # AV
        _av_col = f'av_{_p}'
        data_p3[_av_col] = 0.0
        data_p3[_av_col] = data_p3.apply(av_for_district, p=_p, axis=1, )

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
        _sqrt_state_pops = np.sqrt(data_district.groupby(["state", "year"])[_d_pop].sum())
        _z_state = ((_state_electors * _sqrt_state_pops)
            .reset_index(level=0, drop=True) # Drop state
            .groupby("year")
            .sum()
       )
        _z_district = (np.sqrt(data_p3.loc[_is_split_state_district, _d_pop])
            .groupby(data_p3.loc[_is_split_state_district, "year"])
            .sum()
        )
        _z = _z_state + _z_district

        data_p3['pv_denominator'] = data_p3['year'].map(_z)
        data_p3[_pv_col] = 0.0
        data_p3[_pv_col] = data_p3.apply(pv_for_district, p=_p, axis=1)


    # WVV
    data_p3[['wvv_democrat', 'wvv_republican']] = data_p3.apply(wvv_for_district, p=_p, axis=1, result_type='expand')
    data_p3["wvv_other"] = 0.0


    data_p3
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
        (_n_pop, _s_pop, _d_pop) = population_cols[_p]

        # AV
        _av_col = f'av_{_p}'
        data_p4[_av_col] = data_p4.apply(av_for_district, axis=1, p=_p)

        # PV
        _pv_col = f'pv_{_p}'
        # Denominator for PV calculations
        _state_electors = (data_district
            .groupby(["state", "year"])
            .size().map(lambda _: 2)
        )
        _sqrt_state_pops = np.sqrt(data_district.groupby(["state", "year"])[_d_pop].sum())
        _z_state = ((_state_electors * _sqrt_state_pops)
            .reset_index(level=0, drop=True) # Drop state
            .groupby("year")
            .sum()
        )
        _z_district = (np.sqrt(data_district[_d_pop])
            .groupby(data_district["year"])
            .sum()
        )
        _z = _z_state + _z_district

        data_p4['pv_denominator'] = data_p4['year'].map(_z)
        data_p4[_pv_col] = data_p4.apply(pv_for_district, p=_p, axis=1)


    # WVV
    data_p4[['wvv_democrat', 'wvv_republican']] = data_p4.apply(wvv_for_district, p=_p, axis=1, result_type='expand')
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

    (This expression does not count for the case where $\frac{R_{s, v}}{n_s} e_s$ is an integer exactly, in which case nothing should be added.)

    Now, how do we calculate metrics?

    AV should be unchanged, but we could compute another version of it using exact elector count $\frac{e_{s, v} / E}{R_{s, v} / N_{VP}}$. (This would basically be WVV... but which N do we use?)

    (Is there another version where we assign one elector to each $\frac{n_s}{e_s}$? Well, this gives the same expression...)

    PV: My immediate idea is to assign one elector to each $\frac{n_s}{e_s}$ of population, but these are not WTA, they "fill up all the way" before spilling over to the next elector.

    Instead, in keeping with the original formulation, we need to consider the full $2^{n_s}$ space of state outcomes, then count the number in which voter $x \in s$ is pivotal. Well, the popular outcome is going to be the same $\approx \sqrt{n_s}$-wide normal-ish distribution as before, which is extremely peaked compared to the spacing of the elector seats $\frac{n_s}{e_s} \approx 800\text{k}$. Only the final elector (with odd $e_s$) or the final two electors (with even $e_s$) flip at all—and these flip with the same $\frac{1}{\sqrt{n_s}}$ scaling as before.

    The different is that both parties automatically split up the remaining electors with near-certainty. Only one/two electors per state has any chance to change hands.

    By a strict pivotality calculation where therefore have (for odd $e_s$):

    $$
    \begin{align}
    P[x \text{ is pivotal}] &= (P[x \text{ flips elector 1}] + P[x \text{ flips elector 2}] + \ldots + P[x \text{ flips elector } e_s]) \cdot \frac{1}{\Vert \mathbf{e} \Vert} \\
      &\approx (0 + \ldots + P[x \text{ flips elector } \frac{e_s}{2}] + \ldots + 0) \cdot \frac{1}{\Vert \mathbf{e} \Vert} \\
      &\propto \frac{1 + 1_{e_s \text{ even}}}{\sqrt{n_s}}
    \end{align}
    $$

    It's not clear how to think about the denominator $\Vert \mathbf{e} \Vert$ here, nor how to account for the "value" of a voter just for existing and filling out the population, earning some fraction of the remaining electors.

    But, at least in a simplified view, we can work with the above: we get a PV which does not depend on state elector counts at all (except whether they're odd or even).

    The odd/even thing is weird: most reasonable rounding schemes would just split the electors down the middle for approximately-even states, as again, the highly-unrealistic uniform-distribution setup for this measure assigns basically 0 probability to margins larger than a few thousand votes for even the largest states.


    What about WVV?

    We just do $\frac{e_{s, v} / E}{R_{s, v} / N}$ for both sides. Easy. (But which N do we use?)
    """)
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Once P5 is finished... we will have calculated:
    - 3 values (AV, PV, WVV)
    - times 3 measures (MAD, Var, H)
    - times 5 or so electoral scenarios
    - times 3 or 4 definitions of "population"

    (Obvious next thing to add is Shapley, before striking off on our own)

    which should be enough to architect a prototype of the OneVote app itself.

    What's the right abstraction? Can build an abstraction that allows us to plug together "values" and "scenarios", at least?
    - starting point = an object representing a scenario?
      - this sounds... hard.
    - probably easier to do something alone the lines of this notebook, outputting CSVs, and storing metadata on the calculations somewhere.

    Outputs can be at various "resolutions": (national | state | district | ?) x (entire population | party)
    Can also be defined in terms of different population measures, which could affect how it assigns values. (If you are not included in VEP or VP, the value of your vote = 0?)

    Then the consumer will be able to disable certain measures/scenarios based on the data available:
    - VAP/VEP cannot be calculated before 1980
    - VEP cannot be calculated for districts at all
    - districts cannot be used before 2012

    What about options like:
    - including territories, puerto rico?

    Easiest thing is to just write out a different version of the output files for each option combination, but if there turn out to be a lot this could get hard. Another is to output a copy of the columns w/ and w/o.


    Where do measures go?
    - Separate output files I think.

    What if this gets long/complicated?
    - split up this notebook.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
