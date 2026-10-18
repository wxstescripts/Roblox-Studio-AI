# Task 1.35 — Professional Equipment Forge & Robotic Egg Incubator

**Project:** *Pet Mining Empire*  
**Scope:** Environment Art Upgrade — Central Hub Functional Landmarks  
**Mode Verified:** Roblox Studio Live Play & Edit Mode  
**Place ID:** `109317675035550`  
**Status:** Completed & Traversal/Interaction-Verified  

---

## 1. Executive Summary

In Task 1.35, the crude upgrade counter and egg hatching station in *Pet Mining Empire* were completely redesigned into two distinctive, professionally modeled 3D tycoon landmarks. 

Previously, the equipment station was a basic table made of standard primitive blocks, and the egg incubator was a generic box with primitive shapes. The redesign establishes two distinct yet complementary visual identities:
1. **The Equipment Forge (`EquipmentStation` at $X = +12.0, Z = +14.0$):** An authentic, heavy industrial workstation communicating blacksmithing, equipment reinforcement, and mining machinery. It features a stepped concrete foundation, lower shelf with refined copper/bronze ingots and tool chest, an active forge hearth with glowing embers and exhaust hood, an articulated work lamp, a hazard-framed tool rack displaying pickaxes and sledgehammers, and a custom-generated 3D blacksmith anvil mesh (`rbxassetid://117815378902656`) anchored with iron clamping bands.
2. **The Robotic Egg Incubator (`EggHatchingStation` at $X = -12.0, Z = +14.0$):** A high-tech futuristic-industrial bio-incubation machine communicating pet specimen containment and high-tech hatching. It features beveled concrete footings with glowing cyan energy conduit trims, four robotic yellow clamps, a transparent glass containment cylinder, hydraulic piston rams, a specimen egg with glowing cyan core, a slanted operator terminal with live telemetry readouts (`SurfaceGui`), indicator status LEDs, dual-sided overhead signage, and a custom-generated 3D robotic incubator capsule mesh (`rbxassetid://140176288214859`).
3. **Flawless Gameplay Preservation:** Preserved exact world coordinates, interaction anchors (`TableTop` and `IncubatorConsole`), `ProximityPrompt` names (`UpgradePrompt` and `EggPrompt`), activation distances, keybinds, and server-side upgrade/hatching validation. Live Play-mode tests verified that approaching either station opens its respective UI (`EquipmentShopGui` and `EggHatchGui`) without any collision snagging or path blocking.

---

## 2. In-Game Visual Progression

