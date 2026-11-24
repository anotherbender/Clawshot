# Item tracker

The **Tracker** tab reads the selected seed and a saved game. Dungeon keys come first: **Held**
is the number available to spend now; **Found / total** is the acquired count, including spent
keys, out of that seed's dungeon total. Keys found outside their dungeon still appear under the
correct dungeon. Boss key, map and compass are separate saved flags.

The **Gerudo Fortress** row includes the four jail keys, including keys found in remote chests
with the separate experimental jail-key option. The four guard-floor checks and the Well/Shadow
floor-key checks read their native saved collection Bools, not actor-Hash records. Defeating a
guard or finding a jail key elsewhere does not by itself complete its floor-reward check.
These new source adapters and their played tracker updates still await in-game acceptance.

## Start tracking

1. Generate a seed, or **View seed** under Generate → My seeds.
2. Open **Tracker** and press **Use selected seed**. Alternatively Browse to, or paste, the
   seed's output folder and press **Track seed**. Both `output/seed/spoiler.json` and a raw
   generator folder containing `spoiler.json` are accepted.
3. Leave **Save folder** empty for this seed's own Play saves (`output/user`). Tracking creates
   or changes nothing in your game, seed or save folders; the only file it writes holds your manual
   marks (see **Checks**). Before a new game is saved, the Tracker tab says **No save loaded yet**
   and names the folder it is watching; items, keys and checks fill in about a second after the first
   save.
4. The newest `slot_NN/progress.sav` by modification time is selected automatically. Use
   **Slot** to pin another slot; choose **Newest saved slot** to follow the newest again.
5. Save in the game. The page polls once a second and updates without reloading. This is
   saved progress, not live process memory: unsaved pickups will not appear yet.

Items show current holdings and tiers, songs, stones, medallions, hearts/pieces and Gold Skulltula
tokens. Bottles show the number owned and each slot's current contents, not every content ever
acquired. An acquired-once flag is not proof a consumed trade item or broken shield is still held.
Plain boots have no saved pouch row; the tracker shows Iron/Hover Boots, not an invented normal-boot
ownership flag. Hearts are the meter's capacity; pieces are the raw saved stock, not a claimed
lifetime total. `?` means the field is unknown, not zero. The check list is on its own **Checks** tab
(below); repeatable purchases and unaudited event gates cannot be treated as permanently collected.
A partial/unreadable save keeps the previous good state with a warning until it can be read again.

With Gold Skulltula tokens shuffled, each Skulltula is one check, however many age copies it has. It
counts as collected once its reward has been picked up, whatever that reward is: the game saves two
records for that Skulltula, and the tracker needs both. Killing it without collecting the drop does not
count. The **Gold Skulltulas** number is the game's own token count, so it rises for a token found in a
chest or at a Skulltula and stays the same for any other reward at a Skulltula. Beside it, **Skulltula checks**
counts collected Skulltulas out of the seed's total (in brackets, how many are unknown), in the tab and in
every OBS view that shows the quest group, labels on or off; seeds without Token shuffle don't show it.
A Skulltula shows `?` when only one of its two records is set, or when the save is not the save layout
those records were checked on.

## Checks

The **Checks** tab lists each area's checks by name; their rewards stay hidden unless spoiler mode is
on. Under an area's heading a check's name drops the area part ("Lake Hylia: ", "LH GS " becomes
"Skulltula: "). Areas flow in two or three columns, depending on the window's width. Click an area's
name to fold it away; **Collapse all** and **Expand all** do every area, and the folded areas are
remembered in this browser. Point at a check (or move to it with ↑ ↓) and the right-hand panel shows its
full name, our own directions to it, how your save tracks it, and whether it is in logic and why
(including any items the save could not read, which count as not held).

Each check's look shows its state; the one-line legend above the list repeats it (hover a word for
more). A filled green dot is collected (your save shows it), a filled amber dot is marked done by you,
a ring is open: green and highlighted when in logic, dimmed when out of logic. A square instead of a ring
means your save can't show that check, so you mark it yourself (below). A struck-through name is a check
you chose to skip. Every open check (not collected, not marked done and not skipped) is shown **in logic**
when the seed's own logic says you can reach it with what
your save holds, or **out of logic** otherwise. Each area heading counts its finished checks and "N in
logic".

