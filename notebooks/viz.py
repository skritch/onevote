import altair
import pandas as pd



def viz_value_by_state(df, column_name: str, value_name: str, year: int):
    # Filter for selected year and sort alphabetically by state name
    data_1yr_sorted = df[df['year'] == year].sort_values('state').copy()

    # Create bar plot with Altair
    bars = altair.Chart(data_1yr_sorted).mark_bar().encode(
        x=altair.X('state_po:N', title='State', sort=None),
        y=altair.Y(f'{column_name}:Q', title=value_name),
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
            altair.Tooltip(f'{column_name}:Q', title=value_name, format='.3f')
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
        title=f'{value_name} of Voters by State - {year} Presidential Election\n'
    ).configure_axis(
        grid=True,
        gridOpacity=0.3
    )

    return chart


def viz_value_hist(df, column_name: str, value_name: str, year: int):
    # Filter for selected year and sort alphabetically by state name
    # Create bins for PV (0.1 unit bins from 0 to 4)
    bins = [i * 0.1 for i in range(41)]  # 0.0, 0.1, 0.2, ..., 4.0
    data_1yr_sorted = df[df['year'] == year].sort_values('state').copy()
    data_binned = data_1yr_sorted.copy()
    data_binned['bin'] = pd.cut(data_1yr_sorted[column_name], bins=bins, include_lowest=True)

    # Get bin centers for plotting
    data_binned['bin_center'] = data_binned['bin'].apply(lambda x: (x.left + x.right) / 2)

    # Create long-form data with separate rows for democrat and republican votes
    histogram_data_list = []
    for _, row in data_binned.iterrows():
        histogram_data_list.append({
            'bin_center': row['bin_center'],
            'party': 'democrat',
            'votes': row['votes_democrat']
        })
        histogram_data_list.append({
            'bin_center': row['bin_center'],
            'party': 'republican',
            'votes': row['votes_republican']
        })

    histogram_data_long = pd.DataFrame(histogram_data_list)

    # Group by bin and party, sum votes
    histogram_data = histogram_data_long.groupby(['bin_center', 'party'], as_index=False)['votes'].sum()

    # Create stacked bar chart
    histogram = altair.Chart(histogram_data).mark_bar(width=20).encode(
        x=altair.X('bin_center:Q',
                title=value_name,
                scale=altair.Scale(domain=[0, 4])),
        y=altair.Y('votes:Q',
                title='Total Votes',
                stack=True),
        color=altair.Color('party:N',
                        scale=altair.Scale(domain=['democrat', 'republican'],
                                        range=['blue', 'darkred']),
                        legend=altair.Legend(title='Party')),
        tooltip=[
            altair.Tooltip('bin_center:Q', title=value_name, format='.2f'),
            altair.Tooltip('party:N', title='Party'),
            altair.Tooltip('votes:Q', title='Votes', format=',')
        ]
    ).properties(
        width=900,
        height=400,
        title=f'Vote Distribution by {value_name} and Party - {year} Presidential Election'
    )

    return histogram



def viz_value_vs_ec_popular_by_year(df, column_name: str, value_name: str, selected_party: str):

    # For each year, calculate:
    # - Total EC for selected party / Total EC
    # - Total AV-weighted votes for selected party / Total AV-weighted votes
    # - Total popular votes for selected party / Total popular votes
    # - Number of states won

    party_stats_list = []

    for year in df['year'].unique():
        year_data = df[df['year'] == year].copy()

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

        # Value-weighted votes for party (across all states, not just won states)
        party_v_weighted_votes = (year_data[column_name] * year_data[votes_col]).sum()

        # Total Value-weighted votes
        total_v_weighted_votes = (year_data[column_name] * year_data['votes_total']).sum()

        # Determine national winner (party with most EC)
        national_winner = year_data.groupby('winning_party')['state_electors'].sum().idxmax()

        party_stats_list.append({
            'year': year,
            'ec_pct': party_ec / total_ec * 100,
            'v_pct': party_v_weighted_votes / total_v_weighted_votes * 100,
            'popular_vote_pct': party_votes / total_votes * 100,
            'states_won': states_won,
            'party_ec': party_ec,
            'total_ec': total_ec,
            'national_winner': national_winner
        })

    party_stats = pd.DataFrame(party_stats_list)

    # Create scatter plot
    _scatter_ec = altair.Chart(party_stats).mark_circle(size=100).encode(
        x=altair.X('v_pct:Q',
                title=f'{value_name}-Weighted Vote % for Party',
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
            altair.Tooltip('v_pct:Q', title=f'{value_name} %', format='.1f'),
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

    _chart_ec = (_scatter_ec + _diagonal).properties(
        width=300,
        height=300,
        title=f'EC % vs {value_name}-Weighted Vote %'
    )

    # Create second scatter plot for Popular Vote vs AV
    _scatter_p = altair.Chart(party_stats).mark_circle(size=100).encode(
        x=altair.X('v_pct:Q',
                title=f'{value_name}-Weighted Vote % for Party',
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
            altair.Tooltip('v_pct:Q', title=f'{value_name} %', format='.1f'),
            altair.Tooltip('states_won:Q', title='States Won'),
            altair.Tooltip('party_ec:Q', title='Party EC'),
            altair.Tooltip('total_ec:Q', title='Total EC')
        ]
    )

    _chart_pv = (_scatter_p + _diagonal).properties(
        width=300,
        height=300,
        title=f'Popular Vote % vs {value_name}-Weighted Vote %'
    )

    # Combine charts side by side
    _combined_chart = (_chart_ec | _chart_pv).properties(
        title=f'{selected_party.title()}s (1976-2024)'
    )

    return _combined_chart


def viz_scatter_compare(df, x: str, x_name: str, y: str, y_name: str, year: int, ):
    data_1yr = df[df['year'] == year].copy()

    # Create scatter plot
    scatter = altair.Chart(data_1yr).mark_circle(size=100).encode(
        x=altair.X(f'{x}:Q',
                title=x_name),
        y=altair.Y(f'{y}:Q',
                title=y_name),
        color=altair.Color('winning_party:N',
                        scale=altair.Scale(domain=['democrat', 'republican'],
                                        range=['blue', 'darkred']),
                        legend=altair.Legend(title='Winner')),
        tooltip=[
            altair.Tooltip('state:N', title='State'),
            altair.Tooltip('state_po:N', title='Abbreviation'),
            altair.Tooltip('winning_party:N', title='Winner'),
            altair.Tooltip('state_population:Q', title='Population', format=','),
            altair.Tooltip('state_electors:Q', title='Electors'),
            altair.Tooltip('votes_total:Q', title='Total Votes', format=','),
            altair.Tooltip(f'{x}:Q', title=x_name, format='.3f'),
            altair.Tooltip(f'{y}:Q', title=y_name, format='.3f')
        ]
    )

    chart = scatter.properties(
        width=400,
        height=400,
        title=f'{x_name} vs. {y_name} by State - {year} Presidential Election'
    ).configure_axis(
        grid=True,
        gridOpacity=0.3
    )

    return chart