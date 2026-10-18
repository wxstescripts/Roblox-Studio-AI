# Task 1.46 — Signage, Wayfinding & Plot Orientation Audit

## Executive Summary
In **Task 1.46**, a comprehensive, read-only architectural audit was conducted across **Pet Mining Empire** to evaluate:
1. Every directional, wayfinding, entrance, station, and progression sign in the world for legibility, orientation, obstruction, and correctness.
2. The coordinate systems, azimuths, and local transforms of all six radial tycoon plots (`Plot_1` through `Plot_6`) to determine if plot entrances, spawn locations, and building systems are correctly oriented.
3. The feasibility of plot interior detailing and a rebirth-gated personal mine system that preserves existing tycoon building envelopes.

### Key Audit Findings
- **Major Signage Defect**: All 4 ground-level hub `WayfindingSigns` (`Sign_MineQuarry`, `Sign_Headframe`, `Sign_EastSector`, `Sign_WestSector`) suffer from a severe 3D modeling bug where the vertical support post (`SignPost`, thickness $0.50$ studs) passes directly through the center of the signboard (`SignBoard`, thickness $0.30$ studs), protruding $0.10$ studs in front of the text and bisecting words (`STAGE [POST] QUARRY`, `HEADFRAME [POST] DERRICK`). In addition, these signs display identical arrows and text on both sides, causing directional contradictions for players returning to the hub.
- **Hidden / Occluded Sign**: `MineEntrancePortal.PortalOverheadBeam.CorpBrandingGui` (`★ PROFIT MINING CORP. ★`) is placed directly behind `PortalSignBoard` at the exact same elevation, making it 100% invisible to players.
- **Stage 3 Gate Obstruction**: `ProgressionGate_Stage3.GateSign` has a red warning light part positioned directly over the center of the signboard text, obscuring the word `RESTRICTED`.
- **Plot Alignment & Entrances (PASS)**: All 6 plots are mathematically positioned at radius $R = 160$ studs and rotated to face the origin $(0, 1, 0)$. Entrance ramps, lot placards, and curb transitions connect flush to radial roads on all 6 plots.
- **Plot Spawn Orientation Defect (MAJOR)**: Every plot's `PlotSpawn` pad has its `LookVector` pointing toward the map origin (out the front gate). When players spawn or respawn on their base, **they spawn facing backwards toward the road**, with their factory lines, machines, and base behind them.
- **Claim Station Placement (USABILITY ISSUE)**: While `ClaimStation` is oriented correctly, it is placed at the far back wall of the plot ($Z = +24$, 56 studs from the entrance), forcing approaching players to walk across the entire empty lot to claim it.

---

## 1. World Signage Inventory & Defect Audit

Across the active Roblox Studio DataModel, **57 GUI instances** (SurfaceGuis and BillboardGuis) were inspected:

