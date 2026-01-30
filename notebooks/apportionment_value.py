import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import altair


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # V1: Apportionment Value
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    We target L2.1, apportionment. We will limit our attention to the presidential election.

    We will attempt to devise a measure which is a function of the population and elector accounts *alone*, i.e. ignoring all dynamical effects of the election system on turnout, candidates, etc.

    Imagine first a simple election between two candidates where voter $x$ has some weight $w_x$. Obviously, in this case, the most natural "value of a vote" is exactly its weight

    $$
    V(x) = w_x
    $$

    In our two-tiered electoral-college system, it is as if the states were each casting votes with weights $e_s$ in a single election. In that election the value of the states' votes is:

    $$
    V_{\text{states}}(s) = e_s
    $$

    Now, what value should we assign to the voters *in* the state, if the state assigns all of its electors to its winner?

    The simplest thing to do is to simply divide the state's electors among its population $n_s$:

    $$
    V(x) \stackrel{?}{=} \frac{e_{s(x)}}{n_{s(x)}}
    $$

    (Here $n_{s(x)}$ is probably best taken to be the "apportionment population" AP, i.e. the population which was used to determine the elector count $e_s$ in the first place.)

    It will be more natural to scale this definition so that the sum of all voters across all states is $N$, and the mean "value of a vote" is $1$. (This will allow us to compare this voting system to others which do not involve the arbitrary total elector count $E = \sum_s e_s$.) The sum of the above over all voters is

    $$
    \begin{align}
    \sum_x V(x) &= \sum_x \frac{e_{s(x)}}{n_{s(x)}}\\
      &= \sum_{s \in S} \sum_{x\in s} \frac{e_{s}}{n_{s}} \\
      &= \sum_{s \in S} \frac{e_{s}}{n_{s}} \cdot n_s\\
      &= \sum_{s \in S} e_s \\
      &= E
    \end{align}
    $$

    (For brevity we use the state $s \in S$ both as a set of voters $x \in s$ and as a function giving the state to which a given voter belongs $s(x)$.)

    Therefore we should scale the above by $\frac{N}{E}$ such that $\sum_{x} V(x) = N$:

    $$
    \begin{align}
    V(x) &= \frac{e_{s(x)}}{n_{s(x)}} \cdot \frac{N}{E}
    \end{align}
    $$

    This will be our first definition of a value-of-a-vote, which we will call the **Apportionment Value** or AV:

    $$
    \text{AV}(x) \equiv \frac{e_{s(x)}}{n_{s(x)}} \cdot \frac{N}{E}
    $$

    ---
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    We can express the Apportionment Value in three ways:

    $$
    \begin{align}
    \text{AV(x)} &\equiv \frac{e_{s(x)}}{n_{s(x)}} \cdot \frac{N}{E}  \\
     &= \frac{e_{s(x)} / E}{n_{s(x)} / N} \\
     &= \frac{e_{s(x)} / n_{s(x)}}{E / N}
    \end{align}
    $$

    The second expression expresses this value-of-a-vote as a ratio between this state's "fraction of the electoral college" and its "fraction of the total population".

    The third expression expresses it as a ratio between the "electors per capita" and the national mean "electors per capita".

    It will also be useful to sometimes write this as a function of state itself.

    $$
    \text{AV}(s) = \frac{e_s / E}{n_s / N}
    $$

    The above expression represents the value of each vote *in* state $s$, rather than the total value in the state (which would be $n_s \cdot \text{AV}(s) = \frac{e_s}{E}N$). With this notation we have $\text{AV}(x) = \text{AV}(s(x))$ (but this relationship won't hold for all value functions).

    Note that AV does not depend at all on the "winner take all" nature of state elections. It measures **only** the proportionality of electors-to-population.

    AV would assign a value of $\text{AV(x)} = 1$ to every single voter if electors were assigned to states in perfect proportion to their population. This would hold whether those electors' votes were given to candidates in a "winner take all" fashion, as they are in almost all states at present, or if they were assigned in proportion to the popular vote in the state.

    Of course, without "fractional" electors, there's generally no way to assign electors $e_s \propto n_s$ unless $E = N$. We therefore expect some rounding errors, at a minimum.

    But the U.S. assignment of electors is quite a bit less proportional than that. Every state receives 3 electors at a minimum, regardless of its population, corresponding to its two Senators and its minimum of 1 representative in the House. (D.C. receives 3 electors by the 23rd Amendment instead.)
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Visualizing AV

    The apportionment values of the states are as follows:
    """)
    return


@app.cell(hide_code=True)
def _():
    # This dataset is prepared in https://github.com/skritch/election-datasets and uploaded to Kaggle for general use.

    import kagglehub
    from kagglehub import KaggleDatasetAdapter

    # Load the latest version
    data = kagglehub.dataset_load(
      KaggleDatasetAdapter.PANDAS,
      "samkritch/u-s-presidential-elections-by-state-1976-2024",
      'presidential_elections_1976_2024.csv',
    )

    # data.head()
    return (data,)


@app.cell(hide_code=True)
def _(data):
    # Add apportionment_value column to entire dataframe
    # For each year, AV = (state_electors / state_population) * (national_population / national_electors)

    data_with_av = data.copy()

    # Calculate national totals by year
    national_totals = data_with_av.groupby('year').agg({
        'state_electors': 'sum',
        'state_population': 'sum'
    }).rename(columns={
        'state_electors': 'national_electors',
        'state_population': 'national_population'
    })

    # Merge national totals back to dataframe
    data_with_av = data_with_av.merge(national_totals, left_on='year', right_index=True)

    # Calculate apportionment value
    data_with_av['apportionment_value'] = (
        (data_with_av['state_electors'] / data_with_av['state_population']) *
        (data_with_av['national_population'] / data_with_av['national_electors'])
    )

    data_with_av.head(2)
    return (data_with_av,)


@app.cell(hide_code=True)
def _(data_with_av):

    year_dropdown = mo.ui.dropdown.from_series(data_with_av.year, value=2024, label="Choose a year: ")
    year_dropdown
    return (year_dropdown,)


@app.cell(hide_code=True)
def _(data_with_av, year_dropdown):
    # Filter for selected year and sort alphabetically by state name
    data_1yr_sorted = data_with_av[data_with_av['year'] == year_dropdown.value].sort_values('state').copy()

    # Create bar plot with Altair
    bars = altair.Chart(data_1yr_sorted).mark_bar().encode(
        x=altair.X('state_po:N', title='State', sort=None),
        y=altair.Y('apportionment_value:Q', title='Apportionment Value'),
        color=altair.Color('winning_party:N',
                          scale=altair.Scale(domain=['democrat', 'republican'],
                                           range=['blue', 'darkred']),
                          legend=altair.Legend(title='Winner')),
        tooltip=[
            altair.Tooltip('state:N', title='State'),
            altair.Tooltip('winning_party:N', title='Winner'),
            altair.Tooltip('state_population:Q', title='Population', format=','),
            altair.Tooltip('state_electors:Q', title='Electors'),
            altair.Tooltip('votes_total:Q', title='Total Votes', format=','),
            altair.Tooltip('apportionment_value:Q', title='Apportionment Value', format='.3f')
        ]
    )

    rule = altair.Chart(altair.Data(values=[{'y': 1.0}])).mark_rule(
        color='black',
        strokeDash=[5, 5]
    ).encode(
        y='y:Q'
    )

    chart = (bars + rule).properties(
        width=900,
        height=400,
        title='Value of each Vote by State - 2024 Presidential Election\n(Scenario A1: Winner-Take-All)'
    ).configure_axis(
        grid=True,
        gridOpacity=0.3
    )

    chart
    return (data_1yr_sorted,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Obviously, voters in the smallest states (AK, ME, MT, ND, RI, VT, and WY, as well as DC) have much larger apportionment values than the larger states. These should make up a comparatively small portion of the total, though. To see how much less, we'll look at a histogram of voters-by-AV.
    """)
    return


