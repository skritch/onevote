import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import json
    return json, np, pd


@app.cell
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
def _(data):
    data[data.year==1976].fillna(0).iloc[0].state_vap_estimate
    return


@app.cell
def _(data, np):
    # Create 2028 projection using 2024 data
    data_2024 = data[data['year'] == 2024].copy()
    data_2028 = data_2024.copy()

    # Update year to 2028
    data_2028['year'] = 2028

    # Set vote-related and VAP/VEP columns to NaN
    vote_columns = [
        'state_vap_estimate', 'state_vep_estimate',
        'votes_total', 'votes_democrat', 'votes_other', 'votes_republican',
        'electors_democrat', 'electors_republican', 'electors_other'
    ]
    for col in vote_columns:
        data_2028[col] = np.nan

    # Set winning_party to empty string
    data_2028['winning_party'] = None

    data_2028
    return (data_2028,)


@app.cell
def _(data, data_2028, json, pd):
    # Merge 2028 data into original dataframe
    data_complete = pd.concat([data, data_2028], ignore_index=True)

    # Group by year and create the nested structure
    output = []

    for year in sorted(data_complete['year'].unique()):
        year_data = data_complete[data_complete['year'] == year]

        # Calculate nationwide aggregates (fillna(0) for sums)
        year_summary = {
            'year': int(year),
            'total_vap': float(year_data['state_vap_estimate'].fillna(0).sum()),
            'total_vep': float(year_data['state_vep_estimate'].fillna(0).sum()),
            'total_population': int(year_data['state_population'].fillna(0).sum()),
            'total_votes': int(year_data['votes_total'].fillna(0).sum()),
            'votes_democrat': float(year_data['votes_democrat'].fillna(0).sum()),
            'votes_republican': float(year_data['votes_republican'].fillna(0).sum()),
            'votes_other': float(year_data['votes_other'].fillna(0).sum()),
            'electors_democrat': float(year_data['electors_democrat'].fillna(0).sum()),
            'electors_republican': float(year_data['electors_republican'].fillna(0).sum()),
            'electors_other': int(year_data['electors_other'].fillna(0).sum()),
            'states_won_democrat': int((year_data['winning_party'] == 'democrat').sum()),
            'states_won_republican': int((year_data['winning_party'] == 'republican').sum()),
            'states_won_other': int((year_data['winning_party'] == 'other').sum()),
        }

        # Determine winning party (party with most electors)
        if year_summary['electors_democrat'] > year_summary['electors_republican']:
            year_summary['winning_party'] = 'democrat'
        elif year_summary['electors_republican'] > year_summary['electors_democrat']:
            year_summary['winning_party'] = 'republican'
        else:
            year_summary['winning_party'] = 'tie'

        # Convert states to list of dicts
        # Manually replace np.nan -> None, Pandas only does it with a direct to_json()
        state_data = [
            {
                k: v if not pd.isna(v) else None
                for k, v in state.items()
            }
            for state in year_data.to_dict('records')
        ]
        year_summary['states'] = state_data

        output.append(year_summary)

    # Write to JSON file
    with open('webapp/src/data/presidential_elections.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Written {len(output)} years to presidential_elections.json")
    return (state_data,)


@app.cell
def _(state_data):
    state_data[0]
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
