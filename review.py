"""Review GitHub PR using Open AI Models like Davinci-003, GPT-3 and GPT-4."""
import logging
import json
import os
import time
import requests
import openai
import sys

from openai.error import RateLimitError, InvalidRequestError


class GitFile:
    """A git file with its diff contents."""

    def __init__(self, file_name, diff):
        """Initialize a GitFile object.

        Args:
            file_name (str): The name of the file.
            diff (str): The diff contents of the file.
        """
        self.file_name = file_name
        self.diff = diff


def chunks(s, n):
    """Produce `n`-character chunks from `s`."""
    for start in range(0, len(s), n):
        yield s[start : start + n]


def splits(s):
    for commit in s.split("From: "):
        # for split in commit.split("diff"):
        yield chunks(commit, 3000)


def call_davinci(
    prompt: str,
    temperature=0.10,
    max_tokens=312,
    top_p=1,
    frequency_penalty=0.5,
    presence_penalty=0.0,
) -> str:
    model = os.getenv("GPT_MODEL", "text-davinci-003")

    logging.info(f"\nPrompt sent to GPT-3: {prompt}\n")
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
    )
    return response["choices"][0]["text"]


def call_gpt3(
    prompt: str,
    temperature=0.10,
    max_tokens=312,
    top_p=1,
    frequency_penalty=0.5,
    presence_penalty=0.0,
) -> str:
    try:
        logging.info(f"\nPrompt sent to GPT-3: {prompt}\n")
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )
        logging.info(completion.choices[0].message.content)
        return completion.choices[0].message.content
    except (RateLimitError, InvalidRequestError):
        return call_davinci(prompt, temperature, max_tokens, top_p, frequency_penalty, presence_penalty)


def call_gpt4(
    prompt: str,
    temperature=0.10,
    max_tokens=500,
    top_p=1,
    frequency_penalty=0.5,
    presence_penalty=0.0,
    retry=0,
) -> str:
    try:
        engine = "gpt-4-32k"

        logging.info(f"\nPrompt sent to GPT-4: {prompt}\n")
        completion = openai.ChatCompletion.create(
            engine=engine,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )
        return completion.choices[0].message.content
    except InvalidRequestError:
        return call_gpt3(prompt, temperature, max_tokens, top_p, frequency_penalty, presence_penalty)
    except RateLimitError as error:
        if retry < 5:
            time.sleep(retry * 5)
            return call_gpt4(prompt, temperature, max_tokens, top_p, frequency_penalty, presence_penalty, retry + 1)
        raise RateLimitError("Retry limit exceeded") from error


def call_gpt(
    prompt: str,
    temperature=0.10,
    max_tokens=500,
    top_p=1,
    frequency_penalty=0.5,
    presence_penalty=0.0,
) -> str:
    if os.getenv("AZURE_OPENAI_API_KEY"):
        openai.api_type = "azure"
        openai.api_base = os.getenv("AZURE_OPENAI_API")
        openai.api_version = "2023-03-15-preview"
        openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")

        return call_gpt4(prompt, temperature, max_tokens, top_p, frequency_penalty, presence_penalty)

    openai.api_key = os.getenv("OPENAI_API_KEY")
    return call_gpt3(prompt, temperature, max_tokens, top_p, frequency_penalty, presence_penalty)


def split_diff(git_diff):
    """Split a git diff into a list of files and their diff contents.

    Args:
        git_diff (str): The git diff to split.

    Returns:
        list: A list of tuples containing the file name and diff contents.
    """
    diff = "diff"
    git = "--git a/"
    return git_diff.split(f"{diff} {git}")[1:]  # Use formated string to prevent splitting


def _analyze_test_coverage_bicep(files):
    main_file = files["main.bicep"].diff
    test_file = files["main.test.bicep"].diff if "main.test.bicep" in files else ""

    return f"""
    Are the changes in main.bicep tested in main.test.bicep?
    If not, provide ideas how to test the changes, and create more tests in main.test.bicep.
    main.bicep
    ```
    {main_file}
    ```
    main.test.bicep
    ```
    {test_file}
    ```
    """


