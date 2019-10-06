#!/bin/sh
# create a .zip file ready for kodi

PLUGIN_DIR="$(basename ${PWD})"
RELEASE_FILE="$(basename ${PWD}).zip"

# remove existing release
[ -f ${RELEASE_FILE} ] && rm ${RELEASE_FILE}

cd ..
zip -r "${PLUGIN_DIR}/${RELEASE_FILE}" "${PLUGIN_DIR}/" -x "${PLUGIN_DIR}/.git/*" "${PLUGIN_DIR}/.idea/*" "${PLUGIN_DIR}/venv/*" "${PLUGIN_DIR}/.gitignore" "*.pyo"

cd -
