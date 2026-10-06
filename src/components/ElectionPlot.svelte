<script lang="ts">
  import * as Plot from "@observablehq/plot";
  import { getPlotRows } from "../lib/values.js";
  import type { Scenario, ValueType, PopVar } from "../lib/values.js";
  import type { StatePO } from "../lib/states.js";
  import {
    valueNames,
    validValues,
    validPopVars,
    defaultPopVar,
  } from "../lib/manifest.js";
  import { partyColors } from "../lib/party.js";

  let {
    scenario = "p2" as Scenario,
    year = 2024,
    focusStatePO = "" as StatePO,
    value = "av" as ValueType,
    popVar = undefined as PopVar | undefined,
    sort = $bindable("alpha" as "alpha" | "value"),
  }: {
    scenario?: Scenario;
    year?: number;
    focusStatePO?: StatePO;
    value?: ValueType;
    popVar?: PopVar;
    sort?: "alpha" | "value";
  } = $props();

  const effectivePopVar = $derived(
    (validPopVars[value] ?? []).length > 0 ? popVar : undefined,
  );

  let plotEl: HTMLDivElement | undefined;
  let optionsEl: HTMLDivElement | undefined;
  let width = $state(600);
  let optionsOpen = $state(false);
  const isHorizontal = $derived(width < 520);

  $effect(() => {
    if (!optionsOpen) return;
    const handler = (e: MouseEvent) => {
      if (!optionsEl?.contains(e.target as Node)) {
        optionsOpen = false;
        document.dispatchEvent(new CustomEvent("ui:close"));
      }
    };
    document.addEventListener("pointerdown", handler);
    return () => document.removeEventListener("pointerdown", handler);
  });

  $effect(() => {
    const handler = () => {
      plotEl
        ?.querySelector("svg")
        ?.dispatchEvent(new PointerEvent("pointerleave", { bubbles: true }));
    };
    document.addEventListener("ui:close", handler);
    return () => document.removeEventListener("ui:close", handler);
  });

  $effect(() => {
    if (!plotEl) return;

    const plotRows = getPlotRows(
      scenario,
      year,
      focusStatePO,
      value,
      effectivePopVar,
    );
    const hasData = plotRows.some((r) => r.value !== null);

    const horizontal = isHorizontal;
    const fill = (d: (typeof plotRows)[0]) =>
      partyColors[initCap(d.winningParty ?? "unknown")];
    const fillOpacity = (d: (typeof plotRows)[0]) =>
      !focusStatePO || d.isFocus ? 1 : 0.38;
    const formatVal = (v: number | null) => (v !== null ? v.toFixed(3) : "");
    const initCap = (s: string | null) =>
      s ? s.charAt(0).toUpperCase() + s.slice(1) : "";

    type AugRow = (typeof plotRows)[0];

    const buildStateUrl = (statePO: StatePO): string | null => {
      if (year <= 0) return null;
      const base = import.meta.env.BASE_URL;
      const params = new URLSearchParams();
      params.set("election", `${year}-president`);
      if (scenario !== "p2") params.set("scenario", scenario);
      params.set("value", value);
      const defPop = defaultPopVar[value];
      if (defPop != null && effectivePopVar != null)
        params.set("pop", effectivePopVar);
      if (sort !== "alpha") params.set("sort", sort);
      return `${base}states/${statePO.toLowerCase()}/?${params}`;
    };

    const barOpts = {
      fill,
      fillOpacity,
      href: (d: AugRow) => buildStateUrl(d.statePO),
    };

    const isWvv = value === "wvv";
    const tooltipValue = (d: AugRow) =>
      !isWvv
        ? formatVal(d.value)
        : `
• ${initCap(d.winningParty)}: ${formatVal(d.value)}
• ${d.winningParty == "Democrat" ? "Republican" : "Democrat"}: 0
• Other: 0`;
    const tooltip = (d: AugRow) =>
      `State: ${d.state}\n\n${valueNames[value]}: ${tooltipValue(d)}`;

    const axisLabel = valueNames[value] + (isWvv ? " (winning party)" : "");
    const fontStyle =
      "font-family: Inter, Roboto, 'Helvetica Neue', Arial, sans-serif;";

    const maxVal = hasData ? Math.max(...plotRows.map((r) => r.value ?? 0)) : 0;
    const valueDomain: [number, number] = [0, Math.max(3, maxVal)];

    const effectiveSort = hasData ? sort : "alpha";
    const xSort = effectiveSort === "value" ? { x: "y" } : { x: "x" };
    const ySort = effectiveSort === "value" ? { y: "-x" } : { y: "y" };

    const chart = !horizontal
      ? Plot.plot({
          width,
          height: 300,
          marginBottom: 52,
          style: fontStyle,
          x: {
            label: null,
            padding: 0.15,
            domain: hasData ? undefined : plotRows.map((r) => r.statePO),
          },
          y: {
            label: axisLabel,
            labelAnchor: "center",
            labelArrow: "none",
            grid: true,
            domain: valueDomain,
          },
          marks: [
            Plot.axisX({ tickRotate: -55, fontSize: 9 }),
            Plot.barY(plotRows, {
              x: "statePO",
              y: "value",
              sort: xSort,
              ...barOpts,
            }),
            Plot.ruleY([1], { stroke: "#999", strokeDasharray: "4 2" }),
            Plot.tip(
              plotRows,
              Plot.pointerX({
                x: "statePO",
                y: "value",
                sort: xSort,
                title: tooltip,
              }),
            ),
          ],
        })
      : Plot.plot({
          width,
          height: 600,
          marginLeft: 36,
          style: fontStyle,
          x: { label: axisLabel, grid: true, domain: valueDomain },
          y: {
            label: null,
            domain: hasData ? undefined : plotRows.map((r) => r.statePO),
          },
          marks: [
            Plot.axisY({ fontSize: 8, tickSize: 0 }),
            Plot.barX(plotRows, {
              y: "statePO",
              x: "value",
              sort: ySort,
              ...barOpts,
            }),
            Plot.tip(
              plotRows,
              Plot.pointerY({
                y: "statePO",
                x: "value",
                sort: ySort,
                title: tooltip,
              }),
            ),
            Plot.ruleX([1], { stroke: "#999", strokeDasharray: "4 2" }),
          ],
        });

    plotEl.innerHTML = "";
    plotEl.appendChild(chart);
  });
