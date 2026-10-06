<script lang="ts">
  import { chartState } from "../../lib/chartState.svelte.js";
  import { partyColors } from "../../lib/values.js";
  import districtResultsRaw from "../../data/district_results.json";

  type DistrictData = {
    year_to_congress: Record<string, number>;
    districts_by_congress: Record<string, Record<string, string>>;
    viewbox_by_congress?: Record<string, string>;
  };

  let {
    districtData,
    statePo,
  }: { districtData: DistrictData; statePo: string } = $props();

  const districtResults = districtResultsRaw as Record<string, Record<string, Record<string, string | null>>>;

  const congress = $derived(
    districtData.year_to_congress[chartState.year] ??
    Math.max(...Object.values(districtData.year_to_congress))
  );

  const districtEntries = $derived(
    congress == null
      ? []
      : Object.entries(districtData.districts_by_congress[congress] ?? {})
  );

  const viewBox = $derived(
    congress != null && districtData.viewbox_by_congress?.[congress]
      ? districtData.viewbox_by_congress[congress]
      : "14 14 772 572"
  );

  const yearDistrictResults = $derived(
    districtResults[String(chartState.year)]?.[statePo.toUpperCase()] ?? {}
  );

  // Path keys are '1','2'... but results keys are '01','02'... — normalize both sides.
  function districtColor(districtId: string): string {
    const party = yearDistrictResults[districtId]
      ?? yearDistrictResults[districtId.padStart(2, '0')]
      ?? null;
    return partyColors[party ?? 'unknown'] ?? partyColors.unknown;
  }

  const isSelectable = $derived(
    districtEntries.length > 0 &&
    chartState.year >= 2012 &&
    !(districtEntries.length === 1 && districtEntries[0][0] === 'AL')
  );

  function handleClick(districtId: string) {
    if (!isSelectable) return;
    chartState.districtId = chartState.districtId === districtId ? '' : districtId;
  }
</script>

{#if districtEntries.length > 0}
  <svg
    class="state-logo"
    viewBox={viewBox}
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
    onmousedown={(e) => e.preventDefault()}
  >
    <g class="state-logo__districts" class:has-selection={chartState.districtId} class:selectable={isSelectable}>
      {#each districtEntries as [districtId, d]}
        <path
          {d}
          class:is-selected={chartState.districtId === districtId}
          style="fill: {districtColor(districtId)}"
          onclick={() => handleClick(districtId)}
          onkeydown={(e) => e.key === 'Enter' && handleClick(districtId)}
          role={isSelectable ? "button" : undefined}
          tabindex={isSelectable ? 0 : undefined}
          aria-label={isSelectable ? `District ${districtId}` : undefined}
          aria-pressed={isSelectable ? chartState.districtId === districtId : undefined}
        />
      {/each}
    </g>
  </svg>
{/if}

<style lang="scss">
  @use "../../styles/variables.scss";

  .state-logo {
    display: block;
    width: auto;
    height: auto;
    max-width: 100%;
    max-height: 14rem;

    &__districts path {
      stroke: #000;
      stroke-width: 0.3px;
      vector-effect: non-scaling-stroke;
      outline: none;
      transition: opacity 0.15s, filter 0.15s;

      &:hover {
        transform: none;
      }
    }

    &__districts.selectable path {
      cursor: pointer;
    }

    &__districts.has-selection path {
      opacity: 0.35;

      &.is-selected {
        opacity: 1;
        filter: brightness(0.8);
      }
    }
  }
</style>
