#!/bin/bash

####################################################################### DOCKER

for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done

# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get -y install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

apt-get -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

####################################################################### CODE

curl -fsSL https://code-server.dev/install.sh | sh

WORKSPACE_DIR=/workspace
mkdir -p $WORKSPACE_DIR

VSCODE_USER_DATA_DIR=/user-data
mkdir -p $VSCODE_USER_DATA_DIR

mkdir -p $VSCODE_USER_DATA_DIR/User
cat <<EOT >> $VSCODE_USER_DATA_DIR/User/settings.json
{
    "workbench.editorAssociations": {
      "*.md": "vscode.markdown.preview.editor"
    },
    "terminal.integrated.cwd": "$WORKSPACE_DIR",
    "workbench.settings.applyToAllProfiles": [
        "terminal.integrated.cwd"
    ],
    "terminal.integrated.defaultProfile.linux": "bash",
    "terminal.integrated.hideOnStartup": "never"
}
EOT

mkdir -p $VSCODE_USER_DATA_DIR/Machine
cat <<EOT >> $VSCODE_USER_DATA_DIR/Machine/settings.json
{
    "workbench.startupEditor" : "readme",
    "remote.autoForwardPorts": false
}
EOT

mkdir -p /$WORKSPACE_DIR/.vscode
cat <<EOT >> /$WORKSPACE_DIR/.vscode/tasks.json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "terminal",
            "type": "shell",
            "command": "/usr/bin/bash",
            "args": [
                "-l"
            ],
            "isBackground": true,
            "problemMatcher": [],
            "presentation": {
                "group": "none"
            },
            "runOptions": {
                "runOn": "folderOpen"
            },
        }
    ]
}
EOT

cat <<EOT > /lib/systemd/system/code-server@.service
[Unit]
Description=code-server
After=network.target

[Service]
Type=exec
ExecStart=/usr/bin/code-server --user-data-dir $VSCODE_USER_DATA_DIR --auth none --disable-telemetry --disable-workspace-trust --bind-addr=0.0.0.0:8080
Restart=always
User=%i

[Install]
WantedBy=default.target
EOT

systemctl enable code-server@root
systemctl restart --now code-server@root
