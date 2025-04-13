FROM codercom/code-server:latest

WORKDIR /run
USER root

# ------ Prep Environment

ENV VSCODE_USER_DATA_DIR=/user-data
ENV WORKSPACE_DIR=/workspace
ENV WORKSHOP_DIR=$WORKSPACE_DIR/workshop
ENV VSCODE_WORKSPACE_FILE=${WORKSPACE_DIR}/workspace.code-workspace
ENV PYTHON_BIN_DIR=${WORKSPACE_DIR}/.venv/bin
ENV PYTHON_BIN_FILE=${WORKSPACE_DIR}/.venv/bin/python3
ENV PYTHON_VENV_PARENT_DIR=${WORKSPACE_DIR}

WORKDIR ${WORKSPACE_DIR}

# ------ Prep node

RUN apt -y update
RUN apt install -y nodejs npm

# ------ Prep Python

RUN apt -y update
RUN apt install -y python3 python3-pip gcc python3-dev python3-venv python-is-python3

RUN python3 -m venv .venv
# you can't call source from dockerfile, so just put venv bins first on the path
ENV PATH="$PYTHON_BIN_DIR:$PATH"

# ------ Prep VS Code

RUN python3 -m pip install ipykernel
RUN python3 -m ipykernel install --user

RUN code-server --install-extension ms-python.python --force --user-data-dir ${VSCODE_USER_DATA_DIR}
RUN code-server --install-extension ms-toolsai.jupyter --force --user-data-dir ${VSCODE_USER_DATA_DIR}

COPY vscode-default-python-kernel-0.0.2.vsix .
RUN code-server --install-extension vscode-default-python-kernel-0.0.2.vsix --force --user-data-dir ${VSCODE_USER_DATA_DIR}

# ------ Prep Settings

RUN echo "{ \n\
    \"folders\": [ \n\
        { \n\
            \"path\": \"${WORKSHOP_DIR}\" \n\
        } \n\
    ] \n\
}" >> ${VSCODE_WORKSPACE_FILE}

RUN echo "{ \n\
    \"workbench.editorAssociations\": { \n\
            \"*.md\": \"vscode.markdown.preview.editor\" \n\
    }, \n\
    \"python.venvPath\" : [\"${PYTHON_VENV_PARENT_DIR}\"], \n\
    \"python.defaultInterpreterPath\": \"${PYTHON_BIN_FILE}\", \n\
    \"python.terminal.activateEnvironment\": true, \n\
    \"python.terminal.activateEnvInCurrentTerminal\": true, \n\
    \"terminal.integrated.cwd\": \"${WORKSHOP_DIR}\", \n\
    \"workbench.settings.applyToAllProfiles\": [ \n\
        \"terminal.integrated.cwd\", \n\
        \"python.terminal.activateEnvInCurrentTerminal\" \n\
    ], \n\
    \"terminal.integrated.profiles.linux\": { \n\
      \"BashWithStartup\": { \n\
        \"path\": \"bash\", \n\
        \"args\": [ \n\
          \"--init-file\", \n\
          \"${PYTHON_BIN_DIR}/activate\" \n\
        ] \n\
      } \n\
    }, \n\
    \"terminal.integrated.defaultProfile.linux\": \"BashWithStartup\" \n\
}" >> ${VSCODE_USER_DATA_DIR}/User/settings.json

# set workspace to auto-open readme file
RUN echo "{ \n\
    \"workbench.startupEditor\" : \"readme\", \n\
    \"remote.autoForwardPorts\" : false \n\
}" >> ${VSCODE_USER_DATA_DIR}/Machine/settings.json

CMD ["code-server", "/workspace/workspace.code-workspace", "--user-data-dir", "/user-data", "--auth", "none", "--disable-telemetry", "--disable-workspace-trust"]
