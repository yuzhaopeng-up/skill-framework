# Skill Framework

<p align="center">
  <img src="https://img.shields.io/badge/Skills-208-blue" alt="208 Skills" />
  <img src="https://img.shields.io/badge/Python-3.8+-green" alt="Python 3.8+" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License: MIT" />
  <img src="https://img.shields.io/badge/L0--L4-Classification-orange" alt="L0-L4 Classification" />
</p>

A comprehensive governance framework for **AI Agent Skills** — from classification to quality assurance to tooling.

## Why This Matters

Building AI agents is easy. Governing 200+ skills across a team of agents is hard. This framework provides:

- **L0-L4 Skill Classification** — Every skill categorized by abstraction level
- **208-Skill Inventory** — A fully cataloged, searchable skill database
- **Quality Gates** — Automated compliance checks before any skill goes live
- **YAML Templates** — Copy-paste starters for L1 Base, L2 Gateway, and L3 Ceiling skills
- **Python Tooling** — Lint, scan, and backfill tools for skill lifecycle management
- **4 Industry Verticals** — Financial, telecom, healthcare, and government blueprints

## Architecture

```
L0: Foundation Layer     →  Shared utilities, DB connectors, API clients
L1: Base Skill Layer     →  Single-function atomic skills (info-extractor, data-analyst)
L2: Gateway/Router Layer →  Intent routing, NL2SQL, cross-channel dispatching
L3: Scenario Layer       →  Business-scenario composites (fraud detection, SLA monitoring)
L4: Multi-Agent Layer    →  Agent-team orchestration, multi-phase pipelines
```

## Quick Start

### 1. Use the Templates

```bash
# Create a new L1 Base skill
cp templates/skill-template-l1-base.yaml my-skill.yaml

# Create a new L2 Gateway skill
cp templates/skill-template-l2-gateway.yaml my-gateway.yaml

# Create a new L3 Ceiling skill
cp templates/skill-template-l3-ceiling.yaml my-scenario.yaml
```

### 2. Run the Tools

```bash
# Scan your skill directory and build inventory
python skill-architecture/scripts/inventory-scan.py --dir ./skills

# Lint skill YAML files for compliance
python skill-architecture/scripts/skill-lint.py --dir ./skills

# Backfill missing frontmatter in skill files
python skill-architecture/scripts/backfill-frontmatter.py --dir ./skills
```

### 3. Quality Gate Checklist

Use `templates/audit-checklist.md` to verify your skills meet governance standards before deployment.

## Directory Structure

```
skill-framework/
├── skill-architecture/
│   ├── SKILL-ARCHITECTURE-v1.0.md      # Full architecture specification
│   ├── unified_skill_inventory.json     # 208-skill master inventory (JSON)
│   ├── unified_skill_inventory.csv      # 208-skill master inventory (CSV)
│   ├── skills_inventory.json            # Detailed skill catalog
│   ├── skills_detailed.json             # Per-skill metadata
│   ├── skills_dependencies.json         # Inter-skill dependency graph
│   ├── governance/                      # Quality gates, IM specs, remediation plans
│   ├── l2-patterns/                     # L2 pattern references (alert engine, routing, etc.)
│   ├── l3-scenarios/                    # L3 scenario skill blueprints
│   ├── l4-multi-agent/                  # L4 multi-agent orchestration patterns
│   ├── verticals/                       # Industry vertical blueprints (4 industries)
│   ├── roadmap/                         # Skill development roadmap
│   └── scripts/                         # Python tools (lint, scan, backfill)
├── templates/
│   ├── skill-template-l1-base.yaml      # L1 Base skill template
│   ├── skill-template-l2-gateway.yaml   # L2 Gateway skill template
│   ├── skill-template-l3-ceiling.yaml   # L3 Ceiling skill template
│   └── audit-checklist.md              # Quality gate checklist
└── README.md
```

## Skill Classification Model

| Level | Name | Scope | Example |
|-------|------|-------|---------|
| L0 | Foundation | Shared infra | DB connector, API client |
| L1 | Base Skill | Single function | Info-extractor, data-analyst |
| L2 | Gateway | Routing/orchestration | NL2SQL gateway, cross-channel router |
| L3 | Scenario | Business composite | Fraud detection pipeline |
| L4 | Multi-Agent | Agent team | 5-phase scoring engine |

## Ecosystem

This framework is part of the **Agent Skill Ecosystem**:

| Repo | Description | Skills |
|------|------------|--------|
| [financial-ai-skills](https://github.com/yuzhaopeng-up/financial-ai-skills) | 104 financial AI skills | 104 |
| [teleagent-skills](https://github.com/yuzhaopeng-up/teleagent-skills) | General business skills | 5 |
| [agent-cluster-comm](https://github.com/yuzhaopeng-up/agent-cluster-comm) | Agent cluster communication | 5 |
| **skill-framework** (this repo) | Governance framework + templates | 208 cataloged |

## Contributing

1. Fork this repository
2. Create your feature branch
3. Follow the L0-L4 classification when adding new skills
4. Use the provided YAML templates
5. Run `skill-lint.py` before submitting
6. Submit a pull request

## License

MIT License — use freely in personal and commercial projects.
