# Badges

This directory contains badge documentation for the kong-oidc project.

## Current Badge Implementation

The project now uses **dynamic badges** from [shields.io](https://shields.io/) instead of static SVG files for better maintainability and real-time status updates.

## Available Badges

| Badge | URL | Description |
|-------|-----|-------------|
| ![CI](https://github.com/kedarkekan/kong-oidc/workflows/CI/badge.svg) | `https://github.com/kedarkekan/kong-oidc/workflows/CI/badge.svg` | Continuous Integration status |
| ![Release](https://github.com/kedarkekan/kong-oidc/workflows/Release/badge.svg) | `https://github.com/kedarkekan/kong-oidc/workflows/Release/badge.svg` | Current release version |
| ![Kong Version](https://img.shields.io/badge/Kong-3.9.1-fe7d37?logo=kong&logoColor=white) | `https://img.shields.io/badge/Kong-3.9.1-fe7d37?logo=kong&logoColor=white` | Kong compatibility version |
| ![License](https://img.shields.io/badge/License-MIT-blue.svg) | `https://img.shields.io/badge/License-MIT-blue.svg` | Project license |

## Usage in README

```markdown
[![CI](https://github.com/kedarkekan/kong-oidc/workflows/CI/badge.svg)](https://github.com/kedarkekan/kong-oidc/actions?query=workflow%3ACI)
[![Release](https://github.com/kedarkekan/kong-oidc/workflows/Release/badge.svg)](https://github.com/kedarkekan/kong-oidc/actions?query=workflow%3ARelease)
[![Kong Version](https://img.shields.io/badge/Kong-3.9.1-fe7d37?logo=kong&logoColor=white)](https://konghq.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
```




## Customization

To customize badges, visit [shields.io](https://shields.io/) and use their badge generator:

- **Color**: Use hex codes (e.g., `fe7d37` for Kong orange)
- **Logo**: Use logo names (e.g., `kong` for Kong logo)
- **Style**: Choose from flat, flat-square, for-the-badge, etc.