@app.cell(hide_code=True)
def _(data_1yr_sorted):

    # Create bins for apportionment value (0.1 unit bins from 0 to 4)
    bins = [i * 0.1 for i in range(41)]  # 0.0, 0.1, 0.2, ..., 4.0
    data_binned = data_1yr_sorted.copy()
    data_binned['av_bin'] = pd.cut(data_binned['apportionment_value'], bins=bins, include_lowest=True)

    # Get bin centers for plotting
    data_binned['av_bin_center'] = data_binned['av_bin'].apply(lambda x: (x.left + x.right) / 2)

    # Create long-form data with separate rows for democrat and republican votes
    histogram_data_list = []
    for _, row in data_binned.iterrows():
        histogram_data_list.append({
            'av_bin_center': row['av_bin_center'],
            'party': 'democrat',
            'votes': row['votes_democrat']
        })
        histogram_data_list.append({
            'av_bin_center': row['av_bin_center'],
            'party': 'republican',
            'votes': row['votes_republican']
        })

    histogram_data_long = pd.DataFrame(histogram_data_list)

    # Group by bin and party, sum votes
    histogram_data = histogram_data_long.groupby(['av_bin_center', 'party'], as_index=False)['votes'].sum()

    # Create stacked bar chart
    histogram = altair.Chart(histogram_data).mark_bar(width=20).encode(
        x=altair.X('av_bin_center:Q',
                   title='Apportionment Value',
                   scale=altair.Scale(domain=[0, 4])),
        y=altair.Y('votes:Q',
                   title='Total Votes',
                   stack=True),
        color=altair.Color('party:N',
                          scale=altair.Scale(domain=['democrat', 'republican'],
                                           range=['blue', 'darkred']),
                          legend=altair.Legend(title='Party')),
        tooltip=[
            altair.Tooltip('av_bin_center:Q', title='Apportionment Value', format='.2f'),
            altair.Tooltip('party:N', title='Party'),
            altair.Tooltip('votes:Q', title='Votes', format=',')
        ]
    ).properties(
        width=900,
        height=400,
        title='Vote Distribution by Apportionment Value and Party - 2024 Presidential Election'
    )

    histogram
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Evidently, and unsurprisingly, the vast majority of votes belong to the states with AVs right around 1.0.

    At this point I'm curious how well our AVs actually predict the election. Suppose we conducted a general popular vote, but with every vote weighted according to its AV. How well would this agree with the actual electoral college results each year?

    The following graph compares the percent of electors which went to the party shown to the percent of AV-weighted votes which went to the same party, for all years in our dataset.
    """)
    return


@app.cell
def _(data_with_av):
    party_dropdown = mo.ui.dropdown.from_series(data_with_av.winning_party, value='democrat', label="Choose a party: ")
    party_dropdown
    return (party_dropdown,)


@app.cell(hide_code=True)
def _(data_with_av, party_dropdown):
    # Calculate party statistics by year
    selected_party = party_dropdown.value

    # For each year, calculate:
    # - Total EC for selected party / Total EC
    # - Total AV-weighted votes for selected party / Total AV-weighted votes
    # - Total popular votes for selected party / Total popular votes
    # - Number of states won

    party_stats_list = []

    for year in data_with_av['year'].unique():
        year_data = data_with_av[data_with_av['year'] == year].copy()

        # Total metrics
        total_ec = year_data['state_electors'].sum()
        total_votes = year_data['votes_total'].sum()

        # Party metrics - use actual vote columns
        votes_col = f'votes_{selected_party}'
        electors_col = f'electors_{selected_party}'

        party_votes = year_data[votes_col].sum()
        party_ec = year_data[electors_col].sum()

        # States won by party
        party_data = year_data[year_data['winning_party'] == selected_party]
        states_won = len(party_data)

        # AV-weighted votes for party (across all states, not just won states)
        party_av_weighted_votes = (year_data['apportionment_value'] * year_data[votes_col]).sum()

        # Total AV-weighted votes
        total_av_weighted_votes = (year_data['apportionment_value'] * year_data['votes_total']).sum()

        # Determine national winner (party with most EC)
        national_winner = year_data.groupby('winning_party')['state_electors'].sum().idxmax()

        party_stats_list.append({
            'year': year,
            'ec_pct': party_ec / total_ec * 100,
            'av_pct': party_av_weighted_votes / total_av_weighted_votes * 100,
            'popular_vote_pct': party_votes / total_votes * 100,
            'states_won': states_won,
            'party_ec': party_ec,
            'total_ec': total_ec,
            'national_winner': national_winner
        })

    party_stats = pd.DataFrame(party_stats_list)

    # Create scatter plot
    _scatter = altair.Chart(party_stats).mark_circle(size=100).encode(
        x=altair.X('av_pct:Q',
                   title='AV-Weighted Vote % for Party',
                   scale=altair.Scale(domain=[0, 100])),
        y=altair.Y('ec_pct:Q',
                   title='Electoral College % for Party',
                   scale=altair.Scale(domain=[0, 100])),
        color=altair.Color('national_winner:N',
                          scale=altair.Scale(domain=['democrat', 'republican'],
                                           range=['blue', 'darkred']),
                          legend=altair.Legend(title='National Winner')),
        tooltip=[
            altair.Tooltip('year:O', title='Year'),
            altair.Tooltip('national_winner:N', title='Winner'),
            altair.Tooltip('ec_pct:Q', title='EC %', format='.1f'),
            altair.Tooltip('av_pct:Q', title='AV %', format='.1f'),
            altair.Tooltip('popular_vote_pct:Q', title='Popular Vote %', format='.1f'),
            altair.Tooltip('states_won:Q', title='States Won'),
            altair.Tooltip('party_ec:Q', title='Party EC'),
            altair.Tooltip('total_ec:Q', title='Total EC')
        ]
    )

    # Add diagonal reference line (y = x)
    _diagonal = altair.Chart(pd.DataFrame({'x': [0, 100], 'y': [0, 100]})).mark_line(
        color='gray',
        strokeDash=[5, 5]
    ).encode(
        x='x:Q',
        y='y:Q'
    )

    _chart_av = (_scatter + _diagonal).properties(
        width=300,
        height=300,
        title=f'EC % vs AV-Weighted Vote %'
    )

    # Create second scatter plot for Popular Vote vs AV
    _scatter_pv = altair.Chart(party_stats).mark_circle(size=100).encode(
        x=altair.X('av_pct:Q',
                   title='AV-Weighted Vote % for Party',
                   scale=altair.Scale(domain=[0, 100])),
        y=altair.Y('popular_vote_pct:Q',
                   title='Popular Vote % for Party',
                   scale=altair.Scale(domain=[0, 100])),
        color=altair.Color('national_winner:N',
                          scale=altair.Scale(domain=['democrat', 'republican'],
                                           range=['blue', 'darkred']),
                          legend=altair.Legend(title='National Winner')),
        tooltip=[
            altair.Tooltip('year:O', title='Year'),
            altair.Tooltip('national_winner:N', title='Winner'),
            altair.Tooltip('ec_pct:Q', title='EC %', format='.1f'),
            altair.Tooltip('popular_vote_pct:Q', title='Popular Vote %', format='.1f'),
            altair.Tooltip('av_pct:Q', title='AV %', format='.1f'),
            altair.Tooltip('states_won:Q', title='States Won'),
            altair.Tooltip('party_ec:Q', title='Party EC'),
            altair.Tooltip('total_ec:Q', title='Total EC')
        ]
    )

    _chart_pv = (_scatter_pv + _diagonal).properties(
        width=300,
        height=300,
        title=f'Popular Vote % vs AV-Weighted Vote %'
    )

    # Combine charts side by side
    _combined_chart = (_chart_av | _chart_pv).properties(
        title=f'{selected_party.title()}s (1976-2024)'
    )

    _combined_chart
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Well: it turns out that no, AVs are not much good as predictors of the actual EC outcome. What correlation we do see in the left plot is surely just due to the AV % tracking the popular % closely, as shown in the right plot.

    Apparently AVs are close enough to 1 on average that they don't tell us much about the results of elections. This isn't too surprising.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # **M1**: Apportionment Inequality
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    We will now try to come up with a reasonable measure of the "overall" inequality of the value of voters' votes, according to AV. The obvious thing to characterize is the deviation of AV from a uniform distribution $V(x) = \frac{1}{N}$. We'll therefore call these measures "Apportionment Value Inequality" or "AVI".

    For now we'll compute three measures of AVI. I'll write these as taking "P2" as an argument, meaning these are the definitions of these metrics for presidential election scenario 2 (a simple electoral college).

    **M1.1** Mean absolute deviation (MAD):

    $$
    \begin{align}
    \text{AVI}_{\text{MAD}}[\text{P2}] &= \frac{1}{N}\sum_x \vert\text{AV(x)} - 1 \vert \\
      &= \frac{1}{N}\sum_s \sum_{x \in s} \vert\text{AV(x)} - 1 \vert \\
      &= \frac{1}{N}\sum_s n_s \vert\text{AV(s)} - 1 \vert \\
      &= \sum_s \left\vert \frac{e_s}{E} - \frac{n_s}{N} \right\vert
    \end{align}
    $$

    **M1.2** Variance:

    $$
    \begin{align}
    \text{AVI}_{\text{Var}}[\text{P2}]  &= {\frac{1}{N}\sum_x \left(\text{AV(x)} - 1 \right)^2} \\
      &= {\frac{1}{N}\sum_s \sum_{x \in s} \left(\text{AV(x)} - 1 \right)^2} \\
      &= {\sum_s \frac{n_s}{N} \left(\text{AV(s)} - 1 \right)^2} \\
      &=-1 +  {\sum_s \frac{n_s}{N} \left(\text{AV(s)}\right)^2} \\
    \end{align}
    $$

    (Actually that expression is just $\text{E}[\text{AV}(X)^2] - \text{E}[\text{AV}(X)]^2$. Not surprising.)

    **M1.3** Relative Entropy with respect to a popular election:


    $$
    \begin{align}
    \text{AVI}_{\text{Ent}}[\text{P2}]  = H\left[\frac{\text{AV}(x)}{N} ~\Vert~ \frac{1}{N}\right] &= \sum_x \frac{\text{AV}(x)}{N} \log \frac{\text{AV}(x)/N}{1 / N} \\
      &= \frac{1}{N}\sum_x  \text{AV}(x) \cdot \log \text{AV}(x) \\
      &= \frac{1}{N}\sum_s n_s \cdot \text{AV}(s) \cdot \log \text{AV}(s)
    \end{align}
    $$

    For each of these, 0 represents perfect equality, and is attained when $\text{AV}(x) = 1$ uniformly.
    """)
    return


