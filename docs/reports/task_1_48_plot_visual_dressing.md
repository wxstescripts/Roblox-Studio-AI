# Task 1.48 — Plot Visual Dressing & Construction Detail

## Executive Summary
In **Task 1.48**, an industrial visual dressing pass was engineered and applied across all six player plots in **Pet Mining Empire**. The goal was to transform the barren, generic concrete pads into engineered, authentic mining work sites while strictly respecting protected gameplay envelopes, maintaining clean silhouettes, and preserving all existing game mechanics.

### Key Accomplishments
1. **Concrete Expansion Seams & Surface Grid Lines**:
   - Added flush dark joint sealant seams (`Seam_Transverse`, `Seam_Longitudinal_Mid`, `Seam_Longitudinal_Front`) that divide each plot's $64 \times 64$ slab into civil-engineered concrete sections.
   - All seams are flush ($Y = 2.01$ local), anchored, and 100% non-collidable (`CanCollide = false`).
2. **Drop Zone Caution Stencil**:
   - Added a bold yellow diamond-plate caution line (`DropZoneCautionLine` at $Z = 10.5$) demarcating the industrial staging approach to the `DropOffStation`.
3. **Front-Right Site Power Distribution Cabinet**:
   - Tucked into the previously vacant front-right staging alcove ($X = 20.0, Z = -27.5$), each plot now features a heavy-duty industrial breaker cabinet (`SitePowerCabinet`):
     - Cast concrete plinth $(3.2 \times 0.3 \times 1.8)$ and dark olive steel cabinet body $(2.8 \times 3.8 \times 1.4)$.
     - Overhanging angled weather hood and twin conduit drops diving into the perimeter curb.
     - Custom high-contrast telemetry SurfaceGui with sector-specific electrical identification:
       - Plots 1, 2, 3: `FEEDER E-01` through `FEEDER E-03` (Sector East gold accent).
       - Plots 4, 5, 6: `FEEDER W-01` through `FEEDER W-03` (Sector West cyan accent).
       - Voltage rating: `480V 3Φ MAIN BREAKER`, `STATUS: ENERGIZED`.
4. **Perimeter Utility Conduit & Wall Junction Boxes**:
   - Mounted along the inner face of the left curb wall ($X = -30.8$):
     - A continuous steel conduit pipe (`PerimeterConduitPipe`, length $46$ studs) elevated on 4 standoff brackets.
     - Two wall-mounted cast-iron electrical junction boxes (`JunctionBox_Manufacturing` at $Z = -8.0$, aligned with the dropper line; `JunctionBox_ControlRow` at $Z = 8.0$, aligned with the button row).
5. **Rear Mountain Rock Anchor Tie-Backs**:
   - Placed along the rear cliff curb ($Z = +31.5$):
     - 3 heavy corroded steel rock anchor plates (`AnchorPlate_*` at $X = -18, 0, +18$) with central square tension nuts bolting the concrete foundation into the mountain bedrock behind each plot.
6. **Subtle Secondary Variation**:
   - Odd plots (1, 3, 5): Feature an inline brass pneumatic regulator stem and safety red valve wheel (`ValveWheel`).
   - Even plots (2, 4, 6): Feature a dual conduit riser splitter stub (`ConduitSplitterStub`).
7. **Authoritative Source Synchronization**:
   - Added the modular construction logic to `createPlotModel` in `src/ServerScriptService/Services/PlotService.luau` and synchronized it into Studio's internal `game.ServerScriptService.Source.Services.PlotService` ModuleScript.
   - Encapsulated all details under `model.PlotSiteDetails`, ensuring plot resets and releases never touch or duplicate decorative geometry.

---

## 1. Before & After Hierarchy and Part Counts

