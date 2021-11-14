import os
import sys

import requests


def upload_coverage_badge():

    cov = sys.argv[-1]
    badge_svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="96" height="20" role="img" aria-label="coverage: 11%"><title>coverage: 11%</title><linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="r"><rect width="96" height="20" rx="3" fill="#fff"/></clipPath><g clip-path="url(#r)"><rect width="61" height="20" fill="#555"/><rect x="61" width="35" height="20" fill="#97ca00"/><rect width="96" height="20" fill="url(#s)"/></g><g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110"><text aria-hidden="true" x="315" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="510">coverage</text><text x="315" y="140" transform="scale(.1)" fill="#fff" textLength="510">coverage</text><text aria-hidden="true" x="775" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="250">11%</text><text x="775" y="140" transform="scale(.1)" fill="#fff" textLength="250">{cov}</text></g></svg>
    """  # noqa: E501

    gh_token = os.environ["GITHUB_TOKEN"]
    r = requests.patch(
        url="https://api.github.com/gists/5163dbd0fdea4409fd7a3ae6383c6b66",
        json={"files": {"gistfile1.svg": {"content": badge_svg}}},
        headers={
            "Authorization": f"token {gh_token}",
            "Accept": "application/vnd.github.v3+json",
        },
    )
    print(r.status_code())


if __name__ == "__main__":
    raise SystemExit(upload_coverage_badge())
