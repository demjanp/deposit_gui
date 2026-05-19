#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

DIST_DIR="${REPO_ROOT}/dist"
APP_PATH="${DIST_DIR}/Deposit.app"
PKGPROJ_PATH="${DIST_DIR}/deposit_gui.pkgproj"
MACOS_APP_SIGN_IDENTITY="Developer ID Application: DEMJAN & DRZIK s. r. o. (Z43AG8H4KQ)"
MACOS_INSTALLER_SIGN_IDENTITY="Developer ID Installer: DEMJAN & DRZIK s. r. o. (Z43AG8H4KQ)"

require_command() {
	local command_name="$1"

	if ! command -v "${command_name}" >/dev/null 2>&1; then
		echo "${command_name} is required to build the signed macOS installer." >&2
		exit 1
	fi
}

require_signing_identity() {
	local identity="$1"

	if ! security find-identity -v | grep -F -- "${identity}" >/dev/null 2>&1; then
		if security find-certificate -c "${identity}" >/dev/null 2>&1; then
			echo "Certificate found, but no valid signing identity is available: ${identity}" >&2
			echo "Import the matching private key, typically by importing a .p12 exported from Xcode or Keychain Access." >&2
			exit 1
		fi

		echo "Signing identity not found in the current keychain: ${identity}" >&2
		exit 1
	fi
}

paths_deepest_first() {
	awk '{ print length($0), $0 }' | sort -rn | cut -d ' ' -f 2-
}

remove_codesign_incompatible_duplicates() {
	local shapely_dylibs="${APP_PATH}/Contents/MacOS/shapely/.dylibs"

	if [[ -d "${shapely_dylibs}" ]]; then
		if [[ ! -f "${APP_PATH}/Contents/MacOS/libgeos.3.11.3.dylib" || ! -f "${APP_PATH}/Contents/MacOS/libgeos_c.1.17.3.dylib" ]]; then
			echo "Cannot remove ${shapely_dylibs}; expected top-level GEOS libraries are missing." >&2
			exit 1
		fi

		echo "Removing duplicate Shapely GEOS libraries that break app bundle signing: ${shapely_dylibs}"
		rm -rf "${shapely_dylibs}"
	fi
}

sign_payload_files() {
	local root="$1"
	local path

	find "${root}" -type f -print | paths_deepest_first | while IFS= read -r path; do
		echo "Signing app payload: ${path}"
		codesign --force --timestamp --sign "${MACOS_APP_SIGN_IDENTITY}" "${path}"
	done
}

sign_nested_bundles() {
	local root="$1"
	local path

	find "${root}" -type d \( -name "*.app" -o -name "*.appex" -o -name "*.bundle" -o -name "*.framework" -o -name "*.plugin" -o -name "*.xpc" \) -print \
		| paths_deepest_first \
		| while IFS= read -r path; do
			echo "Signing nested bundle: ${path}"
			codesign --force --timestamp --sign "${MACOS_APP_SIGN_IDENTITY}" "${path}"
		done
}

sign_app() {
	if [[ ! -d "${APP_PATH}" ]]; then
		echo "Expected app bundle was not created: ${APP_PATH}" >&2
		exit 1
	fi

	remove_codesign_incompatible_duplicates
	sign_payload_files "${APP_PATH}/Contents/MacOS"
	sign_nested_bundles "${APP_PATH}/Contents"

	echo "Signing app bundle: ${APP_PATH}"
	codesign --force --timestamp --sign "${MACOS_APP_SIGN_IDENTITY}" "${APP_PATH}"

	echo "Verifying app signature: ${APP_PATH}"
	codesign --verify --deep --strict --verbose=2 "${APP_PATH}"
}

assess_installer_package() {
	local signed_pkg="$1"
	local assessment_output

	if assessment_output="$(spctl -a -vv --type install "${signed_pkg}" 2>&1)"; then
		echo "${assessment_output}"
		return 0
	fi

	echo "${assessment_output}" >&2

	if grep -q "Unnotarized Developer ID" <<<"${assessment_output}"; then
		echo "Installer package is signed, but Gatekeeper rejected it because it is not notarized." >&2
		echo "This is expected for signing-only builds." >&2
		return 0
	fi

	return 1
}

build_signed_package() {
	local version_underscored="$1"
	local unsigned_pkg="${DIST_DIR}/Deposit_${version_underscored}.pkg"
	local signed_pkg="${DIST_DIR}/Deposit_${version_underscored}_signed.pkg"

	if [[ ! -f "${PKGPROJ_PATH}" ]]; then
		echo "Expected Packages project was not created: ${PKGPROJ_PATH}" >&2
		exit 1
	fi

	echo "Building unsigned installer package from ${PKGPROJ_PATH}"
	packagesbuild --build-folder "${DIST_DIR}" "${PKGPROJ_PATH}"

	if [[ ! -f "${unsigned_pkg}" ]]; then
		echo "Expected unsigned installer package was not created: ${unsigned_pkg}" >&2
		exit 1
	fi

	echo "Signing installer package: ${signed_pkg}"
	productsign --sign "${MACOS_INSTALLER_SIGN_IDENTITY}" "${unsigned_pkg}" "${signed_pkg}"

	echo "Verifying installer package signature: ${signed_pkg}"
	pkgutil --check-signature "${signed_pkg}"
	assess_installer_package "${signed_pkg}"
}

require_command brew
require_command codesign
require_command packagesbuild
require_command pkgutil
require_command productsign
require_command security
require_command spctl

require_signing_identity "${MACOS_APP_SIGN_IDENTITY}"
require_signing_identity "${MACOS_INSTALLER_SIGN_IDENTITY}"

rm -rf build
rm -rf "${DIST_DIR}"

if ! brew list graphviz >/dev/null 2>&1; then
	brew install graphviz
fi

source .venv/bin/activate

VERSION_UNDERSCORED="$(python - <<'PY'
from deposit_gui import __version__
print("_".join(__version__.split(".")))
PY
)"

if ! python -c "import pygraphviz" >/dev/null 2>&1; then
	bash scripts/install_pygraphviz.sh
fi

python installer_mac/make_pkgproj.py

python bin/update_imports.py installer_mac

pyinstaller --clean installer_mac/dep_gui.spec

find "${DIST_DIR}" -type d -name "__pycache__" -exec rm -r {} +

sign_app
build_signed_package "${VERSION_UNDERSCORED}"
