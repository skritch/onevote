<script lang="ts">
  import { statePageParams } from "../../lib/statePageParams.svelte.js";
  import { getStateValue, getDistrictDimension } from "../../lib/values.js";
  import { dimensionsStateWinner } from "../../lib/elections.js";
  import type { Party } from "../../lib/elections.js";
  import type { State } from "../../lib/states.js";
  import {
    scenarioNames,
    scenarioDescriptions,
    valueNames,
    valueDescriptions,
    validPopVars,
  } from "../../lib/manifest.js";
  import InfoLink from "../InfoLink.svelte";

  let { stateName, statePO }: State = $props();

  const CURRENT_YEAR = new Date().getFullYear();

  const value = $derived(
    getStateValue(
      statePageParams.scenario,
      statePageParams.year,
      statePO,
      statePageParams.value,
      (validPopVars[statePageParams.value] ?? []).length > 0
        ? statePageParams.popVar
        : undefined,
      // P3/P4 define district-level values; other scenarios are state-level only
      statePageParams.scenario === "p3" || statePageParams.scenario === "p4"
        ? statePageParams.districtId || statePageParams.district || undefined
        : statePageParams.district || undefined,
    ),
  );

  const isRealOutcome = $derived((statePageParams.scenario as string) === "p3");
  const isFuture = $derived(statePageParams.year > CURRENT_YEAR);

  const tense = $derived(
    isRealOutcome
      ? isFuture
        ? "will be"
        : "was"
      : isFuture
        ? "will be"
        : "would have been",
  );

  const isWVV = $derived(statePageParams.value === "wvv");

  // For P3 with a district, use district-level winner — ME-2 and NE-2 differ from their state.
  const winningParty = $derived.by((): Party | null => {
    const stateWinner =
      dimensionsStateWinner[String(statePageParams.year)]?.[statePO] ?? null;
    if (statePageParams.scenario === "p3" && statePageParams.districtId) {
      const distDim = getDistrictDimension(
        statePageParams.year,
        statePO,
        statePageParams.districtId,
      );
      return (distDim?.winningParty as Party | null) ?? stateWinner;
    }
    return stateWinner;
  });

  // statePageParams.party is title-cased ("Democrat"); normalize to lowercase for comparison
  const selectedPartyKey = $derived(
    statePageParams.party ? statePageParams.party.toLowerCase() : null,
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
    const allParties = ["democrat", "republican", "other"] as const;
    return allParties
      .filter((p) => p !== effectivePartyKey)
      .map((p) => ({
        label:
          p === "other"
            ? "third party"
            : p.charAt(0).toUpperCase() + p.slice(1),
        apostrophe: p !== "other",
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
    statePageParams.districtId
      ? `${stateName}'s ${districtLabel(statePageParams.districtId)} district`
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
    in <strong>{statePageParams.year}</strong>, the value of
    {#if isWVV && effectivePartyKey}
      {#if effectivePartyKey === "other"}
        a <strong>Third Party</strong> vote in <strong>{locationLabel}</strong>
      {:else}
        a <strong
          >{effectivePartyKey.charAt(0) + effectivePartyKey.slice(1)}'s</strong
        >
        vote in <strong>{locationLabel}</strong>
      {/if}
    {:else if statePageParams.party}
      {#if statePageParams.party === "Other"}
        a <strong>Third Party</strong> vote in <strong>{locationLabel}</strong>
      {:else}
        a <strong>{statePageParams.party}'s</strong> vote in
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
        text={scenarioNames[statePageParams.scenario]}
        description={scenarioDescriptions[statePageParams.scenario]}
        href={`${import.meta.env.BASE_URL}about/scenarios/`}
      /> scenario
    </p>
  {/if}

  <p class="value-type">
    as determined by <InfoLink
      text={valueNames[statePageParams.value]}
      description={valueDescriptions[statePageParams.value]}
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
