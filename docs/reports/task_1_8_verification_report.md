# Task 1.8 Verification & Implementation Report: Tycoon Base Building & Machine Upgrades

## 1. Executive Summary

Task 1.8 — **Tycoon Base Building & Machine Upgrades** has been implemented, synchronized into Roblox Studio, and verified through an 11-test automated assertion suite in Edit mode followed by a live in-Studio playtest.

Players can now spend Coins earned from mining and selling ores to purchase configured base upgrades on their own claimed plot. When an upgrade is purchased:
1. The server validates active session locks, plot ownership, upgrade existence, prerequisites, reach distance, and affordability.
2. Coins are atomically deducted via `DataService:MutateData`, and the upgrade is recorded in `PlayerData.Base.PurchasedUpgrades`.
3. The machine model is cloned from `ServerStorage.TycoonStorage.Machines` and spawned onto the player's plot at configured plot-relative coordinates.
4. The purchased button is destroyed, and the next unlocked tier in the sequence appears dynamically.
5. All updates replicate cleanly to the client HUD (`CoinsValueLabel`), and plot release/rejoin cycles properly restore owned machines.

---

## 2. Architecture & File Modifications

### 2.1 Configuration: `ReplicatedStorage.Source.Configs.BaseConfig`
- Added the `UpgradeDefinition` Luau type:
  ```luau
  export type UpgradeDefinition = {
      Id: string,
      DisplayName: string,
      Cost: number,
      PrerequisiteId: string?,
      ButtonOffset: Vector3,
      ModelOffset: Vector3,
      Category: string,
      Description: string,
  }
  ```
- Implemented the 4-tier foundational upgrade chain:
  1. **`StarterDropper`** (15 Coins, prereq: `nil`, Button: `(-12, 2.1, 8)`, Model: `(-12, 2.0, -8)`)
  2. **`ConveyorLine1`** (35 Coins, prereq: `StarterDropper`, Button: `(-6, 2.1, 8)`, Model: `(-12, 2.0, 0)`)
  3. **`CopperDropper`** (80 Coins, prereq: `ConveyorLine1`, Button: `(0, 2.1, 8)`, Model: `(-12, 2.0, 8)`)
  4. **`BaseLighting`** (150 Coins, prereq: `CopperDropper`, Button: `(6, 2.1, 8)`, Model: `(0, 2.0, 0)`)
- Added query helper methods: `BaseConfig.GetUpgrade(id)`, `BaseConfig.GetAllUpgrades()`, and `BaseConfig.GetChainOrder()`.

### 2.2 Networking: `ReplicatedStorage.Source.Network`
- Registered `RequestPurchaseUpgrade` in `RemoteFunctionsList`:
  - Client -> Server: `(upgradeId: string) -> { Success: boolean, Message: string, UpgradeId: string?, Cost: number? }`
- Registered `UpgradePurchased` in `RemoteEventsList`:
  - Server -> Client: `(plotIndex: number, upgradeId: string)`

### 2.3 Plots & Tycoon Decoupling: `ServerScriptService.Source.Services.PlotService`
- Added `PurchaseButtons: Folder` to each `PlotRecord` inside `createPlotModel`.
- Added decoupled lifecycle hook slots:
  - `PlotService.OnPlotClaimed: ((player: Player, plot: PlotRecord) -> ())?`
  - `PlotService.OnPlotReleased: ((plotIndex: number, plot: PlotRecord) -> ())?`
- Updated `PlotService:ReleasePlot` to clear `PurchasedObjects`, `ActiveDrops`, and `PurchaseButtons`, invoke `OnPlotReleased`, and defensively clean any dangling entries in `playerToPlot`.
- Added `PlotService:ReleasePlayer(userId: number)`.