| Sign Identifier & Instance Path | Display Type & Face | Canvas & Dimensions | Displayed Text / Content | Orientation & Visual Audit Finding | Recommended Correction |
| :--- | :---: | :---: | :--- | :--- | :--- |
| **`Sign_MineQuarry`**<br>`Workspace.Environment.Hub.WayfindingSigns.Sign_MineQuarry.SignBoard` | SurfaceGui<br>(Both Front & Back) | $800 \times 600$<br>Part: $6.4 \times 1.8 \times 0.3$ | `▲ STAGE 1 QUARRY`<br>`DESCENT SHAFT & ORE EXTRACTION` | **CRITICAL DEFECT**: `SignPost` ($0.5$ thick) intersects through the center of `SignBoard` ($0.3$ thick), cutting directly through the letters. Both faces display identical text with upward arrow `▲`, confusing players exiting the quarry. | Move `SignPost` behind board or use dual side posts. Make Front face display `▼ CENTRAL HUB -- OPERATIONS & SPAWN`. Set canvas to $1280 \times 360$ ($3.55:1$). |
| **`Sign_Headframe`**<br>`Workspace.Environment.Hub.WayfindingSigns.Sign_Headframe.SignBoard` | SurfaceGui<br>(Both Front & Back) | $800 \times 600$<br>Part: $6.4 \times 1.8 \times 0.3$ | `▼ HEADFRAME DERRICK`<br>`CENTRAL HOIST & EQUIPMENT DEPOT` | **CRITICAL DEFECT**: Same bisection bug (post penetrates board). Identical text on both sides causes directional contradiction when approaching from the south. | Recess post behind board. Make outbound face display `▲ CENTRAL HUB -- OPERATIONS & SPAWN`. |
| **`Sign_EastSector`**<br>`Workspace.Environment.Hub.WayfindingSigns.Sign_EastSector.SignBoard` | SurfaceGui<br>(Both Front & Back) | $800 \times 600$<br>Part: $6.4 \times 1.8 \times 0.3$ | `▶ SECTOR EAST`<br>`TYCOON PLOTS 1, 2, 3` | **CRITICAL DEFECT**: Same post bisection bug. Canvas aspect ratio ($1.33:1$) does not match part aspect ratio ($3.55:1$). | Recess post behind board. Correct canvas size to $1280 \times 360$. Add inward-facing text. |
| **`Sign_WestSector`**<br>`Workspace.Environment.Hub.WayfindingSigns.Sign_WestSector.SignBoard` | SurfaceGui<br>(Both Front & Back) | $800 \times 600$<br>Part: $6.4 \times 1.8 \times 0.3$ | `◀ SECTOR WEST`<br>`TYCOON PLOTS 4, 5, 6` | **CRITICAL DEFECT**: Same post bisection bug. Identical text on both sides. | Recess post behind board. Correct canvas size. Add inward-facing text. |
| **`CentralOperationsGantry` Signs (4)**<br>`Workspace.Environment.Hub.Plaza.CentralOperationsGantry.Sign_Gantry_*` | SurfaceGui<br>(Front & Back) | $920 \times 140$<br>Part: $9.2 \times 1.4 \times 0.25$ | North: `SECTOR 1 -- EXCAVATION PIT`<br>South: `SECTOR SOUTH -- HEADFRAME HOIST`<br>East: `SECTOR EAST -- PLOTS 1, 2, 3`<br>West: `SECTOR WEST -- PLOTS 4, 5, 6` | **PASS**: Clean overhead two-sided displays at $Y=13.9$. Distinct inbound and outbound messages. GothamBold typography with gold/cyan accent colors. | No changes needed. |
| **`MineEntrancePortal.PortalSignBoard`**<br>`Workspace.Environment.Hub.MineEntrancePortal.PortalSignBoard` | SurfaceGui<br>(Front & Back) | $1200 \times 200$<br>Part: $16.0 \times 2.4 \times 0.5$ | Back: `SECTOR 1 — EXCAVATION PIT`<br>Front: `SECTOR 0 — CENTRAL HUB` | **PASS**: Fully readable, high-contrast, double-sided sign clearly visible from hub approach and quarry exit. | No changes needed. |
| **`MineEntrancePortal.PortalOverheadBeam`**<br>`Workspace.Environment.Hub.MineEntrancePortal.PortalOverheadBeam` | SurfaceGui<br>(Front) | $800 \times 600$<br>Part: $22.0 \times 2.4 \times 3.8$ | `★ PROFIT MINING CORP. ★` | **DEFECT (Occluded)**: Positioned at $Z = -14.0$, directly behind `PortalSignBoard` ($Z = -11.95$) at the same height ($Y = 16.2$). Completely blocked from view. | Reposition branding to the upper gantry beam ($Y = 19.5$) or remove redundant GUI. |
| **`QuarryEnclosure.DescentSignBoard`**<br>`Workspace.Environment.Hub.QuarryEnclosure.DescentPortalGantry` | SurfaceGui<br>(Back) | $1400 \times 180$<br>Part: $14.0 \times 1.8 \times 0.4$ | `DEEP MINE SHAFT — LEVEL 2 DESCENT` | **PASS**: Bold yellow-orange text directly over the incline rail descent shaft. | No changes needed. |
| **`HeadframeDerrickTower.TowerNameplate`**<br>`Workspace.Environment.Hub.HeadframeDerrickTower.TowerNameplate` | SurfaceGui<br>(Front) | $800 \times 600$<br>Part: $18.0 \times 2.2 \times 0.4$ | `PROFIT MINING CORP. — SHAFT 1`<br>`DEEP EXTRACTION HEADFRAME & HOIST` | **MINOR INCONSISTENCY**: Company name uses `PROFIT MINING CORP.` whereas central hub uses `PET MINING CORP.`. Perfectly visible facing North down Headframe Boulevard. | Align company branding to `PET MINING CORP.` for universal lore consistency. |
| **`ProgressionGate_Stage3.GateSign`**<br>`Workspace.Caves.Stage_2.ProgressionGate_Stage3.GateSign` | SurfaceGui<br>(Back) | $1600 \times 200$<br>Part: $22.0 \times 2.2 \times 0.5$ | `LEVEL 3 SHAFT — RESTRICTED: ADVANCED CLEARANCE REQUIRED` | **DEFECT (Obstruction)**: A red warning light box part is mounted directly in front of the text, obscuring the word `RESTRICTED`. | Move warning light to top edge of sign bracket ($Y = -6.2$). |
| **`Stage 2 Bay Signs (2)`**<br>`Workspace.Caves.Stage_2.*Grotto.*Signboard` | SurfaceGui<br>(Left & Right) | $800 \times 600$<br>Part: $0.3 \times 1.4 \times 8.0$ | `SECTOR 2-A: IRON GROTTO`<br>`SECTOR 2-B: GOLD GROTTO` | **PASS**: Wall-mounted perpendicular signboards clearly visible from the central cavern transit cart track. | No changes needed. |
| **`EquipmentStation.ShopLabel`**<br>`Workspace.Environment.Hub.EquipmentStation.TableTop` | BillboardGui | $6 \times 2.5$ studs | `EQUIPMENT UPGRADE SHOP`<br>`Pickaxes & Backpacks` | **PASS**: Overhead billboard always turns to face approaching players. | No changes needed. |
| **`EggHatchingStation` Telemetry & Sign**<br>`Workspace.Environment.Hub.EggHatchingStation` | SurfaceGui<br>(Top & Front/Back) | Varied | `BIO-INCUBATION CHAMBER • ONLINE`<br>`EGG INCUBATOR [ 250 COINS ]` | **PASS**: Screen telemetry is angled on terminal; overhead sign is double-sided and legible. | No changes needed. |
| **`Plot Gate Placards (12)`**<br>`Workspace.Plots.Plot_*.PlotEntranceGateway.LotPlacard_*` | SurfaceGui<br>(Front) | $240 \times 120$<br>Part: $1.2 \times 0.6 \times 0.1$ | `LOT #1` through `LOT #6` | **PASS**: Mounted on entrance gate pillars facing outward along the incoming road. High contrast gold lettering. | No changes needed. |
| **`Plot Claim Signs (6)`**<br>`Workspace.Plots.Plot_*.ClaimStation.SignBoard` | BillboardGui | $6 \times 3$ studs | `PLOT #X [ AVAILABLE ]` /<br>`OWNER: PlayerName` | **PASS (Visual) / DEFECT (Usability)**: Text rotates to face player, but sign is located at the far back wall of the plot ($Z = +24$), 56 studs away from the road entrance. | Relocate Claim Station to the front entrance ($Z = -24$). |
| **`Plot Drop-Off Signs (6)`**<br>`Workspace.Plots.Plot_*.DropOffStation.DropOffPad` | BillboardGui | $6 \times 2.5$ studs | `ORE DROP-OFF`<br>`[ CLAIM BASE TO USE ]` | **PASS**: Positioned over drop-off pad at $Z = +16$. Billboard faces player. | No changes needed. |

