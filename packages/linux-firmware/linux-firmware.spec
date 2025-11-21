%global debug_package %{nil}

%global fwdir %{_cross_libdir}/firmware

# Many of the firmware files have specialized binary formats that are not supported
# by the strip binary used in __spec_install_post macro. Work around build failures
# by skipping striping.
%global __strip /usr/bin/true

Name: %{_cross_os}linux-firmware
Version: 20230625
Release: 1%{?dist}
Summary: Firmware files used by the Linux kernel
# The following list of SPDX identifiers was constructed with help of scancode
# tooling and has turned up the following licenses for different drivers by
# checking the different LICENCE/LICENSE files and the licenses in WHENCE:
# * BSD-Source-Code - myri10ge
# * LicenseRef-scancode-chelsio-linux-firmware - cxgb4
# * LicenseRef-scancode-qlogic-firmware - netxen_nic
# * LicenseRef-scancode-intel - i915, ice
# * LicenseRef-scancode-proprietary-license - bnx2x, qed
# * LicenseRef-scancode-free-unknown - tg3
License: GPL-1.0-or-later AND GPL-2.0-or-later AND BSD-Source-Code AND LicenseRef-scancode-chelsio-linux-firmware AND LicenseRef-scancode-qlogic-firmware AND LicenseRef-scancode-intel AND LicenseRef-scancode-proprietary-license AND LicenseRef-scancode-free-unknown
URL: https://www.kernel.org/

Source0: https://www.kernel.org/pub/linux/kernel/firmware/linux-firmware-%{version}.tar.xz
Source1: https://www.kernel.org/pub/linux/kernel/firmware/linux-firmware-%{version}.tar.sign
Source2: gpgkey-4CDE8575E547BF835FE15807A31B6BD72486CFD6.asc

Patch0001: 0001-linux-firmware-snd-remove-firmware-for-snd-audio-dev.patch
Patch0002: 0002-linux-firmware-video-Remove-firmware-for-video-broad.patch
Patch0003: 0003-linux-firmware-bt-wifi-Remove-firmware-for-Bluetooth.patch
Patch0004: 0004-linux-firmware-scsi-Remove-firmware-for-SCSI-devices.patch
Patch0005: 0005-linux-firmware-usb-remove-firmware-for-USB-Serial-PC.patch
Patch0006: 0006-linux-firmware-ethernet-Remove-firmware-for-ethernet.patch
Patch0007: 0007-linux-firmware-Remove-firmware-for-Accelarator-devic.patch
Patch0008: 0008-linux-firmware-gpu-Remove-firmware-for-GPU-devices.patch
Patch0009: 0009-linux-firmware-various-Remove-firmware-for-various-d.patch
Patch0010: 0010-linux-firmware-amd-ucode-Remove-amd-microcode.patch

%description
%{summary}.

%prep
%{gpgverify} --data=<(xzcat %{S:0}) --signature=%{S:1} --keyring=%{S:2}
%autosetup -n linux-firmware-%{version} -p1

%build

%install
mkdir -p %{buildroot}/%{fwdir}
mkdir -p %{buildroot}/%{fwdir}/updates

# Use zstd compression for firmware files to reduce size on disk. This relies on
# kernel support through FW_LOADER_COMPRESS (and FW_LOADER_COMPRESS_ZSTD for kernels >=5.19)
make DESTDIR=%{buildroot}/ FIRMWAREDIR=%{fwdir} install-zst

%files
%dir %{fwdir}
%dir %{fwdir}/updates

