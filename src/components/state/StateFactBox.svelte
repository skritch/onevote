<script lang="ts">
  import { chartState } from '../../lib/chartState.svelte.js'
  import { getStateDimension, partyColors, candidatesByYear } from '../../lib/values.js'
  import { popVarDescriptions } from '../../lib/manifest.js'
  import InfoLink from '../InfoLink.svelte'

  let { statePo }: { statePo: string } = $props()

  const CURRENT_YEAR = new Date().getFullYear()

  const dim = $derived(getStateDimension(chartState.year, statePo.toUpperCase()))
  const hasPastResults = $derived(
    dim !== null && chartState.year <= CURRENT_YEAR && dim.votes_total !== null
  )

  const votesSum = $derived(
    dim
      ? (dim.votes_democrat ?? 0) + (dim.votes_republican ?? 0) + (dim.votes_other ?? 0)
      : 0
  )

  function fmt(n: number | null | undefined): string {
    if (n == null) return '—'
    return Math.round(n).toLocaleString('en-US')
  }

  function fmtElectors(n: number | null | undefined): string {
    if (n == null || n === 0) return ''
    return String(Math.round(n))
  }

  function pct(votes: number | null | undefined, total: number): string {
    if (votes == null || total === 0) return '—'
    return ((votes / total) * 100).toFixed(1) + '%'
  }

  function lastName(fullName: string): string {
    const parts = fullName.trim().split(' ')
    return parts[parts.length - 1]
  }

  function displayName(party: 'democrat' | 'republican' | 'other', year: number): string {
    if (party === 'democrat') {
      const name = candidatesByYear[year]?.democrat
      return name ? lastName(name) : 'Democrat'
    }
    if (party === 'republican') {
      const name = candidatesByYear[year]?.republican
      return name ? lastName(name) : 'Republican'
    }
    return 'Other'
  }

  const resultParties = ['democrat', 'republican', 'other'] as const
</script>

<div class="factbox">
  {#if dim}
    <!-- Population -->
    <div class="factbox__section">
      <div class="factbox__pop-header">
        <span class="factbox__pop-title">Population</span>
        <hr class="factbox__pop-hr" />
      </div>
      <div class="factbox__row">
        <span class="factbox__label">
          <InfoLink
            text="Apportionment"
            description={popVarDescriptions.ap}
            href={`${import.meta.env.BASE_URL}about/population`}
          />
        </span>
        <span class="factbox__val">{fmt(dim.apportionment_population)}</span>
      </div>
      {#if dim.vap_estimate != null}
        <div class="factbox__row">
          <span class="factbox__label">
            <InfoLink
              text="Voting Age"
              description={popVarDescriptions.vap}
              href={`${import.meta.env.BASE_URL}about/population`}
            />
          </span>
          <span class="factbox__val">{fmt(dim.vap_estimate)}</span>
        </div>
      {/if}
      {#if dim.vep_estimate != null}
        <div class="factbox__row">
          <span class="factbox__label">
            <InfoLink
              text="Voting-Eligible"
              description={popVarDescriptions.vep}
              href={`${import.meta.env.BASE_URL}about/population`}
            />
          </span>
          <span class="factbox__val">{fmt(dim.vep_estimate)}</span>
        </div>
      {/if}
    </div>

    <!-- Election results -->
    {#if hasPastResults}
      <div class="factbox__section factbox__section--results">
        <div class="factbox__results-title">Election Results</div>
        <hr class="factbox__results-hr" />
        <div class="factbox__results-body">
          <span></span><span></span>
          <span class="factbox__col-header">Votes</span>
          <span class="factbox__col-header">%</span>
          <span class="factbox__col-header">EC</span>
          {#each resultParties as party}
            {@const votes = dim[`votes_${party}` as keyof typeof dim] as number | null}
            {@const electors = dim[`electors_${party}` as keyof typeof dim] as number | null}
            {#if votes != null && votes > 0}
              <span class="factbox__dot" style="background: {partyColors[party]}"></span>
              <span class="factbox__party-name" class:winner={dim.winning_party === party}>
                {displayName(party, chartState.year)}{dim.winning_party === party ? ' ✓' : ''}
              </span>
              <span class="factbox__vote-count" class:winner={dim.winning_party === party}>
                {fmt(votes)}
              </span>
              <span class="factbox__pct" class:winner={dim.winning_party === party}>
                {pct(votes, votesSum)}
              </span>
              <span class="factbox__electors" class:winner={dim.winning_party === party}>
                {fmtElectors(electors)}
              </span>
            {/if}
          {/each}
          {#if votesSum > 0}
            <span class="factbox__total-border"></span>
            <span></span><span></span>
            <span class="factbox__total">{fmt(votesSum)}</span>
            <span></span>
            <span class="factbox__total">{fmtElectors(dim.electors)}</span>
          {/if}
        </div>
      </div>
    {/if}
  {:else}
    <p class="factbox__no-data">No data available for {chartState.year}.</p>
  {/if}
</div>

<style lang="scss">
  @use "../../styles/variables.scss";

  .factbox {
    background: variables.$white;
    border: 1px solid #e5e7eb;
    border-radius: variables.$border-radius;
    padding: variables.$spacing-md;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.07);
    font-size: variables.$font-size-small;
  }

  .factbox__section {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;

    & + & {
      margin-top: variables.$spacing-sm;
      padding-top: variables.$spacing-sm;
    }
  }

  .factbox__pop-header {
    margin-bottom: 0.15rem;
  }

  .factbox__pop-title {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: variables.$medium-gray;
  }

  .factbox__pop-hr {
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 3px 0 0;
  }

  .factbox__row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: variables.$spacing-xs;
  }

  .factbox__label {
    color: variables.$medium-gray;
    white-space: nowrap;
  }

  .factbox__val {
    color: variables.$dark-gray;
    text-align: right;
  }

  .factbox__results-title {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: variables.$medium-gray;
    margin-bottom: 0.15rem;
  }

  .factbox__results-hr {
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 0 0 0.3rem;
  }

  .factbox__col-header {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: variables.$medium-gray;
    text-align: center;
  }

  // Single shared grid: dot | name | % | votes(✓) | electors
  .factbox__results-body {
    display: grid;
    grid-template-columns: 8px 5rem auto auto auto;
    align-items: center;
    column-gap: 0.35rem;
    row-gap: 0.2rem;
  }

  .factbox__dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    justify-self: center;
  }

  .factbox__party-name {
    color: variables.$dark-gray;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;

    &.winner { font-weight: 600; }
  }

  .factbox__pct {
    color: variables.$dark-gray;
    text-align: center;
    font-variant-numeric: tabular-nums;

    &.winner { font-weight: 600; }
  }

  .factbox__vote-count {
    color: variables.$dark-gray;
    text-align: center;
    font-variant-numeric: tabular-nums;

    &.winner { font-weight: 600; }
  }

  .factbox__electors {
    color: variables.$dark-gray;
    text-align: center;
    font-variant-numeric: tabular-nums;

    &.winner { font-weight: 600; }
  }

  // Total row — border-span trick: first cell spans all 5 cols
  .factbox__total-border {
    grid-column: 1 / -1;
    border-top: 1px solid #d1d5db;
    margin-top: 1px;
    height: 0;
  }

  .factbox__total {
    color: variables.$dark-gray;
    text-align: center;
    font-variant-numeric: tabular-nums;

    &--votes { /* column 3 (pct) is empty, this is col 4 — no extra style needed */ }
    &--electors { /* col 5 */ }
  }

  .factbox__no-data {
    color: variables.$medium-gray;
    margin: 0;
    font-style: italic;
  }
</style>
