# /// astro
# title: Wasted Votes
# description:
# ///



import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import altair as alt
    import pandas as pd

    from lib import viz


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
        'electors': 'sum',
        'apportionment_population': 'sum',
        'vap_estimate': 'sum', 
        'vep_estimate': 'sum',
        'votes_total': 'sum',
        'votes_democrat': 'sum',
        'votes_republican': 'sum',
        'electors_democrat': 'sum',
        'electors_republican': 'sum'
    }).rename(columns={
        'electors': 'national_electors',
        'vap_estimate': 'national_vap_estimate',
        'vep_estimate': 'national_vep_estimate',
        'apportionment_population': 'national_apportionment_population',
        'votes_total': 'national_votes_total',
        'votes_democrat': 'national_votes_democrat',
        'votes_republican': 'national_votes_republican',
        'electors_democrat': 'national_electors_democrat',
        'electors_republican': 'national_electors_republican'
    })



    # Merge national totals back to dataframe
    data = data.merge(national_totals, left_on='year', right_index=True)
    data['national_winning_party'] = data.apply(lambda row: 'democrat' if row['national_votes_democrat'] > row['national_votes_republican'] else 'republican', axis=1)

    data['apportionment_population_pct'] = 100 * data['apportionment_population'] / data['national_apportionment_population']
    data['elector_pct'] = 100 * data['electors'] / data['national_electors']
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
    - or it contributes to a winning candidate but in excess of the threshold required to win

    For a two-party election with no abstentions, the threshold to win would be half the total number of votes. But if we allow abstentions, or add a third party, there's no way exact threshold, and we should use the second-place vote count as an effective threshold instead. The version with just two parties is uninteresting, so we'll only consider the general case from here on.

    Let's devise some notation. We'll use $v(x)$ to represent a candidate's vote, and v(s) to represent the vote of an entire state. Let

    $$
    R_p(s) = \sum_{\substack{x \in s \\ v(x) = p}} 1
    $$

    be the number of votes cast for some party $p$ in state $s$.

    Then our two definitions of wasted votes are:

    $$
    \begin{align}
    \text{Wasted}_p(s) &= \begin{cases}
      R_{{p}_1}(s) - R_{p_2}(s) & \\
      R_p(s)  & (p \ne p_1)\\
    \end{cases}
    \quad\quad\quad\quad& \text{(in general)}
    \end{align}
    $$

    where $p_1$ is the first place party, $p_2$ is second place, etc.

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
    We can introduce one standard measure of "waste" here: the **efficiency gap**, which compares the waste of two parties across the entire election.

    $$
    \begin{align}
    \text{EffGap}_1[P2] &= \frac{\text{Wasted}_{1} - \text{Wasted}_{0}}{N} \\
      &= \frac{\sum_s (\text{Wasted}_1(s) - \text{Wasted}_0(s))}{N}
    \end{align}
    $$

    Here $N$ should be VEP or VP, though the interpretation differs in each case.

    In general we expect the winning party to waste fewer votes, so we will compute efficiency gap as the losing party minus the winning, that is,

    $$
    \begin{align}
    \text{EffGap}_L[P2] &= \frac{\text{Wasted}_{L} - \text{Wasted}_{W}}{N} \\
    \end{align}
    $$
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
        lambda row: row['votes_democrat'] - row['votes_republican']
        if row['winning_party'] == 'democrat'
        else row['votes_democrat'],
        axis=1
    )

    # Determine wasted votes for Republicans
    # If they won: votes above threshold are wasted
    # If they lost: all votes are wasted
    data_with_wv['wasted_republican'] = data_with_wv.apply(
        lambda row: row['votes_republican'] - row['votes_democrat']
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
        p_wasted_democrat = total_wasted_democrat / year_data['votes_democrat'].sum()
        p_wasted_republican = total_wasted_republican / year_data['votes_republican'].sum()

        # Determine national winner (party with most electors)
        dem_electors = year_data['electors_democrat'].sum()
        rep_electors = year_data['electors_republican'].sum()
        national_winner = 'democrat' if dem_electors > rep_electors else 'republican'

        # Calculate efficiency gap: (wasted by losers - wasted by winners) / N
        if national_winner == 'democrat':
            # Democrats won nationally, so Republicans are losers
            wasted_by_losers = total_wasted_republican
            wasted_by_winners = total_wasted_democrat
        else:
            # Republicans won nationally, so Democrats are losers
            wasted_by_losers = total_wasted_democrat
            wasted_by_winners = total_wasted_republican

        efficiency_gap = (wasted_by_losers - wasted_by_winners) / (total_votes)
        efficiency_gap_democrat = (total_wasted_democrat - total_wasted_republican) / (total_votes)

        efficiency_gap_b_democrat = p_wasted_democrat - p_wasted_republican
    
        efficiency_gaps.append({
            'year': year,
            'efficiency_gap': efficiency_gap,
            'efficiency_gap_democrat': efficiency_gap_democrat,
            'efficiency_gap_b_democrat': efficiency_gap_b_democrat,
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
    Interesting that it actually goes negative a couple of times: in 2000 and 2004, the Republicans saw more wasted votes than the Democrats despite winning election.

    We can also ask: which party saw more of the votes they *cast* be wasted? For lack of a better name I'll call this **Efficiency Gap B**.


    $$
    \begin{align}
    \text{EffGapB}_2[P2] &= \frac{\text{Wasted}_{L}}{N_L} - \frac{\text{Wasted}_{W}}{N_W} \\
    \end{align}
    $$

    (It might also be interesting to compare this to the net waste $\frac{\text{Wasted}_{L} + \text{Wasted}_{W}}{N}$.)
    """)
    return


@app.cell
def _(efficiency_gap_df):
    # plot a bar graph with altair. Color each bar by the winner of the election. Include mouseover with winner, total votes cast, total wasted votes, and value of efficiency gap.
    _chart = alt.Chart(efficiency_gap_df).mark_bar().encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('efficiency_gap_b_democrat:Q', title='Efficiency Gap B (D - R)'),
        color=alt.Color('national_winner:N',
                       scale=alt.Scale(domain=['democrat', 'republican'],
                                     range=['blue', 'darkred']),
                       legend=alt.Legend(title='National Winner')),
        tooltip=[
            alt.Tooltip('year:O', title='Year'),
            alt.Tooltip('national_winner:N', title='Winner'),
            alt.Tooltip('total_votes:Q', title='Total Votes Cast', format=','),
            alt.Tooltip('total_wasted:Q', title='Total Wasted Votes', format=','),
            alt.Tooltip('efficiency_gap_b_democrat:Q', title='Efficiency Gap B (D - R)', format='.3f')
        ]
    ).properties(
        width=600,
        height=400,
        title='Efficiency Gap B by Year (1976-2024)'
    ).configure_axis(
        grid=True,
        gridOpacity=0.3
    )

    _chart
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    We see that the winning party usually wastes a small fraction of their votes, again with the exception of 2000 and 2004.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## **V3**: Wasted Vote Value
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    The above Efficiency Gap is more-or-less a standard measure, but I do not find it very interesting. Perhaps it's more applicable to gerrymandering.

    My first problem with it is that it does not feel useful or interesting treat *some* of the winning votes as wasted while others are not.

    By the standard definition of waste, $R_W(s) - R_L(s)$ of the winning party's votes in a state $s$ are "wasted", while $R_L(s)$ are "counted". The $R_L(s)$ votes for the losing party are "wasted" was well, for a total waste of $R_W(s)$. Efficiency Gap just measures how these fall out along party lines. T

    Then, along the lines of our earlier WTAV value, the "total" value of the non-wasted votes in the national election is $\frac{e_s}{E}N$.

    Without some notion of the "ordering" of the votes, we can't say *which* are wasted. So we might as well say every one of the $R_W(s)$ votes for the winning party is worth a fraction $\frac{1}{R_W(s)}$ of thetotal value. That is: all of the $R_W(s)$ votes for the winning party are worth $\frac{n_s/2}{R_W(s)} \cdot 2 \cdot \frac{e_s / E}{n_s / N} = \frac{e_s / E}{R_W(s) / N}$ each.

    The weights are already normalized: in each state the sum over the winning party comes to $\frac{e_s}{E}N$, which sums to $N$ over all states.

    This gives us our value-of-a-vote function **Wasted Vote Value** (WVV):

    $$
    \begin{align}
    \text{WVV}(x) = \begin{cases}
    \frac{e_{s(x)} / E}{R_{v(x)}(s(x)) /N} && v(x) = v(s(x)) \\
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

    data_with_wv['wvv_winner'] = (data_with_wv['electors'] * data_with_wv['national_votes_total']) / (data_with_wv['national_electors'] * data_with_wv['winning_party_votes'])

    data_with_wv['wvv_democrat'] = data_with_wv.apply(lambda row: row['wvv_winner'] if row['winning_party'] == 'democrat' else 0, axis=1)
    data_with_wv['wvv_republican'] = data_with_wv.apply(lambda row: row['wvv_winner'] if row['winning_party'] == 'republican' else 0, axis=1)

    viz.viz_value_by_state(data_with_wv, "wvv_winner", "Winning Party's Wasted Votes Value", year_dropdown.value)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    The above resembles apportionment value, but of course only applies to the winners, and varies depending on the margin of victory within a state.

    (But note that margins of victory are, again, *ex post*, and depend on turnout which in turn is causally downstream of forecasts of the margin of victory—votes likely to be wasted tend not to be cast at all!)

    We can compare WVV to AV just to see how well they track against each other, expecting margins of victory to be approximately proportional to populations. We get:
    """)
    return


@app.cell(hide_code=True)
def _(data_with_wv, year_dropdown):
    data_with_wv['apportionment_value'] = data_with_wv['elector_pct'] / data_with_wv['apportionment_population_pct']

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
    ## **M3**: WVV Inequality

    TODO: compute MAD/Var/H?

    How do we determine this for a general election? Do we still count half the votes as wasted? Do we count half the *electoral* votes as wasted, then? Huh?
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## **V3b**: Wasted Vote Value, Nationally

    The electoral college wastes half the *electoral* votes, and these likely aren't uniformly distributed.

    So we can calculate a measure of the overall election by tallying up:
    - for each state in the losing party, all votes are wasted
    - for the winning party, the full "value" of the election $N$ is divided up among the $E_W$ votes for the winning party. Each electoral vote has value $\frac{N}{E_W}$, so state $s$ is worth $\frac{e_s}{E_W}N$ and the votes in that state are worth

    $$
    \text{WVV}_b(x) = \begin{cases}
      \frac{N}{E_W} \frac{e_{s(x)}}{R_W(s(x))} && v(x) = v(s(x)) = W\\
      0 && \text{otherwise}
    \end{cases}
    $$

    where the populations $N, n_s$ are both VP.

    ## **M3b** Relative Waste

    A fully general election would waste $\frac{N}{2}$ of the nation's votes.

    A WTA electoral college wastes half the votes in each state.

    The electoral college vote wasted $\frac{N}{E_W}$ of each of the winning party's electors.

    How many votes are wasted nationally?

    No point in calculating how many are wasted by-party, since all of one party's votes are wasted.
    """)
    return


@app.cell(hide_code=True)
def _(data_with_wv):
    data_with_wv['wasted_democrat_b'] = data_with_wv['votes_democrat'].where(
        ~((data_with_wv['national_winning_party'] == 'democrat') & (data_with_wv['winning_party'] == 'democrat')),
        other=0
    )
    data_with_wv['wasted_republican_b'] = data_with_wv['votes_republican'].where(
        ~((data_with_wv['national_winning_party'] == 'republican') & (data_with_wv['winning_party'] == 'republican')),
        other=0
    )

    def calc_wvvb(row):
        # Returns [wvvb_winner, wvvb_democrat, wvvb_republican]
        d, r, w = 'democrat', 'republican', None
        if row['national_winning_party'] == d and row['winning_party'] == d:
            w = d
        elif row['national_winning_party'] == r and row['winning_party'] == r:
            w = r
        else:
            return (0, 0, 0)

        wvvb = (
            (row['national_votes_total'] / row[f'national_electors_{w}']) 
            * (row['electors'] / row[f'votes_{w}'])
        )
        return (wvvb, wvvb if w == d else 0, wvvb if w == r else 0)


    data_with_wv[['wvvb_winner', 'wvvb_democrat', 'wvvb_republican']] = data_with_wv.apply(calc_wvvb, axis=1, result_type='expand')
    data_with_wv
    return


@app.cell(hide_code=True)
def _(data_with_wv):
    pct_wasted_by_year = 100 * (
        (data_with_wv['wasted_democrat'] + data_with_wv['wasted_republican']).groupby(data_with_wv['year']).sum()
        / data_with_wv['votes_total'].groupby(data_with_wv['year']).sum()
    )
    pct_wasted_b_by_year = 100 * (
        (data_with_wv['wasted_democrat_b'] + data_with_wv['wasted_republican_b']).groupby(data_with_wv['year']).sum()
        / data_with_wv['votes_total'].groupby(data_with_wv['year']).sum()
    )


    # Get national winning party by year
    national_winners = data_with_wv.groupby('year')['national_winning_party'].first()

    plot_data = pd.DataFrame({
        'year': pct_wasted_by_year.index,
        'pct_wasted': pct_wasted_by_year.values,
        'pct_wasted_b': pct_wasted_b_by_year.values,
        'national_winning_party': national_winners.values
    })

    # First bar plot: pct_wasted vs year
    _chart1 = alt.Chart(plot_data).mark_bar().encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('pct_wasted:Q', title='Percentage of Votes Wasted (%)', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('national_winning_party:N',
                       scale=alt.Scale(domain=['democrat', 'republican'],
                                     range=['blue', 'darkred']),
                       legend=alt.Legend(title='National Winner')),
        tooltip=[
            alt.Tooltip('year:O', title='Year'),
            alt.Tooltip('national_winning_party:N', title='National Winner'),
            alt.Tooltip('pct_wasted:Q', title='% Wasted', format='.1f')
        ]
    ).properties(
        width=300,
        height=300,
        title='Percentage of Votes Wasted by Year (w/o EC waste)'
    )

    # Second bar plot: pct_wasted_b vs year
    _chart2 = alt.Chart(plot_data).mark_bar().encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('pct_wasted_b:Q', title='Percentage of Votes Wasted B (%)', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('national_winning_party:N',
                       scale=alt.Scale(domain=['democrat', 'republican'],
                                     range=['blue', 'darkred']),
                       legend=alt.Legend(title='National Winner')),
        tooltip=[
            alt.Tooltip('year:O', title='Year'),
            alt.Tooltip('national_winning_party:N', title='National Winner'),
            alt.Tooltip('pct_wasted_b:Q', title='% Wasted B', format='.1f')
        ]
    ).properties(
        width=300,
        height=300,
        title='Percentage of Votes Wasted by Year (Incl. EC Waste)'
    )

    # Display both charts vertically
    alt.hconcat(_chart1, _chart2).resolve_scale(y='independent')
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Really, I'm surprised the new definition doesn't waste *more* votes.

    ... this can't be right, can it? The EC definition should strictly waste *more* votes. The original definition counted losing votes in all states, + winning votes in excess of margin. The new definition also counts as wasted the losing *states* and the national EC votes in excess of margin...
    - or does it? This might be messed up.
    """)
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
