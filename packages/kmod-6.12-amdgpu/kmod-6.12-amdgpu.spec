%global kernel_sources %{_cross_usrsrc}/kernels/6.12
%define _kernel_version %(cat %{kernel_sources}/include/config/kernel.release)
%global _cross_kmoddir %{_cross_libdir}/modules/%{_kernel_version}
%global amdgpu_kmoddir %{_cross_kmoddir}/kernel/drivers/updates/gpu/drm/amd/amdgpu
%global _ko ko

Name: %{_cross_os}kmod-6.12-amdgpu
Version: 30.20.1
Release: 1%{?dist}
Summary: AMD GPU drivers for the 6.12 kernel
License: MIT AND GPL-2.0-only AND (GPL-2.0-only WITH Linux-syscall-note) AND GPL-2.0-or-later AND (GPL-2.0-or-later WITH Linux-syscall-note) AND LGPL-2.0-or-later AND (BSD-3-Clause OR GPL-2.0-only)
URL: https://repo.radeon.com/amdgpu/

Source0: https://repo.radeon.com/amdgpu/30.20.1/el/10.1/main/x86_64/amdgpu-dkms-6.16.6-2255209.el10.noarch.rpm
Source1: gpgkey-9386B48A1A693C5C.asc

BuildRequires: %{_cross_os}kernel-6.12-devel
Requires: %{_cross_os}kernel-6.12
Requires: %{_cross_os}linux-firmware-amdgpu

%description
%{summary}.

%prep
# Verify RPM signature
rpmkeys --import %{S:1} --dbpath "${PWD}/rpmdb"
rpmkeys --checksig %{S:0} --dbpath "${PWD}/rpmdb"
# Extract driver sources and licenses from RPM
rpm2cpio %{S:0} | cpio -idmu './usr/src/amdgpu-*' './usr/share/doc/amdgpu-dkms/*'
find usr/src/ -mindepth 1 -maxdepth 1 -type d -exec mv {} amdgpu \;
# Copy the LICENSE file to build directory
cp usr/share/doc/amdgpu-dkms/LICENSE .
rm -r usr

# Cross-compilation make macro for kernel builds
%global kmake %{shrink: \
make -s \
  ARCH="%{_cross_karch}" \
  CROSS_COMPILE="%{_cross_target}-" \
  INSTALL_HDR_PATH="%{buildroot}%{_cross_prefix}" \
  INSTALL_MOD_PATH="%{buildroot}%{_cross_prefix}" \
  INSTALL_MOD_STRIP=1 \
  %{nil}}

%build
# Configure and Build AMD GPU driver
pushd %{_builddir}/amdgpu/amd/dkms
sed -i -e 's,AC_TRY_COMMAND(make,AC_TRY_COMMAND(%kmake,g' m4/kernel.m4
autoreconf -fi
%cross_configure \
  KERNELVER="%{_kernel_version}" \
  ARCH="%{_cross_karch}" \
  --with-linux=%{kernel_sources} \
  %{nil}
popd
pushd %{_builddir}/amdgpu
%kmake \
  KERNELVER="%{_kernel_version}" \
  kernel_build_dir=%{kernel_sources} \
  modules
popd

%install
# Install AMD GPU kernel modules to correct location
install -d %{buildroot}%{amdgpu_kmoddir}
find amdgpu -type f -name "*.%{_ko}" -print \
  -exec install -p -m 0644 '{}' \
  %{buildroot}%{amdgpu_kmoddir}/ \;

%files
%license LICENSE
%{_cross_attribution_file}
%{amdgpu_kmoddir}/amdkcl.%{_ko}
%{amdgpu_kmoddir}/amdttm.%{_ko}
%{amdgpu_kmoddir}/amddrm_ttm_helper.%{_ko}
%{amdgpu_kmoddir}/amddrm_buddy.%{_ko}
%{amdgpu_kmoddir}/amddrm_exec.%{_ko}
%{amdgpu_kmoddir}/amd-sched.%{_ko}
%{amdgpu_kmoddir}/amdxcp.%{_ko}
%{amdgpu_kmoddir}/amdgpu.%{_ko}
