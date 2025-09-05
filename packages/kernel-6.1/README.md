# kernel-6.1

This package contains the Bottlerocket Linux kernel of the 6.1 series.

## Configuration Structure

The kernel configuration is organized into multiple files:

* [`config-bottlerocket`](config-bottlerocket) - Common configuration options shared across all architectures
* [`config-bottlerocket-aarch64`](config-bottlerocket-aarch64) - ARM64-specific configuration options
* [`config-bottlerocket-x86_64`](config-bottlerocket-x86_64) - x86_64-specific configuration options

During the build process, these configurations are merged in the following order:
1. Base Amazon Linux config (`../config-<arch>`)
2. Microcode config (x86_64 only)
3. Common Bottlerocket config (`config-bottlerocket`)
4. Architecture-specific Bottlerocket config (`config-bottlerocket-<arch>`)

The final merged configurations are written to:
* [`config-full-bottlerocket-aarch64`](config-full-bottlerocket-aarch64) - Complete ARM64 configuration
* [`config-full-bottlerocket-x86_64`](config-full-bottlerocket-x86_64) - Complete x86_64 configuration

## Testing of Configuration Changes

Bottlerocket kernels are built in multiple flavors (e.g. cloud, bare metal) and for multiple architectures (e.g. aarch64, x86_64).
The kernel configuration for any of those combinations might change independently of the others.
Please use [`tools/latest-kernel-full-config.sh`](https://github.com/bottlerocket-os/bottlerocket-kernel-kit/tree/develop/tools/latest-kernel-full-config.sh) 
script from the this repository to ensure the configuration for any of the combinations does not change inadvertently:

```
# From the top-level bottlerocket-kernel-kit directory:
$ ./tools/latest-kernel-full-config.sh -r ./path/to/srpm
```

Any resulting diff in a [`config-full-bottlerocket-aarch64`](https://github.com/bottlerocket-os/bottlerocket-kernel-kit/blob/develop/packages/kernel-6.1/config-full-bottlerocket-aarch64) 
or [`config-full-bottlerocket-x86_64`](https://github.com/bottlerocket-os/bottlerocket-kernel-kit/blob/develop/packages/kernel-6.1/config-full-bottlerocket-x86_64) file should be PR'd to this package for review.
Changes that can have an effect on the resulting kernel configuration include:

* explicit kernel configuration changes in any of the source config files
* package updates/kernel rebases
