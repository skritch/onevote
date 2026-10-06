<script lang="ts">
  import type { StatePageParams } from "../../lib/statePageParams.js";
  import { getStateValue, getDistrictDimension } from "../../lib/values.js";
  import { dimensionsStateWinner } from "../../lib/elections.js";
  import type { State } from "../../lib/states.js";
  import {
    scenarioNames,
    scenarioDescriptions,
    valueNames,
    valueDescriptions,
    validPopVars,
  } from "../../lib/manifest.js";
  import InfoLink from "../InfoLink.svelte";
  import { PARTIES, type Party } from "../../lib/party.js";

  let { stateName, statePO, params }: State & { params: StatePageParams } =
    $props();

  const CURRENT_YEAR = new Date().getFullYear();

  const value = $derived(
    getStateValue(
      params.scenario,
      params.year,
      statePO,
      params.value,
      (validPopVars[params.value] ?? []).length > 0 ? params.popVar : undefined,
      // P3/P4 define district-level values; other scenarios are state-level only
      params.scenario === "p3" || params.scenario === "p4"
        ? params.districtId || params.district || undefined
        : params.district || undefined,
    ),
  );

  const isRealOutcome = $derived((params.scenario as string) === "p3");
  const isFuture = $derived(params.year > CURRENT_YEAR);

  const tense = $derived(
    isRealOutcome
      ? isFuture
        ? "will be"
        : "was"
      : isFuture
        ? "will be"
        : "would have been",
  );

  const isWVV = $derived(params.value === "wvv");

  // For P3 with a district, use district-level winner — ME-2 and NE-2 differ from their state.
  const winningParty = $derived.by((): Party | null => {
    const stateWinner =
      dimensionsStateWinner[String(params.year)]?.[statePO] ?? null;
    if (params.scenario === "p3" && params.districtId) {
      const distDim = getDistrictDimension(
        params.year,
        statePO,
        params.districtId,
      );
      return distDim?.winningParty ?? stateWinner;
    }
    return stateWinner;
  });

  // params.party is title-cased ("Democrat"); normalize to lowercase for comparison
  const selectedPartyKey = $derived(
    params.party ? params.party.toLowerCase() : null,
  );

  // For WVV with no party selected, auto-use the winning party
  const effectivePartyKey = $derived(
    isWVV && !selectedPartyKey ? winningParty : selectedPartyKey,
  );

  // For WVV, any non-winning party has value 0
  // TODO: don't hardcode this, read it from the source data
  const displayValue = $derived(
    isWVV && effectivePartyKey !== winningParty ? 0 : value,
  );

  // Build a list of parties not being shown in the main display (for the WVV note)
  const wvvOtherParties = $derived.by(() => {
    if (!isWVV || !winningParty)
      return [] as Array<{
        label: string;
        apostrophe: boolean;
        value: number | null;
        isWinner: boolean;
      }>;
    return PARTIES.filter((p) => p !== effectivePartyKey).map((p) => ({
      label: p === "Other" ? "third party" : p,
      apostrophe: p !== "Other",
      value: p === winningParty ? value : 0,
      isWinner: p === winningParty,
    }));
  });

  function districtLabel(d: string): string {
    if (d.toUpperCase() === "AL") return "at-large";
    const n = parseInt(d);
    if (isNaN(n)) return d;
    const suffix = n === 1 ? "st" : n === 2 ? "nd" : n === 3 ? "rd" : "th";
    return `${n}${suffix}`;
  }

  const locationLabel = $derived(
    params.districtId
      ? `${stateName}'s ${districtLabel(params.districtId)} district`
      : stateName,
  );

  function formatValue(v: number): string {
    if (v === 0) return "0";
    const s = v.toFixed(2);
    return s;
  }
</script>

<div class="value-card">
  <p class="subject">
    in <strong>{params.year}</strong>, the value of
    {#if isWVV && effectivePartyKey}
      {#if effectivePartyKey === "other"}
        a <strong>Third Party</strong> vote in <strong>{locationLabel}</strong>
      {:else}
        a <strong
          >{effectivePartyKey.charAt(0) + effectivePartyKey.slice(1)}'s</strong
        >
        vote in <strong>{locationLabel}</strong>
      {/if}
    {:else if params.party}
      {#if params.party === "Other"}
        a <strong>Third Party</strong> vote in <strong>{locationLabel}</strong>
      {:else}
        a <strong>{params.party}'s</strong> vote in
        <strong>{locationLabel}</strong>
      {/if}
    {:else}
      a vote in <strong>{locationLabel}</strong>
    {/if}
    {tense}
  </p>

  {#if displayValue !== null}
    <p class="value">{formatValue(displayValue)}</p>
  {:else}
    <p class="value value--empty">—</p>
  {/if}

  <!-- {#if displayValue !== 0 && displayValue !== null}
    {displayValue > 1 ? "times more than" : "as much as"} the nationwide average
  {/if} -->
  <p class="relative-label">compared to a nationwide average of 1.00</p>
  <div class="sep" aria-hidden="true">—</div>

  {#if !isRealOutcome}
    <p class="scenario">
      in a <InfoLink
        text={scenarioNames[params.scenario]}
        description={scenarioDescriptions[params.scenario]}
        href={`${import.meta.env.BASE_URL}about/scenarios/`}
      /> scenario
    </p>
  {/if}

  <p class="value-type">
    as determined by <InfoLink
      text={valueNames[params.value]}
      description={valueDescriptions[params.value]}
      href={`${import.meta.env.BASE_URL}about/definitions/`}
    />
  </p>

  {#if wvvOtherParties.length > 0}
    <div class="sep" aria-hidden="true">—</div>
    <div class="wvv-others">
      {#each wvvOtherParties as other}
        <p class="wvv-other">
          A {other.label}{other.apostrophe ? "'s" : ""}
          vote {tense} worth
          <strong
            >{other.value !== null ? formatValue(other.value) : "—"}</strong
          >
        </p>
      {/each}
    </div>
  {/if}
</div>

<style lang="scss">
  @use "../../styles/variables.scss";

  .value-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: variables.$spacing-sm variables.$spacing-md;
    background: variables.$white;
    border: 1px solid #e5e7eb;
    border-radius: variables.$border-radius;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.07);
    text-align: center;
  }

  .subject {
    strong {
      color: variables.$dark-gray;
    }
  }

  .value {
    font-size: 3.2rem;
    font-weight: 700;
    color: variables.$dark-gray;

    &--empty {
      color: variables.$medium-gray;
    }
  }

  .sep {
    font-size: 0.6rem;
    line-height: 1;
    color: #c8ccd0;
    margin: -0.15rem 0;
    user-select: none;
  }
  .value-type {
    font-size: 0.72rem;
    color: variables.$medium-gray;
  }

  .scenario {
    font-size: 0.72rem;
    color: variables.$medium-gray;
  }

  .wvv-others {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.15rem;
  }

  .wvv-other {
    font-size: 0.72rem;
    color: variables.$medium-gray;

    strong {
      color: variables.$dark-gray;
    }
  }
</style>
