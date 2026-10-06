<script lang="ts">
  import { untrack } from "svelte";
  import {
    officesByName,
    dimensionsStateWinner,
    getDistrictDimension,
    OFFICES,
  } from "../../lib/elections";
  import type { StatePO } from "../../lib/states.js";
  import {
    defaultStatePageParams,
    fromUrlParams,
    statePageParams,
  } from "../../lib/statePageParams.svelte.js";
  import {
    defaultValue,
    defaultPopVar,
    getValidForYear,
  } from "../../lib/manifest.js";
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
  };

  let { years, statePO = "", districtData = null }: Props = $props();

  // Init from url query params if available
  if (typeof window !== "undefined") {
    Object.assign(
      statePageParams,
      fromUrlParams(new URLSearchParams(window.location.search)),
    );
  }

  // Auto-select winning party when WVV is chosen
  $effect(() => {
    if (statePageParams.value !== "wvv") return;
    untrack(() => {
      const year = statePageParams.year;
      const districtId = statePageParams.districtId;
      const scenario = statePageParams.scenario;
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
        statePageParams.party = winningParty;
      }
    });
  });

  // Congressional districts for this state page, keyed by year
  const availableDistrictIds = $derived(
    districtData
      ? getAvailableDistrictIds(districtData, statePageParams.year)
      : [],
  );

  const districtIdSelectorDisabled = $derived(
    availableDistrictIds.length === 0 ||
      (availableDistrictIds.length === 1 && availableDistrictIds[0] === "AL") ||
      statePageParams.year < 2012,
  );

  // Reset districtId when it becomes invalid (year change, at-large, etc.)
  $effect(() => {
    const year = statePageParams.year;
    const available = availableDistrictIds;
    const isAtLarge = available.length === 1 && available[0] === "AL";
    const curDistrict = untrack(() => statePageParams.districtId);
    if (!curDistrict) return;
    if (
      year < 2012 ||
      available.length === 0 ||
      isAtLarge ||
      !available.includes(curDistrict)
    ) {
      statePageParams.districtId = "";
    }
  });

  // Available districts for this state under the current scenario/year
  const availableDistricts = $derived(
    statePO
      ? getDistrictsForState(
          statePageParams.scenario,
          statePageParams.year,
          statePO,
        )
      : [],
  );

  // Reset district when scenario doesn't support districts or district is no longer valid
  $effect(() => {
    const scenario = statePageParams.scenario;
    const available = availableDistricts;
    if (scenario !== "p3" && scenario !== "p4") {
      if (untrack(() => statePageParams.district))
        statePageParams.district = "";
    } else if (
      statePageParams.district &&
      !available.includes(statePageParams.district)
    ) {
      statePageParams.district = "";
    }
  });

  // Snap value/popVar to a valid combo when year or scenario changes
  $effect(() => {
    const { values, popVarsFor } = getValidForYear(
      statePageParams.year,
      statePageParams.scenario,
    );
    const curVal = untrack(() => statePageParams.value);
    const curPop = untrack(() => statePageParams.popVar);
    const nextVal = values.includes(curVal) ? curVal : (values[0] ?? "av");
    const pops = popVarsFor(nextVal);
    const nextPop =
      pops.length === 0 || pops.includes(curPop) ? curPop : pops[0];
    if (nextVal !== curVal) statePageParams.value = nextVal;
    if (nextPop !== curPop) statePageParams.popVar = nextPop;
  });

  // Reveal page sections hidden by [data-state-loading] once correct values are applied.
  $effect(() => {
    document.documentElement.removeAttribute("data-state-loading");
  });

  // Write URL whenever any relevant state changes (skip first run to let URL read happen first)
  let urlSyncReady = false;
  let settingsWritten = false;
  $effect(() => {
    void [
      statePageParams.year,
      statePageParams.office,
      statePageParams.party,
      statePageParams.scenario,
      statePageParams.value,
      statePageParams.popVar,
      statePageParams.sort,
      statePageParams.district,
      statePageParams.districtId,
    ];
    if (!urlSyncReady) {
      urlSyncReady = true;
      return;
    }
    syncURL();
  });

  function syncURL() {
    const newUrl = new URL(window.location.href);

    if (
      statePageParams.year != defaultStatePageParams.year ||
      statePageParams.office != defaultStatePageParams.office
    ) {
      newUrl.searchParams.set(
        "election",
        `${statePageParams.year}-${statePageParams.office}`,
      );
    } else {
      newUrl.searchParams.delete("election");
    }

    if (statePageParams.party)
      newUrl.searchParams.set("party", statePageParams.party);
    else newUrl.searchParams.delete("party");

    if (statePageParams.scenario !== defaultStatePageParams.scenario)
      newUrl.searchParams.set("scenario", statePageParams.scenario);
    else newUrl.searchParams.delete("scenario");

    if (statePageParams.district)
      newUrl.searchParams.set("district", statePageParams.district);
    else newUrl.searchParams.delete("district");

    if (statePageParams.districtId)
      newUrl.searchParams.set("districtId", statePageParams.districtId);
    else newUrl.searchParams.delete("districtId");

    const defPop = defaultPopVar[statePageParams.value];
    const hasNonDefault =
      statePageParams.value !== defaultValue ||
      (defPop != null && statePageParams.popVar !== defPop) ||
      statePageParams.sort !== "alpha";
    if (hasNonDefault) settingsWritten = true;

    if (settingsWritten) {
      newUrl.searchParams.set("value", statePageParams.value);
      if (defPop != null)
        newUrl.searchParams.set("pop", statePageParams.popVar);
      else newUrl.searchParams.delete("pop");
      if (statePageParams.sort !== "alpha")
        newUrl.searchParams.set("sort", statePageParams.sort);
      else newUrl.searchParams.delete("sort");
    } else {
      newUrl.searchParams.delete("value");
      newUrl.searchParams.delete("pop");
      newUrl.searchParams.delete("sort");
    }

    window.history.replaceState({}, "", newUrl);
  }
</script>

<div class="state-page__controls">
  <Select
    bind:value={statePageParams.year}
    options={years.map((y) => ({ value: y, label: String(y) }))}
  />
  <Select
    bind:value={statePageParams.office}
    options={OFFICES.map((o) => ({
      value: o,
      label: initCap(o),
      disabled: o === "house" || o === "senate",
    }))}
    style="min-width: 6.5rem"
  />
  <Select
    bind:value={statePageParams.districtId}
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
    bind:value={statePageParams.party}
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
