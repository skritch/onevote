<script lang="ts">
  import { statePageParams } from "../../lib/statePageParams.svelte.js";
  import { getCongressForYear } from "../../lib/districts.js";
  import type { DistrictData } from "../../lib/districts.js";
  import type { StatePO } from "../../lib/states.js";
  import districtResultsRaw from "../../data/district_results.json";
  import { partyColors } from "../../lib/party.js";
  import { initCap } from "../../utils/strings.js";

  let {
    districtData,
    statePO,
  }: { districtData: DistrictData; statePO: StatePO } = $props();

  const districtResults = districtResultsRaw as Record<
    string,
    Record<string, Record<string, string | null>>
  >;

  const congress = $derived(
    getCongressForYear(districtData, statePageParams.year),
  );

  const districtEntries = $derived(
    congress == null
      ? []
      : Object.entries(districtData.districtsByCongress[congress] ?? {}),
  );

  const viewBox = $derived(
    congress != null && districtData.viewboxByCongress?.[congress]
      ? districtData.viewboxByCongress[congress]
      : "14 14 772 572",
  );

  const yearDistrictResults = $derived(
    districtResults[String(statePageParams.year)]?.[statePO] ?? {},
  );

  // Path keys are '1','2'... but results keys are '01','02'... — normalize both sides.
  function districtColor(districtId: string): string {
    const party =
      yearDistrictResults[districtId] ??
      yearDistrictResults[districtId.padStart(2, "0")] ?? // TODO
      "unknown";
    return partyColors[initCap(party)] ?? partyColors.Unknown;
  }

  const isSelectable = $derived(
    districtEntries.length > 0 &&
      statePageParams.year >= 2012 &&
      !(districtEntries.length === 1 && districtEntries[0][0] === "AL"),
  );

  function handleClick(districtId: string) {
    if (!isSelectable) return;
    statePageParams.districtId =
      statePageParams.districtId === districtId ? "" : districtId;
  }
</script>

{#if districtEntries.length > 0}
  <svg
    class="state-logo"
    {viewBox}
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
    onmousedown={(e) => e.preventDefault()}
  >
    <g
      class="state-logo__districts"
      class:has-selection={statePageParams.districtId}
      class:selectable={isSelectable}
    >
      {#each districtEntries as [districtId, d]}
        <path
          {d}
          class:is-selected={statePageParams.districtId === districtId}
          style="fill: {districtColor(districtId)}"
          role="button"
          tabindex={isSelectable ? 0 : -1}
          aria-label="District {districtId}"
          aria-pressed={statePageParams.districtId === districtId}
          onclick={() => handleClick(districtId)}
          onkeydown={(e) => e.key === "Enter" && handleClick(districtId)}
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
      transition:
        opacity 0.15s,
        filter 0.15s;

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
