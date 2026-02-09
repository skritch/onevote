import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")

with app.setup(hide_code=True):
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import altair


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
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Winner-Takes-All at L2
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    We observed above that AV and AVI make no use of the "winner-takes-all" assignment of state electors.

    Obviously this is, in some sense, less "fair" than an election where everyone's vote is counted directly: many voters are disincentivized from voting, candidates are disincentivized from paying attention to many of their voters, and campaigning (and likely the exchange of favors and promises for votes) is massively concentrated in a handful of contested "swing states", to an almost comical degree.

    In general we will need to know the party affiliations to determine the *actual* inequality of this arrangement in any given election.

    But it will be useful to try to characterize the inequality without party affiliations first, i.e. to come up with an L2 measure.

    Here are some properties our characterization should capture:
    - Clearly the grouping of voters into states or "districts" (which we will be our general term for such grouping operations) with WTA-within-districts is less fair than a general election (or than proportional repr. within districts).
    - Larger districts are less fair than small ones.
    - If a single district reaches an elector count equal to half of the national population, the value of all votes in the other districts should go to zero.
    - Districting should reduce fairness in a way which is distinct from AVI: however many electors your state has, assigning them by WTA ought to increase the inequality of the individual voters' votes.
    - Likewise, for a given set of district sizes, increasing AVI ought to increase inequality in general.
    - WTA is less fair than any reasonable "proportional" assignment of electors within a state.

    For clarity, let us record our other stipulation:
    - The inequality measure we use should not depend on *actual party affiliations*, for now. We will devise a separate measure using this information later.

    ---
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    What stands out about WTA districting is this: *for each state, only half of the votes + 1 ever affect the outcome of the national election*. Once the state has been won, the remaining votes (on both sides) count for nothing.

    Furthermore, the half which *does* affect the election will have double the effect they would otherwise halve in terms of electors; each individual effectively moves the elector count by 2 units of $\text{AV}(s)$ rather than 1.

    Later, when we bring party affiliation into the mix, we'll be able to determine *which* votes had no effect; for now we only know it was some half.

    So we'll consider a WTA state election to assign values to votes by a function **Winner-Takes-All Value** or $\text{WTAV}(x)$:
    - $\text{WTAV}(x) = 2 \cdot \text{AV}(x) = 2\cdot \frac{e_{s(x)}/E}{n_{s(x)}/N}$ for approximately $\frac{n_{s(x)}}{2}$ members of the state
    - $\text{WTAV}(x) = 0$ to the remaining $\frac{n_{s(x)}}{2}$ voters.

    We won't bother with the exact rounding of $\frac{n_{s(x)}}{2}$, and will ignore ties. For now, we won't think about which population $n_s$ is taken to measure; later we might want to use AP, VEP, or VP.

    Note that this value has the same mean as AV. But it will not have the same MAD, Var, etc.

    ----
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Wasted Votes at L2
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    We'll call the inequality measure derived from $\text{WTAV}$ by the name "Wasted Votes" or WV. This is specifically the waste due to "districting" (a general term for the grouping of an electorate into any kind of hierarchical structure.). Later we will look at WV *with* party affiliation, at the L3 level, perhaps giving this another name.


    What do these measures give for SW?

    **Mean absolute deviation (MAD)**:

    $$
    \begin{align}
    \text{WV}_{\text{MAD}} &= \frac{1}{N}\sum_x \vert\text{WTAV(x)} - 1 \vert \\
      &= \frac{1}{N}\sum_s \sum_{x \in s} \vert\text{WTAV(x)} - 1 \vert\\
      &= \frac{1}{N}\sum_s \left( \frac{n_s}{2}\vert 2\cdot \text{AV(s)} - 1\vert + \frac{n_s}{2}\vert -1\vert\right) \\
      &= \frac{1}{2} +\sum_s \frac{n_s}{N} \left\vert \text{AV(s)} - \frac{1}{2}\right\vert \\
    \end{align}
    $$

    If $\text{AV}(s) \ge \frac{1}{2}$ everywhere, the absolute value signs can be removed, and this expression comes reduces to $\frac{\sum n_s \text{AV}(s)}{N} = 1$. That's not very interesting.

    **RMS Deviation**:

    $$
    \begin{align}
    \text{WV}_{\text{Var}} &= {\frac{1}{N}\sum_x \left(\text{WTAV(x)} - 1 \right)^2} \\
      &= {\frac{1}{N}\sum_s \sum_{x \in s} {(\text{WTAV(x)} - 1 )}^2}\\
      &= {\frac{1}{N}\sum_s \left( \frac{n_s}{2}{(2 \cdot \text{AV(s)} - 1 )}^2 + \frac{n_s}{2}{(-1)}^2\right)}\\
      &= \sum_s \frac{n_s}{N}\left(2 \cdot (\text{AV(s)}) ^2 - 2 \text{AV(s)}  +1\right)\\
      &= \left(2\sum_s \frac{n_s}{N}\cdot (\text{AV(s)}) ^2 \right) - 1\\
    \end{align}
    $$

    If $\text{AV}(s) = 1$ this expression is exactly 1.

    It can also be written as $2 \text{E}[(\text{AV}(x))^2] - 2$.


    **Relative Entropy**:


    $$
    \begin{align}
    \text{WV}_{\text{Ent}} = H\left[\frac{\text{WTAV}(x)}{N} ~\big\Vert~ \frac{1}{N}\right] &= \sum_x \frac{\text{WTAV}(x)}{N} \log \frac{\text{WTAV}(x)/N}{1 / N} \\
      &= \frac{1}{N}\sum_x  \text{AV}(x) \cdot \log \text{AV}(x) \\
      &= \frac{1}{N}\sum_s \left( \frac{n_s}{2} \cdot 2 \cdot  \text{AV}(s) \cdot( \log 2 \cdot \text{AV}(s)) + \frac{n_s}{2} \cdot 0
      \right)\\
      &=\sum_s   \frac{n_s}{N} \cdot \text{AV}(s) \cdot \left(\log \text{AV}(s) + \log 2\right) \\
      &=  H\left[\frac{\text{AV}(x)}{N} ~\big\Vert~ \frac{1}{N}\right] + \log 2
    \end{align}
    $$

    Using WTAV simply adds $\log 2$ to the entropy over AV, and if the base of the log is 2 then this, too, adds exactly 1.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ---

    All of these expression give exactly 1 for uniform $\text{AV}(s) = 1$, i.e. for "perfectly proportional apportionment". So:" considering a WTA election automatically adds 1 to its MAD/Var/Entropy, but this is *completely insensitive to the size of the states*. As long as every voter is in *some* WTA district, their vote counts 0 half the time.

    Note that we are *not* considering the WTA nature of the national election. At the "top" level, every vote has an influence on the candidates, so we don't need to account for this.

    Still: these metrics aren't much use. These will be a handy baseline for when we consider wasted votes *with* parties, but to capture the effect of WTA elections in the states we need some other measure which distinguishes large states from small ones. Intuitively it should be "more fair" to divide a state up into districts than to consider it all as one block--there are more opportunity to have marginal effects on the outermost election. We'll turn our attention to this in the next analysis.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
 
    """)
    return


if __name__ == "__main__":
    app.run()
