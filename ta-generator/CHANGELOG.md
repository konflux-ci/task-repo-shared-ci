# Changelog

<!-- Format guidelines: https://keepachangelog.com/en/1.1.0/#how -->

## Unreleased

### Changed

- Generated `use-trusted-artifact` steps now set project TA default
  `computeResources`: 4Gi memory request=limit, 50m CPU request (no
  `limits.cpu`). Previously this step had no resources.
- Generated `create-trusted-artifact` CPU request lowered from `1` to
  `50m` to match the project TA default (memory stays 3Gi req=lim; still
  no `limits.cpu`).

Golang dependencies update.

## v1.1.0

### Added

The generator supports the `newPrefetchNaming` recipe option. When set
to `true`, generated `use-prefetch` / `create-prefetch` params, results,
and trusted-artifact paths use `PREFETCH_ARTIFACT` and
`/var/workdir/prefetch` instead of `CACHI2_ARTIFACT` and
`/var/workdir/cachi2`. Defaults to `false` so existing recipes keep the
historic cachi2 naming until they opt in.

## v1.0.0

The initial release of the generator. Copied from the previous location in the
[build-definitions](https://github.com/konflux-ci/build-definitions/tree/main/task-generator/trusted-artifacts)
repository.
