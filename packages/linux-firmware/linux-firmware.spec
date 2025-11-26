%global debug_package %{nil}

%global fwdir %{_cross_libdir}/firmware

# Many of the firmware files have specialized binary formats that are not supported
# by the strip binary used in __spec_install_post macro. Work around build failures
# by skipping striping.
%global __strip /usr/bin/true

Name: %{_cross_os}linux-firmware
Version: 20251111
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

%description
%{summary}.

%package amdgpu
Summary: Firmware for amdgpu drivers
License: GPL-1.0-or-later AND GPL-2.0-or-later

%description amdgpu
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
install -d %{buildroot}/%{fwdir}
./copy-firmware.sh --zstd %{buildroot}/%{fwdir}

%files
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
%dir %{fwdir}
%dir %{fwdir}/updates

# Root-level firmware files
%{fwdir}/myri10ge_eth_big_z8e.dat.zst
%{fwdir}/myri10ge_eth_z8e.dat.zst
%{fwdir}/myri10ge_ethp_big_z8e.dat.zst
%{fwdir}/myri10ge_ethp_z8e.dat.zst
%{fwdir}/myri10ge_rss_eth_big_z8e.dat.zst
%{fwdir}/myri10ge_rss_eth_z8e.dat.zst
%{fwdir}/myri10ge_rss_ethp_big_z8e.dat.zst
%{fwdir}/myri10ge_rss_ethp_z8e.dat.zst
%{fwdir}/phanfw.bin.zst

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
%{fwdir}/cxgb4/t4fw-1.27.5.0.bin.zst
%{fwdir}/cxgb4/t4fw.bin.zst
%{fwdir}/cxgb4/t5-config.txt.zst
%{fwdir}/cxgb4/t5fw-1.14.4.0.bin.zst
%{fwdir}/cxgb4/t5fw-1.15.37.0.bin.zst
%{fwdir}/cxgb4/t5fw-1.27.5.0.bin.zst
%{fwdir}/cxgb4/t5fw.bin.zst
%{fwdir}/cxgb4/t6-config.txt.zst
%{fwdir}/cxgb4/t6fw-1.27.5.0.bin.zst
%{fwdir}/cxgb4/t6fw.bin.zst

# Graphics firmware - Intel i915
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
%{fwdir}/i915/bxt_dmc_ver1_07.bin.zst
%{fwdir}/i915/bxt_dmc_ver1.bin.zst
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
%{fwdir}/i915/bmg_dmc.bin.zst
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
%{fwdir}/i915/mtl_gsc_1.bin.zst
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
%{fwdir}/i915/xe2lpd_dmc.bin.zst
%{fwdir}/i915/xe3lpd_*.bin.zst

# Intel network firmware
%dir %{fwdir}/intel
%dir %{fwdir}/intel/ice
%dir %{fwdir}/intel/ice/ddp
%dir %{fwdir}/intel/ice/ddp-comms
%dir %{fwdir}/intel/ice/ddp-wireless_edge
%{fwdir}/intel/ice/ddp-comms/ice_comms-1.3.55.0.pkg.zst
%{fwdir}/intel/ice/ddp-wireless_edge/ice_wireless_edge-1.3.23.0.pkg.zst
%{fwdir}/intel/ice/ddp/ice-1.3.43.0.pkg.zst
%{fwdir}/intel/ice/ddp/ice.pkg.zst

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