### A. Instance Hierarchy Comparison
```
BEFORE (16 Children, 45 Parts):
Plot_X [Model]
├── FoundationFooting [Part]
├── PlotBase [Part]
├── PlotCurbs [Model] (4 pylons, 4 caps, 3 curbs, 3 curb caps, 3 rails)
├── PlotEntranceGateway [Model] (2 plinths, 2 pillars, 2 reflectors, 2 placards)
├── VehicularRoadApron [Part]
├── ApronHazardStrip [Part]
├── PlotEntranceRamp [Part]
├── RampTractionStripes [Part]
├── RampEdgeCurb_L [Part]
├── RampEdgeCurb_R [Part]
├── PlotSpawn [SpawnLocation]
├── ClaimStation [Model] (ClaimPad, SignPost, SignBoard, OwnershipBillboard)
├── DropOffStation [Model] (DropOffPad, DropOffBorder, SellPrompt, SellBillboard)
├── PurchasedObjects [Folder]
├── ActiveDrops [Folder]
└── PurchaseButtons [Folder]

AFTER (17 Children, 68–69 Parts):
Plot_X [Model]
├── ... (All 16 existing children preserved exactly)
└── PlotSiteDetails [Model] (NEW - 23 to 24 parts)
    ├── Seam_Transverse [Part] (CanCollide = false)
    ├── Seam_Longitudinal_Mid [Part] (CanCollide = false)
    ├── Seam_Longitudinal_Front [Part] (CanCollide = false)
    ├── DropZoneCautionLine [Part] (CanCollide = false)
    ├── SitePowerCabinet [Model]
    │   ├── CabinetPlinth [Part]
    │   ├── CabinetBody [Part] (with CabinetPanelGui)
    │   ├── CabinetWeatherHood [Part]
    │   ├── PowerConduitDrop_-1 [Part]
    │   └── PowerConduitDrop_1 [Part]
    ├── PerimeterConduitPipe [Part] (CanCollide = false)
    ├── ConduitBracket (4 instances) [Part] (CanCollide = false)
    ├── JunctionBox_Manufacturing [Part] (CanCollide = false)
    ├── JunctionBox_ControlRow [Part] (CanCollide = false)
    ├── RockAnchorTieBacks [Model]
    │   ├── AnchorPlate_-18 / AnchorNut_-18 [Parts] (CanCollide = false)
    │   ├── AnchorPlate_0 / AnchorNut_0 [Parts] (CanCollide = false)
    │   └── AnchorPlate_18 / AnchorNut_18 [Parts] (CanCollide = false)
    └── Secondary Variation:
        ├── Odd plots: PneumaticRegulatorStem + ValveWheel [Parts]
        └── Even plots: ConduitSplitterStub [Part]
```

### B. Quantitative Part Count Matrix

| Plot Name | Sector Identity | Initial Part Count | Added Parts | Total Parts After | Total Descendants |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **`Plot_1`** | Sector East (E-01) | 45 | +24 (with Valve Wheel) | **69** | 99 |
| **`Plot_2`** | Sector East (E-02) | 45 | +23 (with Conduit Splitter) | **68** | 98 |
| **`Plot_3`** | Sector East (E-03) | 45 | +24 (with Valve Wheel) | **69** | 99 |
| **`Plot_4`** | Sector West (W-01) | 45 | +23 (with Conduit Splitter) | **68** | 98 |
| **`Plot_5`** | Sector West (W-02) | 45 | +24 (with Valve Wheel) | **69** | 99 |
| **`Plot_6`** | Sector West (W-03) | 45 | +23 (with Conduit Splitter) | **68** | 98 |
| **World Total** | All 6 Plots | **270** | **+140** | **410** | **590** |

---

## 2. Exact Changed Source Files & DataModel Paths

