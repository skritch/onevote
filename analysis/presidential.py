import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    return mo, pd, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Presidential Election Dataset
    """)
    return


@app.cell
def _(pd):
    # Get Dataset
    # https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/42MVDX
    data = pd.read_csv(
        '.data/1976-2020-president.csv'
    )
    data.head(3)
    return (data,)


@app.cell
def _(data):
    # Clean Dataset

    party_mapping = {
        'democratic-farmer-labor': 'democrat',
    }

    # Add party colors
    party_colors = {'republican': 'darkred', 'democrat': 'blue', 'other': 'gray'}
    parties = sorted(list(party_colors.keys()))

    def get_party_group(party):
        if party in ('republican', 'democrat'):
            return party
        else:
            return party_mapping.get(party, 'other')

    data_with_parties = data
    data_with_parties.loc[:, 'party_group'] = data['party_simplified'].str.lower().apply(get_party_group)
    data_with_parties.loc[:, 'party_group_color'] = data['party_group'].map(lambda x: party_colors[x])
    data_with_parties.head(3)
    return data_with_parties, party_colors


@app.cell
def _(data_with_parties, party_colors, plt):
    # How many voted for each party?

    # TODO: join in number of nonvoters

    national_by_year = data_with_parties.pivot_table(
        index='year', 
        columns='party_group', 
        values='candidatevotes', 
        aggfunc='sum'
    ).rename_axis(columns='party')

    national_by_year.plot(
        kind='bar', 
        figsize=(16, 3),
        color=[party_colors[c] for c in national_by_year.columns])

    plt.title('popular votes by party by year');
    plt.show()
    return


@app.cell
def _(data_with_parties, party_colors, plt):
    # How many states went for each party?

    # Ignoring a couple small idiosyncracies like:
    # https://en.wikipedia.org/wiki/Nebraska%27s_2nd_congressional_district
    # Hack to get largest row in each group...

    states_by_year = (data_with_parties
        .sort_values('candidatevotes', ascending=False)
        .groupby(['year', 'state'])['party_group'].first()
        .reset_index())

    state_counts_by_year = (states_by_year
        .pivot_table(
             index='year',
             columns='party_group',
             values='state',
             aggfunc='count')
        .fillna(0))

    (state_counts_by_year
         .rename_axis(columns='party')
         .plot(
             kind='bar', 
             figsize=(16, 3), 
             color=[party_colors[c] for c in state_counts_by_year.columns],
             title='states won by year by party'
         )
    );
    plt.show()
    return (states_by_year,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Electoral College Data


    We'll need yearly electoral college vote counts, and we'll need to handle (or ignore) the two states that assign EC votes differently - let's ignore for now.

    I got electoral college counts off [wikipedia](https://en.wikipedia.org/wiki/United_States_Electoral_College), cleaned them up in [this google sheet](https://docs.google.com/spreadsheets/d/1W9iLyLYCgVF3O3Hmk4k8yAXwjJAOQGiOFhnb8D6cUjk/edit?usp=sharing), and copied them into a CSV.
    """)
    return


@app.cell
def _(pd):
    apportionment_data = pd.read_csv('.data/electoral_apportionment.csv')
    apportionment_by_year = apportionment_data.melt(
        id_vars='State', var_name='year', value_name='electors'
    )
    apportionment_by_year = apportionment_by_year.rename(columns={"State": "state"})
    apportionment_by_year['state'] = apportionment_by_year['state'].str.upper()
    apportionment_by_year['year'] = apportionment_by_year['year'].astype(int)
    apportionment_by_year.head(1)
    return (apportionment_by_year,)


@app.cell
def _(apportionment_by_year, states_by_year):
    state_electors = states_by_year.merge(apportionment_by_year, how='left', on=['year', 'state'])
    assert state_electors.isnull().sum().sum() == 0
    state_electors.head(3)
    return (state_electors,)


@app.cell
def _(party_colors, plt, state_electors):
    # TODO: add independent


    state_electors_by_year = (state_electors
        .pivot_table(
            index='year', 
            columns='party_group',
            values='electors',
            aggfunc='sum'
        )
        .fillna(0)
    )
    (state_electors_by_year
         .rename_axis(columns='party')
         .plot(
             kind='bar', 
             figsize=(16, 3), 
             color=[party_colors[c] for c in state_electors_by_year.columns],
             title='electors won by year by party',
             # sort_columns=True
         )
    );

    plt.show()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
