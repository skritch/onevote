import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import altair as alt
    import pandas as pd

    import viz


@app.cell(hide_code=True)
def _():
    # This dataset is prepared in https://github.com/skritch/election-datasets and uploaded to Kaggle for general use.

    import kagglehub
    from kagglehub import KaggleDatasetAdapter

    # Load the latest version
    data = kagglehub.dataset_load(
      KaggleDatasetAdapter.PANDAS,
      "samkritch/u-s-presidential-elections-by-state-1976-2024",
      'pres_by_state_1976_2024.csv',
    )

    # Calculate national totals by year
    national_totals = data.groupby('year').agg({
        'state_electors': 'sum',
        'state_population': 'sum',
        'votes_total': 'sum'
    }).rename(columns={
        'state_electors': 'national_electors',
        'state_population': 'national_population',
        'votes_total': 'national_votes_total'
    })



    # Merge national totals back to dataframe
    data = data.merge(national_totals, left_on='year', right_index=True)
    data['state_population_pct'] = 100 * data['state_population'] / data['national_population']
    data['state_elector_pct'] = 100 * data['state_electors'] / data['national_electors']


    data.head()
    return (data,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Wasted Votes at L3
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    We'll now consider "wasted" votes *with* party affiliations in mind, i.e. at L3. For now we're still going to limit our attention to P3 (a simplified electoral college) and ignore abstentions and third parties.

    The standard definition of a **wasted vote** is this. A state-level vote is "wasted" if:
    - it contributes to a losing candidate
    - or it contributes to a winning candidate but in excess of the threshold required to win (= half the total votes, under our simplified model with no abstentions, but in a model with abstentions could be argued to be the losing party's vote total instead.)


    TODO: efficiency gap here



    Let's devise some notation. We'll use $v(x)$ to represent a candidate's vote, and v(s) to represent the vote of an entire state. Let

    $$
    R_{v, s} = \sum_{\substack{x \in s \\ v(x) = v}} 1
    $$

    be the number of votes equal to some $v$ in state $s$.

    ---
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Efficiency Gap
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    We can introduce one standard measure of "waste" here: the *efficiency gap**, which compares the waste of the two parties across the entire election.

    $$
    \begin{align}
    \text{Wasted}_{v, s} &= \begin{cases}
      R_{v, s} - \frac{n_s}{2} & (R_{v, s} > \frac{n_s}{2})\\
      R_{v, s}  & (R_{v, s} < \frac{n_s}{2})\\
    \end{cases}\\
    \text{EffGap}_1[P2] &= \frac{\text{Wasted}_{1} - \text{Wasted}_{0}}{N} \\
      &= \frac{\sum_s (\text{Wasted}_{1, s} - \text{Wasted}_{0, s})}{N}
    \end{align}
    $$

    with $\text{EffGap}_0 = - \text{EffGap}_1$.

    This is clearly restricted to $[-1, 1]$, but as no particular state election can have more than $\frac{n_s}{2}$ of its votes wasted, it really only ranges from $[-\frac{1}{2}, \frac{1}{2}]$. One of these bounds would be realized in a fully general election—so the quantity of interest to me should divide by $N/2$ instead, and should subtract the winners from the losers, as all but the most pathological cases, this will produce a positive number.

    $$
    \text{EffGap}[P2] = \frac{\sum_s (\text{Wasted}_{L, s} - \text{Wasted}_{W, s})}{N/2}
    $$

    For now we won't consider "abstentions", so we should use the total number of votes cast for $N$, rather than the number of eligible voters.
    """)
    return


@app.cell(hide_code=True)
def _(data):
    data_with_wv = data.copy()

    # calculate my version of the efficiency gap.
    # for each presidential election, compute the wastes votes for each party in each state.


    # Determine wasted votes for Democrats
    # If they won: votes above threshold are wasted
    # If they lost: all votes are wasted
    data_with_wv['wasted_democrat'] = data_with_wv.apply(
        lambda row: row['votes_democrat'] - row['votes_total'] / 2
        if row['winning_party'] == 'democrat'
        else row['votes_democrat'],
        axis=1
    )

    # Determine wasted votes for Republicans
    # If they won: votes above threshold are wasted
    # If they lost: all votes are wasted
    data_with_wv['wasted_republican'] = data_with_wv.apply(
        lambda row: row['votes_republican'] - row['votes_total'] / 2
        if row['winning_party'] == 'republican'
        else row['votes_republican'],
        axis=1
    )
    return (data_with_wv,)


@app.cell(hide_code=True)
def _(data_with_wv):
    # Calculate efficiency gap for each year
    efficiency_gaps = []

    for year in data_with_wv['year'].unique():
        year_data = data_with_wv[data_with_wv['year'] == year]

        # Total votes nationwide for this year
        total_votes = year_data['votes_total'].sum()

        # Calculate total wasted votes by party
        total_wasted_democrat = year_data['wasted_democrat'].sum()
        total_wasted_republican = year_data['wasted_republican'].sum()

        # Determine national winner (party with most electors)
        dem_electors = year_data['electors_democrat'].sum()
        rep_electors = year_data['electors_republican'].sum()
        national_winner = 'democrat' if dem_electors > rep_electors else 'republican'

        # Calculate efficiency gap: (wasted by losers - wasted by winners) / (N/2)
        if national_winner == 'democrat':
            # Democrats won nationally, so Republicans are losers
            wasted_by_losers = total_wasted_republican
            wasted_by_winners = total_wasted_democrat
        else:
            # Republicans won nationally, so Democrats are losers
            wasted_by_losers = total_wasted_democrat
            wasted_by_winners = total_wasted_republican

        efficiency_gap = (wasted_by_losers - wasted_by_winners) / (total_votes / 2)

        efficiency_gaps.append({
            'year': year,
            'efficiency_gap': efficiency_gap,
            'national_winner': national_winner,
            'total_votes': total_votes,
            'total_wasted_democrat': total_wasted_democrat,
            'total_wasted_republican': total_wasted_republican,
            'total_wasted': total_wasted_democrat + total_wasted_republican
        })

    efficiency_gap_df = pd.DataFrame(efficiency_gaps)
    return (efficiency_gap_df,)


@app.cell(hide_code=True)
def _(efficiency_gap_df):
    # plot a bar graph with altair. Color each bar by the winner of the election. Include mouseover with winner, total votes cast, total wasted votes, and value of efficiency gap.
    chart = alt.Chart(efficiency_gap_df).mark_bar().encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('efficiency_gap:Q', title='Efficiency Gap'),
        color=alt.Color('national_winner:N',
                       scale=alt.Scale(domain=['democrat', 'republican'],
                                     range=['blue', 'darkred']),
                       legend=alt.Legend(title='National Winner')),
        tooltip=[
            alt.Tooltip('year:O', title='Year'),
            alt.Tooltip('national_winner:N', title='Winner'),
            alt.Tooltip('total_votes:Q', title='Total Votes Cast', format=','),
            alt.Tooltip('total_wasted:Q', title='Total Wasted Votes', format=','),
            alt.Tooltip('efficiency_gap:Q', title='Efficiency Gap', format='.3f')
        ]
    ).properties(
        width=600,
        height=400,
        title='Efficiency Gap by Year (1976-2024)'
    ).configure_axis(
        grid=True,
        gridOpacity=0.3
    )

    chart
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Wasted Vote Value
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    The above Efficiency Gap is more-or-less a standard measure, but I do not find it very interesting. Perhaps it's more applicable to gerrymandering.

    My first problem with it is that it does not feel useful or interesting treat *some* of the winning votes as wasted while others are not.

    By the standard definition of waste, $R_{v, s} - \frac{n_s}{2}$ of the winning party's votes in a state $s$ are "wasted", while $\frac{n_s}{2}$ are "counted". All the votes for the losing party are "wasted" was well, for a total of half of the state's votes; Efficiency Gap just measures how these fall out along party lines. Then, along the lines of our earlier WTAV, each of the non-wasted votes has a value of $2 AV(s)$ in the national election, such that the state as a whole is worth its usual $\frac{e_s}{E}N$.

    But without some notion of the "ordering" of the votes, we can't say *which* are wasted. So we might as well say every one of the $R_{v,s}$ votes is worth a fraction $\frac{n_s/2}{R_{v, s}}$ of what it would otherwise be worth. If 70% of the state votes for the winning candidate, $\frac{5}{7}$ of each of those votes "counts" and the remainder is wasted, as are all votes for the other candidates.

    That is: all of the $R_{v,s}$ votes for the winning party are worth $\frac{n_s/2}{R_{v, s}} \cdot 2 \cdot \frac{e_s / E}{n_s / N} = \frac{e_s / E}{R_{v, s} / N}$ each.

    The weights are already normalized: in each state the sum over the winning party comes to $\frac{e_s}{E}N$, which sums to $N$ over all states.

    This gives us our value-of-a-vote function **Wasted Vote Value** (WVV):

    $$
    \begin{align}
    \text{WVV}(x) = \begin{cases}
    \frac{e_{s(x)} / E}{R_{v(x), s(x)} /N} && v(x) = v(s(x)) \\
    0 && v(x) \ne v(s(x))
    \end{cases}
    \end{align}
    $$

    Note we are using *actual* election outcomes here, i.e. we are operating in the *ex post* regime. You could write the same measure in terms of any of our other *ex ante* definitions of party affiliation: party membership, forecasts, last election's results, etc.

    And, as before, we should use the total votes cast for $N$ rather than our usual state population.

    We can then plot the value of a vote by state. Here we'll only plot the value of the winning party's votes, as the losing party is uniformly zero. (Thus the value will appear to be uniformly larger than 1, when in fact they are offset by a large numbers of zeros such that the mean is exactly 1.)

    ---
    """)
    return


@app.cell
def _(data):
    year_dropdown = mo.ui.dropdown.from_series(data.year, value=2024, label="Choose a year: ")
    year_dropdown
    return (year_dropdown,)


@app.cell(hide_code=True)
def _(data_with_wv, year_dropdown):
    data_with_wv['winning_party_votes'] = data_with_wv.apply(
        lambda row: max(row['votes_democrat'], row['votes_republican']), axis=1
    )

    data_with_wv['wvv_winner'] = (data_with_wv['state_electors'] * data_with_wv['national_votes_total']) / (data_with_wv['national_electors'] * data_with_wv['winning_party_votes'])

    viz.viz_value_by_state(data_with_wv, "wvv_winner", "Winning Party's Wasted Votes Value", year_dropdown.value)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    The above resembles apportionment value, but of course only applies to the winners, and varies depending on the margin of victory within a state.

    (But note that margins of victory are, again, *ex post*, and depend on turnout which in turn is causally downstream of forecasts of the margin of victory—votes likely to be wasted tend not to be cast at all!)

    We can compare WVV to AV just to how well they track against each other, expecting margins of victory to be approximately proportional to populations. We get:
    """)
    return


@app.cell(hide_code=True)
def _(data_with_wv, year_dropdown):

    data_with_wv['apportionment_value'] = data_with_wv['state_elector_pct'] / data_with_wv['state_population_pct']

    viz.viz_scatter_compare(
        data_with_wv,
        "wvv_winner", "Winning Party Wasted Vote Value",
        "apportionment_value", "Apportionment Value",
        year_dropdown.value
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    TODO: compute MAD/Var/H?

    How do we determine this for a general election? Do we still count half the votes as wasted? Do we count half the *electoral* votes as wasted, then? Huh?
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