### 2.4 Tycoon Service: `ServerScriptService.Source.Services.TycoonService`
- **Asset Templates (`EnsureTemplates`)**: Procedurally generates anchored machine models in `ServerStorage.TycoonStorage.Machines` if not present:
  - `StarterDropper`: Base plate, 4 support pillars, hopper, and neon emitter spout with billboard.
  - `ConveyorLine1`: Metal chassis, diamond plate belt, and side guide rails.
  - `CopperDropper`: Corroded metal hopper and orange neon emitter spout.
  - `BaseLighting`: 4 perimeter lamp posts with bright PointLights illuminating the platform edge.
- **Button Construction (`createPurchaseButton`)**: Creates a pedestal with a neon pad, overhead `BillboardGui` (displaying title and cost in gold), a cross-platform `ProximityPrompt` (`E` / `ButtonX`), and a `Touched` listener with debounce for classic tycoon step-on purchasing.
- **Dynamic Progression (`RefreshPlotButtons`)**: Inspects `profile.Data.Base.PurchasedUpgrades`, iterates through `BaseConfig.GetChainOrder()`, and spawns only the next unpurchased tier whose prerequisite is satisfied.
- **Authoritative Validation (`PurchaseUpgrade`)**:
  1. Transaction mutex (`isPurchasing[userId]`) preventing race conditions.
  2. Anti-spam debounce (0.3s cooldown).
  3. Upgrade definition existence.
  4. Session lock and profile validation via `DataService`.
  5. Plot ownership validation via `PlotService:GetPlayerPlot`.
  6. Duplicate purchase prevention (`ALREADY_PURCHASED`).
  7. Prerequisite satisfaction (`PREREQUISITE_NOT_MET`).
  8. Affordability check (`INSUFFICIENT_FUNDS`).
  9. Reach validation ($\le 25$ studs between character and purchase button).
  10. In-memory atomic mutation via `DataService:MutateData`.
  11. Machine instantiation in `plot.PurchasedObjects` and button advancement.
  12. Client notification and currency replication.

### 2.5 Bootstrapper: `ServerScriptService.Source.ServerLoader`
- Registered Step 4 in bootstrapper dependency chain:
  ```luau
  -- 4. Initialize TycoonService (Tycoon Base Building & Upgrades)
  local TycoonService = require(servicesFolder:WaitForChild("TycoonService"))
  TycoonService:Init()
  ```

---

## 3. Verification Suite Part A: Edit-Mode Automated Assertions

Executed in Studio Edit mode via Luau test harness covering all functional boundaries:

| Test ID | Test Name | Assertion | Result | Detail |
| :--- | :--- | :--- | :---: | :--- |
| **T1** | Button Positioning & Prompts | Button positioned at `(12.0, 3.1, -168.0)`, prompt `E` active, cost text `$15 Coins` | **PASS** | Validated pad, prompt properties, and billboard label |
| **T2** | Affordable Purchase Execution | Deduct 15 Coins (100 $\rightarrow$ 85), update `PurchasedUpgrades['StarterDropper'] = true` | **PASS** | Authoritative deduction and profile persistence |
| **T3** | Machine Spawning & CFrame | `StarterDropper` spawned into `PurchasedObjects` with `PrimaryPart` at `(12.0, 3.0, -152.0)` | **PASS** | CFrame matched `plot.PlotBase.CFrame * ModelOffset` |
| **T4** | Dynamic Button Refresh | `Button_StarterDropper` removed, `Button_ConveyorLine1` spawned with cost `$35 Coins` | **PASS** | Correct sequence advancement |
| **T5** | Unaffordable Purchase Rejection | Attempt to buy `ConveyorLine1` (35) with 10 Coins rejected with `INSUFFICIENT_FUNDS` | **PASS** | 0 Coins deducted, balance remains 10, machine not spawned |
| **T6** | Prerequisite Enforcement | Attempt to buy `CopperDropper` without `ConveyorLine1` rejected with `PREREQUISITE_NOT_MET` | **PASS** | Skipping tiers blocked; balance preserved |
| **T7** | Duplicate Purchase Prevention | Re-purchasing `StarterDropper` rejected with `ALREADY_PURCHASED` | **PASS** | Idempotency confirmed |
| **T8** | Unowned Plot Protection | Player with no claimed plot rejected with `NO_PLOT_OWNED` | **PASS** | Unclaimed player purchases rejected |
| **T9** | Full Chain Progression | Progression through all 4 upgrades exhausted buttons cleanly | **PASS** | 4 machines spawned, 0 buttons remaining, final balance 735 Coins |
| **T10** | Plot Release Cleanup | `ReleasePlot` clears `PurchasedObjects` and `PurchaseButtons`, resets owner to 0 | **PASS** | Zero orphaned instances left on plot |
| **T11** | Re-Claim Session Restoration | Claiming plot with saved upgrades respawns all 4 machines and displays 0 buttons | **PASS** | Offline/saved progress fully restored |

