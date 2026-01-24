# OneVote Project Overview

## Project Purpose
OneVote is a webapp that compares the "value" of Americans' votes between different regions across different elections. The goal is to demonstrate that elections are not fair and highlight low-hanging ways to improve them, approaching the topic from a non-partisan perspective focused on making democracy work better.

## Core Features (Planned)
1. **Location Comparison** - Compare vote values between two locations (e.g., "a New Yorker Democrat's vote is worth 1/5 of a Wyoming Republican")
2. **Location Lookup** - Present curated overviews of compelling arguments across elections
3. **Election Summaries** - Focus on presidency, House, and Senate with "net effect" analysis of various sources of unfairness
4. **Method Toggle** - Switch between different methods of evaluating electoral unfairness
5. **Educational Essays** - Clear explanations of the project and actionable policy changes

## Technical Architecture

### Current State
The project is in early development with:
- **Python Backend**: Minimal setup (`main.py`, `pyproject.toml`)
  - Python 3.13+ required
  - No dependencies currently listed
- **Astro Frontend**: Basic webapp setup
  - Astro 5.16.15
  - Standard Astro structure with components, layouts, pages
  - Default Astro welcome page currently active

### Project Structure
```
onevote/
├── .ai/                    # AI context files
├── analysis/               # Data analysis (Jupyter notebooks)
│   ├── geographic_data.ipynb
│   └── requirements.in     # jupyter, matplotlib, numpy, pandas, etc.
├── docker/                 # Docker configuration
├── notes/                  # Project documentation
│   ├── notes.md           # Research links and datasets
│   └── spec.md            # Full project specification
├── webapp/                 # Astro frontend
│   ├── src/
│   │   ├── components/    # Astro components
│   │   ├── layouts/       # Page layouts
│   │   └── pages/         # Route pages
│   └── package.json       # Astro dependencies
├── main.py                # Python entry point (minimal)
└── pyproject.toml         # Python project config
```

### Data Sources (from notes)
- MIT Election Lab: Senate, House, Presidential data since 1976
- Harvard Dataverse: Presidential data since 1976
- US Census: Demographic and geographic data
- Voter turnout data since 1980
- Various election datasets and resources

### Development Commands
- **Frontend**: `cd webapp && npm run dev` (Astro dev server)
- **Frontend Build**: `cd webapp && npm run build`
- **Python**: `python main.py` (currently just prints hello message)

## Key Technical Components (Planned)
1. **Election Data Pipeline** - Process voting outcomes, census data, forecasts
2. **Algorithms Corpus** - Mathematical methods for measuring electoral unfairness
3. **Interactive Mapping** - Visualize districts and vote values
4. **Widget System** - Exportable graphics for embedding

## Development Status
- ✅ Basic project structure established
- ✅ Astro webapp scaffolded
- ✅ Analysis environment with Jupyter setup
- 🚧 Core features not yet implemented
- 🚧 No election data integration yet
- 🚧 No algorithms implemented yet

## Next Steps
The project needs development of the core webapp features, integration with election datasets, and implementation of vote value comparison algorithms as outlined in the specification.