# === Root-level file pattern excludes ===
%exclude %{fwdir}/*.fw.zst
%exclude %{fwdir}/*.hex.zst
%exclude %{fwdir}/*.inp.zst
%exclude %{fwdir}/*.dlmem.zst
%exclude %{fwdir}/*.ucode.zst
%exclude %{fwdir}/*.pnvm.zst

# === Directory excludes ===
%exclude %{fwdir}/3com
%exclude %{fwdir}/HP
%exclude %{fwdir}/LENOVO
%exclude %{fwdir}/acenic
%exclude %{fwdir}/adaptec
%exclude %{fwdir}/advansys
%exclude %{fwdir}/aeonsemi
%exclude %{fwdir}/airoha
%exclude %{fwdir}/amd
%exclude %{fwdir}/amd-ucode
%exclude %{fwdir}/amdgpu
%exclude %{fwdir}/amdnpu
%exclude %{fwdir}/amdtee
%exclude %{fwdir}/amlogic
%exclude %{fwdir}/amphion
%exclude %{fwdir}/ar3k
%exclude %{fwdir}/arm
%exclude %{fwdir}/ath10k
%exclude %{fwdir}/ath11k
%exclude %{fwdir}/ath12k
%exclude %{fwdir}/ath6k
%exclude %{fwdir}/ath9k_htc
%exclude %{fwdir}/atmel
%exclude %{fwdir}/atusb
%exclude %{fwdir}/av7110
%exclude %{fwdir}/bnx2
%exclude %{fwdir}/brcm
%exclude %{fwdir}/cadence
%exclude %{fwdir}/cavium
%exclude %{fwdir}/cirrus
%exclude %{fwdir}/cis
%exclude %{fwdir}/cnm
%exclude %{fwdir}/cpia2
%exclude %{fwdir}/cxgb3
%exclude %{fwdir}/cypress
%exclude %{fwdir}/dabusb
%exclude %{fwdir}/dell
%exclude %{fwdir}/dpaa2
%exclude %{fwdir}/dsp56k
%exclude %{fwdir}/e100
%exclude %{fwdir}/edgeport
%exclude %{fwdir}/emi26
%exclude %{fwdir}/emi62
%exclude %{fwdir}/ene-ub6250
%exclude %{fwdir}/ess
%exclude %{fwdir}/go7007
%exclude %{fwdir}/imx
%exclude %{fwdir}/inside-secure
%exclude %{fwdir}/isci
%exclude %{fwdir}/ixp4xx
%exclude %{fwdir}/kaweth
%exclude %{fwdir}/keyspan
%exclude %{fwdir}/keyspan_pda
%exclude %{fwdir}/korg
%exclude %{fwdir}/libertas
%exclude %{fwdir}/liquidio
%exclude %{fwdir}/matrox
%exclude %{fwdir}/mediatek
%exclude %{fwdir}/mellanox
%exclude %{fwdir}/meson
%exclude %{fwdir}/microchip
%exclude %{fwdir}/moxa
%exclude %{fwdir}/mrvl
%exclude %{fwdir}/mts_*.fw.zst
%exclude %{fwdir}/mwl8k
%exclude %{fwdir}/mwlwifi
%exclude %{fwdir}/myricom
%exclude %{fwdir}/netronome
%exclude %{fwdir}/nvidia
%exclude %{fwdir}/nxp
%exclude %{fwdir}/ositech
%exclude %{fwdir}/powervr
%exclude %{fwdir}/qat_*.bin.zst
%exclude %{fwdir}/qca
%exclude %{fwdir}/qcom
%exclude %{fwdir}/qlogic
%exclude %{fwdir}/ql*_fw.bin.zst
%exclude %{fwdir}/r128
%exclude %{fwdir}/r8a779x_*.dlmem.zst
%exclude %{fwdir}/radeon
%exclude %{fwdir}/realtek
%exclude %{fwdir}/rockchip
%exclude %{fwdir}/rp2.fw.zst
%exclude %{fwdir}/rsi
%exclude %{fwdir}/rsi_*.fw.zst
%exclude %{fwdir}/rt*.bin.zst
%exclude %{fwdir}/rtl_bt
%exclude %{fwdir}/rtl_nic
%exclude %{fwdir}/rtlwifi
%exclude %{fwdir}/rtw88
%exclude %{fwdir}/rtw89
%exclude %{fwdir}/s2250*.fw.zst
%exclude %{fwdir}/s5p-mfc*.fw.zst
%exclude %{fwdir}/sb16
%exclude %{fwdir}/sdd_*.bin.zst
%exclude %{fwdir}/slicoss
%exclude %{fwdir}/sms1xxx*.fw.zst
%exclude %{fwdir}/sun
%exclude %{fwdir}/sxg
%exclude %{fwdir}/tdmb_*.inp.zst
%exclude %{fwdir}/tehuti
%exclude %{fwdir}/ti
%exclude %{fwdir}/ti-connectivity
%exclude %{fwdir}/ti-keystone
%exclude %{fwdir}/ti_*.fw.zst
%exclude %{fwdir}/tlg2300_firmware.bin.zst
%exclude %{fwdir}/ttusb-budget
%exclude %{fwdir}/ueagle-atm
%exclude %{fwdir}/usbdux*.bin.zst
%exclude %{fwdir}/v4l-*.fw.zst
%exclude %{fwdir}/vicam
%exclude %{fwdir}/vntwusb.fw.zst
%exclude %{fwdir}/vpu_*.bin.zst
%exclude %{fwdir}/vxge
%exclude %{fwdir}/wfx
%exclude %{fwdir}/whiteheat*.fw.zst
%exclude %{fwdir}/wil6210*.zst
%exclude %{fwdir}/wsm_22.bin.zst
%exclude %{fwdir}/xe
%exclude %{fwdir}/yam
%exclude %{fwdir}/yamaha

# === Specific file pattern excludes ===

# Exclude Intel WiFi firmware
%exclude %{fwdir}/iwlwifi-*.ucode.zst
%exclude %{fwdir}/iwlwifi-*.pnvm.zst

# Exclude other wireless firmware
%exclude %{fwdir}/ar*.fw.zst
%exclude %{fwdir}/ar*.bin.zst
%exclude %{fwdir}/ath3k-1.fw.zst
%exclude %{fwdir}/htc_*.fw.zst
%exclude %{fwdir}/carl9170-1.fw.zst
%exclude %{fwdir}/mt*.bin.zst
%exclude %{fwdir}/lbtf_usb.bin.zst
%exclude %{fwdir}/lgs8g75.fw.zst
%exclude %{fwdir}/lt9611uxc_fw.bin.zst

# Exclude misc firmware
%exclude %{fwdir}/as102_*.hex.zst
%exclude %{fwdir}/bmi260-init-data.fw.zst
%exclude %{fwdir}/cbfw-*.bin.zst
%exclude %{fwdir}/ct2fw-*.bin.zst
%exclude %{fwdir}/ctfw-*.bin.zst
%exclude %{fwdir}/ctefx.bin.zst
%exclude %{fwdir}/ctspeq.bin.zst
%exclude %{fwdir}/cs42l43.bin.zst
%exclude %{fwdir}/dvb*.fw.zst
%exclude %{fwdir}/dvb*.inp.zst
%exclude %{fwdir}/f2255usb.bin.zst
%exclude %{fwdir}/hfi1_*.fw.zst
%exclude %{fwdir}/isdbt_*.inp.zst
%exclude %{fwdir}/agere_*.bin.zst
%exclude %{fwdir}/tsse_firmware.bin.zst
%exclude %{fwdir}/cmmb_*.inp.zst

# Exclude TAS and TIAS firmware
%exclude %{fwdir}/TAS*.bin.zst
%exclude %{fwdir}/TIAS*.bin.zst
%exclude %{fwdir}/TXNW*.bin.zst
%exclude %{fwdir}/INT8866RCA2.bin.zst

# Exclude additional firmware patterns
%exclude %{fwdir}/a300_*.fw.zst

# Exclude Intel firmware directories and files
%exclude %{fwdir}/intel/fw_sst_0f28.bin-48kHz_i2s_master.zst
%exclude %{fwdir}/intel/avs
%exclude %{fwdir}/intel/catpt
%exclude %{fwdir}/intel/dsp_fw_*.bin.zst
%exclude %{fwdir}/intel/fw_sst_*.bin.zst
%exclude %{fwdir}/intel/ibt-*.ddc.zst
%exclude %{fwdir}/intel/ibt-*.sfi.zst
%exclude %{fwdir}/intel/ibt-*.bseq.zst
%exclude %{fwdir}/intel/ice/ddp-lag
%exclude %{fwdir}/intel/ipu
%exclude %{fwdir}/intel/ish
%exclude %{fwdir}/intel/iwlwifi
%exclude %{fwdir}/intel/qat
%exclude %{fwdir}/intel/vpu
%exclude %{fwdir}/intel/vsc
%exclude %{fwdir}/intel/IntcSST2.bin.zst
%exclude %{fwdir}/intel/ipu3-fw.bin.zst
%exclude %{fwdir}/intel/irci_*.bin.zst

%files amdgpu
%license LICENSE.amdgpu
%dir %{fwdir}/amdgpu
%{fwdir}/amdgpu/*