---

## 2. Six-Plot Orientation & Layout Audit

### A. Measured World-Space Transforms & Azimuths
All 6 plots were audited for position, rotation, and radial consistency:

```
Map Center: (0, 1, 0) | Base Radius: 160.0 studs | Plot Dimensions: 64 x 4 x 64 studs
```

| Plot Name | Azimuth Angle | World Position $(X, Y, Z)$ | LookVector $(X, Y, Z)$ | Dot Product to Origin | Entrance Ramp Pos $(X, Z)$ | Connecting Road Threshold $(X, Z)$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Plot_1`** | $45^\circ$ | $(113.1, 1.0, -113.1)$ | $(-0.71, 0.00, 0.71)$ | **$1.000$** | $(90.5, -90.5)$ | $(87.7, -87.7)$ [Road 1] |
| **`Plot_2`** | $90^\circ$ | $(160.0, 1.0, 0.0)$ | $(-1.00, 0.00, 0.00)$ | **$1.000$** | $(128.0, 0.0)$ | $(124.0, 0.0)$ [Road 2] |
| **`Plot_3`** | $135^\circ$ | $(113.1, 1.0, 113.1)$ | $(-0.71, 0.00, -0.71)$ | **$1.000$** | $(90.5, 90.5)$ | $(87.7, 87.7)$ [Road 3] |
| **`Plot_4`** | $225^\circ$ | $(-113.1, 1.0, 113.1)$ | $(0.71, 0.00, -0.71)$ | **$1.000$** | $(-90.5, 90.5)$ | $(-87.7, 87.7)$ [Road 4] |
| **`Plot_5`** | $270^\circ$ | $(-160.0, 1.0, 0.0)$ | $(1.00, 0.00, 0.00)$ | **$1.000$** | $(-128.0, 0.0)$ | $(-124.0, 0.0)$ [Road 5] |
| **`Plot_6`** | $315^\circ$ | $(-113.1, 1.0, -113.1)$ | $(0.71, 0.00, 0.71)$ | **$1.000$** | $(-90.5, -90.5)$ | $(-87.7, -87.7)$ [Road 6] |

### B. Orientation Audit Conclusions
1. **Plot Base & Road Transitions (PASS)**:
   - Every plot's `LookVector` points directly toward the center origin $(0, 1, 0)$ with a dot product of exactly $1.000$.
   - In the plot's local coordinate system:
     - Local $-Z$ is **FRONT** (facing the road and central hub).
     - Local $+Z$ is **BACK** (facing the outer perimeter cliff).
     - Local $\pm X$ are the left and right plot boundaries.
   - The entrance ramp is located at local $Z = -32.0$ studs (distance to center = $128.0$ studs), connecting seamlessly to the radial road network across all 6 plots.
   - **Conclusion**: There is NO global rotation or placement bug with the plots or road alignments.
2. **Plot Spawn Point Orientation Defect (MAJOR CONFIRMED DEFECT)**:
   - In `PlotService.luau` line 425:
     `spawnLoc.CFrame = cframe * CFrame.new(spawnOffset.X, ..., spawnOffset.Z)`
   - Because `spawnLoc.CFrame` inherits `cframe.LookVector` without a rotation offset, `PlotSpawn.CFrame.LookVector` points toward the origin (towards the road / out the front gate).
   - When a player respawns on their base or teleports to their base (`PlotService:TeleportToSpawn`), **the character spawns facing OUT of the plot**, with their back to their factory line, machines, droppers, and claim sign!
   - **Correction**: In `PlotService.luau`, rotate `PlotSpawn` by $180^\circ$:
     `spawnLoc.CFrame = cframe * CFrame.new(spawnOffset.X, ..., spawnOffset.Z) * CFrame.Angles(0, math.rad(180), 0)`.
3. **Claim Station Accessibility (MAJOR USABILITY ISSUE)**:
   - `ClaimStation` is placed at local $Z = +24.0$ studs (near the rear wall), $56$ studs from the entrance ramp.
   - Approaching players must walk all the way across the barren plot pad to claim it.
   - **Correction**: Relocate `ClaimStation` to local $Z = -24.0$ studs (flanking the entrance gate) so players can claim the base immediately upon arrival.

---

## 3. Photographic Evidence & Visual Defects

### Evidence 1: Hub Wayfinding Sign Post Bisection Bug
*Ground-level photograph of `Sign_MineQuarry` showing `SignPost` intersecting through the signboard and bisecting words:*

![Wayfinding Sign Post Bisection Bug](file:///C:/Users/heckz/.gemini/antigravity/brain/c6768c4e-042b-423d-9cda-2e91a32eb976/task146_hub_sign_minequarry.jpg)

---

### Evidence 2: Plot Entrance & Remote Claim Station Distance
*Looking into Plot 2 through the entrance gate, displaying the `LOT #2` placards, entrance ramp, `PlotSpawn` pad, and the distant `ClaimStation` at the far rear wall ($56$ studs away):*

