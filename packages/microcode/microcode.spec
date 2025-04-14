# This is a wrapper package for binary-only microcode from Intel and AMD.
%global debug_package %{nil}

# These are specific to the upstream source RPM, and will likely need to be
# updated for each new version.
%global amd_ucode_version 20240909
%global intel_ucode_version 20240813

Name: %{_cross_os}microcode
Version: 0.0
Release: 1%{?dist}
Epoch: 1
Summary: Microcode for AMD and Intel processors
License: LicenseRef-scancode-amd-linux-firmware-export AND LicenseRef-scancode-intel-mcu-2018

# Packaging AMD and Intel microcode together is specific to Bottlerocket, and
# RPM only allows one URL field per package, so this is about as accurate as we
# can be. The real upstream URLs for AMD and Intel microcode are given below in
# the subpackage definitions.
URL: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/tree/develop/packages/microcode

Source0: https://www.kernel.org/pub/linux/kernel/firmware/linux-firmware-%{amd_ucode_version}.tar.xz
Source1: https://www.kernel.org/pub/linux/kernel/firmware/linux-firmware-%{amd_ucode_version}.tar.sign
Source2: gpgkey-4CDE8575E547BF835FE15807A31B6BD72486CFD6.asc
Source3: https://github.com/intel/Intel-Linux-Processor-Microcode-Data-Files/archive/refs/tags/microcode-%{intel_ucode_version}.tar.gz

# Lets us install "microcode" to pull in the AMD and Intel updates.
Requires: %{_cross_os}microcode-amd
Requires: %{_cross_os}microcode-intel-other
Requires: %{_cross_os}microcode-intel-ec2

%description
%{summary}.

%package ec2
Summary: Microcode for AMD and Intel processors available in EC2
License: LicenseRef-scancode-amd-linux-firmware-export AND LicenseRef-scancode-intel-mcu-2018
URL: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/tree/develop/packages/microcode
Requires: %{_cross_os}microcode-amd-ec2
Requires: %{_cross_os}microcode-intel-ec2

%description ec2
%{summary}.

%package amd
Provides: %{_cross_os}microcode-amd-ec2
Provides: %{_cross_os}microcode-amd-other
Summary: Microcode for AMD processors
License: LicenseRef-scancode-amd-linux-firmware-export
URL: https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git/tree/amd-ucode
Requires: %{_cross_os}microcode-amd-license

%description amd
%{summary}.

%package amd-license
Summary: License files for microcode for AMD processors
License: LicenseRef-scancode-amd-linux-firmware-export
URL: https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git/plain/LICENSE.amd-ucode

%description amd-license
%{summary}.

%package intel-other
Summary: Microcode for Intel processors not available in EC2
License: LicenseRef-scancode-intel-mcu-2018
URL: https://github.com/intel/Intel-Linux-Processor-Microcode-Data-Files
Requires: %{_cross_os}microcode-intel-license

%description intel-other
%{summary}.

%package intel-ec2
Summary: Microcode for Intel processors available in EC2
License: LicenseRef-scancode-intel-mcu-2018
URL: https://github.com/intel/Intel-Linux-Processor-Microcode-Data-Files
Requires: %{_cross_os}microcode-intel-license

%description intel-ec2
%{summary}.

%package intel-license
Summary: License files for microcode for Intel processors
License: LicenseRef-scancode-intel-mcu-2018
URL: https://github.com/intel/Intel-Linux-Processor-Microcode-Data-Files/blob/main/license

%description intel-license
%{summary}.

# Lets us install "microcode-licenses" for just the license files.
%package licenses
Summary: License files for microcode for AMD and Intel processors
License: LicenseRef-scancode-amd-linux-firmware-export AND LicenseRef-scancode-intel-mcu-2018
URL: https://github.com/bottlerocket-os/bottlerocket/tree/develop/packages/microcode
Requires: %{_cross_os}microcode-amd-license
Requires: %{_cross_os}microcode-intel-license

%description licenses
%{summary}.

