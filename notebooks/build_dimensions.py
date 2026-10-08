import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import json
    import argparse
    from pathlib import Path


@app.cell
def _():
    # Parse command line arguments
    _parser = argparse.ArgumentParser(description='Presidential Election Scenarios Analysis')
    _parser.add_argument(
        '-o', '--output',
        default="./.data/dimensions/",
        type=str,
        help='Output directory for results')
    _args = _parser.parse_args()
    output_dir = Path(_args.output)
    return (output_dir,)


@app.cell
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

    data
    return KaggleDatasetAdapter, data, kagglehub


@app.cell
def _(data):
    # Create 2028 projection using 2024 data
    data_2024 = data[data['year'] == 2024].copy()
    data_2028 = data_2024.copy()

    # Update year to 2028
    data_2028['year'] = 2028

    # Set vote-related and VAP/VEP columns to NaN
    vote_columns = [
        'vap_estimate', 'vep_estimate',
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
def _(KaggleDatasetAdapter, kagglehub):
    data_district = kagglehub.dataset_load(
      KaggleDatasetAdapter.PANDAS,
      "samkritch/u-s-presidential-elections-by-state-1976-2024",
      'pres_by_district_2012_2024.csv',
    )

    data_district.head(3)
    return (data_district,)


@app.cell
def _(data_district):
    _keep = [
        'apportionment_population', # 'apportionment_voting_age_population',
        'votes_democrat', 'votes_republican', 'votes_other', 'votes_total',
        'electors', 'electors_democrat', 'electors_republican', 'electors_other',
        'winning_party', 'district_code'
    ]

    districts = {}
    for _row in data_district.to_dict('records'):
        _state = _row['state_po'].upper()
        _year = int(_row['year'])
        districts.setdefault(_year, {}).setdefault(_state, []).append(
            {
                k: (None if isinstance(v, float) and pd.isna(v) else v)
                for k, v in _row.items() if k in _keep
            }
        )

    # Synthetic 2028: same states/districts as 2024, only apportionment_population and electors
    for _row in data_district[data_district['year'] == 2024].to_dict('records'):
        _state = _row['state_po'].upper()
        districts.setdefault(2028, {}).setdefault(_state, []).append(
            {
                'apportionment_population': _row['apportionment_population'],
                'electors': _row['electors'],
                'district_code': _row['district_code']
            }
        )
    return (districts,)


@app.cell
def _(data_district, output_dir):
    _PRES_YEARS = [1976, 1980, 1984, 1988, 1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020, 2024]

    def _normalize_id(raw):
        if not raw or str(raw).upper() == "AL":
            return "AL"
        try:
            return str(int(raw))
        except ValueError:
            return str(raw)

    # Build 2012-2024 from CSV
    _csv_by_year = {}
    for _row in data_district.to_dict("records"):
        _y = str(int(_row["year"]))
        _s = _row["state_po"].upper()
        _d = _normalize_id(_row["district_code"])
        _w = _row.get("winning_party") or None
        _csv_by_year.setdefault(_y, {}).setdefault(_s, {})[_d] = {"winningParty": _w}

    # Build pre-2012 from district_index (district IDs only, no winner data)
    _index_path = Path(".data/district_index.json")
    _district_index = json.loads(_index_path.read_text()) if _index_path.exists() else {}

    _dr = {}
    for _year in _PRES_YEARS:
        _ys = str(_year)
        if _ys in _csv_by_year:
            _dr[_ys] = _csv_by_year[_ys]
        else:
            _dr[_ys] = {}
            for _state, _idx in _district_index.items():
                _congress = str(_idx["yearToCongress"].get(_ys, ""))
                _ids = (_idx.get("districtIdsByCongress") or {}).get(_congress, [])
                if _ids:
                    _dr[_ys][_state] = {_id: {"winningParty": None} for _id in _ids}
            _dr[_ys]["DC"] = {"AL": {"winningParty": None}}

    output_dir.mkdir(parents=True, exist_ok=True)
    _out_path = output_dir / "district_results.json"
    _out_path.write_text(json.dumps(_dr, indent=2))
    print(f"Wrote {_out_path} ({len(_dr)} years)")
    return


@app.cell
def _(data, data_2028, districts, output_dir):
    data_complete = pd.concat([data, data_2028], ignore_index=True)

    output = []

    for year in sorted(data_complete['year'].unique()):
        year_data = data_complete[data_complete['year'] == year]

        year_summary = {
            'year': int(year),
            'total_vap': float(year_data['vap_estimate'].sum(min_count=1)),
            'total_vep': float(year_data['vep_estimate'].sum(min_count=1)),
            'total_population': int(year_data['apportionment_population'].fillna(0).sum()),
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
        for s in state_data:
            if d := districts.get(s['year'], {}).get(s['state_po'], []):
                s['districts'] = d
    
        year_summary['states'] = state_data

        year_summary = {
            k: v if not isinstance(v, float) or not pd.isna(v) else None
            for k, v in year_summary.items()
        }

        output.append(year_summary)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = (output_dir / 'presidential_elections.json')

    # Write to JSON file
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Wrote {len(output)} years to {output_file}")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
