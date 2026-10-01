<script lang="ts">
  import { chartState } from "../../lib/chartState.svelte.js";
  import { getStateValue } from "../../lib/values.js";
  import { dimensionsStateWinner } from "../../lib/elections.js";
  import {
    scenarioNames,
    scenarioDescriptions,
    valueNames,
    valueDescriptions,
    validPopVars,
  } from "../../lib/manifest.js";
  import InfoLink from "../InfoLink.svelte";

  let { stateName, statePo }: { stateName: string; statePo: string } = $props();

  const CURRENT_YEAR = new Date().getFullYear();

  const value = $derived(
    getStateValue(
      chartState.scenario,
      chartState.year,
      statePo.toUpperCase(),
      chartState.value,
      (validPopVars[chartState.value] ?? []).length > 0
        ? chartState.popVar
        : undefined,
    ),
  );

  const isRealOutcome = $derived((chartState.scenario as string) === "p3");
  const isFuture = $derived(chartState.year > CURRENT_YEAR);

  const tense = $derived(
    isRealOutcome
      ? isFuture
        ? "will be"
        : "was"
      : isFuture
        ? "would be"
        : "would have been",
  );

  const isWVV = $derived(chartState.value === "wvv");

  // TODO: when P3 district selection is implemented, this must use the district-level winner
  // rather than the statewide winner — ME-2 and NE-2 flip the winning party relative to their state.
  const winningParty = $derived(
    dimensionsStateWinner[String(chartState.year)]?.[statePo.toUpperCase()] ??
      null,
  );

  // chartState.party is title-cased ("Democrat"); normalize to lowercase for comparison
  const selectedPartyKey = $derived(
    chartState.party ? chartState.party.toLowerCase() : null,
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

  function formatValue(v: number): string {
    if (v === 0) return "0";
    const s = v.toFixed(3).replace(/\.?0+$/, "");
    return v < 1 ? s.slice(1) : s;
  }
</script>

<div class="value-card">
  <p class="subject">
    in <strong>{chartState.year}</strong>,
    {#if isWVV && effectivePartyKey}
      {#if effectivePartyKey === "other"}
        a <strong>Third Party</strong> vote in <strong>{stateName}</strong>
      {:else}
        a <strong
          >{effectivePartyKey.charAt(0).toUpperCase() +
            effectivePartyKey.slice(1)}'s</strong
        >
        vote in <strong>{stateName}</strong>
      {/if}
    {:else if chartState.party}
      {#if chartState.party === "Other"}
        a <strong>Third Party</strong> vote in <strong>{stateName}</strong>
      {:else}
        a <strong>{chartState.party}'s</strong> vote in
        <strong>{stateName}</strong>
      {/if}
    {:else}
      a vote in <strong>{stateName}</strong>
    {/if}
    <br />
    {tense} worth
  </p>

  {#if displayValue !== null}
    <p class="value">{formatValue(displayValue)}</p>
  {:else}
    <p class="value value--empty">—</p>
  {/if}

  {#if displayValue !== 0 && displayValue !== null}
    <p class="relative-label">
      {displayValue > 1 ? "times more than" : "of"} the nationwide average
    </p>
    <div class="sep" aria-hidden="true">—</div>
  {/if}

  <p class="value-type">
    as determined by <InfoLink
      text={valueNames[chartState.value]}
      description={valueDescriptions[chartState.value]}
      href={`${import.meta.env.BASE_URL}about/definitions/`}
    />
  </p>

  {#if !isRealOutcome}
    <p class="scenario">
      in a <InfoLink
        text={scenarioNames[chartState.scenario]}
        description={scenarioDescriptions[chartState.scenario]}
        href={`${import.meta.env.BASE_URL}about/scenarios/`}
      /> scenario
    </p>
  {/if}

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

  .wvv-auto-label {
    font-size: 0.7em;
    font-weight: normal;
    color: variables.$medium-gray;
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
