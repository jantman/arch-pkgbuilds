# linux-precision5530

I fought for three days (probably ~30 hours) trying to get graphics working correctly on my Dell Precision 5530 laptop. I managed to get external monitors working with both nvidia proprietary and nouveau drivers, but wasn't able to get the internal laptop screen to work.

I finally found [ArchLinux bug FS#61964](https://bugs.archlinux.org/task/61964) which led me to [Kernel bug 202915](https://bugzilla.kernel.org/show_bug.cgi?id=202915) which in turn led me to [FreeDesktop.org bug 109959](https://bugs.freedesktop.org/show_bug.cgi?id=109959). That last bug confirms this issue as a problem in the ``i915`` kernel driver detection of the eDP laptop display, and includes a patch that fixes it **when ``force_edp_wide=1`` is added to the kernel command line**.

This package is based off of the upstream Arch Linux [linux](https://www.archlinux.org/packages/core/x86_64/linux/) kernel package, with the following changes:

* Addition of the [Precision-i915-force-edp-wide.patch](Precision-i915-force-edp-wide.patch) patch from Mark Weiman in [FreeDesktop.org bug 109959 comment 18](https://bugs.freedesktop.org/show_bug.cgi?id=109959#c18)
