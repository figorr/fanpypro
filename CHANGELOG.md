# [1.2.0](https://github.com/figorr/fanpypro/compare/v1.1.8...v1.2.0) (2026-08-18)


### Features

* add neutral light temperature mode and light options flow ([dd04943](https://github.com/figorr/fanpypro/commit/dd049437d902c8ceff8c892907fb6319899e1444))

## [1.1.8](https://github.com/figorr/fanpypro/compare/v1.1.7...v1.1.8) (2026-08-04)


### Bug Fixes

* sync fan speed from physical remote when on code carries a speed ([4a7570f](https://github.com/figorr/fanpypro/commit/4a7570f66edf866febd74e9281d85c96260504a5))

## [1.1.7](https://github.com/figorr/fanpypro/compare/v1.1.6...v1.1.7) (2026-08-04)


### Bug Fixes

* parametrize rf echo suppression window via RF_ECHO_WINDOW ([4a57ca3](https://github.com/figorr/fanpypro/commit/4a57ca3991c2ffb2f44ced54881c63f2cc718b7e))

## [1.1.6](https://github.com/figorr/fanpypro/compare/v1.1.5...v1.1.6) (2026-08-03)


### Bug Fixes

* revert rf echo suppression to time window to fix speed off-by-one ([9bd59e0](https://github.com/figorr/fanpypro/commit/9bd59e0120d5e23e435c5df17d91da20d40f7084))

## [1.1.5](https://github.com/figorr/fanpypro/compare/v1.1.4...v1.1.5) (2026-08-02)


### Bug Fixes

* suppress rf echo by code instead of time window to avoid blocking buttons. ([3c6056f](https://github.com/figorr/fanpypro/commit/3c6056f05303ae3b05db2234b29dd064e64b7096))

## [1.1.4](https://github.com/figorr/fanpypro/compare/v1.1.3...v1.1.4) (2026-07-29)


### Bug Fixes

* fix esphome chip revision ([54eb4d3](https://github.com/figorr/fanpypro/commit/54eb4d37a385b2760c899777899bfff34948189c))

## [1.1.3](https://github.com/figorr/fanpypro/compare/v1.1.2...v1.1.3) (2026-07-21)


### Bug Fixes

* fix light resync button ([825bcaa](https://github.com/figorr/fanpypro/commit/825bcaa34db35b34597ae367850f54723e301af7))

## [1.1.2](https://github.com/figorr/fanpypro/compare/v1.1.1...v1.1.2) (2026-07-18)


### Bug Fixes

* implement options_flow for remote setups ([1fc3a1b](https://github.com/figorr/fanpypro/commit/1fc3a1ba9214abdb22f6e0a0f158c963b21783b8))

## [1.1.1](https://github.com/figorr/fanpypro/compare/v1.1.0...v1.1.1) (2026-07-18)


### Bug Fixes

* fix fan speed after restart ([803de34](https://github.com/figorr/fanpypro/commit/803de34f18bbd8e727e966c601b9030caab5b277))
* fix handle speed change at restart ([ebc0ab0](https://github.com/figorr/fanpypro/commit/ebc0ab0e9eda46774f7c9ca714ce586a9beb759c))

# [1.1.0](https://github.com/figorr/fanpypro/compare/v1.0.3...v1.1.0) (2026-07-17)


### Features

* include hybrid rf+broadlink mode ([4b4d756](https://github.com/figorr/fanpypro/commit/4b4d7562e024b44f45eeb9480fca200abdcfe114))

## [1.0.3](https://github.com/figorr/fanpypro/compare/v1.0.2...v1.0.3) (2026-07-16)


### Bug Fixes

* fix light on / off not booleans ([af26826](https://github.com/figorr/fanpypro/commit/af26826073c74963514c8018fc2cfde717c09e65))
* fix light toggle when on / off share the same code ([30eeaf3](https://github.com/figorr/fanpypro/commit/30eeaf3bb4e6b9e130a05b51af279b5fe8a0ab6a))

## [1.0.2](https://github.com/figorr/fanpypro/compare/v1.0.1...v1.0.2) (2026-07-16)


### Bug Fixes

* fix entity_id name ([a3a6712](https://github.com/figorr/fanpypro/commit/a3a6712733b609e2558e842108bcbc366606d753))
* fix entity_id name ([8cee7d2](https://github.com/figorr/fanpypro/commit/8cee7d28d025c2aa90b0aa98099fa284cdedfb26))
* fix entiy_id name and add echo supression ([f1d71b6](https://github.com/figorr/fanpypro/commit/f1d71b6ca2b4f7f92193994460603e9d37bab6c0))
* fix gateway step ([6a45239](https://github.com/figorr/fanpypro/commit/6a452390f3c3b6b7ff1c29ab7fa8ee528824a203))
* fix hardcoded protocol ([49e7f24](https://github.com/figorr/fanpypro/commit/49e7f242963f3a250040d31b3c856213a63d5436))
* fix hardcoded protocol ([3a0360a](https://github.com/figorr/fanpypro/commit/3a0360ac60a80a1d454c49d325ab5d6fe288a108))
* fix hardcoded protocol ([15edc82](https://github.com/figorr/fanpypro/commit/15edc823c359058cb8d90c89ba2eafb6d7f5c8f9))
* fix scripts generation, handle rf_code and match code ([ba8d8a8](https://github.com/figorr/fanpypro/commit/ba8d8a80f7ce473eaaa079102be9ce831de25453))

## [1.0.1](https://github.com/figorr/fanpypro/compare/v1.0.0...v1.0.1) (2026-07-15)


### Bug Fixes

* fix esphome_fanpypro_rf_code service ([db3b186](https://github.com/figorr/fanpypro/commit/db3b186da7f2fafbb0e94d71a54dbc09cf0a3dab))
* fix icon button ([855e6eb](https://github.com/figorr/fanpypro/commit/855e6eb47ffcee6c4ad5ecd404770faaf72e9ee2))

# 1.0.0 (2026-07-15)


### Features

* initial release of fanpypro ([1d98668](https://github.com/figorr/fanpypro/commit/1d98668952ec0b56d6d64e106034adf367c8fe56))
