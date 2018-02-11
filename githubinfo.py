import os
import argparse
from github import Github
from collections import namedtuple
from datetime import datetime, timezone, timedelta
from dateutil.parser import parse

PullRequestInfo = namedtuple('PullRequestInfo',
    ['id','html_url','state', 'size', 'duration', 'created_at', 'closed_at'])


DAYS_TO_COSIDER_OLD_A_PR = 8
DAYS_TO_COSIDER_OLD_A_BRANCH = 8


class GitHubIntegration:
    def __init__(self, username=None, password=None, oauth_token=None):
        self.username = username
        self.password = password
        self.oauth_token = oauth_token

    def get_repositories(self, organization_name):
        client = self._get_client()
        organization = client.get_organization(organization_name)
        return organization.get_repos()

    def get_all_branches(self, repo):
        return [b for b in repo.get_branches()]

    def get_pullrequests_info(self, repo):
        result = []
        for pr in repo.get_pulls():
            if pr.closed_at:
                duration = (pr.closed_at-pr.created_at).days
            else:
                duration = (datetime.now()-pr.created_at).days
            result.append(PullRequestInfo(
                    pr.number,
                    pr.html_url,
                    pr.state,
                    pr.additions + pr.deletions,
                    duration,
                    pr.created_at,
                    pr.closed_at
                ))
        return result

    def _get_client(self):
        if self.oauth_token:
            return Github(self.oauth_token)
        else:
            return Github(self.username, self.password)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbosity", action="store_true", default=False, help="increase output verbosity")
    parser.add_argument("--dump_old_prs", action="store_true", default=False, help="dump old PR")
    parser.add_argument("--dump_old_branches", action="store_true", default=False, help="dump old Branches")
    parser.add_argument("organization", help="github organization")
    args = parser.parse_args()
    if args.verbosity:
        print("verbosity turned on")

    github_client = GitHubIntegration(os.environ['GITHUB_OAUTH_TOKEN'])
    for repo in github_client.get_repositories(args.organization):

        branches = github_client.get_all_branches(repo)
        pull_requests = github_client.get_pullrequests_info(repo)
        durations = sorted([pr.duration for pr in pull_requests])
        sizes = sorted([pr.size for pr in pull_requests])

        if durations:
            old_prs_message = "Older PR {} days".format(max(durations))
        else:
            old_prs_message = ""

        print(repo.name, "OpenBranches", len(branches),
            "OpenPRs", len(pull_requests), old_prs_message)
        if args.dump_old_prs:
            print("Old PRs")
            for pr in sorted(pull_requests, key=lambda x: x.duration, reverse=True):
                if pr.duration >= DAYS_TO_COSIDER_OLD_A_PR:
                    print("\t", pr.duration, "days", pr.html_url)

        if args.dump_old_branches:
            print("Old branches")
            for branch in sorted(branches, key=lambda b: parse(b.commit.commit.last_modified)):
                last_modification = parse(branch.commit.commit.last_modified)
                last_commit_age = (datetime.now(timezone.utc) - last_modification).days
                if  last_commit_age > DAYS_TO_COSIDER_OLD_A_BRANCH:
                    print("\t", last_commit_age, "days", branch.name,
                          "last commit author:", branch.commit.commit.author.name)
        print()


if __name__ == '__main__':
    main()