An amber diamond, **Needs a source**, means the check is in logic only after obtaining a resource
the logic derives from a reachable source, rather than stock your save holds. Point at the check:
the side panel names the event (for example `Deku Stick Drop`), its reachable region(s), the age
that supplies it and its rule. It shows one sufficient route; alternatives may exist.
This annotation does not change reachability, assume a shop purchase, collect an unchecked reward or
reveal a shuffled item. It follows the age selector and disappears when saved stock already suffices.
The source-marker design is provisional (Claude, round 22); Kareem may change it.

**Show** chooses the rows: **All checks** (the default), **Open checks** (collected, marked and skipped checks
leave the list) or **Open and in logic**. Areas with nothing left to show fold away, and **Hide finished
areas** also hides an area whose every check is done. Both choices are remembered in this browser.
Before any save is read, the tab lists the seed's checks with a **No save loaded yet** line and nothing
can be marked.

- **What counts as held.** Only what your save holds: items, upgrades, songs, stones and medallions,
  hearts, Gold Skulltula tokens, bottles, magic and dungeon items, plus the seed's starting items.
  The spoiler's placements are never used, so in-logic gives nothing away.
- **Used-up items.** A trade item, Ruto's Letter or a shield counts once the save shows you got it,
  even after you traded it on, delivered it, or lost the shield. Bombchus count once found, even when
  used, but only with a held Bomb Bag. Bought Bombchus without the bag are not explosives.
  Other items count only while you hold them.
- **Small keys** count every key you found in that dungeon, spent ones included. Boss keys, maps and
  compasses count once you have them.
- **Silver rupees.** Fifteen puzzle groups count as five rupees once the room's own saved clear flag is set,
  including all four silver-rupee trial puzzles in Ganon's Castle. An unfinished puzzle counts none;
  missing flags remain unknown. The Gerudo Training Ground lava room remains unmapped because its saved
  clear key is not established. These are logic counts, not extra item tiles or individual pickup checks
  ([flag audit](../plans/rounds/r22-tracker.md)).
- **Bottles.** Each bottle you own counts as a bottle, except one holding Ruto's Letter, which counts as
  the letter only: as in the seed's logic, the letter is not also an empty bottle.
