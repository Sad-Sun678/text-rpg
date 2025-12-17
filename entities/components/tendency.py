# entities/components/tendency.py

from ..component import Component

'''

Separate tendency and personality through : TENDENCIES → DECISIONS → BEHAVIOR OVER TIME → PERSONALITY
Tendency Range: -1.0 → +1.0

Tendency Axes Overview (−1.0 to +1.0)

Each tendency is a **decision bias**, not a fixed behavior or personality trait.
Values range from **−1.0 (strong aversion)** to **+1.0 (strong preference)**.

Tendencies **tilt action scoring**, they never force actions.

# risk — Danger Tolerance

Willingness to accept physical or strategic danger.

`-0.7` → avoids danger unless desperate
`0.0` → reacts based on situation
`+0.7` → accepts danger as normal

Example:
`risk = +0.6` → hunts in storms, takes risky routes if payoff is high.

# aggression — Force Threshold

Likelihood of escalating conflict through force or coercion.

`-0.6` → avoids confrontation
`0.0` → situational escalation
`+0.7` → force is a valid first option

Example:
`aggression = +0.7` → responds to threats with intimidation or violence.

# social — Self vs Group Orientation

Bias toward personal benefit vs collective welfare.

`-0.5` → cooperates conditionally, prioritizes self
`0.0` → flexible, context-driven
`+0.6` → prioritizes group survival

Example:
`social = -0.5` → helps others when cost is low, abandons failing groups.

# authority — Rule & Hierarchy Acceptance

Willingness to obey and enforce rules or leadership.

`-0.6` → distrusts authority, breaks norms
`0.0` → pragmatic obedience
`+0.6` → rules are necessary for survival

Example:
`authority = +0.6` → enforces laws strictly to prevent chaos.

# patience — Time Horizon

Preference for short-term gain vs long-term planning.

`-0.5` → impulsive, reacts immediately
`0.0` → balances now vs later
`+0.6` → plans, stores, endures hardship

Example:
`patience = +0.3` → stockpiles supplies but won’t wait forever.

# novelty — Openness to Change

Willingness to explore, experiment, or deviate from routine.

 `-0.6` → tradition-bound, avoids change
 `0.0` → neutral, situational
 `+0.6` → explores and experiments often

Example:
`novelty = +0.1` → tolerates change only when necessary.

Important Notes

`0.0` means no bias, not “average behavior”.
Tendencies interact; always interpret them together, not in isolation.
Culture and environment modulate expression, not the base value.
Tendencies bias decisions like:
  
  score += tendency * action_property
  

Tendencies describe resistance and attraction under pressure — not identity.

'''

class TendencyComponent(Component):
    def __init__(self, tendencies=None):
        super().__init__("tendency")
        self.tendencies = tendencies or {
            # Risk Sensitivity (Avoidance ↔ Seeking), How much danger am I willing to tolerate?
            "risk": 0.5,

            # Aggression Threshold (Passive ↔ Confrontational), When do I use force or coercion?
            "aggression": 0.5,

            # Social Orientation (Self ↔ Group), Whose outcome matters most?
            "social": 0.5,

            # Authority Orientation (Independent ↔ Conformist), Do I trust rules and hierarchy?
            "authority": 0.5,

            # Time Horizon (Impulsive ↔ Patient), Now or later?
            "patience": 0.5,

            # Novelty Orientation (Routine ↔ Exploratory), Do I stick to known patterns?
            "novelty": 0.5,
        }

    def apply_geo_bias(self, geo_pressure):
        """
        Adjusts tendencies based on environmental 'truth' provided by worldgen.
        Expects keys: resource_stability, environmental_threat,
        mobility_constraint, population_density, isolation_level.
        """
        # --- 1. Resource Stability ---
        # Logic: Scarcity (negative stability) breeds impulsivity and caution.
        # Abundance (positive stability) allows for long-term planning and social trust.
        res_stab = geo_pressure.get("resource_stability", 0)
        self.tendencies["patience"] += res_stab * 0.5
        self.tendencies["social"] += res_stab * 0.3
        self.tendencies["risk"] -= res_stab * 0.3

        # --- 2. Environmental Threat ---
        # Logic: High danger requires strict hierarchy and defensive readiness.
        # Safety allows for exploration and lower aggression.
        env_threat = geo_pressure.get("environmental_threat", 0)
        self.tendencies["aggression"] += env_threat * 0.4
        self.tendencies["authority"] += env_threat * 0.4
        self.tendencies["novelty"] -= env_threat * 0.2

        # --- 3. Mobility Constraint ---
        # Logic: Hard terrain (mountains/deep water) creates isolated, routine-based cultures.
        # Easy terrain encourages exploration and risk-taking.
        mob_con = geo_pressure.get("mobility_constraint", 0)
        self.tendencies["novelty"] -= mob_con * 0.2  # Hard to move = stick to routine
        self.tendencies["risk"] -= mob_con * 0.3  # Hard to move = play it safe
        self.tendencies["patience"] += mob_con * 0.2  # Life moves slower in hard terrain

        # --- 4. Population Density ---
        # Logic: High density increases social friction and the need for laws.
        pop_dens = geo_pressure.get("population_density", 0)
        self.tendencies["authority"] += pop_dens * 0.4
        self.tendencies["aggression"] += pop_dens * 0.3
        self.tendencies["novelty"] += pop_dens * 0.2  # Crowds drive people to look for new space

        # --- 5. Isolation Level ---
        # Logic: High isolation (no water/routes) forces local social cohesion.
        # Connectivity (low isolation) encourages global authority and novelty.
        iso_lvl = geo_pressure.get("isolation_level", 0)
        self.tendencies["social"] += iso_lvl * 0.4  # Isolated groups must trust each other
        self.tendencies["novelty"] -= iso_lvl * 0.4  # Isolated groups see less of the world
        self.tendencies["authority"] += iso_lvl * 0.3  # Remote areas care less about central rules

        # Final Clamp to range: -1.0 to 1.0
        for k in self.tendencies:
            self.tendencies[k] = max(-1.0, min(1.0, self.tendencies[k]))

    def get(self, tendency):
        return self.tendencies.get(tendency, 0.5)

    def to_json(self):
        return dict(self.tendencies)
