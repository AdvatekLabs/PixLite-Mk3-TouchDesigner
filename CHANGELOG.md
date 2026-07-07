# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Each released version is tagged in git as `vX.Y.Z`.

## [1.2.0] - 2026-07-07

### Added
- **About page** via Derivative's official `docsHelper` component — shows the
  component version, a help link, and the `.tox` save-build stamp.
- **Infer from Pixel Data** toggle on the Input page. When enabled, the transmit
  base address (Net / Subnet / Universe / Start Channel) is derived from the first
  pixel output (Port 0) and the fields are locked read-only.

### Changed
- Renamed the Input source parameter label to **Pixel Data POP**.

### Removed
- **Channel Gap** parameter from the Input page — it applies to spacing between
  discrete DMX fixtures and is not meaningful for a contiguous pixel stream.
- **TDVersionExt** and **TDToxExt** extensions, along with their **Version** and
  **Component** parameter pages. Component versioning, remote update checks, and
  automatic tox export are no longer part of the component; versioning is now
  tracked with git tags and this changelog.

## [1.1.0] - 2026-07-07
- Add Input parameters

## [1.0.7] - 2026-04-01
- Update POPs network

## [1.0.5] - 2026-04-01
- Fix Pixel Data output format

## [1.0.4] - 2026-04-01
- Add POPs output

## [1.0.3] - 2026-04-01
- Add System page

## [1.0.2] - 2026-03-31
- Add Pixel Data

## [1.0.1] - 2026-03-31
- Add pixel outputs