</script>

<div class="plot-outer" class:wide={!isHorizontal}>
  <div class="plot-content">
    <div bind:this={plotEl} bind:clientWidth={width}></div>
  </div>
  <div class="plot-toolbar">
    <div class="toolbar-item" bind:this={optionsEl}>
      <button
        class="toolbar-item__btn"
        class:active={optionsOpen}
        onclick={() => (optionsOpen = !optionsOpen)}
        aria-label="Sort options"
        aria-expanded={optionsOpen}>{isHorizontal ? "⇅" : "⇄"}</button
      >
      {#if optionsOpen}
        <div
          class="toolbar-item__panel"
          role="dialog"
          aria-label="Sort options"
        >
          <button
            class="toolbar-item__choice"
            class:selected={sort === "value"}
            onmousedown={() => {
              sort = "value";
              optionsOpen = false;
              document.dispatchEvent(new CustomEvent("ui:close"));
            }}>by value</button
          >
          <button
            class="toolbar-item__choice"
            class:selected={sort === "alpha"}
            onmousedown={() => {
              sort = "alpha";
              optionsOpen = false;
              document.dispatchEvent(new CustomEvent("ui:close"));
            }}>A–Z</button
          >
        </div>
      {/if}
    </div>
  </div>
</div>

<style lang="scss">
  @use "../styles/variables.scss";

  $border-color: #d0d0d0;
  $btn-size: 26px;

  .plot-outer {
    display: flex;
    align-items: flex-start;
    width: 100%;

    &.wide {
      align-items: flex-end;
    }
  }

  .plot-content {
    flex: 1;
    min-width: 0;
    border: 0.5px solid $border-color;
    border-radius: 4px;
    min-height: 180px;
    padding: 0 12px;

    :global(svg) {
      display: block;
    }

    :global(svg a) {
      cursor: pointer;
    }

    :global(.no-data) {
      color: variables.$medium-gray;
      text-align: center;
      padding: 2rem 0;
      font-size: 0.9rem;
    }
  }

  .plot-toolbar {
    display: flex;
    flex-direction: column;
    margin-left: 4px;
    gap: 2px;
  }

  .toolbar-item {
    position: relative;

    &__btn {
      width: $btn-size;
      height: $btn-size;
      display: flex;
      align-items: center;
      justify-content: center;
      background: none;
      border: none;
      border-radius: 3px;
      font-size: 0.7rem;
      color: variables.$medium-gray;
      cursor: pointer;
      padding: 0;

      &:hover,
      &.active {
        background: variables.$light-gray;
        color: variables.$dark-gray;
      }
    }

    &__panel {
      position: absolute;
      top: calc(100% + 4px);
      right: 0;
      background: variables.$white;
      border: 1px solid $border-color;
      border-radius: 4px;
      box-shadow: 0 3px 12px rgba(0, 0, 0, 0.1);
      padding: 0.3rem 0.4rem;
      z-index: 200;
      display: flex;
      flex-direction: column;
      gap: 1px;
      white-space: nowrap;
    }

    &__choice {
      font-size: 0.68rem;
      padding: 3px 8px;
      border: none;
      border-radius: 3px;
      background: none;
      color: variables.$medium-gray;
      cursor: pointer;
      text-align: left;

      &:hover {
        background: variables.$light-gray;
        color: variables.$dark-gray;
      }

      &.selected {
        color: variables.$royal-blue;
        font-weight: 600;
      }
    }
  }
</style>
