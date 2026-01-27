
# OneVote Spec

What it is: a webapp which compares the "value" of the Americans' votes between different regions, across different elections. 

The message is: our elections are not fair, there are low-hanging ways to improve them, and this is a worthy goal on its own, not for partisan reasons but in the interest of making the world feel like it was designed by and for adults. 

The core features are:
1. Comparison of two locations. The core feature. This view is intended to make for splashy links on social media: "in the House, a New Yorker Democrat's vote is worth 1/5 of a Wyoming Republican..."
2. Lookup by location. This view should present a curated overview of the most compelling arguments across recent and memorable elections, and should link out to other views (comparison, overview of mathematical methods, summaries of certain elections)
3. Summaries by election. Our initial targets will be the presidency, House, and Senate. A key feature of the summaries should be to clearly communicate the approximate "net" effect of each source of injustice on the overall outcome, e.g., what portion of the deviation of the presidential outcome from the popular vote is due to a) Electoral College winner-takes-all, b) house apportionment in the EC, c) senate apportionment contributing to the EC, e) spoiler effects, f) election day not being a holiday etc.? It should be possible to turn these features on/off and estimate the effect on past elections.
4. The ability to toggle between methods of evaluating electoral unfairness, along with clear overviews of the different methods.
5. A handful essays describing the project, its intended argument, and the simplest actionable policy changes with extreme clarity. These should "fly above" partisan rhetoric, while acknowledging what the local partisan advantages of the changes proposed would be.

A further ambition is to aid the public in *imagining* far larger evolutions of American electoral changes—making election day a holiday, bans on gerrymandering, proportional representation, etc. (A people will never seriously consider changing their mind if they cannot envision how the new state after the change will equilibrate. This is an empirical fact about human nature, which presents a major obstacle to most progressive causes, e.g. anticapitalism, climate, police reform. But our progressives are largely unable to think this way, and tend to condemn this resistance as selfish instead; this is felt to be unjust, and discredits the movements entirely.)

Technically we will organize the project into the following components:
1. Core webapp:
	1. Location-lookup and comparison features 1 and 2 above, providing various views of the underlying data: dedicated pages, exportable widgets, etc. Dependencies on:
		1. Election data
		2. Algorithms corpus.
		3. Possibly, some elaborate configuration which determines how large views can get.
		4. Some kind of mapping feature visualizing districts interactively.
	2. Static hosting for reports (on specific elections, algorithms) and essays. 
		1. Should be able to embed the widgets and graphics from (1).
2. Election data pipeline. The basic is voting outcomes by election. But eventually, we might be interested in fair finer-grained data, such as:
	1. Census data, which might be of use in estimating gerrymandering effects
	2. Forecasts leading up to past elections, which might have some dynamical effect on outcomes themselves, or be used in estimating degrees of unfairness a priori.
3. Algorithms corpus. This may be crowd-sourced, probably stored directly in Git or something. It can be hardcoded at first. Largely this is outside of my expertise, but I could become an expert; my first goal is just to build a platform to serve these algorithms.



## 1. Webapp

Pages:

`/` (in `index.astro`). Splashy front page which, depending on what you enter, either:
- takes you to a report on your state, state+party, or your exact district
- or, compares to another state/state+party/state+district+party
- across presidential, house, or senate race
- across all years for which we have data
- uses the default measure for everything.
- MVP = president only at state level

Design should have just the left panel + a button to "add a comparison" on the right, which expands into two panel view.

Ideally pulls up your state outline + party color + district.

`/compare` (in `compare.astro`). 
- compares everything with a single component?
- query parameters determine everything: states, parties, locations, etc.
- should be able to toggle the methods and counterfactuals
- for MVP, just compare states with the only method we have.
- could split this up by race, or by state vs state+party


`/state/<id>` (`report.astro).
A general report on a given state for a given election. Defaults to 2024.

- query parameters determine election + year
- MVP = president only
- possibly this is just a Marimo notebook we run on demand and render as an astro page somehow?

`/elections/<president|senate|house>/<year>`: 
Report on an entire election

MNaybe: `/elections/<president|senate|house>/<year>/<state_id>`:
Same as `/state/<id>`, or an alternative static route for it?
Might be too many routes to render statically, perhaps we use a query param for the state and/or year., 

`/elections/`
`/elections/<president|senate|house>`:
Landing pages to navigate to individual reports, possibly including summary stats.

`/methods/...`
Various markdown pages (possibly incl graphics) which document the methods we use to value votes / measure fairness.


`/essays/...` (or perhaps `/blog`?)
- some kind of writeup of the principles behind the project, the argument.

Components:
- menu bar: links to election, state, and various writeups