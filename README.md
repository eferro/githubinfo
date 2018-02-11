# githubinfo #
Dump information about branches and PRs.

Initial idea and tests from: https://github.com/Fortiz2305/pr-alarm-bot
To access to github you need to export your GITHUB_OAUTH_TOKEN

To create one:
[Github help: create a personal access token](https://help.github.com/articles/

# Install #
python3 -m venv venv
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Execute #
export GITHUB_OAUTH_TOKEN=<githubaccesstoken>
python githubinfo.py --dump_old_prs --dump_old_branches <github-organization>

# Help #
python githubinfo.py -h