# Network firmware - Broadcom NetXtreme II (bnx2x)
%dir %{fwdir}/bnx2x
%{fwdir}/bnx2x/bnx2x-e1-7.13.1.0.fw.zst
%{fwdir}/bnx2x/bnx2x-e1-7.13.11.0.fw.zst
%{fwdir}/bnx2x/bnx2x-e1-7.13.15.0.fw.zst
%{fwdir}/bnx2x/bnx2x-e1-7.13.21.0.fw.zst
%{fwdir}/bnx2x/bnx2x-e1h-7.13.1.0.fw.zst
%{fwdir}/bnx2x/bnx2x-e1h-7.13.11.0.fw.zst
%{fwdir}/bnx2x/bnx2x-e1h-7.13.15.0.fw.zst
%{fwdir}/bnx2x/bnx2x-e1h-7.13.21.0.fw.zst
%{fwdir}/bnx2x/bnx2x-e2-7.13.1.0.fw.zst
%{fwdir}/bnx2x/bnx2x-e2-7.13.11.0.fw.zst
%{fwdir}/bnx2x/bnx2x-e2-7.13.15.0.fw.zst
%{fwdir}/bnx2x/bnx2x-e2-7.13.21.0.fw.zst

# Network firmware - Chelsio T4/T5/T6 (cxgb4)
%dir %{fwdir}/cxgb4
%dir %{fwdir}/cxgb4/configs
%{fwdir}/cxgb4/aq1202_fw.cld.zst
%{fwdir}/cxgb4/bcm8483.bin.zst
%{fwdir}/cxgb4/configs/t4-config-default.txt.zst
%{fwdir}/cxgb4/configs/t5-config-default.txt.zst
%{fwdir}/cxgb4/configs/t5-config-hashfilter.txt.zst
%{fwdir}/cxgb4/configs/t6-config-default.txt.zst
%{fwdir}/cxgb4/configs/t6-config-hashfilter.txt.zst
%{fwdir}/cxgb4/t4-config.txt.zst
%{fwdir}/cxgb4/t4fw-1.14.4.0.bin.zst
%{fwdir}/cxgb4/t4fw-1.15.37.0.bin.zst
%{fwdir}/cxgb4/t4fw-1.27.3.0.bin.zst
%{fwdir}/cxgb4/t4fw.bin.zst
%{fwdir}/cxgb4/t5-config.txt.zst
%{fwdir}/cxgb4/t5fw-1.14.4.0.bin.zst
%{fwdir}/cxgb4/t5fw-1.15.37.0.bin.zst
%{fwdir}/cxgb4/t5fw-1.27.3.0.bin.zst
%{fwdir}/cxgb4/t5fw.bin.zst
%{fwdir}/cxgb4/t6-config.txt.zst
%{fwdir}/cxgb4/t6fw-1.27.3.0.bin.zst
%{fwdir}/cxgb4/t6fw.bin.zst

# Network firmware - Myricom 10G (myri10ge)
%{fwdir}/myri10ge_eth_big_z8e.dat.zst
%{fwdir}/myri10ge_eth_z8e.dat.zst
%{fwdir}/myri10ge_ethp_big_z8e.dat.zst
%{fwdir}/myri10ge_ethp_z8e.dat.zst
%{fwdir}/myri10ge_rss_eth_big_z8e.dat.zst
%{fwdir}/myri10ge_rss_eth_z8e.dat.zst
%{fwdir}/myri10ge_rss_ethp_big_z8e.dat.zst
%{fwdir}/myri10ge_rss_ethp_z8e.dat.zst

# Network firmware - NetXen/QLogic
%{fwdir}/phanfw.bin.zst

