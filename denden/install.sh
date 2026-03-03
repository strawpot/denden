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

# Default install directory per platform
if [ -z "$INSTALL_DIR" ]; then
  if [ "$OS" = "windows" ]; then
    INSTALL_DIR="${LOCALAPPDATA}/denden"
  else
    INSTALL_DIR="/usr/local/bin"
  fi
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
  mv "${BINARY_NAME}${EXT}" "${INSTALL_DIR}/${BINARY_NAME}${EXT}"
elif [ "$OS" = "windows" ]; then
  echo "Error: cannot write to ${INSTALL_DIR}" >&2
  exit 1
else
  echo "Moving to ${INSTALL_DIR} (requires sudo)..."
  sudo mv "${BINARY_NAME}${EXT}" "${INSTALL_DIR}/${BINARY_NAME}${EXT}"
fi

echo "Installed to ${INSTALL_DIR}/${BINARY_NAME}${EXT}"

if [ "$OS" = "windows" ]; then
  echo "Add ${INSTALL_DIR} to your PATH if it is not already."
fi
