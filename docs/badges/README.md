# Badges

This directory contains static SVG badge files for the kong-oidc project.

## Available Badges

| Badge | File | Description |
|-------|------|-------------|
| ![CI](ci.svg) | `ci.svg` | Continuous Integration status |
| ![Coverage](coverage.svg) | `coverage.svg` | Test coverage percentage |
| ![Release](release.svg) | `release.svg` | Current release version |
| ![Kong Version](kong-version.svg) | `kong-version.svg` | Kong compatibility version |
| ![License](license.svg) | `license.svg` | Project license |

## Usage

These badges can be used in documentation, README files, or anywhere you need to display project status.

### Markdown Example

```markdown
![CI](docs/badges/ci.svg)
![Coverage](docs/badges/coverage.svg)
![Release](docs/badges/release.svg)
![Kong Version](docs/badges/kong-version.svg)
![License](docs/badges/license.svg)
```

### HTML Example

```html
<img src="docs/badges/ci.svg" alt="CI Status">
<img src="docs/badges/coverage.svg" alt="Coverage">
<img src="docs/badges/release.svg" alt="Release">
<img src="docs/badges/kong-version.svg" alt="Kong Version">
<img src="docs/badges/license.svg" alt="License">
```

## Badge Generation

These badges are generated using the standard shields.io format and can be customized as needed. The SVG files are optimized for web use and include proper accessibility attributes.

## Colors

- **Green (#4c1)**: Success/passing status
- **Blue (#007ec6)**: Information/neutral status
- **Orange (#fe7d37)**: Kong brand color
- **Gray (#555)**: Label background
