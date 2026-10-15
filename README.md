# aicommit

`aicommit` generates Conventional Commit messages from your staged Git changes. It installs a Git `prepare-commit-msg` hook that reads the staged diff and asks an AI model to draft a message for you.

By default, it uses Amazon Bedrock with the Amazon Nova Lite model. The generated message is placed at the start of Git's commit-message file so you can review or edit it before committing.

## Requirements

- Python 3.11 or later
- Git
- AWS credentials with access to invoke the configured Amazon Bedrock model

## Install

From the project directory, install the package:

```bash
python -m pip install .
```

To install it for development and have source changes take effect immediately:

```bash
python -m pip install -e .
```

If you use a virtual environment, activate it before installing and before running `aicommit install`. The Git hook uses the Python interpreter that was active when the hook was installed.

## Configure AWS

The default provider is Amazon Bedrock. `aicommit` uses Boto3's standard AWS credential chain, so configure credentials using your usual method, such as an AWS profile or environment variables. The credentials need permission to invoke the selected Bedrock model, and the model must be available in the configured AWS region.

You can put AWS environment variables in a `.env` file in the repository; `aicommit` loads it when the hook runs. Do not commit credentials.

## Install the Git hook

Run this from inside the repository where you want to enable generated commit messages:

```bash
aicommit install
```

The command creates `.git/hooks/prepare-commit-msg`. If a hook already exists and was not installed by `aicommit`, installation stops without replacing it. To replace an existing hook:

```bash
aicommit install --force
```

To remove the `aicommit` hook:

```bash
aicommit uninstall
```

The hook only generates a message when Git has not already supplied a commit-message source. For example, commits started with `git commit -m "..."` keep the message you supplied. For the generated message, stage your changes and start a commit without `-m`:

```bash
git add .
git commit
```

Git opens your configured editor with the generated message so you can review it before saving.

## Project configuration

Optionally, create an `.aicommit.toml` file in the repository root:

```toml
model_id = "amazon.nova-lite-v1:0"
region = "ap-southeast-2"
max_diff_chars = 12000

# Set this to replace the built-in ignore patterns.
ignore = ["*.lock", "*.png", "*.jpg"]
```

All settings are optional:

| Setting | Default | Description |
| --- | --- | --- |
| `model_id` | `amazon.nova-lite-v1:0` | Amazon Bedrock model ID |
| `region` | `ap-southeast-2` | AWS region used for Bedrock |
| `max_diff_chars` | `12000` | Maximum number of staged-diff characters sent to the model |
| `ignore` | Built-in patterns | Diff file patterns to omit; defining this list replaces the defaults |

By default, lock files, minified JavaScript, source maps, `.env` files, and common image, PDF, and ZIP files are omitted from the staged diff.

## Local testing

For a local smoke test without calling Bedrock, set `AICOMMIT_PROVIDER=fake`. The fake provider returns a fixed example commit message:

```bash
aicommit install
git add .
AICOMMIT_PROVIDER=fake git commit
```

## Development

Run the test suite with:

```bash
python -m pytest
```

To see available CLI commands:

```bash
aicommit --help
```
