# Task 1.47 — Signage Repair & Plot Onboarding Polish

## Executive Summary
In **Task 1.47**, the confirmed signage defects, readability bottlenecks, backwards spawn orientations, and onboarding accessibility issues identified during the Task 1.46 audit were fully repaired and verified in live Roblox Studio Play mode.

### Key Accomplishments
1. **Four Hub Wayfinding Signs Rebuilt with Twin Supports**:
   - Eliminated the severe post bisection bug across all 4 hub wayfinding signs (`Sign_MineQuarry`, `Sign_Headframe`, `Sign_EastSector`, `Sign_WestSector`). The single $0.50$-stud center post was replaced with twin industrial side posts (`SignPost_L`, `SignPost_R`) and concrete footings (`SignBase_L`, `SignBase_R`) flanking the board, leaving the entire $6.0$-stud display surface completely open.
   - Reconfigured SurfaceGuis to a pristine $1280 \times 360$ canvas size ($3.55:1$ aspect ratio), matching the physical board dimensions ($6.4 \times 1.8$ studs).
   - Resolved arrow and directional contradictions by establishing distinct, purposeful typography on both faces:
     - **Outward Face (`NormalId.Back`)**: Outbound destination messaging with appropriate directional arrows (`▲ STAGE 1 QUARRY`, `▲ HEADFRAME DERRICK`, `▶ SECTOR EAST`, `◀ SECTOR WEST`).
     - **Inward Face (`NormalId.Front`)**: Unambiguous return guidance to the hub (`▲ CENTRAL OPERATIONS` / `OPERATIONS PLAZA & TYCOON SECTORS`).
2. **Two Additional Sign Defects Resolved**:
   - **Stage 3 Progression Gate**: Repositioned `GateAlertBeacon` from $Y = -6.30$ to $Y = -5.60$ with an industrial mounting bracket (`BeaconMountBracket` at $Y = -6.30$). The warning light now rests squarely on top of the signboard frame instead of hanging down, making the word `RESTRICTED` 100% visible.
   - **Mine Entrance Portal Branding**: Removed the hidden, occluded `CorpBrandingGui` from `PortalOverheadBeam` ($Z = -14.0$). Installed a prominent `PortalCompanyBanner` on the upper tower crossbeam `TowerCrossbeam_40` ($Y = 26.6, Z = -13.25$) displaying `★ PET MINING CORP. ★` in bold gold lettering, creating a clean vertical hierarchy above the lower sector sign.
   - **Branding Standardization**: Unified lore branding on `HeadframeDerrickTower.TowerNameplate` from `PROFIT MINING CORP.` to `PET MINING CORP.`.