# Network firmware - QLogic FastLinQ (qed)
%dir %{fwdir}/qed
%{fwdir}/qed/qed_init_values-8.10.9.0.bin.zst
%{fwdir}/qed/qed_init_values-8.14.6.0.bin.zst
%{fwdir}/qed/qed_init_values-8.18.9.0.bin.zst
%{fwdir}/qed/qed_init_values-8.20.0.0.bin.zst
%{fwdir}/qed/qed_init_values-8.30.12.0.bin.zst
%{fwdir}/qed/qed_init_values-8.33.12.0.bin.zst
%{fwdir}/qed/qed_init_values-8.37.7.0.bin.zst
%{fwdir}/qed/qed_init_values-8.40.33.0.bin.zst
%{fwdir}/qed/qed_init_values_zipped-8.10.10.0.bin.zst
%{fwdir}/qed/qed_init_values_zipped-8.10.5.0.bin.zst
%{fwdir}/qed/qed_init_values_zipped-8.15.3.0.bin.zst
%{fwdir}/qed/qed_init_values_zipped-8.20.0.0.bin.zst
%{fwdir}/qed/qed_init_values_zipped-8.33.1.0.bin.zst
%{fwdir}/qed/qed_init_values_zipped-8.33.11.0.bin.zst
%{fwdir}/qed/qed_init_values_zipped-8.37.2.0.bin.zst
%{fwdir}/qed/qed_init_values_zipped-8.37.7.0.bin.zst
%{fwdir}/qed/qed_init_values_zipped-8.4.2.0.bin.zst
%{fwdir}/qed/qed_init_values_zipped-8.42.2.0.bin.zst
%{fwdir}/qed/qed_init_values_zipped-8.59.1.0.bin.zst
%{fwdir}/qed/qed_init_values_zipped-8.7.3.0.bin.zst

# Network firmware - Broadcom Tigon3 (tg3)
%dir %{fwdir}/tigon
%{fwdir}/tigon/tg3.bin.zst
%{fwdir}/tigon/tg357766.bin.zst
%{fwdir}/tigon/tg3_tso.bin.zst
%{fwdir}/tigon/tg3_tso5.bin.zst

