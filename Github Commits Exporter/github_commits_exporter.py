import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

with open('user.txt', 'r') as file:
    user = file.read()

repos_url = 'https://api.github.com/users/{}/repos?per_page=100'
repos_url = repos_url.format(user)

commits_url = 'https://api.github.com/repos/{}'
commits_url = commits_url.format(user)
commits_url = commits_url + '/{}/commits?per_page=100'

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

response = session.get(repos_url)
repos = pd.DataFrame(response.json())

commits = pd.DataFrame(columns=['message', 'url', 'comment_count', 'author.name', 'author.email', 'author.date', 'committer.name', 'committer.email', 'committer.date', 'tree.sha', 'tree.url', 'verification.verified', 'verification.reason', 'verification.signature', 'verification.payload'])

for name in repos['name']:
    response = session.get(commits_url.format(name))
    result = pd.DataFrame(response.json())
    result = result['commit']
    for i in range(len(result)):
        json = pd.json_normalize(result[i])
        commits = pd.concat([commits, json])

commits.drop(['verification.signature', 'verification.payload'], axis=1, inplace=True)
commits.to_csv('commits.csv', index=False)