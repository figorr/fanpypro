## [3.0.3](https://github.com/figorr/fanpypro/compare/v3.0.2...v3.0.3) (2026-07-10)


### Bug Fixes

* light on/off commands ([7934d43](https://github.com/figorr/fanpypro/commit/7934d4355e0ad71befe95940849aecb00827ad00))

## [3.0.2](https://github.com/figorr/fanpypro/compare/v3.0.1...v3.0.2) (2026-07-09)


### Bug Fixes

* add extra attributes for direct mode ([3e44fa9](https://github.com/figorr/fanpypro/commit/3e44fa90db8d2e0f545d94da08a8566dde8c0c68))
* fix timer listener ([79b8a36](https://github.com/figorr/fanpypro/commit/79b8a3610a2b3b787c5fc001ce137915f863f067))

## [3.0.1](https://github.com/figorr/fanpypro/compare/v3.0.0...v3.0.1) (2026-07-07)


### Bug Fixes

* set guard for fan timers ([59393b7](https://github.com/figorr/fanpypro/commit/59393b7b0cea69a52b08f8b20ed98d564f96cc70))

# [3.0.0](https://github.com/figorr/fanpypro/compare/v2.0.3...v3.0.0) (2026-07-07)


### Features

* New Fanpy structure for Remotes modes ([2293aff](https://github.com/figorr/fanpypro/commit/2293aff6e0bf37a4b642d6a87681518cd5f1dd06))


### BREAKING CHANGES

* New fan and light entities for Remotes modes

## [2.0.3](https://github.com/figorr/fanpypro/compare/v2.0.2...v2.0.3) (2026-07-05)


### Bug Fixes

* fix switch state restore ([7a0cf5f](https://github.com/figorr/fanpypro/commit/7a0cf5f5f667f55980821a669dc1df30a3017830))

## [2.0.2](https://github.com/figorr/fanpypro/compare/v2.0.1...v2.0.2) (2026-07-05)


### Bug Fixes

* fix scripts.yaml generation ([e3f4292](https://github.com/figorr/fanpypro/commit/e3f42929c978fcd9c8ad2161860fb34e10453501))
* update images ([903fa09](https://github.com/figorr/fanpypro/commit/903fa09e5effb6424429ae45c9af2292aed0065f))
* update README scripts example to match new generated formats ([fcafc73](https://github.com/figorr/fanpypro/commit/fcafc7385a69519dbfa78457ecb761c113d7d4d3))

## [2.0.1](https://github.com/figorr/fanpypro/compare/v2.0.0...v2.0.1) (2026-07-04)


### Bug Fixes

* branding images ([a2e8742](https://github.com/figorr/fanpypro/commit/a2e87426c6c2adcf1dbac21ddf0e95a46c249e9a))
* fanpy-card images ([b456211](https://github.com/figorr/fanpypro/commit/b456211150f887b9007d7d91cf1ca5a6a52d02ac))
* update README ([c0f7821](https://github.com/figorr/fanpypro/commit/c0f7821159f195c1e344eac4e3eb8f8ac6fdac33))

# [2.0.0](https://github.com/figorr/fanpypro/compare/v1.0.6...v2.0.0) (2026-07-04)


* feat!: timer redesign â€” num_timers dropdown, native timer.start/cancel, auto power-off on expiry ([800c962](https://github.com/figorr/fanpypro/commit/800c96280fde0c6b8ea489ef0f6811e4c70e79f4))


### BREAKING CHANGES

* has_timer toggle replaced by num_timers (0-3) dropdown in config flow.
* OptionsFlow removed; re-add integration to change settings.
* IR timer commands (command_timer_*) no longer requested.
* No timer entities or timer scripts are auto-generated.
* Card now calls native timer.start/cancel services instead of scripts.
* Timer expiry triggers automatic power-off via state listener.

Features:
- num_timers select entity (select.fanpypro_*_num_timers) bridges count to card
- Auto power-off when a timer naturally expires (active -> idle transition)
- Timer cancellation by user is tracked to prevent false power-off triggers
- Config flow descriptions updated with detailed timer helper path
- Services.yaml removed (no custom fanpy.* timer services)
- has_ring toggle to hide SVG ring, keeping speed buttons visible
- Speed section label (VELOCIDAD) added above speed buttons

## [1.0.6](https://github.com/figorr/fanpypro/compare/v1.0.5...v1.0.6) (2026-07-03)


### Bug Fixes

* fix scripts.yaml creation and restoration ([fd26fef](https://github.com/figorr/fanpypro/commit/fd26fef502f088536d71ac33c62c9ae8b2c0f204))
* images for README ([f60148a](https://github.com/figorr/fanpypro/commit/f60148ab34fb6549012acba6fb9f3e19d5adaf68))
* improve select entity creation ([2bc85dd](https://github.com/figorr/fanpypro/commit/2bc85dd12033658bce2b56221270d1d2a1f9721e))
* remove unnecessary button entities ([df8e2c1](https://github.com/figorr/fanpypro/commit/df8e2c1ac8817f8a944fb3163eb01f6202be89d1))
* update README ([5aaf09e](https://github.com/figorr/fanpypro/commit/5aaf09ec71ddb7757ea8bc6139f1e5eea9e1c2c5))

## [1.0.5](https://github.com/figorr/fanpypro/compare/v1.0.4...v1.0.5) (2026-07-02)


### Bug Fixes

* test zip attachment in release workflow ([64720e3](https://github.com/figorr/fanpypro/commit/64720e30198e7140ae7ffb47b71ef8382053caa5))

## [1.0.4](https://github.com/figorr/fanpypro/compare/v1.0.3...v1.0.4) (2026-07-02)


### Bug Fixes

* update publish workflow ([5282a1f](https://github.com/figorr/fanpypro/commit/5282a1f32c035fe178ede11d55b8fe3ef78652d2))

## [1.0.3](https://github.com/figorr/fanpypro/compare/v1.0.2...v1.0.3) (2026-07-02)


### Bug Fixes

* test publish-zip workflow ([cc3fdaa](https://github.com/figorr/fanpypro/commit/cc3fdaac607f48207516bb6774465df266e0c327))

## [1.0.2](https://github.com/figorr/fanpypro/compare/v1.0.1...v1.0.2) (2026-07-02)


### Bug Fixes

* update README ([1bd16a7](https://github.com/figorr/fanpypro/commit/1bd16a7716873a29204ce0a030fc6b921623a4e0))

## [1.0.1](https://github.com/figorr/fanpypro/compare/v1.0.0...v1.0.1) (2026-07-02)


### Bug Fixes

* add Fanpy prefix to entity names ([7a147c8](https://github.com/figorr/fanpypro/commit/7a147c85282729fa1ce81f5a05adb2928688a8f9))

# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] â€” 2026-07-01

### Added

- Initial release
- Multi-step config flow (area, mode, features, Broadlink, speed commands)
- Binary sensor platform for card more-info (power, luz)
- Button platform for manual script triggers
- YAML generation for input_boolean, input_select, input_button, template binary_sensors
- Full Broadlink RF scripts generation
- Translations: English, Spanish, Catalan