````carousel
![Equipment Forge Overview from Viewing Distance](file:///C:/Users/heckz/.gemini/antigravity/brain/c6768c4e-042b-423d-9cda-2e91a32eb976/task135_equipment_forge_overview.jpg)
<!-- slide -->
![Equipment Forge Close-Up: Custom Anvil Mesh, Glowing Hearth, & Tool Rack](file:///C:/Users/heckz/.gemini/antigravity/brain/c6768c4e-042b-423d-9cda-2e91a32eb976/task135_equipment_forge_closeup.jpg)
<!-- slide -->
![Robotic Egg Incubator Overview from Viewing Distance](file:///C:/Users/heckz/.gemini/antigravity/brain/c6768c4e-042b-423d-9cda-2e91a32eb976/task135_egg_incubator_overview.jpg)
<!-- slide -->
![Robotic Egg Incubator Close-Up: Glass Cylinder, Capsule Mesh, & Terminal](file:///C:/Users/heckz/.gemini/antigravity/brain/c6768c4e-042b-423d-9cda-2e91a32eb976/task135_egg_incubator_closeup.jpg)
<!-- slide -->
![Central Hub Wide Perspective: Dual Stations Framing Plaza and Mine Portal](file:///C:/Users/heckz/.gemini/antigravity/brain/c6768c4e-042b-423d-9cda-2e91a32eb976/task135_hub_dual_stations_wide.jpg)
````

---

## 3. Detailed Architectural & Asset Specifications

### 3.1 The Equipment Forge (`Workspace.Environment.Hub.EquipmentStation`)

- **World Position:** $(12.0, 1.2, 14.0)$  
- **Orientation:** `CFrame.Angles(0, math.rad(-90), 0)` (Front faces West toward central boulevard)  
- **PrimaryPart:** `Foundation`  
- **Child Count:** 36 structured parts & fixtures  

| Component | Dimensions / Class | Material & Color | Function / Art Direction |
| :--- | :--- | :--- | :--- |
| **Foundation Pad** | $8.0 \times 0.4 \times 5.2$ studs | `Concrete`, RGB `(72, 75, 80)` | Heavy stepped footing anchoring workstation into plaza flagstones. |
| **Foundation Kickplate** | $8.4 \times 0.3 \times 5.6$ studs | `DiamondPlate`, RGB `(42, 45, 50)` | Low-profile steel skirting with corner hazard pads. |
| **Hazard Corner Pads** | $1.0 \times 0.32 \times 1.0$ studs (x4) | `DiamondPlate`, RGB `(245, 180, 25)` | High-visibility yellow safety footing markers. |
| **Workbench Legs & Feet** | $0.6 \times 2.0 \times 0.6$ studs (x4) | `Metal`, RGB `(40, 44, 52)` | Heavy steel I-beam uprights with diamond-plate bedplates. |
| **Lower Storage Shelf** | $6.4 \times 0.2 \times 3.6$ studs | `Metal`, RGB `(38, 42, 48)` | Sub-bench storage platform holding raw inventory. |
| **Tool Storage Chest** | $1.8 \times 0.8 \times 1.2$ studs | `Metal`, RGB `(50, 55, 62)` | Reinforced steel jobsite lockbox for smithing tools. |
| **Refined Ingot Stack** | $1.4 \times 0.5 \times 1.0$ studs | `Metal`, RGB `(215, 145, 65)` | Stacked refined bronze/copper bars ready for forging. |
| **TableTop (Gameplay Anchor)** | $6.8 \times 0.5 \times 3.8$ studs | `DiamondPlate`, RGB `(48, 52, 60)` | Primary heavy counter housing `UpgradePrompt` & `ShopLabel`. |
| **Counter Edge Trim** | $7.0 \times 0.6 \times 4.0$ studs | `Metal`, RGB `(32, 35, 40)` | Dark steel protective perimeter rim around tabletop. |
| **Forge Hearth Crucible** | $2.2 \times 1.2 \times 2.4$ studs | `CorrodedMetal`, RGB `(42, 44, 48)` | Firepot chamber for heating and tempering mining equipment. |
| **Glowing Embers Bed** | $1.6 \times 0.3 \times 1.8$ studs | `Neon`, RGB `(255, 110, 20)` | Active forge firebed with warm orange/yellow ember glow. |
| **Ember PointLight** | `PointLight` (Range: 12, Brightness: 2.0) | Color: RGB `(255, 120, 30)` | Casts dynamic ambient forge firelight onto tabletop. |
| **Exhaust Hood & Flue** | $2.4 \times 1.2 \times 2.6$ & $1.0 \times 2.4 \times 1.0$ | `Metal`, RGB `(38, 40, 45)` | Heavy sheet metal ventilation cowl venting forge smoke upwards. |
| **Anvil Mounting Stump** | $1.8 \times 1.0 \times 1.6$ studs | `WoodPlanks`, RGB `(65, 48, 35)` | Solid timber stump with dark steel retention clamping strap. |
| **Custom Blacksmith Anvil** | Custom Mesh (`rbxassetid://117815378902656`) | Size: $2.5 \times 1.42 \times 1.34$, `Metal` | Genuine low-poly heavy duty blacksmith anvil with horn and base. |
| **Tool Rack Backboard** | $2.2 \times 2.8 \times 0.2$ studs | `Metal`, RGB `(35, 38, 44)` | Steel tool storage wall with hazard yellow outer framing. |
| **Display Pickaxe** | $0.25 \times 2.2 \times 0.25$ + Head | `WoodPlanks` & `Metal` | Angled reinforced mining pickaxe on display. |
| **Display Sledgehammer** | $0.2 \times 1.8 \times 0.2$ + Head | `WoodPlanks` & `Metal` | Heavy forging sledge mounted beside the pickaxe. |
| **Articulated Work Lamp** | Mast, Arm, Shade & Bulb ($0.7 \times 0.2 \times 0.7$) | `Metal` & `Neon`, RGB `(255, 235, 180)` | Overhead gooseneck industrial lamp providing focused task lighting. |
| **WorkLight** | `PointLight` (Range: 18, Brightness: 2.4) | Color: RGB `(255, 235, 190)` | Warm tungsten task light illuminating anvil and work area. |
| **ShopLabel BillboardGui** | `BillboardGui` (Size: $6 \times 1.8$ studs) | Text: Cyan Title, Gold Subtitle | `"EQUIPMENT UPGRADE SHOP"` / `"Pickaxes & Backpacks"`. |
| **UpgradePrompt** | `ProximityPrompt` (MaxDist: 14.0) | Action: `"Upgrade Equipment"`, Key: `E` | Gameplay-critical prompt triggering `EquipmentController`. |

---

### 3.2 The Robotic Egg Incubator (`Workspace.Environment.Hub.EggHatchingStation`)

- **World Position:** $(-12.0, 1.2, 14.0)$  
- **Orientation:** `CFrame.Angles(0, math.rad(90), 0)` (Front faces East toward central boulevard)  
- **PrimaryPart:** `Foundation`  
- **Child Count:** 31 structured parts & fixtures  

| Component | Dimensions / Class | Material & Color | Function / Art Direction |
| :--- | :--- | :--- | :--- |
| **Foundation Pad** | $7.6 \times 0.4 \times 5.2$ studs | `Concrete`, RGB `(72, 75, 80)` | Heavy stepped foundation plinth matching the Equipment Forge. |
| **Foundation Kickplate** | $8.0 \times 0.3 \times 5.6$ studs | `DiamondPlate`, RGB `(38, 42, 48)` | Protective machinery perimeter rim. |
| **Energy Conduit Trims** | $7.0 \times 0.1 \times 0.2$ studs (x2) | `Neon`, RGB `(0, 200, 240)` | High-tech recessed cyan bio-power conduit strips along the base. |
| **Hazard Corner Pads** | $1.0 \times 0.32 \times 1.0$ studs (x4) | `DiamondPlate`, RGB `(245, 180, 25)` | Symmetrical yellow safety corner pads. |
| **Incubator Pedestal** | $3.8 \times 1.2 \times 3.4$ studs | `Metal`, RGB `(42, 46, 54)` | Elevated machinery sub-chassis supporting the incubation capsule. |
| **Mounting Collar** | $2.8 \times 0.4 \times 2.8$ studs | `DiamondPlate`, RGB `(55, 60, 70)` | Circular diamond-plate mounting ring. |
| **Robotic Clamps (x4)** | $0.5 \times 0.8 \times 0.5$ studs (radial) | `Metal`, RGB `(245, 180, 25)` | 4 radial safety clamps locking the containment chamber in place. |
| **Incubator Capsule Mesh** | Custom Mesh (`rbxassetid://140176288214859`) | Size: $2.04 \times 3.20 \times 1.95$, `Metal` | Genuine custom robotic bio-incubator pod mesh with containment fittings. |
| **Glass Containment Cylinder** | Cylinder ($2.8 \times 2.4 \times 2.4$) | `Glass`, `Transparency = 0.55` | Transparent tinted energy shield surrounding specimen egg. |
| **Specimen Egg Shell** | $1.4 \times 1.9 \times 1.4$ studs | `SmoothPlastic`, RGB `(160, 165, 175)` | Suspended quarry egg specimen inside the chamber. |
| **Egg Hazard Band** | $1.55 \times 0.35 \times 1.55$ studs | `Metal`, RGB `(245, 165, 35)` | Hazard amber stabilizer collar around egg midline. |
| **Cyan Core Energy Cell** | $0.5 \times 0.5 \times 0.5$ studs | `Neon`, RGB `(0, 220, 255)` | Internal bio-pulse glowing core inside egg. |
| **IncubationGlow** | `PointLight` (Range: 16, Brightness: 2.4) | Color: RGB `(0, 220, 255)` | Emits soft cyan illumination through the glass chamber. |
| **Gantry Posts (L/R)** | $0.5 \times 5.2 \times 0.5$ studs (x2) | `Metal`, RGB `(45, 50, 58)` | Vertical structural columns holding the overhead stabilization assembly. |
| **Top Crossbeam & Cap** | $5.6 \times 0.5 \times 0.6$ & $2.4 \times 0.6 \times 2.4$ | `DiamondPlate`, RGB `(35, 38, 44)` | Overhead crown locking assembly. |
| **Hydraulic Pistons (L/R)** | $0.3 \times 3.0 \times 0.3$ studs (x2) | `Metal`, RGB `(180, 190, 205)` | Chrome hydraulic pressure equalization cylinders. |
| **IncubatorConsole (Anchor)** | $4.2 \times 1.4 \times 1.8$ studs | `Metal`, RGB `(45, 50, 58)` | Front operator console housing `EggPrompt` and telemetry terminal. |
| **Terminal Screen** | $3.6 \times 0.1 \times 1.2$ studs (slanted $-25^\circ$) | `SmoothPlastic`, RGB `(15, 20, 28)` | Ergonomic angled terminal housing live telemetry `SurfaceGui`. |
| **Terminal SurfaceGui** | `SurfaceGui` (Top face, $600 \times 200$) | Cyan header & Amber status readout | `"BIO-INCUBATION CHAMBER • ONLINE"` / `"SPECIMEN: QUARRY EGG | CORE TEMP: 37.4°C"`. |
| **Status LEDs** | $0.2 \times 0.1 \times 0.2$ studs (x2) | `Neon` (Green RGB `(50, 255, 100)` & Cyan) | Console operational readiness indicators. |
| **Overhead SignBoard** | $4.4 \times 1.2 \times 0.3$ studs + Cyan Border | Dual `SurfaceGui` (Front & Back) | `"EGG INCUBATOR"` (Cyan) & `"[ 250 COINS ]"` (Gold). |
| **EggPrompt** | `ProximityPrompt` (MaxDist: 12.0) | Action: `"Inspect Capsules"`, Key: `E` | Gameplay-critical prompt triggering `PetController`. |

---

## 4. Live Play-Mode Verification Log

Live tests were executed in Roblox Studio Play mode (`start_stop_play`) with client and server DataModels active:

```
=== LIVE PLAY MODE VERIFICATION LOG ===
EquipmentStation exists: true (Children: 36)
  TableTop exists: true
  UpgradePrompt: Enabled = true, MaxDist = 14.0, Action = "Upgrade Equipment", Object = "Gear Station", Key = [E] / [ButtonX]
  Anvil MeshPart: rbxassetid://117815378902656 (Verified)
  Forge Embers & PointLight: Active (Color: 255, 120, 30, Range: 12)

EggHatchingStation exists: true (Children: 31)
  IncubatorConsole exists: true
  EggPrompt: Enabled = true, MaxDist = 12.0, Action = "Inspect Capsules", Object = "Quarry Egg Incubator", Key = [E] / [ButtonX]
  IncubatorCapsuleMesh MeshPart: rbxassetid://140176288214859 (Verified)
  Cyan Containment Light: Active (Color: 0, 220, 255, Range: 16)
  Terminal Telemetry: Active (SurfaceGui on slanted terminal face)

Live Interaction Tests:
  Step 1: Player moved to EquipmentStation at (9.0, 3.0, 14.0) -> Distance: 3.0 studs.
          Triggered UpgradePrompt -> EquipmentShopGui MainFrame opened successfully!
  Step 2: Player moved to EggHatchingStation at (-9.0, 3.0, 14.0) -> Distance: 3.6 studs.
          Triggered EggPrompt -> EggHatchGui EggModal opened successfully with CommonEgg rewards & hatch odds!
  Step 3: Traversal between stations along central boulevard (24 studs clearance) -> 100% collision-free.
  Step 4: Console Output Audit -> 0 runtime errors from game scripts. Clean boot and synchronization.
```

---

## 5. Script & Model Changes Summary

1. **Workspace Models:**
   - Replaced `Workspace.Environment.Hub.EquipmentStation` with the 36-part Equipment Forge model.
   - Inserted permanent `Workspace.Environment.Hub.EggHatchingStation` with the 31-part Robotic Egg Incubator model.
2. **ServerStorage Templates:**
   - Saved `ServerStorage.TycoonStorage.AnvilMesh` (`rbxassetid://117815378902656`).
   - Saved `ServerStorage.TycoonStorage.IncubatorCapsuleMesh` (`rbxassetid://140176288214859`).
3. **Services Updated:**
   - [`src/ServerScriptService/Services/EquipmentService.luau`](file:///c:/Users/heckz/Downloads/Roblox%20Studio/src/ServerScriptService/Services/EquipmentService.luau#L117-L290): Updated `buildPhysicalStation` procedural fallback to construct the upgraded Equipment Forge with anvil mount, tool rack, and glowing hearth if missing from workspace.
   - [`src/ServerScriptService/Services/PetService.luau`](file:///c:/Users/heckz/Downloads/Roblox%20Studio/src/ServerScriptService/Services/PetService.luau#L700-L865): Updated `constructEggHatchingStation` procedural fallback to construct the upgraded Robotic Egg Incubator with capsule mesh, cyan illumination, terminal screen, and gantry sign if missing from workspace.
4. **Preserved Gameplay Guarantees:**
   - Zero changes to equipment upgrade costs, tiers, stats, or network remotes.
   - Zero changes to egg hatch odds, reward tables, costs (250 Coins), or pet follow behavior.
   - Zero changes to data persistence, plots, mining nodes, or cave progression.
