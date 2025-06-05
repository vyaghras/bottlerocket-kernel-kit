TOP := $(dir $(abspath $(firstword $(MAKEFILE_LIST))))
TOOLS_DIR := $(TOP)tools
TWOLITER_DIR := $(TOOLS_DIR)/twoliter
TWOLITER := $(TWOLITER_DIR)/twoliter
CARGO_HOME := $(TOP).cargo
KERNEL_CONFIG_SCRIPT := $(TOOLS_DIR)/latest-kernel-full-config.sh

TWOLITER_VERSION ?= "0.11.0"
TWOLITER_SHA256_AARCH64 ?= "418f762baf1698472af697d40bc4877dd5fa0b033fda31250b3d38e02d72a289"
TWOLITER_SHA256_X86_64 ?= "d5842179c445b5a64ee2f80d42b370b61f6272cdc1cb4a8c1b4b0fdffef22bec"
KIT ?= bottlerocket-kernel-kit
UNAME_ARCH = $(shell uname -m)
ARCH ?= $(UNAME_ARCH)
VENDOR ?= bottlerocket

ifeq ($(UNAME_ARCH), aarch64)
	TWOLITER_SHA256=$(TWOLITER_SHA256_AARCH64)
else
	TWOLITER_SHA256=$(TWOLITER_SHA256_X86_64)
endif


all: build

merge-kernel-configs:
	@echo "Validating parameters for merge-kernel-configs..."
	@usage_msg="Usage: make merge-kernel-configs RPM_FILE=/path/to/kernel-source.rpm SDK_IMAGE=image:tag KVER=x.y"; \
	validate_param() { \
		param_name="$${1}"; param_value="$${2}"; error_msg="$${3}"; \
		[ -n "$${param_value}" ] || { echo "Error: $${error_msg}"; echo "$${usage_msg}"; exit 1; }; \
	}; \
	validate_param "SDK_IMAGE" "$(SDK_IMAGE)" "SDK_IMAGE parameter is required"; \
	validate_param "KVER" "$(KVER)" "KVER parameter is required"; \
	echo "All parameter checks passed. Merging kernel configs for version $(KVER)..."

	@tmpdir=$$(mktemp -d); \
	if [ $$? -ne 0 ]; then \
		echo "Error: Failed to create temporary directory"; \
		exit 1; \
	fi; \
	cp "$(RPM_FILE)" "$${tmpdir}/kernel-source.rpm"; \
	if [ $$? -ne 0 ]; then \
		echo "Error: Failed to copy RPM file to temporary directory"; \
		rm -rf "$${tmpdir}"; \
		exit 1; \
	fi; \
	cd packages/kernel-$(KVER) && \
	docker run --rm \
		-v "$(PWD)/packages/kernel-$(KVER)/":/kernel-package \
		-v "$${tmpdir}":/work \
		-v "$(PWD)/packages/microcode/":/microcode \
		-v "$(PWD)/tools/latest-kernel-full-config.sh":/latest-kernel-full-config.sh \
		--user "$$(id -u):$$(id -g)" \
		--name "kernel-$(KVER)-inner-full" \
		"$(SDK_IMAGE)" \
		bash -c "source /latest-kernel-full-config.sh && inner_full_config"; \
	docker_exit_code=$$?; \
	rm -rf "$${tmpdir}"; \
	if [ $$docker_exit_code -ne 0 ]; then \
		echo "Error: Docker container execution failed with exit code $$docker_exit_code"; \
		exit $$docker_exit_code; \
	fi; \
	echo "Successfully merged kernel configs for version $(KVER)"

full-config:
	@if [ -z "$(RPM_FILE)" ]; then \
		echo "Error: RPM_FILE parameter is required"; \
		echo "Usage: make full-config RPM_FILE=/path/to/kernel-source.rpm"; \
		exit 1; \
	fi; \
	echo "Checking kernel configuration dependencies..."; \
	source $(KERNEL_CONFIG_SCRIPT) && check_dependencies; \
	echo "All dependencies are available."; \
	rpm_file=$$(realpath "$(RPM_FILE)"); \
	if [ ! -f "$${rpm_file}" ]; then \
		echo "Error: RPM file not found: $${rpm_file}"; \
		exit 1; \
	fi; \
	sdk_image=$$(source $(KERNEL_CONFIG_SCRIPT) && resolve_bottlerocket_sdk); \
	kver=$$(rpm --query --nosignature --queryformat '%{VERSION}' "$${rpm_file}" | sed 's/\.[^.]*$$//'); \
	echo "Processing kernel version: $${kver}"; \
	echo "Using SDK image: $${sdk_image}"; \
	echo "Using RPM file: $${rpm_file}"; \
	$(MAKE) merge-kernel-configs RPM_FILE="$${rpm_file}" SDK_IMAGE="$${sdk_image}" KVER="$${kver}"

prep:
	@mkdir -p $(TWOLITER_DIR)
	@mkdir -p $(CARGO_HOME)
	@$(TOOLS_DIR)/install-twoliter.sh \
		--repo "https://github.com/bottlerocket-os/twoliter" \
		--version v$(TWOLITER_VERSION) \
		--directory $(TWOLITER_DIR) \
		--reuse-existing-install \
		--allow-binary-install $(TWOLITER_SHA256) \
		--allow-from-source

update: prep
	@$(TWOLITER) update

fetch: prep
	@$(TWOLITER) fetch --arch $(ARCH)

build: fetch
	@$(TWOLITER) build kit $(KIT) --arch $(ARCH)

publish: prep
	@$(TWOLITER) publish kit $(KIT) $(VENDOR)

TWOLITER_MAKE = $(TWOLITER) make --cargo-home $(CARGO_HOME) --arch $(ARCH)

# Treat any targets after "make twoliter" as arguments to "twoliter make".
ifeq (twoliter,$(firstword $(MAKECMDGOALS)))
  TWOLITER_MAKE_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(TWOLITER_MAKE_ARGS):;@:)
endif

# Transform "make twoliter" into "twoliter make", for access to tasks that are
# only available through the embedded Makefile.toml.
twoliter: prep
	@$(TWOLITER_MAKE) $(TWOLITER_MAKE_ARGS)

.PHONY: prep update fetch build publish twoliter merge-kernel-configs full-config