3. **Plot Spawn Direction Corrected (180° Inward Flip)**:
   - Updated `PlotSpawn.CFrame` in [`PlotService.luau`](file:///c:/Users/heckz/Downloads/Roblox%20Studio/src/ServerScriptService/Services/PlotService.luau) and the active Studio DataModel with a $180^\circ$ yaw rotation (`* CFrame.Angles(0, math.pi, 0)`).
   - Verified across all six plots (`Plot_1` through `Plot_6`) in live Play mode: player characters spawning or teleporting to their base now face directly **inward** toward their tycoon machines, conveyor belts, and build envelope (`LookVector = (0, 0, 1)` local), rather than facing backwards toward the road.
4. **Claim Station Moved to Forward Entrance Area**:
   - Relocated `ClaimStation` from the far back wall ($Z = +24.0$ studs, $56$ studs from the entrance) to the front entrance-side envelope:
     - `ClaimPad`: local $X = -9.0, Z = -22.5$, size $6 \times 0.3 \times 6$ studs.
     - `SignPost` & `SignBoard`: local $X = -9.0, Z = -26.0$, directly facing incoming players stepping off the entrance ramp.
   - Maintains generous clearances: $>3.0$ studs from `PlotSpawn`, $>3.5$ studs from the entrance ramp, and $>9.5$ studs from the starter dropper envelope.
   - Claim proximity prompts, billboard ownership tracking, and drop-off pad activations were tested and verified functional.

---

## 1. Inventory of Changes & Exact DataModel Paths

### A. Four Hub Wayfinding Signs
Path: `Workspace.Environment.Hub.WayfindingSigns.*`

| Sign Model | Component Changed | Before State | After State | Architectural Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **`Sign_MineQuarry`** | Supports & Footings | 1 center post `(0.5, 7.2, 0.5)` slicing through center of board | Twin side posts `SignPost_L`, `SignPost_R` at $X = \pm 3.0$; twin bases `SignBase_L`, `SignBase_R` | Completely removes post bisection; text is 100% visible from both sides. |
| | Canvas & Scaling | $800 \times 600$ ($1.33:1$) squashed onto $3.55:1$ board | $1280 \times 360$ ($3.55:1$) with GothamBold title and GothamMedium sub | Pixel-perfect aspect ratio matching with zero typography distortion. |
| | Outward Face (`Back`) | `▲ STAGE 1 QUARRY` | `▲ STAGE 1 QUARRY` / `DESCENT SHAFT & ORE EXTRACTION` | Clear destination title and facility description for outbound players. |
| | Inward Face (`Front`) | Identical `▲ STAGE 1 QUARRY` (contradictory) | `▲ CENTRAL OPERATIONS` / `OPERATIONS PLAZA & TYCOON SECTORS` | Directs returning miners back into the hub plaza and operations center. |
| **`Sign_Headframe`** | Supports & Footings | 1 center post slicing through center of board | Twin side posts and bases at $X = \pm 3.0$ | Eliminates text obstruction; structural framing aesthetic. |
| | Canvas & Scaling | $800 \times 600$ squashed | $1280 \times 360$ ($3.55:1$) | Perfect typography rendering. |
| | Outward Face (`Back`) | `▼ HEADFRAME DERRICK` (downward arrow) | `▲ HEADFRAME DERRICK` / `CENTRAL HOIST & EQUIPMENT DEPOT` | Standardizes forward navigation arrow `▲` for outbound heading. |
| | Inward Face (`Front`) | Identical text facing headframe approach | `▲ CENTRAL OPERATIONS` / `OPERATIONS PLAZA & TYCOON SECTORS` | Directs northbound returning players toward central operations. |
| **`Sign_EastSector`** | Supports & Footings | 1 center post slicing through center of board | Twin side posts and bases at $X = \pm 3.0$ | Eliminates text obstruction. |
| | Canvas & Scaling | $800 \times 600$ squashed | $1280 \times 360$ ($3.55:1$) | Standardized canvas size. |
| | Outward Face (`Back`) | `▶ SECTOR EAST` | `▶ SECTOR EAST` / `TYCOON PLOTS 1, 2, 3` | Clear directional arrow towards plots 1, 2, 3. |
| | Inward Face (`Front`) | Identical `▶ SECTOR EAST` facing returning miners | `▲ CENTRAL OPERATIONS` / `OPERATIONS PLAZA & CENTRAL HUB` | Clear return guidance into the hub plaza. |
| **`Sign_WestSector`** | Supports & Footings | 1 center post slicing through center of board | Twin side posts and bases at $X = \pm 3.0$ | Eliminates text obstruction. |
| | Canvas & Scaling | $800 \times 600$ squashed | $1280 \times 360$ ($3.55:1$) | Standardized canvas size. |
| | Outward Face (`Back`) | `◀ SECTOR WEST` | `◀ SECTOR WEST` / `TYCOON PLOTS 4, 5, 6` | Clear directional arrow towards plots 4, 5, 6. |
| | Inward Face (`Front`) | Identical `◀ SECTOR WEST` facing returning miners | `▲ CENTRAL OPERATIONS` / `OPERATIONS PLAZA & CENTRAL HUB` | Clear return guidance into the hub plaza. |

---

### B. Additional Sign Defects & Corporate Branding

| Instance Path | Defect Identified | Action Taken | Verification Result |
| :--- | :--- | :--- | :--- |
| `Workspace.Caves.Stage_2`<br>`.ProgressionGate_Stage3`<br>`.GateAlertBeacon` | Centered at $Y = -6.30$, hanging down over `GateSign` ($Y = -7.50$, top edge $Y = -6.40$), obscuring `RESTRICTED`. | Repositioned beacon up to $Y = -5.60$; added `BeaconMountBracket` at $Y = -6.30$ touching top of sign frame. | Sign text `LEVEL 3 SHAFT — RESTRICTED: ADVANCED CLEARANCE REQUIRED` is 100% visible and unobstructed. |
| `Workspace.Environment.Hub`<br>`.MineEntrancePortal`<br>`.PortalOverheadBeam`<br>`.CorpBrandingGui` | Positioned at $Z = -14.00, Y = 16.20$, directly behind `PortalSignBoard` ($Z = -11.95, Y = 16.20$). Completely hidden. | Removed occluded GUI from beam. Created `PortalCompanyBanner` Part $(11.2, 1.1, 0.2)$ on `TowerCrossbeam_40` at $Y = 26.60, Z = -13.25$ with gold `★ PET MINING CORP. ★`. | Branding is prominently visible from the hub approach, elevated above the lower destination sign without stacking collision. |
| `Workspace.Environment.Hub`<br>`.HeadframeDerrickTower`<br>`.TowerNameplate` | Text read `PROFIT MINING CORP. — SHAFT 1`, inconsistent with central hub lore. | Updated TextLabel string to `PET MINING CORP. — SHAFT 1`. | Unifies industrial company identity across all surface structures. |

---

### C. Plot Spawn & Claim Station Relocation
Path: `Workspace.Plots.Plot_1` through `Plot_6` and `PlotService.luau`

| Parameter / Object | Original Audit Value | Updated Value | Impact on Gameplay & Ergonomics |
| :--- | :---: | :---: | :--- |
| **`PlotSpawn` CFrame Yaw** | $0^\circ$ relative to `cframe`<br>(`LookVector` toward origin) | $+180^\circ$ relative to `cframe`<br>(`LookVector` toward factory) | Players respawning or teleporting to base spawn facing into their tycoon machinery instead of out toward the road. |
| **`ClaimPad` Position (Local)** | $(0.0, 2.15, +24.0)$ studs | $(-9.0, 2.15, -22.5)$ studs | Relocates claim interaction from the rear cliff wall ($56$ studs away) to immediately flanking the front entrance ramp ($6$ studs away). |
| **`ClaimPad` Size** | $(8.0, 0.4, 8.0)$ studs | $(6.0, 0.3, 6.0)$ studs | Sleek footprint providing $>3.0$ studs clearance to `PlotSpawn` and $>9.5$ studs clearance to `StarterDropper`. |
| **`SignPost` & `SignBoard` (Local)** | $(0.0, Y, +19.0)$ studs | $(-9.0, Y, -26.0)$ studs | Positioned at the front edge of the pad facing inbound players arriving from the road. |
| **ProximityPrompt Max Distance** | $14$ studs | $14$ studs (Preserved) | Players can activate the claim prompt immediately upon stepping off the entrance ramp onto the plot apron. |

---

## 2. Code Changes

### [`PlotService.luau`](file:///c:/Users/heckz/Downloads/Roblox%20Studio/src/ServerScriptService/Services/PlotService.luau#L418-L515)
The authoritative plot generator in `PlotService.luau` was updated to incorporate the $180^\circ$ spawn flip and the forward claim station layout:

```luau
	-- 3. Dedicated Plot SpawnLocation (Disabled globally; used explicitly for owner respawns)
	local spawnOffset = baseSettings.SpawnOffset
	local spawnLoc = Instance.new("SpawnLocation")
	spawnLoc.Name = "PlotSpawn"
	spawnLoc.Size = Vector3.new(6, 0.2, 6)
	-- Rotated 180 degrees so player spawns facing inward toward factory/build area (+Z local)
	spawnLoc.CFrame = cframe * CFrame.new(spawnOffset.X, baseSettings.PlotSize.Y / 2 + 0.1, spawnOffset.Z) * CFrame.Angles(0, math.pi, 0)
	spawnLoc.Anchored = true
	spawnLoc.CanCollide = false
	spawnLoc.Enabled = true
	spawnLoc.Neutral = false
	spawnLoc.Material = Enum.Material.SmoothPlastic
	spawnLoc.Color = Color3.fromRGB(100, 105, 115)
	spawnLoc.Parent = model

	-- 4. Containers for machines, drops, and purchase buttons
	local purchasedObjects = Instance.new("Folder")
	purchasedObjects.Name = "PurchasedObjects"
	purchasedObjects.Parent = model

	local activeDrops = Instance.new("Folder")
	activeDrops.Name = "ActiveDrops"
	activeDrops.Parent = model

	local purchaseButtons = Instance.new("Folder")
	purchaseButtons.Name = "PurchaseButtons"
	purchaseButtons.Parent = model

	-- 5. Physical Claim Station (Stand with interactive ProximityPrompt at entrance area)
	local claimStation = Instance.new("Model")
	claimStation.Name = "ClaimStation"

	local padCFrame = cframe * CFrame.new(-9.0, baseSettings.PlotSize.Y / 2 + 0.15, -22.5)

	local claimPad = Instance.new("Part")
	claimPad.Name = "ClaimPad"
	claimPad.Size = Vector3.new(6, 0.3, 6)
	claimPad.CFrame = padCFrame
	claimPad.Anchored = true
	claimPad.CanCollide = true
	claimPad.Material = Enum.Material.Neon
	claimPad.Color = Color3.fromRGB(0, 200, 150)
	claimPad.TopSurface = Enum.SurfaceType.Smooth
	claimPad.BottomSurface = Enum.SurfaceType.Smooth
	claimPad.Parent = claimStation

	local prompt = Instance.new("ProximityPrompt")
	prompt.Name = "ClaimPrompt"
	prompt.ActionText = "Claim Base"
	prompt.ObjectText = string.format("Plot #%d", index)
	prompt.HoldDuration = 0
	prompt.MaxActivationDistance = 14
	prompt.RequiresLineOfSight = false
	prompt.ClickablePrompt = true
	prompt.KeyboardKeyCode = Enum.KeyCode.E
	prompt.GamepadKeyCode = Enum.KeyCode.ButtonX
	prompt.Parent = claimPad

	-- Sign Board Post (Positioned at Z = -26.0, directly facing approaching players from entrance)
	local signPost = Instance.new("Part")
	signPost.Name = "SignPost"
	signPost.Size = Vector3.new(0.5, 6, 0.5)
	signPost.CFrame = cframe * CFrame.new(-9.0, baseSettings.PlotSize.Y / 2 + 3.0, -26.0)
	signPost.Anchored = true
	signPost.CanCollide = false
	signPost.Material = Enum.Material.Metal
	signPost.Color = Color3.fromRGB(50, 50, 50)
	signPost.TopSurface = Enum.SurfaceType.Smooth
	signPost.BottomSurface = Enum.SurfaceType.Smooth
	signPost.Parent = claimStation

	local signBoard = Instance.new("Part")
	signBoard.Name = "SignBoard"
	signBoard.Size = Vector3.new(6, 2.6, 0.4)
	signBoard.CFrame = cframe * CFrame.new(-9.0, baseSettings.PlotSize.Y / 2 + 5.5, -26.0)
	signBoard.Anchored = true
	signBoard.CanCollide = false
	signBoard.Material = Enum.Material.SmoothPlastic
	signBoard.Color = Color3.fromRGB(30, 30, 35)
	signBoard.TopSurface = Enum.SurfaceType.Smooth
	signBoard.BottomSurface = Enum.SurfaceType.Smooth
	signBoard.Parent = claimStation

	local billboard = Instance.new("BillboardGui")
	billboard.Name = "OwnershipBillboard"
	billboard.Size = UDim2.new(6, 0, 2.6, 0)
	billboard.StudsOffset = Vector3.new(0, 0, 0)
	billboard.AlwaysOnTop = false
	billboard.MaxDistance = 120
	billboard.Adornee = signBoard
	billboard.Parent = signBoard
```

The script was updated on disk and synchronized into `game.ServerScriptService.Source.Services.PlotService` via Studio tooling, guaranteeing identical behavior across development and live generation.

---

## 3. Photographic Evidence & Visual Verifications

### Evidence 1: Hub Wayfinding Sign Outward Face (Twin Posts, No Bisection)
*The repaired `Sign_MineQuarry` outward face. Twin industrial posts frame the board on the left and right edges with zero text obstruction. The sign displays `▲ STAGE 1 QUARRY` with clean Gotham bold typography on a calibrated $1280 \times 360$ canvas:*

![Hub Wayfinding Sign Outward Face](file:///C:/Users/heckz/.gemini/antigravity/brain/c6768c4e-042b-423d-9cda-2e91a32eb976/task147_hub_sign_outward.jpg)

---

### Evidence 2: Hub Wayfinding Sign Inward Face (Return to Hub Guidance)
*The reverse face of `Sign_MineQuarry` viewed from the quarry approach heading south. The sign displays `▲ CENTRAL OPERATIONS` / `OPERATIONS PLAZA & TYCOON SECTORS`, directing returning miners toward the hub plaza and spawn ahead:*

![Hub Wayfinding Sign Inward Face](file:///C:/Users/heckz/.gemini/antigravity/brain/c6768c4e-042b-423d-9cda-2e91a32eb976/task147_hub_sign_inward.jpg)

---

### Evidence 3: Stage 3 Progression Gate Warning Light Unobstructed
*View of `ProgressionGate_Stage3.GateSign`. `GateAlertBeacon` is now elevated on a mounting bracket above the signboard frame. The warning light sits atop the sign, leaving the text `LEVEL 3 SHAFT — RESTRICTED: ADVANCED CLEARANCE REQUIRED` 100% visible:*

![Stage 3 Gate Sign Unobstructed](file:///C:/Users/heckz/.gemini/antigravity/brain/c6768c4e-042b-423d-9cda-2e91a32eb976/task147_stage3_gate_sign.jpg)

---

### Evidence 4: Elevated Mine Portal Corporate Branding
*View looking north toward the Mine Entrance Portal from the hub plaza. `PortalCompanyBanner` is mounted high on `TowerCrossbeam_40` ($Y = 26.6$), displaying `★ PET MINING CORP. ★` clearly above the portal lintel without conflicting with `PortalSignBoard`:*

![Mine Portal Corporate Branding](file:///C:/Users/heckz/.gemini/antigravity/brain/c6768c4e-042b-423d-9cda-2e91a32eb976/task147_mine_portal_branding.jpg)

---

### Evidence 5: Plot Entrance with Forward Claim Station Kiosk
*Framed view through the `LOT #2` entrance pillars. The entrance ramp leads directly onto the plot where the relocated `ClaimStation` pad and status billboard sit immediately on the left ($X = -9.0, Z = -22.5$), replacing the $56$-stud walk to the back wall:*

![Plot Entrance with Forward Claim Station](file:///C:/Users/heckz/.gemini/antigravity/brain/c6768c4e-042b-423d-9cda-2e91a32eb976/task147_plot_entrance_claim.jpg)

---

### Evidence 6: Inward-Facing Player Spawn Orientation
*Over-the-shoulder view of the player character standing on `PlotSpawn` immediately upon spawning on Plot 2. The character faces directly inward (`LookVector = (0, 0, 1)` local) toward the factory build space, pet, and drop-off pad:*

![Inward-Facing Player Spawn Orientation](file:///C:/Users/heckz/.gemini/antigravity/brain/c6768c4e-042b-423d-9cda-2e91a32eb976/task147_spawn_facing_inward.jpg)

---

## 4. Live Play-Mode Verification Matrix

All tests were executed in active Roblox Studio Play mode:

| Test Item | Verification Method | Expected Result | Measured Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Wayfinding Posts** | Inspected geometry of all 4 wayfinding models | Twin posts `SignPost_L/R` at $X = \pm 3.0$; 0 parts intersecting board center | Center unobstructed; twin posts present on all 4 models | **PASS** |
| **Wayfinding Typography** | Audited SurfaceGui canvas and labels | $1280 \times 360$ canvas; distinct inward vs outward text | Outward: destination; Inward: `▲ CENTRAL OPERATIONS` | **PASS** |
| **Stage 3 Gate Beacon** | Measured `GateAlertBeacon.Position.Y` relative to `GateSign` | Beacon bottom $\ge$ sign top ($Y \ge -6.40$) | Beacon center $Y = -5.60$, bracket $Y = -6.30$; text unobstructed | **PASS** |
| **Portal Branding** | Checked visibility of `PortalCompanyBanner` from plaza | Elevated at $Y = 26.6$, visible from road | Clearly visible between gantry legs; no sign overlap | **PASS** |
| **Plot Spawn Inward Yaw** | Measured `HumanoidRootPart.CFrame.LookVector` on spawn | Local $Z \approx 1.0$ (facing factory) | `LookVector` local $= (0.00, 0.00, 1.00)$ on all 6 plots | **PASS** |
| **Claim Station Proximity** | Measured local pad position | Local $X \approx -9.0, Z \approx -22.5$ | `ClaimPad` at $(-9.0, 2.15, -22.5)$ across all 6 plots | **PASS** |
| **Claim Interaction** | Called `PlotService:ClaimPlot(player, 2)` | Pad turns slate gray; billboard shows owner; prompt disables | Pad slate `(0.24, 0.27, 0.31)`; Owner: `InsecureWasTaken`; prompt disabled | **PASS** |
| **Drop-Off Activation** | Checked `DropOffPad` color on claim | Inactive gray turns to active gold | Pad color changed to `Color3.fromRGB(255, 215, 0)` | **PASS** |
| **Plot Release & Reset** | Called `PlotService:ReleasePlot(2)` | Pad returns to neon green; billboard resets to available | Pad neon green `(0, 200, 150)`; text: `[ AVAILABLE ]`; prompt enabled | **PASS** |

---

## 5. Preservation of Unrelated Systems
- **Economy & Progression**: Pickaxe stats, backpack storage, coin balances, rebirth counters, and cave progression requirements were 100% untouched.
- **Mining Mechanics**: Ore health, respawn timers, hit detection, particle bursts, and mining assist pet behaviors continue to operate normally.
- **Tycoon Logic**: Machine spawn offsets, purchase button placement coordinates, conveyor speeds, and auto-sell collector mechanics remain completely intact.
- **World Geometry**: Perimeter mountain ridges, valley cliffs, radial asphalt roads, and central plaza architecture were preserved.

---

## 6. Studio State
- Roblox Studio has been returned to **Edit** mode (`DataModel: Edit`).
- No further background tasks or sessions remain active.