- **Hearts** count whole hearts; loose Pieces of Heart are not added.
- **Story steps.** Meeting Zelda (Impa's send-off) and the owl's arrival in Hyrule Field are read from
  the save. Other story steps are worked out from the logic itself.
- **Goron's Bracelet.** The seed's logic counts the child's Bracelet only from Darunia's gift, so the
  tracker counts it once the save records the cutscene in which Darunia hands it over, not from a
  Bracelet found in a chest or from the adult gauntlets. Confirmed on real saves: Kareem's Longshot saves
  from just before and just after Darunia's dance (2026-11-13) read the Bracelet as not held, then held, and
  the vanilla **Darunia's Dance** row as open, then collected ([check record](../plans/rounds/r21-checks.md)).
- **Unknown fields.** Anything the save cannot show counts as not held, and the side panel's **In logic**
  row names it for the check you point at: in-logic may then be more cautious than the game.

**In logic for**, beside the list, chooses the age: **Either age** (the default: a check counts when either age can reach
it, as the seed's logic does), **Follow save**, **Child** or **Adult**. Follow save reads the save's
`Sequence_IsChildhood` flag, which normal play keeps right but Longshot's debug age switch does not
change. When the save does not say, Follow save shows either age and says so. Your choice is remembered
in this browser. Styling, area counts, the details panel and the **Show** filter all follow it.

In-logic needs a seed made by this same Clawshot version, whose settings rebuild into the seed's logic
and whose every location is in this version's world. Otherwise the age control and filter are greyed
out with the reason, and the rest of the tracker works as before. A save, not live play, is read: pick
something up and save before it counts.

**Marking checks done.** Some checks the save cannot show (a square): shop items, a few gifts, some
floor pickups. Click such a check once you have it, so it leaves the open list; click it again to undo.
If **Open checks** hid a check you clicked by mistake, switch to **All checks** and click it again. A
marked check shows as marked by you, not as collected, never adds its item to what you hold, and keeps
its reward hidden in spoiler-free mode. If a later save does show that check, the save wins and the
mark is removed. Marks are kept per seed and per save folder (the game writes each save to its next
slot, so they follow you from slot to slot), survive a restart of Clawshot, and **Clear my marks**
removes this seed and save folder's marks after asking. They live in
`tracker-marks.json` in Clawshot's preferences folder: `%APPDATA%/Clawshot` on Windows,
`~/Library/Application Support/Clawshot` on macOS, `$XDG_CONFIG_HOME/clawshot` (default
`~/.config/clawshot`) on Linux. If that file cannot be read, the tracker warns, shows no marks and
leaves the file alone until you change a mark.

**Skipping checks.** A check your save does show, but which you do not mean to get (a windmill rupee, a
heart piece you can do without), can be skipped: click it and it leaves the open list and the "in logic"
counts; click it again to undo. A skipped check is shown struck through, never counts as collected, and
keeps its reward hidden. Unlike a mark, a skip stays when a later save is read; if you collect the check
anyway, the save wins and it shows as collected. Skips are kept beside the marks, per seed and save
folder, and **Clear my marks** removes them too. The OBS view never shows them.

**Gifts read automatically.** Many gifts are read from records the game itself keeps once it gives
them: minigame and NPC prizes (the Skull Kid's games, the archery and shooting galleries, fishing,
bowling, the diving game, Anju's Cuccos, Talon's Cuccos, the Gold Skulltula rewards up to 50, the frogs),
song and cutscene gifts (Saria, Malon, Impa, Sheik, the Ocarina of Time, the Light Arrows, Zelda's
Letter, Darunia), and a few quests (the Lost Dog, Biggoron). Once one reads as given, it counts as
collected and shows its reward even in spoiler-free mode, as an opened chest does. Others still need
marking by hand: the trade hand-ins, shops, and the gifts whose records do not tell (such as the 10 Big
Poes and the 100 Gold Skulltula reward). Until each of these records has been confirmed in a played
game, a gift it reads as not given yet keeps the square and can be marked done, and your mark on it stays
(and keeps its reward hidden) until the record reads given. That square is the only sign that a record
is still unconfirmed: no label or style shows it.
Ten records are confirmed so far: each read as given after Kareem got that gift on Longshot 3.0.0
(2026-11-23). They are the Zora's River frogs' prizes for Zelda's Lullaby, Saria's Song and Sun's Song, the
Hyrule Field moat item and the Song of Time, Malon's song, Talon's Cuccos, Sheik at the Temple of Time, the
Kakariko Shooting Gallery prize and the man on the Kakariko roof. These show no square.
Reading these records needs a seed made by this same Clawshot version; for other seeds the tracker says
so in one line and reads gifts as before ([design record](../plans/tracker-auto-checks.md)).

**Vanilla pick-ups.** Some places your seed does not shuffle still hold an item the logic needs.
Ruto's Letter at the bottom of Lake Hylia is one: until you hold it, Jabu-Jabu's Belly stays out of
logic. So the tracker also lists these places in their area, tagged **vanilla**, with their usual item
shown even in spoiler-free mode (your settings decide it, not the seed). They get the same in-logic
styling, and the area heading counts them with the area's own checks. One counts as collected once
the save shows you hold its item (or ever had it, for used-up items as above; Saria's Fairy Ocarina
also counts once you hold the Ocarina of
Time). If the save cannot tell, or a shuffled check could also give that item, it shows a square and
you can mark it done. A few rows always need marking, because the save cannot tell which source gave the item: the
Magic Bean salesman and Talon's bottle of milk when that gift is not shuffled.

Only items that come from that one place, and that your seed's logic uses, are listed. For example:
songs and trade items when they are not shuffled, the ocarinas, Ruto's and Zelda's Letters, the Gerudo
card, the Great Fairies' spells, the Fire and Light Arrows, masks, and the stones and medallions the
logic asks for. Items found in many places, such as Gold Skulltula tokens, silver rupees and ordinary
Pieces of Heart, are not listed. Neither are items your seed's logic never counts, such as a fixed
Silver Scale, a wallet or a Great Fairy's magic meter: the logic counts only the upgrades your seed
shuffles, so those are a bonus. Unchecking **Vanilla pick-ups** turns the rows off; the choice is remembered
in this browser. They need in-logic, so they are hidden when in-logic is unavailable.

The OBS view shows none of this: no check names, no in-logic data, no vanilla pick-ups and no marks.

## Hookshot Play

Use Clawshot's **Play**, or the pack's Play launcher. These isolate saves under the seed's
`user` folder. Leave **Save folder** empty. Installing a mod manually in Hookshot instead uses
Hookshot's normal user folder: choose that folder explicitly and back up saves before New Game.
Do not choose the game dump or a generated `romfs` folder as a save folder.

## Longshot and emulators

Clawshot **Play** uses the same per-seed `user` layout for a supported Longshot installation.
Leave **Save folder** empty when using it. If you manually copied the seed to Longshot's mods,
choose the Longshot **user** folder where that run saves instead. Clawshot only reads it. From Longshot 3.1 on,
the game also keeps a working copy in `user/save-work/` beside `user/save/`; the tracker reads only the finished
saves in `save/` and ignores `save-work`, so each slot is listed once (checked on a copy of a Longshot 3.1.1
user folder).

For an emulator, choose this game's save folder (containing `slot_NN`), or its enclosing
user/save folder. Nested user-ID/title-ID folders are searched. Multiple profiles can contain
identically named slots: use the full listed slot path to distinguish them. Back up your normal
emulator saves before starting a randomizer; the tracker does not isolate or repair them.

A save does not reliably identify its seed. The tracker reports any mismatch it can establish,
but **cannot certify that a vanilla/older save belongs to this seed**. Confirm the game is loading
only the intended seed and select its matching save folder; a warning is not permission to ignore
this. Never use similar inventory or check counts as seed-identity proof.

## Spoilers

Default mode does not return an unvisited location's reward. **Show locations (spoilers)**
requires confirmation and then reveals the seed's location list and rewards. Turn it off to
return to spoiler-free tracking. The spoiler log, play note and screenshots of revealed locations
must not be shared with players avoiding spoilers. The OBS view is always location-spoiler-free,
even while the app tab's spoiler mode is on.

## OBS Browser Source

1. Configure the Tracker tab and keep Clawshot running.
2. Choose **OBS item labels**, **OBS columns** (Auto or 1–8), **OBS dungeon names**,
   **Transparent OBS background** and, under **OBS shows**, the sections to show, then **Copy URL**.
   These OBS-only controls do not change the in-app tracker layout.
3. In OBS add a **Browser Source** and use that URL. Sections stack vertically in a narrow block.
   The default view has no item labels: about 260 pixels wide and under 1000 tall with dungeon keys,
   the collection line, items, and stones and medallions, so it fits beside a 1080p game. With item
   labels it is about 340 wide and 1850 tall. Text fallbacks can increase height. The OBS view never
   shows warnings: check save/seed warnings in the app's Tracker tab.
   The surface has no controls and follows the same seed/save/slot as the app tracker.
4. Disable OBS's shutdown-when-not-visible option if you want continuous refresh while hidden.

The URL includes a private, random per-run token. Do not publish it or paste it into a public
chat. Closing/restarting Clawshot invalidates it; copy the new URL into OBS. Nothing is exposed
on the network: the server binds only `127.0.0.1` on a random port, keeps its Host/Origin checks,
and makes no external requests. OBS must run on the same computer.

The URL fragment defaults to
`labels=0&icons=1&transparent=0&names=short&sections=dungeons,collection,items,rewards`; `labels=1`
asks for labelled cells. `columns` accepts whole numbers 1–8; missing/invalid values (the app's
**Auto**) use six without labels and four with them. Copy the updated URL into OBS after changing
controls. Cells have a faint outline and no tile behind them. A held item is bright, a missing one is
dimmed; no caption says "held" or "not held". Captions appear only for tiers and counts (with labels)
and as badges without labels: top-left for upgrade tiers, bottom-right for counts (bottles, ammo,
rupees or magic capacity). Dashed cells and `?` mean the save could not show that field. Before the
first save every item is simply dimmed, under one short "No save yet" line. Names and the full state
remain available as tooltips and accessible labels. Without a usable item icon, text stays visible
even with labels off.

Compact quest cells use flat CSS, not game art: songs are `ZL`, `Ep`, `Sa`, `Su`, `SoT`, `SoS`,
`Min`, `Bol`, `Ser`, `Req`, `Noc`, `Pre`, `Scr`; stones are `Kok`, `Gor`, `Zor`.
Medallions are circles: forest green, fire red, water blue, shadow purple, spirit orange,
light yellow. Missing holdings use the same grey-out. Full names remain in tooltips and accessible
labels. Single-tier entries never display a tier number, in either the tab or OBS.

Without labels, OBS hides the heading, the section titles and warning paragraphs. Normal following
needs no status line; waiting/unavailable states show one short line, and a single missed update
changes nothing (after three in a row it says "Tracker connection lost"). The app keeps its status and
warnings on the Tracker tab and the check list on the Checks tab.

Each dungeon row shows only the items that dungeon has in this seed: no boss key at the Deku Tree,
no small-key cell where the seed holds none, no map or compass where there is none; an empty slot
keeps the columns lined up. `names` sets the dungeon names: `short` (the default: Deku, Dodongo,
Jabu, Forest, Fire, Water, Shadow, Spirit, Well, Ice, GTG, Ganon, Fortress), `full`, or `none` to
hide them; any other value is `short`, and the full name stays in the tooltip. The small-key badge
(bottom right) is **held**, available to spend, and shows only when it is not zero; the corner
number at the bottom left is **found / seed total**, including spent keys. Other icons are greyed
out when missing. Hover for the full description; unknown flags show `?`. With icons disabled or
unavailable, each indicator uses its name and saved value instead. Collection counts stay visible
with item labels off.

`sections` accepts comma-separated `dungeons`, `collection` (hearts, pieces, tokens and Skulltula
checks), `items`, `songs`, `rewards` (stones and medallions) and `areas` (**Checks by area**, a
spoiler-free count per area). `quest`, from older URLs, means collection, songs and rewards. Missing,
empty or any unknown section value shows the defaults (`dungeons,collection,items,rewards`); songs add
about 120 pixels without labels, and Checks by area is off unless asked for. The original order is
kept, not the order typed in the URL. Clearing the last section checkbox restores the defaults; the
app tab always keeps every group.

### Two browser sources for a 1080p stream

1. Leave **OBS item labels** off and **Local item icons** on.
2. Under **OBS shows** check only **Dungeon keys**, **Copy URL**, and use it for the first Browser
   Source (`sections=dungeons`).
3. Check only **Collection**, **Items**, **Songs** and **Stones & medallions**, copy that URL, and use it
   for the second source. Place the sources side by side; both follow the same seed/save.

Start each source at **290×1080**. Increase columns if text fallbacks make a part taller.
Changing checkboxes updates the copied URL, not URLs already configured in OBS; paste each new URL
into its corresponding source.


## Local icons and fallback

No game art or fonts are included. Icons are decoded at runtime from **your own** checked Game
dump (`UI/Tex/Icon/*.bntx.zs`), including `.nup` and `.nx` inputs and a separately chosen update
(its copy of an icon wins), using the optional UI texture decoder.
The optional `ui` extra includes [texture2ddecoder 1.0.6](https://pypi.org/project/texture2ddecoder/1.0.6/)
([MIT licence](https://github.com/K0lb3/texture2ddecoder/blob/master/LICENSE)); compatible wheels exist
for Windows, Linux and macOS. Use `uv run --extra ui python -m clawshot.ui` from source.
Windows's starter installs the extra; the current Linux/macOS starter omits it and uses text fallback
unless you install the extra yourself. Dependency installation may need internet; the running
interface and icon extraction make no network requests. Linux/macOS icon execution is not certified here.

Decoded PNGs are private game-derived data, never shipped in this repository or a seed pack.
Cache folders: Windows `%LOCALAPPDATA%/Clawshot/Cache/icons`; macOS
`~/Library/Caches/Clawshot/icons`; Linux `$XDG_CACHE_HOME/clawshot/icons` (default `~/.cache/clawshot/icons`).
Do not share them. Filenames include the source icon's hash; changing the dump or its update invalidates that icon.
Small keys, boss keys, maps and compasses use the game's `Item_Dungeon_*` icon files through
the same decoder/cache. Songs, stones and medallions have no file in `UI/Tex/Icon`: labelled views
use text, and compact OBS uses the CSS quest chips described above.
If a dump, decoder or texture is unavailable, the same view still works; uncheck **Local item icons**
to force text/CSS.
All fonts are installed system fonts.

## Safe headless operation

`uv run python -m clawshot.ui --no-open` prints a token URL without opening any window or dialog.
Paste paths to track saves; Browse/Open/Play remain disabled. The standalone OBS view is also
available in this mode. The tracker never starts a game, writes a save, or changes seed contents;
it writes only its manual-marks file in the preferences folder.

The automated evidence uses synthetic saves, read-only copies of real saves and headless browser
captures. Those checks do not prove in-game pickup/update behavior; the maintainers' staged
Longshot acceptance checklist is in `plans/rounds/r14-tracker.md`.
