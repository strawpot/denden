#!/bin/sh
set -e

REPO="strawpot/denden"
BINARY_NAME="denden"

# Detect OS
OS=$(uname -s)
case "$OS" in
  Linux)  OS="linux" ;;
  Darwin) OS="darwin" ;;
  MINGW*|MSYS*|CYGWIN*) OS="windows" ;;
  *) echo "Unsupported OS: $OS" >&2; exit 1 ;;
esac

# Default install directory — current working directory.
# When run by strawhub, INSTALL_DIR is set to the package directory.
if [ -z "$INSTALL_DIR" ]; then
  INSTALL_DIR="$(pwd)"
fi

# Detect architecture
ARCH=$(uname -m)
case "$ARCH" in
  x86_64|amd64)  ARCH="amd64" ;;
  aarch64|arm64)  ARCH="arm64" ;;
  *) echo "Unsupported architecture: $ARCH" >&2; exit 1 ;;
esac

EXT=""
if [ "$OS" = "windows" ]; then
  EXT=".exe"
fi

ASSET="denden-${OS}-${ARCH}${EXT}"
URL="https://github.com/${REPO}/releases/latest/download/${ASSET}"

echo "Downloading ${ASSET}..."
if command -v curl >/dev/null 2>&1; then
  curl -fsSL -o "${BINARY_NAME}${EXT}" "$URL"
elif command -v wget >/dev/null 2>&1; then
  wget -q -O "${BINARY_NAME}${EXT}" "$URL"
else
  echo "Error: curl or wget is required" >&2
  exit 1
fi

chmod +x "${BINARY_NAME}${EXT}"
mkdir -p "$INSTALL_DIR"

if [ -w "$INSTALL_DIR" ]; then
  # Skip mv when already downloaded into the install directory (e.g. strawhub sets cwd = INSTALL_DIR)
  SRC="$(cd "$(dirname "${BINARY_NAME}${EXT}")" && pwd)/$(basename "${BINARY_NAME}${EXT}")"
  DST="$(cd "$INSTALL_DIR" && pwd)/${BINARY_NAME}${EXT}"
  if [ "$SRC" != "$DST" ]; then
    mv "${BINARY_NAME}${EXT}" "${INSTALL_DIR}/${BINARY_NAME}${EXT}"
  fi
else
  echo "Error: cannot write to ${INSTALL_DIR}" >&2
  exit 1
fi

echo "Installed to ${INSTALL_DIR}/${BINARY_NAME}${EXT}"