def summarize_test_coverage(git_diff):
    files = {}
    for diff in split_diff(git_diff):
        path = diff.split(" b/")[0]
        git_file = GitFile(path.split("/")[len(path.split("/")) - 1], diff)

        files[git_file.file_name] = git_file

    if "main.bicep" in files:
        prompt = _analyze_test_coverage_bicep(files)
    else:
        prompt = f"""
Are the changes tested?
```
{git_diff}
```
"""

    return call_gpt(prompt, temperature=0.0, max_tokens=1500)


def summarize_file(diff):
    git_file = GitFile(diff.split(" b/")[0], diff)
    prompt = f"""
Summarize the changes to the file {git_file.file_name}.
- Do not include the file name in the summary.
- list the summary with bullet points
{diff}
"""
    response = call_gpt(prompt, temperature=0.0)
    return f"""
### {git_file.file_name}
{response}
"""


def summarize_pr(git_diff):
    # Summarize the changes in this GitHub diff report.
    gpt4_big_prompot = f"""
{git_diff}
"""
    response = call_gpt(gpt4_big_prompot)
    logging.info(response)
    return response


def summarize_bugs_in_pr(git_diff):
    # Summarize any bugs that may be introduced in this GitHub diff report.
    gpt4_big_prompot = f"""
Summarize bugs that may be introduced.

{git_diff}
"""
    response = call_gpt(gpt4_big_prompot)
    logging.info(response)
    return response


def summarize_files(git_diff):
    """Summarize git files."""
    summary = f"""
# Summary by GPT-4
{summarize_pr(git_diff)}
## Changes
"""

    for diff in split_diff(git_diff):
        summary += summarize_file(diff)

    summary += f"""
## Test Coverage
{summarize_test_coverage(git_diff)}

## Potential Bugs
{summarize_bugs_in_pr(git_diff)}
"""
    return summary


def get_review(pr_patch):
    review = summarize_files(pr_patch)
    print(review)

    if os.getenv("LINK"):
        _post_pr_comment(review)
    else:
        logging.warning("No PR to post too")


def _post_pr_comment(review):
    GIT_COMMIT_HASH = os.getenv("GIT_COMMIT_HASH")
    data = {"body": review, "commit_id": GIT_COMMIT_HASH, "event": "COMMENT"}
    data = json.dumps(data)

    pr_link = os.getenv("LINK")
    OWNER = pr_link.split("/")[-4]
    REPO = pr_link.split("/")[-3]
    PR_NUMBER = pr_link.split("/")[-1]

    ACCESS_TOKEN = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
    }
    response = requests.get(
        f"https://api.github.com/repos/{OWNER}/{REPO}/pulls/{PR_NUMBER}/reviews", headers=headers, timeout=10
    )
    comments = response.json()

    for comment in comments:
        if (
            "user" in comment
            and comment["user"]["login"] == "github-actions[bot]"
            and "body" in comment
            and "Summary by GPT-4" in comment["body"]
        ):
            review_id = comment["id"]
            data = {"body": review}
            data = json.dumps(data)

            response = requests.put(
                f"https://api.github.com/repos/{OWNER}/{REPO}/pulls/{PR_NUMBER}/reviews/{review_id}",
                headers=headers,
                data=data,
                timeout=10,
            )
            logging.info(response.json())
            break
    else:
        # https://api.github.com/repos/OWNER/REPO/pulls/PULL_NUMBER/reviews
        response = requests.post(
            f"https://api.github.com/repos/{OWNER}/{REPO}/pulls/{PR_NUMBER}/reviews",
            headers=headers,
            data=data,
            timeout=10,
        )
        logging.info(response.json())


def _get_pr_diff():
    """
    Replicate the logic from this command

    PATCH_OUTPUT=$(curl --silent --request GET \
        --url https://api.github.com/repos/$PATCH_REPO/pulls/$PATCH_PR \
        --header "Accept: application/vnd.github.diff" \
        --header "Authorization: Bearer $GITHUB_TOKEN")
    """
    patch_repo = os.getenv("PATCH_REPO")
    patch_pr = os.getenv("PATCH_PR")
    access_token = os.getenv("GITHUB_TOKEN")

    headers = {
        "Accept": "application/vnd.github.v3.diff",
        "authorization": f"Bearer {access_token}",
    }

    response = requests.get(f"https://api.github.com/repos/{patch_repo}/pulls/{patch_pr}", headers=headers, timeout=10)
    return response.text


if __name__ == "__main__":
    pr_notes = _get_pr_diff() if len(sys.argv) == 1 else sys.argv[1]
    get_review(pr_notes)
