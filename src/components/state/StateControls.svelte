<script lang="ts">
  import { untrack } from "svelte";
  import {
    officesByName,
    dimensionsStateWinner,
    getDistrictDimension,
  } from "../../lib/elections";
  import type { StatePO } from "../../lib/states.js";
  import { chartState } from "../../lib/chartState.svelte.js";
  import {
    valueNames,
    popVarNames,
    defaultValue,
    defaultPopVar,
    getValidForYear,
  } from "../../lib/manifest.js";
  import { getDistrictsForState } from "../../lib/values.js";
  import type { ValueType, PopVar, Scenario } from "../../lib/values.js";
  import { getAvailableDistrictIds } from "../../lib/districts.js";
  import type { DistrictData } from "../../lib/districts.js";
  import Select from "../Select.svelte";

  type Props = {
    years: number[];
    offices: string[];
    statePO?: StatePO;
    districtData?: DistrictData | null;
  };

  let {
    years,
    offices,
    statePO = "",
    districtData = null,
  }: Props = $props();

  const parties = ["Democrat", "Republican", "Other"];

  const _urlParams =
    typeof window !== "undefined"
      ? new URLSearchParams(window.location.search)
      : null;
  const _election = _urlParams?.get("election") ?? null;
  const [_yearParam, _officeParam] = _election
    ? _election.split("-")
    : [null, null];

  // Apply chartState fields from URL before effects run
  if (_urlParams) {
    const scenarioParam = _urlParams.get("scenario");
    if (
      scenarioParam === "p1" ||
      scenarioParam === "p2" ||
      scenarioParam === "p3" ||
      scenarioParam === "p4" ||
      scenarioParam === "p5"
    )
      chartState.scenario = scenarioParam as Scenario;
    const valueParam = _urlParams.get("value");
    if (valueParam && valueParam in valueNames)
      chartState.value = valueParam as ValueType;
    const popParam = _urlParams.get("pop");
    if (popParam && popParam in popVarNames)
      chartState.popVar = popParam as PopVar;
    const sortParam = _urlParams.get("sort");
    if (sortParam === "alpha" || sortParam === "value")
      chartState.sort = sortParam;
    const districtParam = _urlParams.get("district");
    if (districtParam) chartState.district = districtParam;
    const districtIdParam = _urlParams.get("districtId");
    if (districtIdParam) chartState.districtId = districtIdParam;
  }

  const _initialYear = (() => {
    if (_yearParam && years.includes(Number(_yearParam))) return _yearParam;
    const now = new Date().getFullYear();
    return String(years.find((y) => y <= now) ?? years[0] ?? 2024);
  })();
  const _initialOffice = (() => {
    if (_officeParam) {
      const displayName = Object.entries(officesByName).find(
        ([, v]) => v === _officeParam,
      )?.[0];
      if (displayName) return displayName;
    }
    return offices[0] ?? "";
  })();
  const _partyParam = _urlParams?.get("party") ?? null;

  let selectedYear = $state(_initialYear);
  let selectedOffice = $state(_initialOffice);
  let selectedParty = $state(
    _partyParam
      ? (parties.find((p) => p.toLowerCase() === _partyParam.toLowerCase()) ??
          "")
      : "",
  );

  // Sync local selectors → chartState
  $effect(() => {
    chartState.year = Number(selectedYear);
  });
  $effect(() => {
    chartState.office = officesByName[selectedOffice] ?? "president";
  });
  $effect(() => {
    chartState.party = selectedParty;
  });

  // Auto-select winning party when WVV is chosen
  $effect(() => {
    if (chartState.value !== "wvv") return;
    untrack(() => {
      const year = chartState.year;
      const districtId = chartState.districtId;
      const scenario = chartState.scenario;
      let winner: string | null = null;
      if (scenario === "p3" && districtId) {
        winner =
          getDistrictDimension(year, statePO, districtId)?.winningParty ??
          null;
      }
      if (!winner) {
        winner = dimensionsStateWinner[String(year)]?.[statePO] ?? null;
      }
      if (winner) {
        const display = winner.charAt(0).toUpperCase() + winner.slice(1);
        if (parties.includes(display)) selectedParty = display;
      }
    });
  });

  // Congressional districts for this state page, keyed by year
  const availableDistrictIds = $derived(
    districtData
      ? getAvailableDistrictIds(districtData, Number(selectedYear))
      : [],
  );

  const showDistrictIdSelector = true;
  const districtIdSelectorDisabled = $derived(
    availableDistrictIds.length === 0 ||
      (availableDistrictIds.length === 1 && availableDistrictIds[0] === "AL") ||
      Number(selectedYear) < 2012,
  );

  // Reset districtId when it becomes invalid (year change, at-large, etc.)
  $effect(() => {
    const year = Number(selectedYear);
    const available = availableDistrictIds;
    const isAtLarge = available.length === 1 && available[0] === "AL";
    const curDistrict = untrack(() => chartState.districtId);
    if (!curDistrict) return;
    if (
      year < 2012 ||
      available.length === 0 ||
      isAtLarge ||
      !available.includes(curDistrict)
    ) {
      chartState.districtId = "";
    }
  });

  // Available districts for this state under the current scenario/year
  const availableDistricts = $derived(
    statePO
      ? getDistrictsForState(chartState.scenario, chartState.year, statePO)
      : [],
  );

  // Reset district when scenario doesn't support districts or district is no longer valid
  $effect(() => {
    const scenario = chartState.scenario;
    const available = availableDistricts;
    if (scenario !== "p3" && scenario !== "p4") {
      if (untrack(() => chartState.district)) chartState.district = "";
    } else if (
      chartState.district &&
      !available.includes(chartState.district)
    ) {
      chartState.district = "";
    }
  });

  // Snap value/popVar to a valid combo when year or scenario changes
  $effect(() => {
    const year = Number(selectedYear);
    const { values, popVarsFor } = getValidForYear(year, chartState.scenario);
    const curVal = untrack(() => chartState.value);
    const curPop = untrack(() => chartState.popVar);
    const nextVal = values.includes(curVal) ? curVal : (values[0] ?? "av");
    const pops = popVarsFor(nextVal);
    const nextPop =
      pops.length === 0 || pops.includes(curPop) ? curPop : pops[0];
    if (nextVal !== curVal) chartState.value = nextVal;
    if (nextPop !== curPop) chartState.popVar = nextPop;
  });

  // Reveal page sections hidden by [data-state-loading] once correct values are applied.
  $effect(() => {
    document.documentElement.removeAttribute("data-state-loading");
  });

  // Write URL whenever any relevant state changes (skip first run to let URL read happen first)
  let urlSyncReady = false;
  // Once any non-default setting has appeared, always write all settings (even if reverted to default)
  let settingsWritten = false;
  $effect(() => {
    void [
      selectedYear,
      selectedOffice,
      selectedParty,
      chartState.scenario,
      chartState.value,
      chartState.popVar,
      chartState.sort,
      chartState.district,
      chartState.districtId,
    ];
    if (!urlSyncReady) {
      urlSyncReady = true;
      return;
    }
    syncURL();
  });

  function syncURL() {
    const officeKey = officesByName[selectedOffice] ?? "president";
    const newUrl = new URL(window.location.href);
    newUrl.searchParams.set("election", `${selectedYear}-${officeKey}`);

    if (selectedParty) newUrl.searchParams.set("party", selectedParty);
    else newUrl.searchParams.delete("party");

    if (chartState.scenario !== "p2")
      newUrl.searchParams.set("scenario", chartState.scenario);
    else newUrl.searchParams.delete("scenario");

    if (chartState.district)
      newUrl.searchParams.set("district", chartState.district);
    else newUrl.searchParams.delete("district");

    if (chartState.districtId)
      newUrl.searchParams.set("districtId", chartState.districtId);
    else newUrl.searchParams.delete("districtId");

    const defPop = defaultPopVar[chartState.value];
    const hasNonDefault =
      chartState.value !== defaultValue ||
      (defPop != null && chartState.popVar !== defPop) ||
      chartState.sort !== "alpha";
    if (hasNonDefault) settingsWritten = true;

    if (settingsWritten) {
      newUrl.searchParams.set("value", chartState.value);
      if (defPop != null) newUrl.searchParams.set("pop", chartState.popVar);
      else newUrl.searchParams.delete("pop");
      if (chartState.sort !== "alpha")
        newUrl.searchParams.set("sort", chartState.sort);
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
    bind:value={selectedYear}
    options={years.map((y) => ({ value: String(y), label: String(y) }))}
  />
  <Select
    bind:value={selectedOffice}
    options={offices.map((o) => ({
      value: o,
      label: o,
      disabled: o === "House" || o === "Senate",
    }))}
    style="min-width: 6.5rem"
  />
  {#if showDistrictIdSelector}
    <Select
      bind:value={chartState.districtId}
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
  {/if}
  <Select
    bind:value={selectedParty}
    options={[
      { value: "", label: "Any Party" },
      ...parties.map((p) => ({ value: p, label: p })),
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