---

## 4. Verification Suite Part B: Live Studio Playtest

Executed in live Studio play session using `start_stop_play`:

```mermaid
sequenceDiagram
    autonumber
    actor Player as Local Player (Client)
    participant Plot as Plot 1
    participant Tycoon as TycoonService (Server)
    participant Data as DataService (Server)
    participant HUD as Client MainHUD

    Player->>Plot: RequestClaimPlot(1)
    Plot-->>Player: Plot #1 Claimed
    Tycoon->>Plot: Spawn Button_StarterDropper ($15)
    
    Note over Player: Mines Coal Lump (+72 Coins) & Sells at Drop-Off Pad
    Data-->>HUD: CurrencyUpdated: 73 Coins
    
    Player->>Plot: Steps on StarterDropper Pad
    Plot->>Tycoon: Pad.Touched Trigger
    Tycoon->>Data: MutateData: -15 Coins (Balance: 58)
    Tycoon->>Plot: Spawn StarterDropper Machine
    Tycoon->>Plot: Destroy Button_StarterDropper, Spawn Button_ConveyorLine1 ($35)
    Tycoon-->>HUD: CurrencyUpdated: 58 Coins
    
    Player->>Tycoon: RequestPurchaseUpgrade("ConveyorLine1")
    Tycoon->>Data: MutateData: -35 Coins (Balance: 23)
    Tycoon->>Plot: Spawn ConveyorLine1 Machine
    Tycoon->>Plot: Destroy Button_ConveyorLine1, Spawn Button_CopperDropper ($80)
    Tycoon-->>HUD: CurrencyUpdated: 23 Coins
    
    Player->>Tycoon: RequestPurchaseUpgrade("CopperDropper") [Player has 23 Coins]
    Tycoon-->>Player: INSUFFICIENT_FUNDS (Needs 57 more Coins)
    Note over Player,HUD: 0 Coins deducted; Warning notification displayed
```

### Live Log Verification Highlights:
- `[TycoonService] InsecureWasTaken purchased Starter Ore Dropper for 15 Coins. Remaining balance: 58 Coins`
- `[MiningController] Currencies updated: 58 Coins, 0 Gems (Source: UpgradePurchase)`
- `[Notification - Success] Purchased Starter Ore Dropper for 15 Coins!`
- `[TycoonService] InsecureWasTaken purchased Basic Conveyor Belt for 35 Coins. Remaining balance: 23 Coins`
- `[MiningController] Currencies updated: 23 Coins, 0 Gems (Source: UpgradePurchase)`
- `[Notification - Success] Purchased Basic Conveyor Belt for 35 Coins!`
- `[Notification - Warning] You need 57 more Coins for Copper Ore Dropper!`

---

## 5. Scope & Boundary Compliance

- **No premature feature expansion**: No pets, hatching, eggs, quests, rebirths, additional cave stages, second floors, or extraneous machine catalogs were implemented.
- **Architectural continuity**: Reused existing `DataService`, `PlotService`, `MiningService`, `OreConfig`, `BaseConfig`, `Network`, and `UIController`.
- **Clean state**: All temporary test profiles and mock structures were cleared; Studio cleanly returned to Edit mode.