# Intel i915 Graphics firmware
%dir %{fwdir}/i915
%{fwdir}/i915/adlp_dmc.bin.zst
%{fwdir}/i915/adlp_dmc_ver2_09.bin.zst
%{fwdir}/i915/adlp_dmc_ver2_10.bin.zst
%{fwdir}/i915/adlp_dmc_ver2_12.bin.zst
%{fwdir}/i915/adlp_dmc_ver2_14.bin.zst
%{fwdir}/i915/adlp_dmc_ver2_16.bin.zst
%{fwdir}/i915/adlp_guc_62.0.3.bin.zst
%{fwdir}/i915/adlp_guc_69.0.3.bin.zst
%{fwdir}/i915/adlp_guc_70.1.1.bin.zst
%{fwdir}/i915/adlp_guc_70.bin.zst
%{fwdir}/i915/adls_dmc_ver2_01.bin.zst
%{fwdir}/i915/bxt_dmc_ver1.bin.zst
%{fwdir}/i915/bxt_dmc_ver1_07.bin.zst
%{fwdir}/i915/bxt_guc_32.0.3.bin.zst
%{fwdir}/i915/bxt_guc_33.0.0.bin.zst
%{fwdir}/i915/bxt_guc_49.0.1.bin.zst
%{fwdir}/i915/bxt_guc_62.0.0.bin.zst
%{fwdir}/i915/bxt_guc_69.0.3.bin.zst
%{fwdir}/i915/bxt_guc_70.1.1.bin.zst
%{fwdir}/i915/bxt_guc_ver8_7.bin.zst
%{fwdir}/i915/bxt_guc_ver9_29.bin.zst
%{fwdir}/i915/bxt_huc_2.0.0.bin.zst
%{fwdir}/i915/bxt_huc_ver01_07_1398.bin.zst
%{fwdir}/i915/bxt_huc_ver01_8_2893.bin.zst
%{fwdir}/i915/cml_guc_33.0.0.bin.zst
%{fwdir}/i915/cml_guc_49.0.1.bin.zst
%{fwdir}/i915/cml_guc_62.0.0.bin.zst
%{fwdir}/i915/cml_guc_69.0.3.bin.zst
%{fwdir}/i915/cml_guc_70.1.1.bin.zst
%{fwdir}/i915/cml_huc_4.0.0.bin.zst
%{fwdir}/i915/cnl_dmc_ver1_06.bin.zst
%{fwdir}/i915/cnl_dmc_ver1_07.bin.zst
%{fwdir}/i915/dg1_dmc_ver2_02.bin.zst
%{fwdir}/i915/dg1_guc_49.0.1.bin.zst
%{fwdir}/i915/dg1_guc_62.0.0.bin.zst
%{fwdir}/i915/dg1_guc_69.0.3.bin.zst
%{fwdir}/i915/dg1_guc_70.1.1.bin.zst
%{fwdir}/i915/dg1_guc_70.bin.zst
%{fwdir}/i915/dg1_huc.bin.zst
%{fwdir}/i915/dg1_huc_7.7.1.bin.zst
%{fwdir}/i915/dg1_huc_7.9.3.bin.zst
%{fwdir}/i915/dg2_dmc_ver2_06.bin.zst
%{fwdir}/i915/dg2_dmc_ver2_07.bin.zst
%{fwdir}/i915/dg2_dmc_ver2_08.bin.zst
%{fwdir}/i915/dg2_guc_70.1.2.bin.zst
%{fwdir}/i915/dg2_guc_70.4.1.bin.zst
%{fwdir}/i915/dg2_guc_70.bin.zst
%{fwdir}/i915/dg2_huc_gsc.bin.zst
%{fwdir}/i915/ehl_guc_33.0.4.bin.zst
%{fwdir}/i915/ehl_guc_49.0.1.bin.zst
%{fwdir}/i915/ehl_guc_62.0.0.bin.zst
%{fwdir}/i915/ehl_guc_69.0.3.bin.zst
%{fwdir}/i915/ehl_guc_70.1.1.bin.zst
%{fwdir}/i915/ehl_huc_9.0.0.bin.zst
%{fwdir}/i915/glk_dmc_ver1_04.bin.zst
%{fwdir}/i915/glk_guc_32.0.3.bin.zst
%{fwdir}/i915/glk_guc_33.0.0.bin.zst
%{fwdir}/i915/glk_guc_49.0.1.bin.zst
%{fwdir}/i915/glk_guc_62.0.0.bin.zst
%{fwdir}/i915/glk_guc_69.0.3.bin.zst
%{fwdir}/i915/glk_guc_70.1.1.bin.zst
%{fwdir}/i915/glk_huc_4.0.0.bin.zst
%{fwdir}/i915/glk_huc_ver03_01_2893.bin.zst
%{fwdir}/i915/icl_dmc_ver1_07.bin.zst
%{fwdir}/i915/icl_dmc_ver1_09.bin.zst
%{fwdir}/i915/icl_guc_32.0.3.bin.zst
%{fwdir}/i915/icl_guc_33.0.0.bin.zst
%{fwdir}/i915/icl_guc_49.0.1.bin.zst
%{fwdir}/i915/icl_guc_62.0.0.bin.zst
%{fwdir}/i915/icl_guc_69.0.3.bin.zst
%{fwdir}/i915/icl_guc_70.1.1.bin.zst
%{fwdir}/i915/icl_huc_9.0.0.bin.zst
%{fwdir}/i915/icl_huc_ver8_4_3238.bin.zst
%{fwdir}/i915/kbl_dmc_ver1.bin.zst
%{fwdir}/i915/kbl_dmc_ver1_01.bin.zst
%{fwdir}/i915/kbl_dmc_ver1_04.bin.zst
%{fwdir}/i915/kbl_guc_32.0.3.bin.zst
%{fwdir}/i915/kbl_guc_33.0.0.bin.zst
%{fwdir}/i915/kbl_guc_49.0.1.bin.zst
%{fwdir}/i915/kbl_guc_62.0.0.bin.zst
%{fwdir}/i915/kbl_guc_69.0.3.bin.zst
%{fwdir}/i915/kbl_guc_70.1.1.bin.zst
%{fwdir}/i915/kbl_guc_ver9_14.bin.zst
%{fwdir}/i915/kbl_guc_ver9_39.bin.zst
%{fwdir}/i915/kbl_huc_4.0.0.bin.zst
%{fwdir}/i915/kbl_huc_ver02_00_1810.bin.zst
%{fwdir}/i915/mtl_dmc.bin.zst
%{fwdir}/i915/mtl_dmc_ver2_10.bin.zst
%{fwdir}/i915/mtl_guc_70.bin.zst
%{fwdir}/i915/mtl_huc_gsc.bin.zst
%{fwdir}/i915/rkl_dmc_ver2_02.bin.zst
%{fwdir}/i915/rkl_dmc_ver2_03.bin.zst
%{fwdir}/i915/skl_dmc_ver1.bin.zst
%{fwdir}/i915/skl_dmc_ver1_23.bin.zst
%{fwdir}/i915/skl_dmc_ver1_26.bin.zst
%{fwdir}/i915/skl_dmc_ver1_27.bin.zst
%{fwdir}/i915/skl_guc_32.0.3.bin.zst
%{fwdir}/i915/skl_guc_33.0.0.bin.zst
%{fwdir}/i915/skl_guc_49.0.1.bin.zst
%{fwdir}/i915/skl_guc_62.0.0.bin.zst
%{fwdir}/i915/skl_guc_69.0.3.bin.zst
%{fwdir}/i915/skl_guc_70.1.1.bin.zst
%{fwdir}/i915/skl_guc_ver1.bin.zst
%{fwdir}/i915/skl_guc_ver4.bin.zst
%{fwdir}/i915/skl_guc_ver6.bin.zst
%{fwdir}/i915/skl_guc_ver6_1.bin.zst
%{fwdir}/i915/skl_guc_ver9_33.bin.zst
%{fwdir}/i915/skl_huc_2.0.0.bin.zst
%{fwdir}/i915/skl_huc_ver01_07_1398.bin.zst
%{fwdir}/i915/tgl_dmc_ver2_04.bin.zst
%{fwdir}/i915/tgl_dmc_ver2_06.bin.zst
%{fwdir}/i915/tgl_dmc_ver2_08.bin.zst
%{fwdir}/i915/tgl_dmc_ver2_12.bin.zst
%{fwdir}/i915/tgl_guc_35.2.0.bin.zst
%{fwdir}/i915/tgl_guc_49.0.1.bin.zst
%{fwdir}/i915/tgl_guc_62.0.0.bin.zst
%{fwdir}/i915/tgl_guc_69.0.3.bin.zst
%{fwdir}/i915/tgl_guc_70.1.1.bin.zst
%{fwdir}/i915/tgl_guc_70.bin.zst
%{fwdir}/i915/tgl_huc.bin.zst
%{fwdir}/i915/tgl_huc_7.0.12.bin.zst
%{fwdir}/i915/tgl_huc_7.0.3.bin.zst
%{fwdir}/i915/tgl_huc_7.5.0.bin.zst
%{fwdir}/i915/tgl_huc_7.9.3.bin.zst

# Intel ice (E810) network firmware
%dir %{fwdir}/intel
%dir %{fwdir}/intel/ice
%dir %{fwdir}/intel/ice/ddp
%dir %{fwdir}/intel/ice/ddp-comms
%dir %{fwdir}/intel/ice/ddp-wireless_edge
%{fwdir}/intel/ice/ddp-comms/ice_comms-1.3.40.0.pkg.zst
%{fwdir}/intel/ice/ddp-wireless_edge/ice_wireless_edge-1.3.10.0.pkg.zst
%{fwdir}/intel/ice/ddp/ice-1.3.30.0.pkg.zst
%{fwdir}/intel/ice/ddp/ice.pkg.zst

# License files
%license GPL-2
%license GPL-3
%license LICENCE.chelsio_firmware
%license LICENCE.myri10ge_firmware
%license LICENCE.phanfw
%license LICENSE.i915
%license LICENSE.ice
%license LICENSE.ice_enhanced
%license WHENCE
%{_cross_attribution_file}
