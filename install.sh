#!/bin/sh
# quick and dirty installation for https://github.com/behrtam/bvg-cli

BVG_CLI_CLIENT_URL="https://raw.githubusercontent.com/behrtam/bvg-cli/master/bvg_cli.py"
BVG_CLI_REQUIREMENTS_URL="https://raw.githubusercontent.com/behrtam/bvg-cli/master/requirements.txt"

echo "BVG CLI – Installation"

cd /usr/local/bin/

rm bvg_cli.py

echo "  Downloading needed files."

if [ -z "$(which wget)" ]; then
  curl -s -o tmp_bvg_cli_requirements $BVG_CLI_REQUIREMENTS_URL
  curl -s -O $BVG_CLI_CLIENT_URL
else
  wget -qO tmp_bvg_cli_requirements $BVG_CLI_REQUIREMENTS_URL
  wget -qO bvg_cli.py $BVG_CLI_CLIENT_URL
fi

echo "  Installing needed packages."

pip install -q -r tmp_bvg_cli_requirements
rm tmp_bvg_cli_requirements

chmod u+x bvg_cli.py

echo "  Process almost finished."
echo ""

echo "Add an alias to your \"~/.bashrc\" or \"~/.bash_profile\":"
echo "$ echo 'alias bvg-cli=\"python `pwd`/bvg_cli.py\"' >> ~/.bash_profile"
echo "$ source ./bash_profile"
