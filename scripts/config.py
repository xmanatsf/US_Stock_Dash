"""Config loading. One place that knows where the JSON lives and what shape it must have."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONFIG_DIR = os.path.join(ROOT, "config")

_REQUIRED = {
    "universes": ["rawDir", "processedDir", "siteDataDir", "benchmarkSource", "universes"],
    "parameters": ["windows", "coverage", "breadth", "structure", "weights", "regime"],
    "sectors": ["sources", "rollup"],
    "charts": ["charts", "panels"],
}


class ConfigError(Exception):
    pass


@dataclass
class Config:
    universes: dict
    parameters: dict
    sectors: dict
    charts: dict
    root: str = ROOT

    def path(self, rel: str) -> str:
        return rel if os.path.isabs(rel) else os.path.join(self.root, rel)

    @property
    def raw_dir(self) -> str:
        return self.path(self.universes["rawDir"])

    @property
    def processed_dir(self) -> str:
        return self.path(self.universes["processedDir"])

    @property
    def site_data_dir(self) -> str:
        return self.path(self.universes["siteDataDir"])

    def universe(self, key: str) -> dict:
        try:
            return self.universes["universes"][key]
        except KeyError:
            raise ConfigError(
                f"unknown universe {key!r}; known: {sorted(self.universes['universes'])}"
            ) from None

    def universe_keys(self) -> list:
        return [k for k, _ in sorted(self.universes["universes"].items(),
                                     key=lambda kv: kv[1].get("order", 99))]

    def sub_baskets(self, key: str):
        name = self.universe(key).get("subBaskets")
        return self.parameters["subBaskets"].get(name) if name else None


def _load_one(name: str) -> dict:
    p = os.path.join(CONFIG_DIR, f"{name}.json")
    if not os.path.exists(p):
        raise ConfigError(f"missing config file: {p}")
    with open(p, encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"{name}.json is not valid JSON: {e}") from None
    for k in _REQUIRED[name]:
        if k not in data:
            raise ConfigError(f"{name}.json is missing required key {k!r}")
    return data


def load() -> Config:
    cfg = Config(
        universes=_load_one("universes"),
        parameters=_load_one("parameters"),
        sectors=_load_one("sectors"),
        charts=_load_one("charts"),
    )
    w = {k: v for k, v in cfg.parameters["weights"].items() if isinstance(v, (int, float))}
    if set(w) != {"A", "B", "C", "E", "F", "G", "H"}:
        raise ConfigError(
            f"pillar weights must be exactly A,B,C,E,F,G,H (there is deliberately no pillar D); "
            f"got {sorted(w)}"
        )
    if sum(w.values()) != 100:
        raise ConfigError(f"pillar weights must sum to 100; got {sum(w.values())}")
    return cfg