%prep
%{gpgverify} --data=<(xzcat %{S:0}) --signature=%{S:1} --keyring=%{S:2}
mkdir amd intel
tar -C amd --strip-components=1 -xof %{S:0}
tar -C intel --strip-components=1 -xof %{S:3}
# CVE-2023-20569 - "AMD Inception"
# This is adding new microcode for Zen3/Zen4 AMD cpus. The patch was taken
# directly from the linux-firmware repository, but has not been part of a
# release there, yet.
# Unfortunately the setup here with two separate sources being brought into
# separate directories and the patch only affecting one of the two is not conducive
# of using the standard way of applying git binary patches through `autosetup -S git ...`
# Hence we have to extract some of the parts from that macro to let the patch
# apply.
#
# As soon as we update to a release that includes this patch everything from here...
pushd amd
%global __scm git
%__scm_setup_git
%autopatch -p1
popd
# ... to here can be dropped
cp {amd/,}LICENSE.amd-ucode
cp intel/intel-ucode-with-caveats/* intel/intel-ucode
cp intel/license LICENSE.intel-ucode

# Create links to the SPDX identifiers we're using, so they're easier to match
# up with the license text.
ln -s LICENSE.intel-ucode LicenseRef-scancode-intel-mcu-2018
ln -s LICENSE.amd-ucode LicenseRef-scancode-amd-linux-firmware-export

%build

%install
install -d %{buildroot}%{_cross_libdir}/firmware/{amd,intel}-ucode
install -p -m 0644 amd/amd-ucode/*.bin %{buildroot}%{_cross_libdir}/firmware/amd-ucode
install -p -m 0644 intel/intel-ucode/* %{buildroot}%{_cross_libdir}/firmware/intel-ucode

%files

%files amd
%dir %{_cross_libdir}/firmware
%dir %{_cross_libdir}/firmware/amd-ucode
%{_cross_libdir}/firmware/amd-ucode/microcode_amd*.bin

%files amd-license
%license LICENSE.amd-ucode LicenseRef-scancode-amd-linux-firmware-export

%files ec2

%files intel-ec2
%dir %{_cross_libdir}/firmware
%dir %{_cross_libdir}/firmware/intel-ucode
%{_cross_libdir}/firmware/intel-ucode/06-1a-05
%{_cross_libdir}/firmware/intel-ucode/06-2c-02
%{_cross_libdir}/firmware/intel-ucode/06-2d-06
%{_cross_libdir}/firmware/intel-ucode/06-2d-07
%{_cross_libdir}/firmware/intel-ucode/06-3e-04
%{_cross_libdir}/firmware/intel-ucode/06-3f-02
%{_cross_libdir}/firmware/intel-ucode/06-3f-04
%{_cross_libdir}/firmware/intel-ucode/06-4f-01
%{_cross_libdir}/firmware/intel-ucode/06-55-04
%{_cross_libdir}/firmware/intel-ucode/06-55-07
%{_cross_libdir}/firmware/intel-ucode/06-6a-06
%{_cross_libdir}/firmware/intel-ucode/06-8f-08
%{_cross_libdir}/firmware/intel-ucode/06-cf-02

%files intel-other
%dir %{_cross_libdir}/firmware
%dir %{_cross_libdir}/firmware/intel-ucode
%{_cross_libdir}/firmware/intel-ucode/06-03-02
%{_cross_libdir}/firmware/intel-ucode/06-05-00
%{_cross_libdir}/firmware/intel-ucode/06-05-01
%{_cross_libdir}/firmware/intel-ucode/06-05-02
%{_cross_libdir}/firmware/intel-ucode/06-05-03
%{_cross_libdir}/firmware/intel-ucode/06-06-00
%{_cross_libdir}/firmware/intel-ucode/06-06-05
%{_cross_libdir}/firmware/intel-ucode/06-06-0a
%{_cross_libdir}/firmware/intel-ucode/06-06-0d
%{_cross_libdir}/firmware/intel-ucode/06-07-01
%{_cross_libdir}/firmware/intel-ucode/06-07-02
%{_cross_libdir}/firmware/intel-ucode/06-07-03
%{_cross_libdir}/firmware/intel-ucode/06-08-01
%{_cross_libdir}/firmware/intel-ucode/06-08-03
%{_cross_libdir}/firmware/intel-ucode/06-08-06
%{_cross_libdir}/firmware/intel-ucode/06-08-0a
%{_cross_libdir}/firmware/intel-ucode/06-09-05
%{_cross_libdir}/firmware/intel-ucode/06-0a-00
%{_cross_libdir}/firmware/intel-ucode/06-0a-01
%{_cross_libdir}/firmware/intel-ucode/06-0b-01
%{_cross_libdir}/firmware/intel-ucode/06-0b-04
%{_cross_libdir}/firmware/intel-ucode/06-0d-06
%{_cross_libdir}/firmware/intel-ucode/06-0e-08
%{_cross_libdir}/firmware/intel-ucode/06-0e-0c
%{_cross_libdir}/firmware/intel-ucode/06-0f-02
%{_cross_libdir}/firmware/intel-ucode/06-0f-06
%{_cross_libdir}/firmware/intel-ucode/06-0f-07
%{_cross_libdir}/firmware/intel-ucode/06-0f-0a
%{_cross_libdir}/firmware/intel-ucode/06-0f-0b
%{_cross_libdir}/firmware/intel-ucode/06-0f-0d
%{_cross_libdir}/firmware/intel-ucode/06-16-01
%{_cross_libdir}/firmware/intel-ucode/06-17-06
%{_cross_libdir}/firmware/intel-ucode/06-17-07
%{_cross_libdir}/firmware/intel-ucode/06-17-0a
%{_cross_libdir}/firmware/intel-ucode/06-1a-04
%{_cross_libdir}/firmware/intel-ucode/06-1c-02
%{_cross_libdir}/firmware/intel-ucode/06-1c-0a
%{_cross_libdir}/firmware/intel-ucode/06-1d-01
%{_cross_libdir}/firmware/intel-ucode/06-1e-05
%{_cross_libdir}/firmware/intel-ucode/06-25-02
%{_cross_libdir}/firmware/intel-ucode/06-25-05
%{_cross_libdir}/firmware/intel-ucode/06-26-01
%{_cross_libdir}/firmware/intel-ucode/06-2a-07
%{_cross_libdir}/firmware/intel-ucode/06-2e-06
%{_cross_libdir}/firmware/intel-ucode/06-2f-02
%{_cross_libdir}/firmware/intel-ucode/06-37-08
%{_cross_libdir}/firmware/intel-ucode/06-37-09
%{_cross_libdir}/firmware/intel-ucode/06-3a-09
%{_cross_libdir}/firmware/intel-ucode/06-3c-03
%{_cross_libdir}/firmware/intel-ucode/06-3d-04
%{_cross_libdir}/firmware/intel-ucode/06-3e-06
%{_cross_libdir}/firmware/intel-ucode/06-3e-07
%{_cross_libdir}/firmware/intel-ucode/06-45-01
%{_cross_libdir}/firmware/intel-ucode/06-46-01
%{_cross_libdir}/firmware/intel-ucode/06-47-01
%{_cross_libdir}/firmware/intel-ucode/06-4c-03
%{_cross_libdir}/firmware/intel-ucode/06-4c-04
%{_cross_libdir}/firmware/intel-ucode/06-4d-08
%{_cross_libdir}/firmware/intel-ucode/06-4e-03
%{_cross_libdir}/firmware/intel-ucode/06-55-03
%{_cross_libdir}/firmware/intel-ucode/06-55-05
%{_cross_libdir}/firmware/intel-ucode/06-55-06
%{_cross_libdir}/firmware/intel-ucode/06-55-0b
%{_cross_libdir}/firmware/intel-ucode/06-56-02
%{_cross_libdir}/firmware/intel-ucode/06-56-03
%{_cross_libdir}/firmware/intel-ucode/06-56-04
%{_cross_libdir}/firmware/intel-ucode/06-56-05
%{_cross_libdir}/firmware/intel-ucode/06-5c-02
%{_cross_libdir}/firmware/intel-ucode/06-5c-09
%{_cross_libdir}/firmware/intel-ucode/06-5c-0a
%{_cross_libdir}/firmware/intel-ucode/06-5e-03
%{_cross_libdir}/firmware/intel-ucode/06-5f-01
%{_cross_libdir}/firmware/intel-ucode/06-66-03
%{_cross_libdir}/firmware/intel-ucode/06-6a-05
%{_cross_libdir}/firmware/intel-ucode/06-6c-01
%{_cross_libdir}/firmware/intel-ucode/06-7a-01
%{_cross_libdir}/firmware/intel-ucode/06-7a-08
%{_cross_libdir}/firmware/intel-ucode/06-7e-05
%{_cross_libdir}/firmware/intel-ucode/06-8a-01
%{_cross_libdir}/firmware/intel-ucode/06-8c-01
%{_cross_libdir}/firmware/intel-ucode/06-8c-02
%{_cross_libdir}/firmware/intel-ucode/06-8d-01
%{_cross_libdir}/firmware/intel-ucode/06-8e-09
%{_cross_libdir}/firmware/intel-ucode/06-8e-0a
%{_cross_libdir}/firmware/intel-ucode/06-8e-0b
%{_cross_libdir}/firmware/intel-ucode/06-8e-0c
%{_cross_libdir}/firmware/intel-ucode/06-8f-05
%{_cross_libdir}/firmware/intel-ucode/06-8f-06
%{_cross_libdir}/firmware/intel-ucode/06-8f-07
%{_cross_libdir}/firmware/intel-ucode/06-96-01
%{_cross_libdir}/firmware/intel-ucode/06-97-02
%{_cross_libdir}/firmware/intel-ucode/06-97-05
%{_cross_libdir}/firmware/intel-ucode/06-9a-03
%{_cross_libdir}/firmware/intel-ucode/06-9a-04
%{_cross_libdir}/firmware/intel-ucode/06-9c-00
%{_cross_libdir}/firmware/intel-ucode/06-9e-09
%{_cross_libdir}/firmware/intel-ucode/06-9e-0a
%{_cross_libdir}/firmware/intel-ucode/06-9e-0b
%{_cross_libdir}/firmware/intel-ucode/06-9e-0c
%{_cross_libdir}/firmware/intel-ucode/06-9e-0d
%{_cross_libdir}/firmware/intel-ucode/06-a5-02
%{_cross_libdir}/firmware/intel-ucode/06-a5-03
%{_cross_libdir}/firmware/intel-ucode/06-a5-05
%{_cross_libdir}/firmware/intel-ucode/06-a6-00
%{_cross_libdir}/firmware/intel-ucode/06-a6-01
%{_cross_libdir}/firmware/intel-ucode/06-a7-01
%{_cross_libdir}/firmware/intel-ucode/06-aa-04
%{_cross_libdir}/firmware/intel-ucode/06-b7-01
%{_cross_libdir}/firmware/intel-ucode/06-ba-02
%{_cross_libdir}/firmware/intel-ucode/06-ba-03
%{_cross_libdir}/firmware/intel-ucode/06-ba-08
%{_cross_libdir}/firmware/intel-ucode/06-be-00
%{_cross_libdir}/firmware/intel-ucode/06-bf-02
%{_cross_libdir}/firmware/intel-ucode/06-bf-05
%{_cross_libdir}/firmware/intel-ucode/06-cf-01
%{_cross_libdir}/firmware/intel-ucode/0f-00-07
%{_cross_libdir}/firmware/intel-ucode/0f-00-0a
%{_cross_libdir}/firmware/intel-ucode/0f-01-02
%{_cross_libdir}/firmware/intel-ucode/0f-02-04
%{_cross_libdir}/firmware/intel-ucode/0f-02-05
%{_cross_libdir}/firmware/intel-ucode/0f-02-06
%{_cross_libdir}/firmware/intel-ucode/0f-02-07
%{_cross_libdir}/firmware/intel-ucode/0f-02-09
%{_cross_libdir}/firmware/intel-ucode/0f-03-02
%{_cross_libdir}/firmware/intel-ucode/0f-03-03
%{_cross_libdir}/firmware/intel-ucode/0f-03-04
%{_cross_libdir}/firmware/intel-ucode/0f-04-01
%{_cross_libdir}/firmware/intel-ucode/0f-04-03
%{_cross_libdir}/firmware/intel-ucode/0f-04-04
%{_cross_libdir}/firmware/intel-ucode/0f-04-07
%{_cross_libdir}/firmware/intel-ucode/0f-04-08
%{_cross_libdir}/firmware/intel-ucode/0f-04-09
%{_cross_libdir}/firmware/intel-ucode/0f-04-0a
%{_cross_libdir}/firmware/intel-ucode/0f-06-02
%{_cross_libdir}/firmware/intel-ucode/0f-06-04
%{_cross_libdir}/firmware/intel-ucode/0f-06-05
%{_cross_libdir}/firmware/intel-ucode/0f-06-08
%exclude %{_cross_libdir}/firmware/intel-ucode/??-??-??_DUPLICATE

%files intel-license
%license LICENSE.intel-ucode LicenseRef-scancode-intel-mcu-2018

%files licenses
%{_cross_attribution_file}

%changelog
