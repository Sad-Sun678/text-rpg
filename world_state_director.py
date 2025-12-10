# world_state_director.py
"""
World State Director

This module acts as the global "story temperature" regulator for the simulation.
It aggregates signals from all subsystems and produces world-level indices that
drive pacing, tension, and emergent narrative arcs.

The controller does NOT micromanage systems.
It detects global patterns → raises/lower world-level pressures → systems respond.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class DirectorState:
    # Core world-level tension indicators
    global_stress: float = 0.0            # disasters, shortages, fear
    global_prosperity: float = 0.0        # surplus, safety, growth
    conflict_index: float = 0.0           # wars, hostility, raids
    migration_pressure: float = 0.0       # famine, jobs, safety
    faction_pressure: float = 0.0         # political instability, rivalry

    # Derived value — the "world phase" for macro storytelling
    world_phase: str = "stable"

    # Allow attaching raw signals from subsystems
    signals: Dict[str, Any] = field(default_factory=dict)


class DirectorController:
    def __init__(self):
        self.state = DirectorState()

    # --- PUBLIC API ----------------------------------------------------------

    def register_signal(self, key: str, value: float):
        """
        Subsystems call this once per tick.
        Example: economy subsystem pushes unemployment_rate, food_surplus, etc.
        """
        self.state.signals[key] = value

    def update(self, dt: float):
        """
        Called once per world tick by main.py / timesim.
        Converts subsystem signals into world indices.
        """
        s = self.state

        # --- EXTRACT SIGNALS SAFELY -----------------------------------------
        econ_shortage = s.signals.get("econ_food_shortage", 0)
        econ_surplus  = s.signals.get("econ_surplus", 0)
        crime_rate    = s.signals.get("crime_rate", 0)
        warfare       = s.signals.get("active_conflicts", 0)
        refugees      = s.signals.get("refugee_count", 0)
        faction_tension = s.signals.get("faction_tension", 0)

        # --- COMPUTE GLOBAL INDICES -----------------------------------------

        # Stress rises from shortages, disasters, conflicts
        s.global_stress = (
            econ_shortage * 0.6 +
            crime_rate    * 0.3 +
            warfare       * 1.2
        )

        # Prosperity rises from surplus, security, low stress
        s.global_prosperity = (
            econ_surplus * 1.0 -
            s.global_stress * 0.4
        )

        # Conflict index = active wars + political tension
        s.conflict_index = warfare * 1.5 + faction_tension * 0.5

        # Migration pressure = shortages + conflicts
        s.migration_pressure = econ_shortage * 0.7 + warfare * 1.0 + refugees * 0.5

        # Faction pressure = political instability
        s.faction_pressure = faction_tension + warfare * 0.2

        # --- DETERMINE WORLD PHASE (ARC) ------------------------------------

        s.world_phase = self._determine_phase(
            s.global_stress,
            s.global_prosperity,
            s.conflict_index
        )

        # Clear signals each tick
        s.signals.clear()

    # --- INTERNAL LOGIC ------------------------------------------------------

    def _determine_phase(self, stress: float, prosperity: float, conflict: float) -> str:
        """
        Converts numeric world tensions into clean phase labels.
        This is what systems can branch on.
        """

        if conflict > 80 or stress > 70:
            return "collapse"

        if stress > 40:
            return "tension"

        if prosperity > 40 and stress < 20:
            return "prosperity"

        if prosperity < 10 and stress < 20 and conflict < 20:
            return "recovery"

        return "stable"

    # --- OPTIONAL: DEBUG -----------------------------------------------------

    def debug_state(self) -> Dict[str, float]:
        """External modules can use this for logging or plotting."""
        s = self.state
        return {
            "stress": s.global_stress,
            "prosperity": s.global_prosperity,
            "conflict": s.conflict_index,
            "migration_pressure": s.migration_pressure,
            "faction_pressure": s.faction_pressure,
            "phase": s.world_phase,
        }
