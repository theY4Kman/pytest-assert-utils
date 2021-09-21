# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## [Unreleased]


## [0.3.0] — 2021-09-21
### Added
 - Added `containing_only` and `containing_exactly` methods to `util.Collection` classes — see [GH#1](https://github.com/theY4Kman/pytest-assert-utils/pull/1) (thanks, [sjhewitt](https://github.com/sjhewitt))
 - Added `util.Model` class to check attrs of objects using an equality comparison — see [GH#2](https://github.com/theY4Kman/pytest-assert-utils/pull/2) (thanks, [sjhewitt](https://github.com/sjhewitt))
 - Added tests for `util.Collection` classes


## [0.2.2] — 2021-03-27
### Fixed
 - Add support for Python 3.10


## [0.2.1] — 2020-08-25
### Added
 - Add documentation to README
 - Transfer ownership to @theY4Kman


## [0.2.0] — 2020-08-04
### Added
 - Allow `util.Collection` classes to be used directly in comparisons
 - Add `util.Dict` and `util.Str` comparison classes


## [0.1.1] — 2020-03-30
### Fixed
 - Added setuptools entrypoint, so pytest will perform assertion rewriting


## [0.1.0] — 2019-12-08
### Added
 - Introducing `util.Any(*types)` and `util.Optional(value)` meta-values to allow flexibility when performing equality comparisons.
 - Added `util.Collection`, `util.List`, and `util.Set` to flexibly perform assertions on collection types when performing equality comparisons.


## [0.0.1] — 2019-08-14
### Added
 - Introducing `assert_dict_is_subset` and `assert_model_attrs` assertion utilities
