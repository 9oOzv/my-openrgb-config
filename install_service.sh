#!/usr/bin/env bash
script_dir="$(dirname "$(readlink -f "$0")")"
cd "$script_dir"

python_bin="$script_dir/venv/bin/python"
rgb_py="$script_dir/rgb.py"
target="$HOME/.config/systemd/user/rgb.service"

cat rgb.service | sed "s|RGB_CMD|$python_bin $rgb_py|" > "$target"
systemctl --user daemon-reload
systemctl --user enable --now rgb.service
