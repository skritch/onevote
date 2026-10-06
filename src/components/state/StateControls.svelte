<script lang="ts">
  import { untrack } from "svelte";
  import {
    dimensionsStateWinner,
    getDistrictDimension,
    OFFICES,
  } from "../../lib/elections";
  import type { StatePO } from "../../lib/states.js";
  import type { StatePageParams } from "../../lib/statePageParams.js";
  import { getValidForYear } from "../../lib/manifest.js";
  import { getDistrictsForState } from "../../lib/values.js";
  import { getAvailableDistrictIds } from "../../lib/districts.js";
  import type { DistrictData } from "../../lib/districts.js";
  import Select from "../Select.svelte";
  import { PARTIES, type Party } from "../../lib/party.js";
  import { initCap } from "../../utils/strings.js";

  type Props = {
    years: number[];
    statePO?: StatePO;
    districtData?: DistrictData | null;
    params: StatePageParams;
  };

  let { years, statePO = "", districtData = null, params }: Props = $props();

  // Auto-select winning party when WVV is chosen
  $effect(() => {
    if (params.value !== "wvv") return;
    untrack(() => {
      const year = params.year;
      const districtId = params.districtId;
      const scenario = params.scenario;
      let winner: string | null = null;
      if (scenario === "p3" && districtId) {
        winner =
          getDistrictDimension(year, statePO, districtId)?.winningParty ?? null;
      }
      if (!winner) {
        winner = dimensionsStateWinner[String(year)]?.[statePO] ?? null;
      }
      if (winner) {
        const winningParty =
          PARTIES.find((p) => p.toLowerCase() === winner.toLowerCase()) ??
          undefined;
        params.party = winningParty;
      }
    });
  });

  // Congressional districts for this state page, keyed by year
  const availableDistrictIds = $derived(
    districtData ? getAvailableDistrictIds(districtData, params.year) : [],
  );

  const districtIdSelectorDisabled = $derived(
    availableDistrictIds.length === 0 ||
      (availableDistrictIds.length === 1 && availableDistrictIds[0] === "AL") ||
      params.year < 2012,
  );

  // Reset districtId when it becomes invalid (year change, at-large, etc.)
  $effect(() => {
    const year = params.year;
    const available = availableDistrictIds;
    const isAtLarge = available.length === 1 && available[0] === "AL";
    const curDistrict = untrack(() => params.districtId);
    if (!curDistrict) return;
    if (
      year < 2012 ||
      available.length === 0 ||
      isAtLarge ||
      !available.includes(curDistrict)
    ) {
      params.districtId = "";
    }
  });

  // Available districts for this state under the current scenario/year
  const availableDistricts = $derived(
    statePO
      ? getDistrictsForState(params.scenario, params.year, statePO)
      : [],
  );

  // Reset district when scenario doesn't support districts or district is no longer valid
  $effect(() => {
    const scenario = params.scenario;
    const available = availableDistricts;
    if (scenario !== "p3" && scenario !== "p4") {
      if (untrack(() => params.district)) params.district = "";
    } else if (params.district && !available.includes(params.district)) {
      params.district = "";
    }
  });

  // Snap value/popVar to a valid combo when year or scenario changes
  $effect(() => {
    const { values, popVarsFor } = getValidForYear(params.year, params.scenario);
    const curVal = untrack(() => params.value);
    const curPop = untrack(() => params.popVar);
    const nextVal = values.includes(curVal) ? curVal : (values[0] ?? "av");
    const pops = popVarsFor(nextVal);
    const nextPop =
      pops.length === 0 || pops.includes(curPop) ? curPop : pops[0];
    if (nextVal !== curVal) params.value = nextVal;
    if (nextPop !== curPop) params.popVar = nextPop;
  });
</script>

<div class="state-page__controls">
  <Select
    bind:value={params.year}
    options={years.map((y) => ({ value: y, label: String(y) }))}
  />
  <Select
    bind:value={params.office}
    options={OFFICES.map((o) => ({
      value: o,
      label: initCap(o),
      disabled: o === "house" || o === "senate",
    }))}
    style="min-width: 6.5rem"
  />
  <Select
    bind:value={params.districtId}
    disabled={districtIdSelectorDisabled}
    options={[
      { value: "", label: "All Districts" },
      ...availableDistrictIds.map((d) => ({
        value: d,
        label: `District ${d}`,
      })),
    ]}
    style="min-width: 7rem"
  />
  <Select
    bind:value={params.party}
    options={[
      { value: undefined, label: "Any Party" },
      ...PARTIES.map((p) => ({ value: p, label: p })),
    ]}
    style="min-width: 6.5rem"
  />
</div>

<style lang="scss">
  .state-page__controls {
    display: flex;
    gap: 0.4rem;
    align-items: center;
  }

  @media (max-width: 768px) {
    .state-page__controls {
      width: 100%;
      flex-wrap: wrap;
    }
  }
</style>
