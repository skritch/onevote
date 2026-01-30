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
    # **V2**: Electoral Winner-Takes-All
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


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Where to begin?


    Observe that $\text{AV}(s)$ can be thought of as a "mean scaled electoral votes $\frac{e_s}{E}N$ per voter in the state":

    $$
    \begin{align}
    \text{AV}(s) &= \left\langle\frac{e_{s(x)}}{E}N \right\rangle_{x \in s(x)} \\
    &= \frac{N}{E}\frac{\sum_{x\in s} \frac{e_{s(x)}}{n_{s(x)}}}{\sum_{x \in s} 1} = \frac{n_s\frac{e_s}{n_s}}{n_s}\frac{N}{E} \\
    &= \frac{e_s / E}{n_s / N}
    \end{align}
    $$


    Now, what stands out about WTA districting is this: *for each state, only half of the votes + 1 ever affect the outcome of the national election*. Once the state has been won, the remaining votes (on both sides) count for nothing.

    Furthermore, the half which *does* affect the election will have double the effect they would otherwise halve in terms of electors; each individual effectively moves the elector count by 2 units of $\text{AV}(s)$ rather than 1.

    Later, when we bring party affiliation into the mix, we'll be able to determine *which* votes had no effect; for now we only know it was some half.

    So we'll consider a WTA state election to assign values to votes by a function **Winner-Takes-All W** or $\text{WW}(x)$:
    - value $\text{WW}(x) = 2 \cdot \text{AV}(x) = 2\cdot \frac{e_{s(x)}/E}{n_{s(x)}/N}$ to $\approx \frac{n_{s(x)}}{2}$ members of the state
    - value $\text{WW}(x) = 0$ to the remaining $\approx \frac{n_{s(x)}}{2}$ voters.

    We won't bother with the exact rounding of $\frac{n_{s(x)}}{2}$, and will ignore ties. For now, we won't think about which population $n_s$ is taken to measure; later we might want to use AP, VEP, or VP.


    This assignment of values $V(x)$ will still have the same mean, $V(x) = \text{AV}(s(x)) = \left\langle\frac{e_{s(x)}}{E}N \right\rangle_{x \in s(x)}$.

    But the inequality metrics MAD, RMS, and relative entropy _will_ be affected.


    ----
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # **M2:** Wasted Votes (w/o parties)

    We'll call the inequality measure derived from $\text{EW}$ by the name "Wasted Votes" or WV. This is specifically the waste due to "districting" (a general term for the grouping of an electorate into any kind of hierarchical structure.). Later we will look at WV *with* party affiliation, at the L3 level, perhaps giving this another name.


    What do these measures give for SW?

    **M2.1** Mean absolute deviation (MAD):

    $$
    \begin{align}
    \text{MAD}[\text{EW}] &= \frac{1}{N}\sum_x \vert\text{EW(x)} - 1 \vert \\
      &= \frac{1}{N}\sum_s \sum_{x \in s} \vert\text{EW(x)} - 1 \vert\\
      &= \frac{1}{N}\sum_s \left( \frac{n_s}{2}\vert 2\cdot \text{AV(s)} - 1\vert + \frac{n_s}{2}\vert -1\vert\right) \\
      &= \frac{N}{2} +\frac{1}{N}\sum_s n_s \left\vert \text{AV(s)} - \frac{1}{2}\right\vert \\
    \end{align}
    $$

    Note This expression is always $\ge 1$, and gives 1 when $\text{AV}(s)$ is uniformly equal to $1$ (or $0$, but we don't care about that).

    **M2.2** RMS Deviation:

    $$
    \begin{align}
    \text{RMS}[\text{EW}] &= \sqrt{\frac{1}{N}\sum_x \left(\text{EW(x)} - 1 \right)^2} \\
      &= \sqrt{\frac{1}{N}\sum_s \sum_{x \in s} {(\text{EW(x)} - 1 )}^2}\\
      &= \sqrt{\frac{1}{N}\sum_s \left( \frac{n_s}{2}{(2 \cdot \text{AV(s)} - 1 )}^2 + \frac{n_s}{2}{(-1)}^2\right)}\\
      &= \sqrt{\frac{N}{2} + \frac{1}{N}\sum_s n_s \left(\text{AV(s)} - \frac{1}{4} \right)^2}
    \end{align}
    $$


    **M2.3** Relative Entropy:


    $$
    \begin{align}
    H\left[\frac{\text{EW}(X)}{N} ~\Vert~ \frac{1}{N}\right] &= \sum_x \frac{\text{EW}(x)}{N} \log \frac{\text{EW}(x)/N}{1 / N} \\
      &= \frac{1}{N}\sum_x  \text{AV}(x) \cdot \log \text{AV}(x) \\
      &= \frac{1}{N}\sum_s n_s \cdot \text{AV}(s) \cdot \log \text{AV}(s)
    \end{align}
    $$
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    TODO: all of these = 1 if AV is uniform... this means they really aren't doing what I want.

    That, also, is exactly what these give for a national general election. They might be capturing some inequality in the elector counts, but...


    TODO: half the votes are always "wasted" in a national election. Can we subtract this off any of the above?
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
