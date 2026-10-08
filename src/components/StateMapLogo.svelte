<script lang="ts">
  import { getCongressForYear } from "../lib/districts.js";
  import type { DistrictIndex } from "../lib/districts.js";
  import type { StatePO } from "../lib/states.js";
  import districtResultsRaw from "../data/district_results.json";
  import { partyColors } from "../lib/party.js";
  import { initCap } from "../utils/strings.js";

  type Props = {
    districtIndex: DistrictIndex;
    statePO: StatePO;
    year: number;
    districtId?: string;
    onDistrictChange?: (id: string | undefined) => void;
  };

  let { districtIndex, statePO, year, districtId, onDistrictChange }: Props = $props();

  const districtResults = districtResultsRaw as Record<
    string,
    Record<string, Record<string, string | null>>
  >;

  type PathEntry = { id: string; d: string };
  type SvgData = { viewBox: string; paths: PathEntry[] };

  const congress = $derived(getCongressForYear(districtIndex, year));

  async function fetchSvgData(po: StatePO, cong: number): Promise<SvgData | null> {
    const url = `${import.meta.env.BASE_URL}maps/${po}-${cong}.svg`;
    try {
      const res = await fetch(url);
      if (!res.ok) return null;
      const text = await res.text();
      const parser = new DOMParser();
      const doc = parser.parseFromString(text, "image/svg+xml");
      const svg = doc.querySelector("svg");
      if (!svg) return null;
      const viewBox = svg.getAttribute("viewBox") ?? "14 14 772 572";
      const paths = Array.from(svg.querySelectorAll("path"))
        .map((p) => ({ id: p.getAttribute("id") ?? "", d: p.getAttribute("d") ?? "" }))
        .filter((p) => p.id && p.d);
      return { viewBox, paths };
    } catch {
      return null;
    }
  }

  const svgDataPromise = $derived(fetchSvgData(statePO, congress));

  const yearDistrictResults = $derived(
    districtResults[String(year)]?.[statePO] ?? {},
  );

  function districtColor(id: string): string {
    const party =
      yearDistrictResults[id] ??
      yearDistrictResults[id.padStart(2, "0")] ??
      "unknown";
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
