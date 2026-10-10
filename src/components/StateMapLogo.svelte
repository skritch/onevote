<script lang="ts">
  import type { StatePO } from "../lib/states.js";
  import { districtResults } from "../lib/districts.js";
  import { partyColors } from "../lib/party.js";
  import { initCap } from "../utils/strings.js";
  import { fetchSvgData, type PathEntry } from "../lib/maps.js";

  type Props = {
    statePO: StatePO;
    year: number;
    districtId?: string;
    mapUrl: string;
    onDistrictChange?: (id: string | undefined) => void;
  };

  let { statePO, year, districtId, mapUrl, onDistrictChange }: Props = $props();



  const svgDataPromise = $derived(fetchSvgData(mapUrl));

  const yearDistrictResults = $derived(
    districtResults[String(year)]?.[statePO] ?? {} as Record<string, import("../lib/districts.js").DistrictResult>,
  );

  function districtColor(id: string): string {
    const party = yearDistrictResults[id]?.winningParty ?? "unknown";
    return partyColors[initCap(party)] ?? partyColors.Unknown;
  }

  function isSelectable(paths: PathEntry[]): boolean {
    return (
      paths.length > 0 &&
      year >= 2012 &&
      !(paths.length === 1 && paths[0].id === "AL")
    );
  }

  function handleClick(id: string, paths: PathEntry[]) {
    if (!isSelectable(paths)) return;
    onDistrictChange?.(districtId === id ? undefined : id);
  }
</script>

{#await svgDataPromise then svgData}
  {#if svgData && svgData.paths.length > 0}
    {@const selectable = isSelectable(svgData.paths)}
    <svg
      class="state-logo"
      viewBox={svgData.viewBox}
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      onmousedown={(e) => e.preventDefault()}
    >
      <g
        class="state-logo__districts"
        class:has-selection={districtId}
        class:selectable
      >
        {#each svgData.paths as { id, d }}
          <path
            {d}
            class:is-selected={districtId === id}
            style="fill: {districtColor(id)}"
            role="button"
            tabindex={selectable ? 0 : -1}
            aria-label="District {id}"
            aria-pressed={districtId === id}
            onclick={() => handleClick(id, svgData.paths)}
            onkeydown={(e) => e.key === "Enter" && handleClick(id, svgData.paths)}
          />
        {/each}
      </g>
    </svg>
  {/if}
{/await}

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