![Plot Entrance and Distant Claim Station](file:///C:/Users/heckz/.gemini/antigravity/brain/c6768c4e-042b-423d-9cda-2e91a32eb976/task146_plot_entrance_view.jpg)

---

### Evidence 3: Backwards Plot Spawn Orientation
*Player character standing on `PlotSpawn` immediately upon spawning, facing OUT of the plot toward the road and distant Headframe, with their entire tycoon factory area behind them:*

![Backwards Plot Spawn Orientation](file:///C:/Users/heckz/.gemini/antigravity/brain/c6768c4e-042b-423d-9cda-2e91a32eb976/task146_spawn_facing_backwards.jpg)

---

### Evidence 4: Stage 3 Progression Gate Sign Obstruction
*`ProgressionGate_Stage3.GateSign` with the red warning light beacon intersecting down through the center of the signboard, obscuring the word `RESTRICTED`:*

![Stage 3 Gate Sign Obstruction](file:///C:/Users/heckz/.gemini/antigravity/brain/c6768c4e-042b-423d-9cda-2e91a32eb976/task146_stage3_gate_sign.jpg)

---

## 4. Confirmed Defects vs. Possible Improvements

### Confirmed Defects (Requiring Fixes)
1. **Wayfinding Sign Post Clipping**: In all 4 `WayfindingSigns` (`Sign_MineQuarry`, `Sign_Headframe`, `Sign_EastSector`, `Sign_WestSector`), the vertical post penetrates through the signboard and bisects text on both faces.
2. **Wayfinding Sign Directional Arrows**: All 4 wayfinding signs display identical arrows on front and back faces, directing players backwards when returning to the hub.
3. **Backwards Plot Respawn Direction**: `PlotSpawn` faces the road instead of the tycoon base interior.
4. **Stage 3 Gate Warning Light Obstruction**: Red beacon box part covers text on `GateSign`.
5. **Occluded Branding GUI**: `MineEntrancePortal.PortalOverheadBeam.CorpBrandingGui` is completely hidden behind `PortalSignBoard`.

### Possible Architectural & Usability Improvements
1. **Claim Station Forward Relocation**: Moving the claim station from the back ($Z = +24$) to the front ($Z = -24$) improves player onboarding and matches classic tycoon gameplay UX.
2. **Branding Lore Standardization**: Unify company naming across all assets (`PET MINING CORP.` vs. `PROFIT MINING CORP.`).
3. **Wayfinding Canvas Rescaling**: Update `WayfindingSigns` canvas sizes from $800 \times 600$ to $1280 \times 360$ to match the $3.55:1$ signboard aspect ratio.

---

## 5. Proposed Plot Interior Decoration Plan

To make plots feel developed without interfering with tycoon machines or purchase buttons:

```
PLOT FOOTPRINT ENVELOPE: 64 x 64 studs (X in [-32, 32], Z in [-32, 32])
┌────────────────────────────────────────────────────────┐
│ [REAR BOUNDARY - Z = +32] (Wall & Perimeter Cliff)     │
│                                                        │
│  [Zone C: Future Personal Mine Shaft - X in [14, 28]]  │
│  [Drop-Off Pad - X = 0, Z = +16]                       │
│                                                        │
│  [Purchase Buttons - X in [-16, 8], Z in [6, 10]]      │
│  [Machine Conveyor - X = -12, Z in [-11, 11]]          │
│                                                        │
│  [Zone B: Open Tycoon Build Space - X in [6, 28]]      │
│  [Plot Spawn - X = 0, Z = -20]                         │
│                                                        │
│  [Zone A: Relocated Claim Kiosk - X = -8, Z = -24]     │
│  [Zone D: Tool Storage Shed Alcove - X = 20, Z = -24]  │
│                                                        │
│ [FRONT ENTRANCE - Z = -32] (Ramp & Gate Pillars)       │
└────────────────────────────────────────────────────────┘
```

### Proposed Detailing Items (100% Non-Collidable / Outside Build Lines)
1. **Flush Foundation Construction Seams**: Add low-contrast expansion joint lines and yellow survey chalk crosshairs flush on `PlotBase` ($Y = 1.01$).
2. **Perimeter Utility Junction Stubs**: Add non-collidable cast-iron electrical boxes, yellow conduit pipes, and wall-mounted hazard warning decals mounted along `PlotCurbs`.
3. **Industrial Field Office / Tool Shed Alcove**: Position a compact, weathered corrugated-metal site locker in the unused front-right corner ($X \in [18, 26], Z \in [-28, -20]$), containing decorative tool racks, hard hats, and an exterior work lantern.
4. **Forward Claim Station Kiosk**: Move the Claim Station to the front-left perimeter ($X = -8, Z = -24$), featuring an illuminated podium console and clear status monitor.

---

## 6. Personal Mine Progression Design & Feasibility

### A. Current Progression & Rebirth Architecture
- **Data Persistence**: `DataSchema.luau` already defines `Rebirth: { RebirthCount: number, PermanentMultipliers: {...}, PermanentUpgrades: {...} }` and `Stats.TotalRebirths`.
- **Multiplier Consumers**: `PlotService:SellBackpack` and `TycoonService` already query `profile.Data.Rebirth.PermanentMultipliers.CoinMultiplier`.
- **Node Spawning System**: `MiningService.luau` contains an isolated, production-ready node constructor:
  `createNode(id: string, oreType: string, cframe: CFrame, parent: Instance): OreNodeRecord`
  This constructor wires health replication, damage networking, particle bursts, depletion, and respawning.

### B. Proposed Personal Mine Design
1. **Unlock Condition**:
   - Gated behind **Rebirth 1+** (or a progression milestone).
   - An interactive mine shaft hatch / industrial hoist elevator appears in the rear-right sector of the plot ($X \in [14, 26], Z \in [16, 26]$).
2. **World Placement & Plot Isolation Architecture**:
   - Rather than creating complex client-only streaming caves, **create 6 physical instanced mine caverns** directly beneath the 6 plots at $Y = -80$ studs!
   - Each personal mine cavern is positioned directly beneath its corresponding plot index:
     `Mine_Plot_1` beneath `Plot_1`, `Mine_Plot_2` beneath `Plot_2`, etc.
   - Caverns are separated from each other by $>120$ studs of void/rock, ensuring complete visual and physical isolation.
   - Stepping on the plot mine elevator teleports the player smoothly between plot ground level and their private subterranean shaft.
3. **Data Ownership & Plot Lifecycle Rules**:
   - *Plot Release Rule*: When a player disconnects or releases their plot, `PlotService:ReleasePlot(index)` automatically clears active drops and resets the personal mine nodes for that plot index.
   - *Ownership Rule*: `MiningService` verifies that the player attempting to mine a personal node owns the plot associated with that node (`personalNode.PlotIndex == playerPlotIndex`).
   - *Rebirth Scaling*: Personal mine nodes scale with Rebirth Count (e.g., Rebirth 1 unlocks Iron/Gold veins; Rebirth 2 unlocks Cyanite geodes; Rebirth 3+ unlocks Prismatic/Void clusters).

---

## 7. Verification of Scope & Studio State
- **Strict Read-Only Adherence**: Zero parts were modified, created, deleted, or moved.
- **Scripts & Services**: Zero code changes were made to `PlotService`, `TycoonService`, `MiningService`, or any client controller.
- **Studio State**: Roblox Studio has been safely returned to **Edit** mode (`DataModel: Edit`).
