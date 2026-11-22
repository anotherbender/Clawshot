"use strict";

// OBS sections, in drawing order. `quest` (older URLs) means collection, songs and rewards. Missing, empty or
// unknown selections use the defaults, which keep the compact view within about 300x1000 px: dungeon keys, the
// collection line, items, stones and medallions (songs and Checks by area are opt-in).
const TRACKER_SECTIONS = ["dungeons", "collection", "items", "songs", "rewards", "areas"];
const DEFAULT_SECTIONS = ["dungeons", "collection", "items", "rewards"];
const SECTION_ALIASES = {quest: ["collection", "songs", "rewards"]};

function parseTrackerSections(fragment) {
  const value = new URLSearchParams(fragment.replace(/^#/, "")).get("sections");
  if (!value) return DEFAULT_SECTIONS.slice();
  const selected = value.split(",").map((part) => part.trim()).flatMap((part) => SECTION_ALIASES[part] || [part]);
  if (selected.some((part) => !TRACKER_SECTIONS.includes(part))) return DEFAULT_SECTIONS.slice();
  return TRACKER_SECTIONS.filter((part) => selected.includes(part));
}

// OBS dungeon names: full, short (the default) or none; anything else is short.
const DUNGEON_NAME_MODES = ["full", "short", "none"];

function parseDungeonNames(fragment) {
  const value = new URLSearchParams(fragment.replace(/^#/, "")).get("names");
  return DUNGEON_NAME_MODES.includes(value) ? value : "short";
}

// One renderer for the app's Tracker and Checks tabs and the control-free OBS surface. All labels are text nodes.
(() => {
  const root = document.getElementById("tracker-root");
  if (!root) return;
  const standalone = document.body.dataset.tracker === "obs";
  const checksRoot = standalone ? null : document.getElementById("checks-root");
  const prefix = location.pathname.slice(0, location.pathname.lastIndexOf("/") + 1);
  const token = prefix.split("/")[2];
  const options = new URLSearchParams(location.hash.slice(1));
  // Compact (no item labels) is the default; labels=1 asks for labelled cells.
  const compact = standalone && options.get("labels") !== "1";
  const sections = new Set(standalone ? parseTrackerSections(location.hash) : TRACKER_SECTIONS);
  const dungeonNames = parseDungeonNames(location.hash);
  if (standalone && options.get("transparent") === "1") document.body.classList.add("tracker-transparent");
  let icons = options.get("icons") !== "0";
  // Labelled cells default to 4 columns (about 340 px); compact cells to 6 (about 285 px).
  const defaultColumns = compact ? 6 : 4;
  const requestedColumns = Number(options.get("columns") ?? defaultColumns);
  const columns = Number.isInteger(requestedColumns) && requestedColumns >= 1 && requestedColumns <= 8 ? requestedColumns : defaultColumns;
  if (standalone) {
    root.style.setProperty("--tracker-columns", columns);
    document.body.classList.toggle("tracker-no-labels", compact);
    document.body.dataset.dungeonNames = dungeonNames;
  }
  let lastRevision = "", pending = false, initialized = false;
  const node = (tag, cls = "", text) => {
    const el = document.createElement(tag);
    el.className = cls;
    if (text !== undefined) el.textContent = text;
    return el;
  };
  async function request(route, body) {
    const response = await fetch(prefix + "api/" + route, {
      method: body === undefined ? "GET" : "POST", credentials: "omit", cache: "no-store",
      headers: {"X-Clawshot-Token": token, ...(body === undefined ? {} : {"Content-Type": "application/json"})},
      ...(body === undefined ? {} : {body: JSON.stringify(body)}),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Tracker request failed");
    return data;
  }
  const heading = node("div", "heading");
  heading.append(node("h1", "", "Tracker"), node("p", "", "Saved inventory · keys by dungeon · no location spoilers"));
  const status = node("p", "tracker-status");
  status.setAttribute("role", "status");
  const warnings = node("div", "tracker-warnings");
  const content = node("div", "tracker-content");
  root.append(heading);
  let seedInput, saveInput, slotSelect, reveal, obsUrl, iconToggle, transparent, labelToggle, columnSelect, namesSelect;
  let ageSelect, showSelect, hideFinished, vanillaToggle, clearMarks, lastData = null;
  const sectionToggles = {};
  // Remembered in this browser only when not the default; storage may be absent (a private window).
  function stored(key, allowed, fallback) {
    try {
      const value = window.localStorage.getItem(key);
      return allowed.includes(value) ? value : fallback;
    } catch { return fallback; }
  }
  function store(key, value, fallback) {
    try {
      if (value === fallback) window.localStorage.removeItem(key);
      else window.localStorage.setItem(key, value);
    } catch { /* storage unavailable: the choice lasts until the page closes */ }
  }
  const AGE_KEY = "clawshot.tracker.age", AGES = ["either", "save", "child", "adult"];
  // Vanilla pick-ups (spec D19): shown by default (Q4).
  const VANILLA_KEY = "clawshot.tracker.vanilla";
  // Which rows the Checks tab lists: all, only open ones, or only open ones in logic.
  const SHOW_KEY = "clawshot.tracker.show", SHOWS = ["all", "open", "logic"];
  const FINISHED_KEY = "clawshot.tracker.hide-finished";
  const COLLAPSED_KEY = "clawshot.tracker.collapsed";
  function storedCollapsed() {
    try {
      const value = JSON.parse(window.localStorage.getItem(COLLAPSED_KEY) || "[]");
      return new Set(Array.isArray(value) ? value.filter((name) => typeof name === "string") : []);
    } catch { return new Set(); }
  }
  const collapsed = storedCollapsed();
  function storeCollapsed() {
    try {
      if (collapsed.size) window.localStorage.setItem(COLLAPSED_KEY, JSON.stringify([...collapsed].sort()));
      else window.localStorage.removeItem(COLLAPSED_KEY);
    } catch { /* storage unavailable */ }
  }
  function redraw() {
    lastRevision = "";
    if (lastData) render(lastData);
  }
  function checkbox(parent, text, checked, id) {
    const label = node("label");
    const input = node("input");
    input.type = "checkbox";
    input.checked = checked;
    if (id) input.id = id;
    label.append(input, document.createTextNode(" " + text));
    parent.append(label);
    return input;
  }
  function select(parent, text, id, choices, value) {
    const label = node("label", "", text + " ");
    const input = node("select");
    input.id = id;
    for (const [choice, caption] of choices) input.append(new Option(caption, choice));
    input.value = value;
    label.append(input);
    parent.append(label);
    return input;
  }
  if (!standalone) {
    const controls = node("form", "tracker-controls");
    function pathRow(label, placeholder, kind) {
      const row = node("div", "tracker-path");
      const input = node("input");
      input.placeholder = placeholder;
      input.autocomplete = "off";
      input.spellcheck = false;
      input.id = "tracker-" + kind;
      const caption = node("label", "", label);
      caption.htmlFor = input.id;
      const browse = node("button", "", "Browse…");
      browse.type = "button";
      browse.disabled = true;
      browse.dataset.trackerBrowse = kind;
      browse.addEventListener("click", async () => {
        try {
          const data = await request("tracker-browse", {kind});
          if (data.path) input.value = data.path;
        } catch (error) { status.textContent = error.message; }
      });
      row.append(caption, input, browse);
      controls.append(row);
      return input;
    }
    seedInput = pathRow("Seed output", "Use selected seed, or paste its output folder", "seed");
    saveInput = pathRow("Save folder", "Empty = this seed’s own Play saves", "save");
    const actions = node("div", "tracker-actions");
    const apply = node("button", "primary", "Track seed");
    apply.type = "submit";
    const useSelected = node("button", "", "Use selected seed");
    useSelected.type = "button";
    useSelected.addEventListener("click", async () => {
      seedInput.value = "";
      saveInput.value = "";
      slotSelect.value = "";
      reveal.checked = false;
      await configure();
    });
    slotSelect = node("select");
    slotSelect.id = "tracker-slot";
    slotSelect.append(new Option("Newest saved slot", ""));
    slotSelect.addEventListener("change", configure);
    const slotLabel = node("label", "", "Slot ");
    slotLabel.append(slotSelect);
    actions.append(apply, useSelected, slotLabel);
    controls.append(actions);
    const flags = node("div", "tracker-options");
    reveal = checkbox(flags, "Show locations (spoilers)", false);
    reveal.addEventListener("change", async () => {
      if (reveal.checked && !window.confirm("Reveal every seed location and its item? This spoils unvisited checks. OBS remains spoiler-free.")) {
        reveal.checked = false;
        return;
      }
      await configure();
    });
    iconToggle = checkbox(flags, "Local item icons", true);
    iconToggle.addEventListener("change", () => { icons = iconToggle.checked; lastRevision = ""; updateObs(); refresh(); });
    controls.append(flags);
    const obsFlags = node("div", "tracker-options tracker-obs-options");
    transparent = checkbox(obsFlags, "Transparent OBS background", false);
    transparent.addEventListener("change", updateObs);
    labelToggle = checkbox(obsFlags, "OBS item labels", false, "tracker-obs-labels");
    labelToggle.addEventListener("change", updateObs);
    columnSelect = select(obsFlags, "OBS columns", "tracker-obs-columns",
      [["", "Auto"], ...Array.from({length: 8}, (_, index) => [String(index + 1), String(index + 1)])], "");
    columnSelect.parentElement.title = "Auto: 4 with item labels, 6 without";
    columnSelect.addEventListener("change", updateObs);
    namesSelect = select(obsFlags, "OBS dungeon names", "tracker-obs-names",
      [["short", "Short"], ["full", "Full"], ["none", "Hidden"]], "short");
    namesSelect.addEventListener("change", updateObs);
    const sectionRow = node("div", "tracker-options tracker-obs-sections");
    sectionRow.append(document.createTextNode("OBS shows"));
    for (const [name, caption] of [["dungeons", "Dungeon keys"], ["collection", "Collection"], ["items", "Items"],
      ["songs", "Songs"], ["rewards", "Stones & medallions"], ["areas", "Checks by area"]]) {
      const input = checkbox(sectionRow, caption, DEFAULT_SECTIONS.includes(name), "tracker-obs-sections-" + name);
      sectionToggles[name] = input;
      input.addEventListener("change", () => {
        // No selection means the defaults, matching the empty/unknown fragment fallback.
        if (!Object.values(sectionToggles).some((toggle) => toggle.checked))
          for (const [other, toggle] of Object.entries(sectionToggles)) toggle.checked = DEFAULT_SECTIONS.includes(other);
        updateObs();
      });
    }
    controls.append(obsFlags, sectionRow);
    const obs = node("div", "tracker-obs-link");
    const obsLabel = node("label", "", "OBS Browser Source URL (private; changes each app start)");
    obsUrl = node("input");
    obsUrl.id = "tracker-obs-url";
    obsUrl.readOnly = true;
    obsLabel.htmlFor = obsUrl.id;
    const copy = node("button", "", "Copy URL");
    copy.type = "button";
    copy.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(obsUrl.value); status.textContent = "OBS URL copied"; }
      catch { obsUrl.focus(); obsUrl.select(); status.textContent = "Press Ctrl+C or Command+C to copy"; }
    });
    obs.append(obsLabel, obsUrl, copy);
    controls.append(obs);
    controls.addEventListener("submit", (event) => { event.preventDefault(); configure(); });
    root.append(controls);
    updateObs();
  }
  root.append(status, warnings, content);
  // The Checks tab: its own heading, the in-logic and list controls beside the list, a legend, then the areas.
  const checksHeading = node("div", "heading");
  const checksStatus = node("p", "tracker-checks-status");
  const checksNotes = node("div", "tracker-checks-notes");
  const checksList = node("div", "tracker-areas");
  let legend = null, lastAreas = [];
  if (checksRoot) {
    checksHeading.append(node("h1", "", "Checks"), node("p", "", "Choose a seed on the Tracker tab."));
    const bar = node("div", "tracker-options tracker-logic-controls");
    ageSelect = select(bar, "In logic for", "tracker-age",
      [["either", "Either age"], ["save", "Follow save"], ["child", "Child"], ["adult", "Adult"]], stored(AGE_KEY, AGES, "either"));
    ageSelect.addEventListener("change", () => { store(AGE_KEY, ageSelect.value, "either"); redraw(); });
    showSelect = select(bar, "Show", "tracker-show",
      [["all", "All checks"], ["open", "Open checks"], ["logic", "Open and in logic"]], stored(SHOW_KEY, SHOWS, "all"));
    showSelect.addEventListener("change", () => { store(SHOW_KEY, showSelect.value, "all"); redraw(); });
    hideFinished = checkbox(bar, "Hide finished areas", stored(FINISHED_KEY, ["1"], "") === "1", "tracker-hide-finished");
    hideFinished.parentElement.title = "Areas whose every check is collected, marked done or skipped";
    hideFinished.addEventListener("change", () => { store(FINISHED_KEY, hideFinished.checked ? "1" : "", ""); redraw(); });
    vanillaToggle = checkbox(bar, "Vanilla pick-ups", stored(VANILLA_KEY, ["shown", "hidden"], "shown") === "shown", "tracker-vanilla");
    vanillaToggle.parentElement.title = "Checks this seed does not shuffle that still hold an item the logic needs, such as Ruto's Letter";
    vanillaToggle.addEventListener("change", () => { store(VANILLA_KEY, vanillaToggle.checked ? "shown" : "hidden", "shown"); redraw(); });
    const tools = node("div", "tracker-options tracker-check-tools");
    for (const [text, fold] of [["Collapse all", true], ["Expand all", false]]) {
      const button = node("button", "tracker-fold", text);
      button.type = "button";
      button.id = fold ? "tracker-collapse-all" : "tracker-expand-all";
      button.addEventListener("click", () => {
        for (const area of lastAreas) fold ? collapsed.add(area) : collapsed.delete(area);
        storeCollapsed();
        redraw();
      });
      tools.append(button);
    }
    clearMarks = node("button", "", "Clear my marks");
    clearMarks.type = "button";
    clearMarks.id = "tracker-clear-marks";
    clearMarks.title = "Remove every check you marked done or skipped for this seed and save folder";
    clearMarks.addEventListener("click", async () => {
      if (!window.confirm("Remove every check you marked done or skipped for this seed and save folder? Your save is not changed.")) return;
      try { render(await request("tracker-clear-marks", {confirmed: true})); }
      catch (error) { checksStatus.textContent = error.message; }
    });
    tools.append(clearMarks);
    legend = node("div", "tracker-legend");
    legend.setAttribute("aria-label", "What the marks mean");
    checksRoot.append(checksHeading, bar, tools, legend, checksStatus, checksNotes, checksList);
  }
  function updateObs() {
    const fragment = new URLSearchParams({
      transparent: transparent.checked ? "1" : "0", icons: icons ? "1" : "0",
      labels: labelToggle.checked ? "1" : "0", columns: columnSelect.value, names: namesSelect.value,
      sections: TRACKER_SECTIONS.filter((name) => sectionToggles[name].checked).join(","),
    });
    if (!columnSelect.value) fragment.delete("columns");  // Auto: 4 labelled, 6 compact
    obsUrl.value = new URL(prefix + "tracker.html#" + fragment, location.origin).href;
  }
  async function configure() {
    if (pending) return;
    pending = true;
    try {
      const data = await request("tracker-configure", {
        seed: seedInput.value.trim() || null,
        save_folder: saveInput.value.trim() || null,
        slot: slotSelect.value || null,
        show_locations: reveal.checked,
        confirmed: reveal.checked,
      });
      initialized = true;
      lastRevision = "";
      render(data);
    } catch (error) { status.textContent = error.message; }
    finally { pending = false; }
  }
  const show = (value) => value === null || value === undefined ? "?" : String(value);
  const yes = (value) => value === null || value === undefined ? "?" : value ? "Yes" : "No";
  function section(title, parent = content) {
    const section = node("section", "tracker-group");
    section.append(node("h2", "section-title", title));
    parent.append(section);
    return section;
  }
  function localIcon(el, actor) {
    if (!icons || !actor) return;
    const image = node("img", "tracker-icon");
    image.alt = "";
    image.width = 40;
    image.height = 40;
    image.loading = "lazy";
    image.addEventListener("load", () => el.classList.add("tracker-has-icon"), {once: true});
    image.addEventListener("error", () => {
      el.classList.remove("tracker-has-icon");
      image.remove();
    }, {once: true});
    image.src = prefix + "tracker-icons/" + encodeURIComponent(actor) + ".png";
    el.append(image);
  }
  function badge(el, text, kind, description) {
    const value = node("span", "tracker-badge tracker-badge-" + kind, text);
    value.title = description;
    el.append(value);
  }
  // Flat CSS quest chips, not bundled game art. Full names remain on the cell's title/ARIA label.
  const questChips = {
    zeldas_lullaby: "ZL", eponas_song: "Ep", sarias_song: "Sa", suns_song: "Su",
    song_of_time: "SoT", song_of_storms: "SoS", minuet: "Min", bolero: "Bol",
    serenade: "Ser", requiem: "Req", nocturne: "Noc", prelude: "Pre", scarecrows_song: "Scr",
    kokiri_emerald: "Kok", goron_ruby: "Gor", zora_sapphire: "Zor",
  };
  // Short OBS dungeon names, by the save's DungeonInfo struct (state.dungeons[].id).
  const shortDungeons = {
    InsideTheDekuTree: "Deku", DodongoCavern: "Dodongo", InsideJabuJabuBelly: "Jabu", ForestTemple: "Forest",
    FireTemple: "Fire", WaterTemple: "Water", ShadowTemple: "Shadow", SpiritTemple: "Spirit", BottomOfTheWell: "Well",
    IceCavern: "Ice", GerudoTrainingGround: "GTG", InsideGanonCastle: "Ganon", GerudoFortress: "Fortress",
  };
  // Before any save is read every holding is unknown; OBS then draws a new game's empty inventory, not "?" tiles.
  function cells(title, entries, noSave) {
    if (!entries?.length) return;
    const group = section(title), grid = node("div", "tracker-cells");
    for (const cell of entries) {
      const held = noSave && cell.held == null ? false : cell.held;
      const el = node("div", "tracker-cell" + (held === false ? " tracker-missing" : "") + (held == null ? " tracker-unknown" : ""));
      const label = cell.label || cell.name || cell.id;
      const medallion = cell.group === "rewards" && cell.id.endsWith("_medallion");
      if (compact && (questChips[cell.id] || medallion)) {
        el.classList.add("tracker-quest-cell");
        el.setAttribute("role", "img");
        const chip = node("span", "tracker-quest-chip", questChips[cell.id] || "");
        if (medallion) {
          chip.classList.add("tracker-medallion");
          chip.dataset.medallion = cell.id;
        }
        el.append(chip);
      } else {
        localIcon(el, cell.icon);
        el.append(node("span", "tracker-cell-label", label));
      }
      // Without a save, counts and tiers are unread too. The tile's look says held or not; a caption appears only
      // for a tier or a count (Tier 2, 30, 2 bottles), and the full description stays in the tooltip.
      let detail = noSave ? "No save yet" : held == null ? "Unknown" : held ? "Held" : "Not held";
      let caption = "";
      if (!noSave && cell.basis === "slots") detail = caption = cell.count == null ? "Count unknown" : cell.count + " bottle" + (cell.count === 1 ? "" : "s");
      else if (!noSave) {
        if (cell.max_tier > 1 && cell.tier != null && cell.tier > 0) detail = caption = "Tier " + cell.tier;
        if (cell.count != null) {
          detail += " · " + cell.count;
          caption = caption ? caption + " · " + cell.count : String(cell.count);
        }
      }
      if (caption && held !== false) el.append(node("small", "", caption));
      if (cell.contents?.length) el.append(node("small", "", cell.contents.map((bottle) => bottle.content || "?").join(", ")));
      el.title = label + " · " + detail + (cell.contents?.length ? " · " + cell.contents.map((bottle) => bottle.content || "?").join(", ") : "");
      el.setAttribute("aria-label", el.title);
      // A missing item's greyed icon says enough: tier and count badges only on what is held (or unknown).
      if (standalone && held !== false) {
        if (cell.max_tier > 1 && cell.basis !== "slots") badge(el, show(cell.tier), "tier", "Tier " + show(cell.tier));
        if (cell.count != null || cell.basis === "slots") badge(el, show(cell.count), "count", detail);
        if (held == null && cell.max_tier <= 1) badge(el, "?", "count", "Unknown holding");
      }
      grid.append(el);
    }
    group.append(grid);
  }
  // Which dungeon items a dungeon has in this seed: small keys only where the seed holds some (or the save has any).
  function dungeonKinds(dungeon) {
    const keys = dungeon.small_keys || {};
    return {
      small_key: (keys.total ?? 0) > 0 || (keys.held ?? 0) > 0 || (keys.found ?? 0) > 0,
      boss_key: dungeon.has_boss_key !== false, map: dungeon.has_map !== false, compass: dungeon.has_compass !== false,
    };
  }
  function dungeonRows(group, state, noSave) {
    const list = node("div", "tracker-dungeon-rows");
    for (const dungeon of state.dungeons || []) {
      const row = node("div", "tracker-dungeon-row"), keys = dungeon.small_keys || {}, has = dungeonKinds(dungeon);
      const name = node("strong", "tracker-dungeon-name", dungeonNames === "short" ? shortDungeons[dungeon.id] || dungeon.name : dungeon.name);
      name.title = dungeon.name;
      if (dungeonNames !== "none") row.append(name);
      for (const [kind, label, value] of [
        ["small_key", "Small keys", keys.held == null ? null : keys.held > 0],
        ["boss_key", "Boss key", dungeon.boss_key],
        ["map", "Map", dungeon.map],
        ["compass", "Compass", dungeon.compass],
      ]) {
        if (!has[kind]) {
          // Not in this dungeon: an empty slot keeps the columns aligned.
          row.append(node("span", "tracker-dungeon-none"));
          continue;
        }
        const held = noSave && value == null ? false : value;
        const cell = node("div", "tracker-cell tracker-dungeon-item" + (held === false ? " tracker-missing" : "") + (held == null ? " tracker-unknown" : ""));
        localIcon(cell, state.dungeon_icons?.[kind]);
        const detail = noSave ? "no save yet" + (kind === "small_key" ? " · " + show(keys.total) + " in this seed" : "") :
          kind === "small_key" ? show(keys.held) + " held · " + show(keys.found) + " / " + show(keys.total) + " found / total" : held == null ? "Unknown" : held ? "Held" : "Not held";
        cell.title = dungeon.name + " · " + label + " · " + detail;
        cell.setAttribute("aria-label", cell.title);
        cell.append(node("span", "tracker-cell-label", label));
        if (kind === "small_key") {
          if (!noSave && keys.held !== 0) badge(cell, show(keys.held), "count", "Keys held");
          cell.append(node("small", "tracker-key-total", (noSave ? "0" : show(keys.found)) + "/" + show(keys.total)));
        } else {
          cell.append(node("small", "tracker-dungeon-flag", noSave ? "" : yes(held)));
          if (held == null) badge(cell, "?", "count", "Unknown holding");
        }
        row.append(cell);
      }
      list.append(row);
    }
    group.append(list);
  }
  // The in-logic view of the Checks tab: which age key to read, and the one-line notes above the areas.
  function logicView(state, noSave) {
    const logic = state.logic || {};
    if (standalone || !checksRoot) return {key: null, notes: [], unknown: []};
    const available = logic.available === true && !noSave;
    ageSelect.disabled = vanillaToggle.disabled = !available;
    for (const option of showSelect.options) if (option.value === "logic") option.disabled = !available;
    if (!state.logic || noSave) return {key: null, notes: [], unknown: []};
    if (!available) return {key: null, notes: ["In logic unavailable: " + (logic.reason || "unknown reason")], unknown: []};
    const notes = [];
    let key = ageSelect.value;
    if (key === "save") {
      key = logic.save_age || "either";
      if (!logic.save_age) notes.push("Follow save: the save's age could not be read, so either age is shown.");
    }
    const labels = Object.fromEntries([...(state.items || []), ...(state.songs || []), ...(state.rewards || [])].map((cell) => [cell.id, cell.label]));
    const unknown = (logic.unknown_items || []).map((id) => labels[id] || id);
    // The full list of unread items goes to the side panel's In logic row, not above the list.
    return {key, notes, unknown};
  }
  // A check's state in the Checks tab: ``markable`` offers Mark done (D9), ``skippable`` offers Skip.
  const markable = (check) => check.markable === true;
  function checkState(check, key, noSave) {
    const done = check.collected === true ? "collected" : check.skipped ? "skipped" : check.marked ? "marked" : null;
    const open = !done;
    const inLogic = key && open && check.in_logic ? check.in_logic[key] ?? null : null;
    const manual = open && markable(check);
    let action = null;
    if (!noSave) {
      if (done === "marked") action = "unmark";
      else if (done === "skipped") action = "unskip";
      else if (manual) action = "mark";
      else if (open && check.skippable) action = "skip";
    }
    return {done, open, inLogic, manual, action};
  }
  const STATE_WORDS = {collected: "Collected (your save)", marked: "Marked done by you", skipped: "Skipped by you"};
  function stateWords(state, noSave) {
    if (state.done) return STATE_WORDS[state.done];
    if (noSave) return "Not read yet: no save";
    const logic = state.inLogic === true ? ", in logic" : state.inLogic === false ? ", out of logic" : "";
    return "Open" + logic + (state.manual ? "; your save can't show it" : "");
  }
  const ACTION_WORDS = {
    mark: "Click when you have it: marks it done",
    unmark: "Click to undo your mark",
    skip: "Click to skip it: it leaves the open checks",
    unskip: "Click to undo the skip",
  };
  // Marker shapes for the legend and the rows (CSS only, no fonts or art).
  const LEGEND = [
    ["collected", "Collected", "Your save shows it collected"],
    ["marked", "Marked", "Marked done by you"],
    ["skipped", "Skipped", "Skipped by you"],
    ["in-logic", "In logic", "Open, and in logic with what your save holds"],
    ["out-of-logic", "Out of logic", "Open, and out of logic with what your save holds"],
    ["manual", "Mark by hand", "Your save can't show this check: click it when you have it"],
  ];
  function marker(kind) {
    const el = node("span", "tracker-state tracker-state-" + kind);
    el.setAttribute("aria-hidden", "true");
    return el;
  }
  // One line: a marker and a word each (the longer meaning on hover). Without a save it steps aside.
  function drawLegend(skippable, noSave) {
    legend.replaceChildren();
    legend.hidden = noSave;
    for (const [kind, text, meaning] of LEGEND) {
      if (kind === "skipped" && !skippable) continue;
      const item = node("span", "tracker-legend-item");
      item.title = meaning;
      item.append(marker(kind), document.createTextNode(text));
      legend.append(item);
    }
  }
  // Row names drop their area's prefix under the area heading ("Lake Hylia: ", "LH ", "LH GS " becomes
  // "Skulltula: "); the side panel keeps the full name. Codes are OoT Randomizer's location-name prefixes.
  const AREA_CODES = {
    "Kokiri Forest": ["KF"], "Lost Woods": ["LW"], "Sacred Forest Meadow": ["SFM"], "Hyrule Field": ["HF"],
    "Lon Lon Ranch": ["LLR"], "Market": ["MK"], "Temple of Time": ["ToT"], "Hyrule Castle": ["HC"],
    "Land outside Ganon's Castle": ["OGC"], "Kakariko Village": ["Kakariko", "Kak"], "Graveyard": ["GY"],
    "Death Mountain Trail": ["DMT"], "Death Mountain Crater": ["DMC"], "Goron City": ["GC"], "Zora's River": ["ZR"],
    "Zora's Domain": ["ZD"], "Zora's Fountain": ["ZF"], "Lake Hylia": ["LH"], "Gerudo Valley": ["GV"],
    "Gerudo's Fortress": ["GF"], "Haunted Wasteland": ["Wasteland"], "Desert Colossus": ["Colossus"],
  };
  const loosely = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/'/g, "'?").replace(/[- ]/g, "[- ]");
  function shortLabel(label, area) {
    const prefixes = [area, ...(AREA_CODES[area] || [])].map(loosely).join("|");
    let rest = label.replace(new RegExp("^(?:" + prefixes + ")(?::\\s*|\\s+)", "i"), "");
    if (rest === label || !rest) return label;
    rest = rest.replace(/^GS(?:\s+|$)/, (gap) => gap.trim() === gap ? "Skulltula" : "Skulltula: ");
    return rest[0].toUpperCase() + rest.slice(1);
  }
  // The side panel: the pointed-at or focused check's own directions and state (app only).
  const panel = checksRoot ? {
    screen: document.getElementById("checks"),
    title: document.getElementById("description-title"),
    text: document.getElementById("description-text"),
    note: document.getElementById("description-note"),
    details: document.getElementById("check-details"),
  } : null;
  let selected = null;  // the selected check's id
  let rows = new Map();  // check id -> {check, state, area}
  let view = {key: null, notes: [], unknown: []}, noSaveNow = false, logicReason = null, skipOffered = false;
  const checksShown = () => panel && panel.screen && !panel.screen.hidden && panel.title && panel.details;
  const KIND_WORDS = {
    chest: "Chest", token: "Gold Skulltula", boss_heart: "Boss heart", freestanding: "Freestanding item",
    scrub: "Deku Scrub", gift: "Gift or song", shop: "Shop item", other: "Other",
  };
  function howWords(check) {
    if (check.vanilla) return "Not shuffled in this seed: it keeps its usual item. Read from your inventory, as the logic counts it.";
    if (markable(check) && check.collected == null) return "Your save can't show this check" + (check.reason ? " (" + check.reason + ")" : "") + ". Click it when you have it.";
    if (markable(check)) return "Your save reads it through a flag not yet confirmed in play; if it is wrong, click it when you have it.";
    const kind = check.kind;
    if (check.basis === "placement_hash") return "Your save records this pickup once it is collected; until then it shows as open.";
    if (check.basis === "source_pair" || kind === "token") return "Your save records this Gold Skulltula once its token is collected.";
    if (kind === "chest") return "Your save records this chest once it is opened.";
    if (kind === "scrub") return "Your save records this scrub's sale once it completes.";
    if (kind === "gift") return "Your save records this gift once it is given.";
    return "Your save records this check once it is collected.";
  }
  function logicWords(entry) {
    const {check, state} = entry;
    if (noSaveNow) return "Shown after your first save.";
    if (logicReason) return "Unavailable: " + logicReason;
    if (state.done === "collected") return "Collected; no longer counted.";
    if (state.done) return "Done by you; no longer counted.";
    const ages = check.in_logic;
    if (!ages) return "No logic data for this check.";
    let words;
    if (ages.child && ages.adult) words = "In logic for child and adult.";
    else if (ages.child) words = "In logic as child; adult can't reach it yet with what you hold.";
    else if (ages.adult) words = "In logic as adult; child can't reach it yet with what you hold.";
    else if (ages.either) words = "In logic using both ages: it needs a trip between them.";
    else words = "Out of logic: neither age can reach it yet with what your save holds.";
    if (view.unknown.length) words += " May be conservative: the save could not read " + view.unknown.join(", ") + ", so they count as not held.";
    return words;
  }
  function showDetails() {
    if (!checksShown()) return;
    const entry = selected && rows.get(selected);
    panel.note.hidden = true;
    panel.details.hidden = false;
    panel.details.replaceChildren();
    if (!entry) {
      panel.title.textContent = "Checks";
      panel.text.textContent = noSaveNow || !rows.size ? "Every check of the seed, by area. Save in the game once to see what is done and what is in logic." :
        "Point at a check, or move to it with ↑ ↓, to see where it is, how your save tracks it and whether it is in logic. " +
        "Click a check your save can't show (square mark) to mark it done" + (skipOffered ? ", or one it shows to skip it" : "") +
        "; click again to undo. “All checks” shows everything you marked. Marks never change your save.";
      return;
    }
    const {check, state, area} = entry;
    panel.title.textContent = check.label || check.name || check.id;
    panel.text.textContent = check.where || "No directions recorded for this check.";
    const list = node("dl", "tracker-detail-list");
    const add = (term, value) => { if (value) list.append(node("dt", "", term), node("dd", "", value)); };
    add("State", stateWords(state, noSaveNow));
    add("In logic", logicWords(entry));
    add("Save", howWords(check));
    add("Area", area + (check.dungeon && check.dungeon !== area ? " · " + check.dungeon : ""));
    add("Kind", KIND_WORDS[check.kind] || check.kind);
    if (check.item) add(check.vanilla ? "Usual item" : "Item", check.item_label || check.item);
    if (state.action) add("Click", ACTION_WORDS[state.action]);
    panel.details.append(list);
  }
  function choose(id) {
    if (selected === id) return;
    selected = id;
    for (const row of checksList.querySelectorAll("[data-check]")) row.classList.toggle("tracker-check-selected", row.dataset.check === id);
    showDetails();
  }
  if (panel?.screen && typeof MutationObserver !== "undefined") {
    new MutationObserver(() => {
      if (!panel.screen.hidden) { showDetails(); refresh(); }
      else if (panel.details) panel.details.hidden = true;
    }).observe(panel.screen, {attributes: true, attributeFilter: ["hidden"]});
  }
  async function act(check, action) {
    const body = {check: check.id, marked: action === "mark" || action === "skip"};
    if (action === "skip" || action === "unskip") body.kind = "skip";
    try { render(await request("tracker-mark", body)); }
    catch (error) { checksStatus.textContent = error.message; }
  }
  function checkLine(check, area, filter) {
    const state = checkState(check, view.key, noSaveNow);
    const kind = state.done || (noSaveNow ? "unread" : state.inLogic === true ? "in-logic" : state.inLogic === false ? "out-of-logic" : "open");
    const style = state.done ? " tracker-check-" + state.done : state.inLogic === true ? " tracker-check-in-logic" : state.inLogic === false ? " tracker-check-out-of-logic" : "";
    const line = node("button", "tracker-check" + style + (state.manual && !noSaveNow ? " tracker-check-manual" : "") + (state.action ? " tracker-check-actionable" : ""));
    line.type = "button";
    line.dataset.check = check.id;
    line.append(marker(kind));
    const label = check.label || check.name || check.id;
    line.append(node("span", "tracker-check-label", shortLabel(label, area) + (check.item ? ": " + (check.item_label || check.item) : "")));
    if (check.vanilla) {
      line.classList.add("tracker-check-vanilla");
      const tag = node("span", "tracker-vanilla-tag", "vanilla");
      tag.title = "Not shuffled in this seed: this check keeps its usual item";
      line.append(tag);
    }
    const words = stateWords(state, noSaveNow);
    line.title = words + (state.action ? ". " + ACTION_WORDS[state.action] : "");
    line.setAttribute("aria-label", label + ": " + words);
    if (!state.action) line.setAttribute("aria-disabled", "true");
    else line.dataset.keyAction = state.action === "mark" ? "Mark done" : state.action === "skip" ? "Skip" : "Undo";
    line.addEventListener("click", () => { choose(check.id); if (state.action) act(check, state.action); });
    line.addEventListener("pointerover", () => choose(check.id));
    line.addEventListener("focus", () => choose(check.id));
    if (selected === check.id) line.classList.add("tracker-check-selected");
    rows.set(check.id, {check, state, area});
    line.hidden = (filter === "open" && !state.open) || (filter === "logic" && (view.key ? state.inLogic !== true : !state.open));
    return {line, state};
  }
  function renderChecks(data, state, noSave) {
    if (!checksRoot) return;
    const focused = document.activeElement?.dataset?.check;
    noSaveNow = noSave;
    view = logicView(state, noSave);
    logicReason = state.logic && state.logic.available !== true ? state.logic.reason || "unknown reason" : null;
    const seed = state.seed || {};
    checksHeading.querySelector("p").textContent = "Seed " + show(seed.seed ?? seed.number) + " · " + (state.areas || []).reduce((sum, area) => sum + (area.checks || []).length, 0) +
      " checks · " + (state.show_locations ? "LOCATION SPOILERS ON" : "spoiler-free");
    clearMarks.disabled = showSelect.disabled = hideFinished.disabled = noSave;
    checksStatus.textContent = noSave ? "No save loaded yet. This is the seed's check list; done and in-logic states appear once you save in the game." : "";
    checksStatus.classList.toggle("tracker-no-save", noSave);
    checksNotes.replaceChildren(...view.notes.map((note) => node("p", "tracker-logic-note", note)));
    rows = new Map();
    const filter = noSave ? "all" : showSelect.value;
    // Vanilla rows join their area by name; an area with only vanilla rows follows the seed's areas.
    const vanillaShown = view.key !== null && vanillaToggle.checked;
    const vanilla = new Map(vanillaShown ? (state.vanilla_areas || []).map((area) => [area.name, area]) : []);
    const listed = [...(state.areas || []), ...[...vanilla.keys()].filter((name) => !(state.areas || []).some((area) => area.name === name)).map((name) => ({name, checks: []}))];
    let skippable = false;
    lastAreas = listed.map((area) => area.name);
    checksList.replaceChildren();
    for (const area of listed) {
      const checks = [...(area.checks || []), ...(vanilla.get(area.name)?.checks || [])];
      const lines = checks.map((check) => checkLine(check, area.name, filter));
      skippable ||= checks.some((check) => check.skippable || check.skipped);
      const finished = lines.filter(({state}) => !state.open).length;
      const inLogic = lines.filter(({state}) => state.inLogic === true).length;
      const folded = collapsed.has(area.name);
      const item = node("section", "tracker-area" + (folded ? " tracker-area-collapsed" : ""));
      const head = node("button", "tracker-area-head");
      head.type = "button";
      head.setAttribute("aria-expanded", String(!folded));
      head.dataset.keyAction = folded ? "Expand" : "Collapse";
      const counts = noSave ? lines.length + " checks" : finished + " / " + lines.length + " done" + (view.key ? " · " + inLogic + " in logic" : "");
      head.append(node("span", "tracker-area-fold"), node("strong", "", area.name), node("span", "tracker-area-counts", counts));
      head.title = (folded ? "Expand " : "Collapse ") + area.name;
      head.addEventListener("click", () => {
        folded ? collapsed.delete(area.name) : collapsed.add(area.name);
        storeCollapsed();
        redraw();
      });
      const body = node("div", "tracker-area-checks");
      body.hidden = folded;
      body.append(...lines.map(({line}) => line));
      item.append(head, body);
      item.hidden = (!noSave && hideFinished.checked && finished === lines.length) ||
        (filter !== "all" && !lines.some(({line}) => !line.hidden));
      checksList.append(item);
    }
    skipOffered = skippable;
    drawLegend(skippable, noSave);
    if (selected && !rows.has(selected)) selected = null;
    showDetails();
    if (focused) [...checksList.querySelectorAll("[data-check]")].find((row) => row.dataset.check === focused)?.focus();
  }
  function noSaveCard(data) {
    const card = node("section", "tracker-no-save");
    card.append(node("h2", "section-title", "No save loaded yet"));
    const folder = data.save_folder;
    card.append(node("p", "", data.status === "no_save_folder" ? "Choose the folder your game saves in, then Track seed." :
      "Start this seed and save in the game once: items, keys and checks fill in from that save, about a second after it is written."));
    if (folder) {
      const where = node("p", "tracker-no-save-folder", "Watching ");
      where.append(node("code", "", folder));
      card.append(where);
    }
    card.append(node("p", "", "Longshot and Hookshot Play saves inside the seed's folder; emulator players choose their emulator's save folder above. Saves are only read, never changed."));
    content.append(card);
  }
  function render(data) {
    lastData = data;
    const idle = data.status === "idle" || data.status === "unconfigured";
    initialized = initialized || !idle;
    const state = data.state;
    const noSave = data.status === "waiting" || data.status === "no_save_folder";
    const labels = {ok: "Following saved progress", ready: "Following saved progress", waiting: "No save loaded yet", stale: "Waiting for a complete save", no_save_folder: "Choose a save folder", error: "Unable to read this seed"};
    status.textContent = idle ? "Choose a seed to begin. Reads saves only; never changes them." :
      (labels[data.status] || data.status) +
      (data.selected_slot ? " · " + data.selected_slot : "") + (data.save_folder && !standalone ? " · " + data.save_folder : "");
    if (compact) {
      status.hidden = data.status === "ok" || data.status === "ready";
      status.textContent = idle ? "Choose a seed in the app" : noSave ? "No save yet" : labels[data.status] || "Tracker unavailable";
    }
    warnings.replaceChildren();
    // OBS never shows warnings (seed identity, read problems): they stay on the app's Tracker tab.
    // Without a save the waiting reason is the no-save card itself.
    const waitingReasons = noSave ? new Set(data.warnings || []) : new Set();
    if (!standalone)
      for (const warning of [...new Set([...(data.warnings || []), ...(state?.warnings || [])])])
        if (!waitingReasons.has(warning)) warnings.append(node("p", "", warning));
    if (!standalone) {
      const selectedSlot = slotSelect.value;
      const signature = JSON.stringify(data.slots || []);
      if (slotSelect.dataset.slots !== signature) {
        slotSelect.replaceChildren(new Option("Newest saved slot", ""));
        for (const slot of data.slots || []) slotSelect.append(new Option(slot.label || slot.id || slot.name, slot.id || slot.name));
        slotSelect.value = selectedSlot;
        slotSelect.dataset.slots = signature;
      }
    }
    if (!state) {
      content.replaceChildren();
      checksList.replaceChildren();
      rows = new Map();
      if (checksRoot) {
        checksStatus.textContent = idle ? "Choose a seed on the Tracker tab." : (labels[data.status] || data.status);
        showDetails();
      }
      return;
    }
    const revision = JSON.stringify([data.revision, data.status, state, icons]);
    if (revision === lastRevision) return;
    lastRevision = revision;
    content.replaceChildren();
    const seed = state.seed || {};
    heading.querySelector("p").textContent = "Seed " + show(seed.seed ?? seed.number) + " · saved inventory · " + (standalone ? "spoiler-free" : reveal.checked ? "LOCATION SPOILERS ON" : "spoiler-free");
    renderChecks(data, state, noSave);
    if (noSave && !standalone) {
      noSaveCard(data);
      document.documentElement.dataset.trackerReady = "true";
      return;
    }
    if (sections.has("dungeons")) {
      const dungeonGroup = section("Dungeon keys");
      if (standalone) dungeonRows(dungeonGroup, state, noSave);
      else {
        const table = node("table", "tracker-dungeons");
        const head = node("thead"), row = node("tr");
        for (const title of ["Dungeon", "Held", "Found / total", "Boss", "Map", "Compass"]) row.append(node("th", "", title));
        head.append(row); table.append(head);
        const body = node("tbody");
        for (const dungeon of state.dungeons || []) {
          const tr = node("tr"), keys = dungeon.small_keys || {}, has = dungeonKinds(dungeon);
          // A blank cell: this dungeon has no such item in this seed.
          for (const value of [dungeon.name, has.small_key ? show(keys.held) : "", has.small_key ? show(keys.found) + " / " + show(keys.total) : "",
            has.boss_key ? yes(dungeon.boss_key) : "", has.map ? yes(dungeon.map) : "", has.compass ? yes(dungeon.compass) : ""]) tr.append(node("td", "", value));
          body.append(tr);
        }
        table.append(body); dungeonGroup.append(table);
      }
    }
    if (sections.has("collection")) {
      const health = state.hearts || {}, skulltulas = state.skulltula_checks || {};
      const counts = section("Collection");
      // Token stock and Skulltula source checks differ once Tokens are shuffled; Token-off seeds have no source checks.
      const sources = skulltulas.total ? " · Skulltula checks " + show(skulltulas.collected) + " / " + show(skulltulas.total) +
        (skulltulas.unknown ? " (" + skulltulas.unknown + " unknown)" : "") : "";
      counts.append(node("p", "tracker-counts", noSave ? "No save yet" :
        "Hearts " + show(health.containers ?? health.capacity) + " · Pieces " + show(health.pieces) + " · Gold Skulltulas " + show(state.tokens) + sources));
    }
    if (sections.has("items")) cells("Items & equipment", state.items, noSave);
    if (sections.has("songs")) cells("Songs", state.songs, noSave);
    if (sections.has("rewards")) cells("Stones & medallions", state.rewards, noSave);
    if (standalone && sections.has("areas")) {
      // OBS keeps a spoiler-free per-area count; the check list itself lives on the app's Checks tab.
      const areas = section("Checks by area");
      areas.classList.add("tracker-areas-group");
      const areaGrid = node("div", "tracker-areas");
      for (const area of state.areas || []) {
        const item = node("div", "tracker-area");
        item.append(node("strong", "", area.name), node("span", "tracker-area-counts", show(noSave ? 0 : area.collected) + " / " + show(area.total)));
        areaGrid.append(item);
      }
      areas.append(areaGrid);
    }
    document.documentElement.dataset.trackerReady = "true";
  }
  let failures = 0;
  async function refresh() {
    if (pending || (!standalone && document.getElementById("tracker")?.hidden && (!panel?.screen || panel.screen.hidden))) return;
    pending = true;
    try {
      const data = await request(standalone ? "tracker-obs" : "tracker");
      failures = 0;
      render(data);
      if (!standalone && !initialized && ["idle", "unconfigured"].includes(data.status)) {
        // Seed choice is explicit. Loading a tab never opens or reveals the selected seed's spoiler.
        status.textContent = "Use selected seed, or choose a seed output and Track seed.";
      }
    } catch (error) {
      // OBS rides out a missed poll (the next one comes a second later) and never shows a raw error message.
      failures += 1;
      if (!standalone || failures >= 3) {
        status.hidden = false;
        status.textContent = standalone ? "Tracker connection lost" : error.message;
      }
    }
    finally { pending = false; }
  }
  if (!standalone) request("schema").then((data) => {
    for (const button of root.querySelectorAll("[data-tracker-browse]")) {
      button.disabled = !data.dialogs_available;
      if (button.disabled) button.title = "Disabled in --no-open; paste a path instead";
    }
  }).catch((error) => { status.textContent = error.message; });
  refresh();
  const timer = setInterval(refresh, 1000);
  window.addEventListener("pagehide", () => clearInterval(timer), {once: true});
})();
