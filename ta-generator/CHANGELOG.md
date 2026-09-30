# Changelog

<!-- Format guidelines: https://keepachangelog.com/en/1.1.0/#how -->

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
