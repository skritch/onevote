<script lang="ts">
  import { getCongressForYear } from "../lib/districts.js";
  import type { DistrictData } from "../lib/districts.js";
  import type { StatePO } from "../lib/states.js";
  import districtResultsRaw from "../data/district_results.json";
  import { partyColors } from "../lib/party.js";
  import { initCap } from "../utils/strings.js";

  type Props = {
    districtData: DistrictData;
    statePO: StatePO;
    year: number;
    districtId?: string;
    onDistrictChange?: (id: string | undefined) => void;
  };

  let { districtData, statePO, year, districtId, onDistrictChange }: Props = $props();

  const districtResults = districtResultsRaw as Record<
    string,
    Record<string, Record<string, string | null>>
  >;

  const congress = $derived(getCongressForYear(districtData, year));

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
    districtResults[String(year)]?.[statePO] ?? {},
  );

  // Path keys are '1','2'... but results keys are '01','02'... — normalize both sides.
  function districtColor(id: string): string {
    const party =
      yearDistrictResults[id] ??
      yearDistrictResults[id.padStart(2, "0")] ?? // TODO
      "unknown";
    return partyColors[initCap(party)] ?? partyColors.Unknown;
  }

  const isSelectable = $derived(
    districtEntries.length > 0 &&
      year >= 2012 &&
      !(districtEntries.length === 1 && districtEntries[0][0] === "AL"),
  );

  function handleClick(id: string) {
    if (!isSelectable) return;
    onDistrictChange?.(districtId === id ? undefined : id);
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
      class:has-selection={districtId}
      class:selectable={isSelectable}
    >
      {#each districtEntries as [id, d]}
        <path
          {d}
          class:is-selected={districtId === id}
          style="fill: {districtColor(id)}"
          role="button"
          tabindex={isSelectable ? 0 : -1}
          aria-label="District {id}"
          aria-pressed={districtId === id}
          onclick={() => handleClick(id)}
          onkeydown={(e) => e.key === "Enter" && handleClick(id)}
        />
      {/each}
    </g>
  </svg>
{/if}

<style lang="scss">
  @use "../styles/variables.scss";

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
