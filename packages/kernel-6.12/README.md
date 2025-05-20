# kernel-6.12

This package contains the Bottlerocket Linux kernel of the 6.12 series.


## Testing of Configuration Changes

Bottlerocket kernels are built in multiple flavors (e.g. cloud, bare metal) and for multiple architectures (e.g. aarch64, x86_64).
The kernel configuration for any of those combinations might change independently of the others.
Please use [`tools/latest-kernel-full-config.sh`](https://github.com/bottlerocket-os/bottlerocket-kernel-kit/tree/develop/tools/latest-kernel-full-config.sh) 
script from the this repository to ensure the configuration for any of the combinations does not change inadvertently:

```
# From the top-level bottlerocket-kernel-kit directory:
$ ./tools/latest-kernel-full-config.sh -r ./path/to/srpm
```

Any resulting diff in a [`config-full-bottlerocket-aarch64`](https://github.com/bottlerocket-os/bottlerocket-kernel-kit/blob/develop/packages/kernel-6.12/config-full-bottlerocket-aarch64) 
or [`config-full-bottlerocket-x86_64`](https://github.com/bottlerocket-os/bottlerocket-kernel-kit/blob/develop/packages/kernel-6.12/config-full-bottlerocket-x86_64) file should be PR'd to this package for review.
Changes that can have an effect on the resulting kernel configuration include:

* explicit kernel configuration changes
* package updates/kernel rebases