@app.cell(hide_code=True)
def _(data_with_av):
    # Compute the three inequality measures for each year
    inequality_stats = []

    for _year in sorted(data_with_av['year'].unique()):
        _year_data = data_with_av[data_with_av['year'] == _year].copy()

        # For each voter (approximated by vote), calculate the AV
        # We'll weight by state_population to get the voter-level statistics
        _av_values = _year_data['apportionment_value'].values
        _pop = _year_data['state_population'].values
        _N = _pop.sum()

        # 1. Mean Absolute Deviation: (1/N) * sum(|AV(x) - 1|)
        # For each state, we have votes[i] voters with AV = av_values[i]
        _mad = sum(abs(_av_values[i] - 1) * _pop[i] for i in range(len(_av_values))) / _N

        # 2. RMS Deviation: sqrt((1/N) * sum((AV(x) - 1)^2))
        _var = (sum((_av_values[i] - 1)**2 * _pop[i] for i in range(len(_av_values))) / _N)

        # 3. Relative Entropy: (1/N) sum_s n_s AV(s) log (AV(s))
        _r = 0
        for s in range(len(_av_values)):
            _r += _pop[s] * _av_values[s] * np.log(_av_values[s])
        _relative_entropy = _r / _N



        # Determine national winner
        _national_winner = _year_data.groupby('winning_party')['state_electors'].sum().idxmax()

        inequality_stats.append({
            'year': _year,
            'MAD': _mad,
            'Var': _var,
            'Relative_Entropy': _relative_entropy,
            'winning_party': _national_winner
        })

    inequality_df = pd.DataFrame(inequality_stats)

    # Create four side-by-side bar charts
    _metrics = [
        ('MAD', 'Mean Absolute Deviation'),
        ('Var', 'Variance'),
        ('Relative_Entropy', 'Relative Entropy')
    ]

    _charts = []
    for _col, _title in _metrics:
        _chart = altair.Chart(inequality_df).mark_bar().encode(
            x=altair.X('year:O', title='Year'),
            y=altair.Y(f'{_col}:Q', title=_title),
            color=altair.Color('winning_party:N',
                              scale=altair.Scale(domain=['democrat', 'republican'],
                                               range=['blue', 'darkred']),
                              legend=altair.Legend(title='Winner')),
            tooltip=[
                altair.Tooltip('year:O', title='Year'),
                altair.Tooltip('winning_party:N', title='Winner'),
                altair.Tooltip(f'{_col}:Q', title=_title, format='.4f')
            ]
        ).properties(
            width=200,
            height=300,
            title=_title
        )
        _charts.append(_chart)

    # Combine charts side by side
    _combined = _charts[0]
    for _chart in _charts[1:]:
        _combined = _combined | _chart

    _combined
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ... they all look pretty similar.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Further Thoughts on AVI
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    These numbers aren't very meaningful on their own, but we'll use them later when we want to compare different approachs to the *same* election, for example, if we switch to proportional assignments of electors, or remove non-citizens from AP before assigning electors.

    Recording a few thoughts on these measures:

    What "population" variable should we use?
    - The obvious guess is "apportionment population", but not everyone counted in AP can vote
      - This suggests we might use VEP or VP
    - If we want to gauge the effect of AV in an actual election, it would seem we should use VP, but VP is downstream of actual turnout, which we expect to be affected by incentivize to vote under apportionment.
      - Therefore VEP is probably best
    - But then do we use VEP in the definition of AV, or only in the definition of App. Inequality?, i.e. in the means?
      - Probably the latter, but still use AP in AV itself
      - It might be interesting, separately, to compute AV in terms of VEP or VP



    We could also try to characterize the EC distribution $\frac{e_s}{E}$ relative to the state population distribution $\frac{n_s}{N}$.

    An obvious one is relative entropy:

    $$
    \begin{align}
    H\left[ \frac{e_s}{E} ~\Vert \frac{n_s}{N} \right] &= \sum_s \frac{e_s}{E} \log \frac{e_s / E}{n_s / N} \\
     &= \sum_s \frac{n_s}{N}\cdot \frac{e_s / E}{n_s / N} \log \frac{e_s / E}{n_s / N}  \\
     &= \frac{1}{N} \sum_s n_s \cdot \text{AV}(s) \log \text{AV}(s)\\
     &= H\left[\frac{\text{AV}(X)}{N} ~\Vert~ \frac{1}{N}\right]
    \end{align}
    $$

    ... but interestingly, this is the same as the relative entropy on the population level of $\text{AV}[x]/N$ relative to $\frac{1}{N}$.


    Other questions:
    - Is it worth considering relative entropy going the other way, $H[1/N ~\Vert~ \text{AV}/N]$? AI tells me this is called a "Theil index" of inequality, but I can't see the sense in it.
    - Worth considering RMS w.r.t. 0 instead of 1?

    TODO:
    - compare these measures between P1-P5
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