### A. Source Files
1. [`src/ServerScriptService/Services/PlotService.luau`](file:///c:/Users/heckz/Downloads/Roblox%20Studio/src/ServerScriptService/Services/PlotService.luau#L586-L840):
   - Added `SiteDetails: Model?` to `export type PlotRecord`.
   - Inserted complete `PlotSiteDetails` construction inside `createPlotModel(index, cframe)`.
   - Assigned `SiteDetails = siteDetails` to the returned `PlotRecord`.

### B. Studio DataModel Paths
1. `game.ServerScriptService.Source.Services.PlotService` (ModuleScript):
   - Synchronized with disk via `multi_edit`, ensuring dynamic runtime generation matches source code.
2. `Workspace.Plots.Plot_1.PlotSiteDetails` through `Plot_6.PlotSiteDetails`:
   - Pre-instantiated and active in the Studio DataModel.

---

## 3. Placement Strategy & Protected-Envelope Checks

To guarantee zero interference with gameplay, character movement, prompts, machine building, and camera sightlines, every element was audited against strict bounding boxes:

```
PLOT FOOTPRINT ENVELOPE: 64 x 64 studs (Local X in [-32, 32], Local Z in [-32, 32])
┌────────────────────────────────────────────────────────┐
│ [REAR CURB - Z = +31.5]                                │
│  ✦ RockAnchorTieBacks (X = -18, 0, 18) [CANCOLLIDE=F]  │
│                                                        │
│  [DropOffPad - X in [-5, 5], Z in [11, 21]]            │
│  ✦ DropZoneCautionLine (X in [-6, 6], Z = 10.5)        │
│                                                        │
│  [Purchase Buttons - X in [-12, 6], Z = 8.0]           │
│  ✦ JunctionBox_ControlRow (X = -31.0, Z = 8.0)         │
│                                                        │
│  [Machine Corridor - X = -12.0, Z in [-8, 4]]          │
│  ✦ JunctionBox_Manufacturing (X = -31.0, Z = -8.0)     │
│  ✦ PerimeterConduitPipe (X = -30.8, Z in [-28, 18])    │
│                                                        │
│  ✦ Seam_Transverse (X = 0) / Seam_Longitudinal (Z = 0) │
│                                                        │
│  [PlotSpawn - X in [-3, 3], Z in [-23, -17]]           │
│                                                        │
│  [ClaimStation]                   ✦ SitePowerCabinet   │
│  (X = -9.0, Z = -22.5)             (X = 20.0, Z = -27.5)
│                                                        │
│ [FRONT ENTRANCE - Z = -32.0]                           │
│  [PlotEntranceRamp - X in [-5, 5], Z in [-35, -29]]    │
└────────────────────────────────────────────────────────┘
```

### Clearance Verification Table

| Protected Element | Element Envelope | Nearest Added Detail | Measured Separation | Collision Trap Check |
| :--- | :--- | :--- | :---: | :---: |
| **`PlotSpawn`** | $X \in [-3, 3], Z \in [-23, -17]$ | `SitePowerCabinet` ($X = 20.0, Z = -27.5$) | **$17.0$ studs** | **CLEAR** (Seams underneath are non-collidable) |
| **`ClaimStation`** | $X \in [-12, -6], Z \in [-26, -19.5]$ | `SitePowerCabinet` ($X = 20.0, Z = -27.5$) | **$26.0$ studs** | **CLEAR** (Opposite side of entrance) |
| **`PlotEntranceRamp`** | $X \in [-5, 5], Z \in [-35, -29]$ | `SitePowerCabinet` ($X = 20.0, Z = -27.5$) | **$15.0$ studs** | **CLEAR** (No obstructions in path) |
| **Machine Line** | $X = -12.0, Z \in [-8, 4]$ | `PerimeterConduitPipe` ($X = -30.8$) | **$18.8$ studs** | **CLEAR** (Conduit is against outer curb wall) |
| **Button Row** | $X \in [-12, 6], Z = 8.0$ | `JunctionBox_ControlRow` ($X = -31.0$) | **$19.0$ studs** | **CLEAR** (Flush on curb wall) |
| **`DropOffStation`** | $X \in [-5, 5], Z \in [11, 21]$ | `RockAnchorTieBacks` ($Z = 31.5$) | **$10.5$ studs** | **CLEAR** (Rear tie-backs flush against curb) |

---

## 4. Photographic Evidence & Visual Verifications

### Evidence 1: Front-Right Site Power Cabinet Close-Up
*Close-up of the newly installed `SitePowerCabinet` on Plot 2 ($X = 20.0, Z = -27.5$). Shows the concrete plinth, industrial diamond plate housing, weather hood, and telemetry GUI with the sector feeder tag `FEEDER E-02 / 480V 3Φ MAIN BREAKER / STATUS: ENERGIZED`:*

![Front-Right Site Power Cabinet](file:///C:/Users/heckz/.gemini/antigravity/brain/c6768c4e-042b-423d-9cda-2e91a32eb976/task148_plot_site_power_cabinet.jpg)

---

### Evidence 2: Floor Expansion Seams & Drop Zone Caution Line
*Ground-level perspective across the slab surface on Plot 2. Displays the dark joint sealant expansion seams dividing the concrete slab into civil-engineered panels, with the yellow diamond-plate caution line framing the approach to the drop-off station:*

![Floor Expansion Seams & Caution Line](file:///C:/Users/heckz/.gemini/antigravity/brain/c6768c4e-042b-423d-9cda-2e91a32eb976/task148_plot_seams_and_caution.jpg)

---

### Evidence 3: Perimeter Utility Conduit & Wall Junction Box
*Looking along the left perimeter curb wall ($X = -31.0$). Displays the elevated steel utility conduit pipe resting on standoff brackets, with the wall-mounted cast-iron electrical junction box (`JunctionBox_Manufacturing`) and secondary conduit splitter:*

![Perimeter Utility Conduit & Junction Box](file:///C:/Users/heckz/.gemini/antigravity/brain/c6768c4e-042b-423d-9cda-2e91a32eb976/task148_plot_perimeter_conduit.jpg)

---

### Evidence 4: Rear Mountain Rock Anchor Tie-Backs
*View along the rear boundary curb ($Z = +31.5$) backing into the mountain cliff. Displays the heavy steel tie-back plates (`AnchorPlate_*`) with central square tension nuts bolting the concrete foundation into the mountain bedrock:*

![Rear Mountain Rock Anchor Tie-Backs](file:///C:/Users/heckz/.gemini/antigravity/brain/c6768c4e-042b-423d-9cda-2e91a32eb976/task148_plot_rear_rock_anchors.jpg)

---

### Evidence 5: Elevated Wide Overview of Fully Dressed Plot
*Elevated wide perspective looking into Plot 2 from the entrance gate. Demonstrates the complete visual balance: entrance ramp in foreground, `ClaimStation` on the right, `SitePowerCabinet` on the left, expansion seams dividing the floor, `PlotSpawn` in the center, and rear anchors along the back cliff:*

![Elevated Wide Overview of Dressed Plot](file:///C:/Users/heckz/.gemini/antigravity/brain/c6768c4e-042b-423d-9cda-2e91a32eb976/task148_plot_full_dressed_overview.jpg)

---

## 5. Play-Mode Test Results

| Test Case | Verification Action | Expected Result | Measured Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| **All Plots Present** | Inspected `Workspace.Plots` in Play mode | 6 plots with `PlotSiteDetails` child | All 6 plots contain `PlotSiteDetails` (23–24 parts each) | **PASS** |
| **Spawn Direction** | Measured `LookVector` on spawn for all 6 plots | Local $Z \approx 1.0$ (facing inward toward factory) | Local $Z = 1.000$ across all 6 plots | **PASS** |
| **Claim Station Function** | ProximityPrompt claim on Plot 2 | Pad turns slate; billboard shows owner; prompt disables | Claim succeeded; owner set to `InsecureWasTaken`; prompt disabled | **PASS** |
| **Tycoon Button Spawning** | Triggered `TycoonService:SpawnNextButtons` | `Button_StarterDropper` spawns at $(-12, 2.1, 8)$ | Button spawned cleanly; no overlap with `JunctionBox` | **PASS** |
| **Machine Purchase** | Purchased `StarterDropper` with coins | `StarterDropper` spawns at $(-12, 2.0, -8)$ | Dropper spawned and produced ores; $18.8$ studs from conduit | **PASS** |
| **Plot Release Cleanup** | Called `PlotService:ReleasePlot(2)` | `PurchasedObjects` & `PurchaseButtons` cleared; `PlotSiteDetails` preserved | Machines and buttons cleared; `PlotSiteDetails` intact with 23 parts | **PASS** |
| **Collision Trap Audit** | Walked player across all details | Zero snagging, zero physics jams, smooth transit | Expansion seams and wall conduits are non-collidable; cabinet is clear | **PASS** |
| **Console Errors** | Inspected server output logs | Zero errors related to plot construction or tycoon services | Zero errors from game code | **PASS** |

### Untested Cases
- **Simultaneous 6-player claim stress test**: Tested with single live player claiming/releasing; multi-client replication was verified via RemoteEvents but not with 6 concurrent human clients.

---

## 6. Preservation of Unrelated Systems
- **Economy & Mining**: Node health, pickaxe damage, backpack capacities, ore selling prices, and drop rates remain unchanged.
- **Data Persistence**: DataStore saving, mock profile loading, and session locks were untouched.
- **Pets & Equipment**: Pet follow dynamics, damage bonuses, and equipment shop inventories remain intact.
- **Roads & Central Hub**: Wayfinding signs, central operations gantry, portals, and roads remain in their Task 1.47 states.

---

## 7. Known Limitations & Studio State
- **Known Limitations**: Visual details are static fixtures; the breaker cabinet switches and telemetry dials are decorative and do not toggle electrical power.
- **Studio State**: Roblox Studio has been safely returned to **Edit** mode (`DataModel: Edit`).
