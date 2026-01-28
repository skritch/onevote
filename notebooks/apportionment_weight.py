import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    return mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## **Apportionment Weight**

    We target L:2.1, apportionment alone.

    Let $s$ range over $S$ states, with AP $n_s$ and electors $e_s$, with total AP called $N = \sum_s n_s$ and total electors $E = \sum_s e_s$.

    Let $x_s$ be the value of the vote of each voter in state $s$, with $p_s = \frac{x_s}{N}$ as above.


    We will attempt to devise a measure which is a function of the population and elector accounts *alone*, i.e. ignoring all dynamical effects of the election system on turnout, candidates, etc.

    Recall again we have two separate questions to answer: Q1 (value of any given vote) and Q2 (overall fairness).

    Suppose we consider just the subproblem of the election being held "by the states", with each getting votes = $e_s$. Call the variables in this case $y_s, q_s$. Obviously in this election we ought to have $e_s$ be the value of each state's vote,

    $$
    \begin{align}
    y_s = e_s && && && q_s = \frac{e_s}{\sum_s e_s} \equiv \frac{e_s}{E}
    \end{align}
    $$

    Now, for an individual of state $s$, we can either the define the value of their vote $x_s$ such that the "total number of votes" is either $E$ or that it's $N$. That is,

    $$
    \begin{align}
    \sum_s n_s x_s \stackrel{?}{=} E && && && \sum_s n_s x_s \stackrel{?}{=} N
    \end{align}
    $$

    These give:

    $$
    \begin{align}
    x_s \stackrel{?}{=} \frac{e_s}{n_s}  && && && x_s \stackrel{?}{=} \frac{e_s / E}{n_s / N} = \frac{e_s}{n_s}\cdot \frac{N}{E} = \frac{N/E}{n_s / e_s}
    \end{align}
    $$

    The two differ by a constant factor, and won't affect *relative* values of votes. Which to choose?

    - Suppose every state is awarded electors $e_s$ = $n_s$. Then $E = N$ and both definitions give $x_s = 1$.
    - Suppose every state has population $n_s = 1$. Then the left definition gives $x_s = e_s$, while the right definition becomes $\frac{e_s}{E}{S}$, with $S$ the number of states, because the total number of "votes" in this case is $N = S$ and we fixed $\sum_s n_s x_s = N$.
    - What are the average values $x_s$ across voters in either case? Obviously $\frac{E}{N}$ and $1$.

    Well, I can see arguments for both, but I prefer the RHS definition because $\sum_s n_s x_s = N$ makes sense to me. So we'll go with that:

    $$
    x_s \stackrel{?}{=} \frac{e_s / E}{n_s / N} = \frac{e_s}{n_s}\cdot \frac{N}{E} = \frac{N/E}{n_s / e_s}
    $$

    The third epxression is perhaps the clearest: this measures the ratio between "national population per elector" $N/E$ and "state population per elector" $n_s / e_s$.


    Let's now compare the values of votes of different states according to this criteria using the idealized scenario A1.
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

    data.head()
    return (data,)


@app.cell
def _(data, plt):
    # Filter for 2024 election

    year = 2020
    pop_var = 'ap'

    pop_col = {
        'ap': 'state_population',
        'vap': 'state_vap_estimate',
        'vep': 'state_vep_estimate',
        'vp': 'votes_total'
    }[pop_var]

    data_1yr = data[data['year'] == year].copy()

    # Calculate value of a voter's vote: (electors / votes) normalized by (total_electors / total_votes)
    # This is x_s = (e_s / n_s) * (N / E) from the formula above
    total_electors = data_1yr['state_electors'].sum()
    total_votes = data_1yr[pop_col].sum()

    data_1yr['voter_value'] = (data_1yr['state_electors'] / data_1yr[pop_col]) * (total_votes / total_electors)

    # Sort alphabetically by state name
    data_1yr_sorted = data_1yr.sort_values('state')

    # Create bar plot
    _fig, _ax = plt.subplots(figsize=(20, 6))
    _ax.bar(data_1yr_sorted['state_po'], data_1yr_sorted['voter_value'])
    _ax.axhline(y=1.0, color='red', linestyle='--', linewidth=1, label='Average voter value')
    _ax.set_ylabel('Value of each Vote (relative to national average)')
    _ax.set_xlabel('State')
    _ax.set_title('Value of each Vote by State - 2024 Presidential Election\n(Scenario A1: Winner-Take-All)')
    _ax.legend()
    _ax.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=90)
    plt.tight_layout()
    _ax
    return (data_1yr_sorted,)


@app.cell
def _(data_1yr_sorted, np, plt):
    # visualization: a histogram of "population vs value of vote"
    # x-axis = "value of vote" from min to max, 0.8 to 3.2ish (but axis should go down to 0)
    # y = bar, height = population with that (binned value)
    # 2 bars for each bin, darkred=republican, blue=democrat, drop "other"

    # Filter out states won by "other" parties (if any)
    data_party = data_1yr_sorted[data_1yr_sorted['winning_party'].isin(['democrat', 'republican'])].copy()

    # Separate by winning party
    data_dem = data_party[data_party['winning_party'] == 'democrat']
    data_rep = data_party[data_party['winning_party'] == 'republican']

    # Create bins for voter value
    bins = np.arange(0, 4, 0.1)
    bin_width = bins[1] - bins[0]

    # Calculate histogram values manually for side-by-side bars
    dem_hist, _ = np.histogram(data_dem['voter_value'], bins=bins, weights=data_dem['state_population'])
    rep_hist, _ = np.histogram(data_rep['voter_value'], bins=bins, weights=data_rep['state_population'])

    # Create histogram
    _fig, _ax = plt.subplots(figsize=(12, 6))

    # Plot bars side-by-side
    bin_centers = (bins[:-1] + bins[1:]) / 2
    _ax.bar(bin_centers - bin_width/4, dem_hist, width=bin_width/2.2,
            label='Democrat', color='blue', edgecolor='black', alpha=0.7)
    _ax.bar(bin_centers + bin_width/4, rep_hist, width=bin_width/2.2,
            label='Republican', color='darkred', edgecolor='black', alpha=0.7)

    _ax.axvline(x=1.0, color='black', linestyle='--', linewidth=1, label='Average voter value')
    _ax.set_xlabel('Value of a Voter\'s Vote (relative to national average)')
    _ax.set_ylabel('Population')
    _ax.set_title('Population Distribution by Voter Value and Winning Party - 2024 Presidential Election\n(Scenario A1: Winner-Take-All)')
    _ax.legend()
    _ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    _ax
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
