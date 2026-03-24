<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./.github/logo_dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="./.github/logo_light.svg">
    <img src="./.github/logo_light.svg"  width="500px" alt="NeoFS logo">
  </picture>
</p>
<p align="center">
  <a href="https://fs.neo.org">NeoFS</a> is a decentralized distributed object storage integrated with the <a href="https://neo.org">Neo blockchain</a>.
</p>

# GitHub Action to Publish to NeoFS

This GitHub action allows you to save files as objects in the [NeoFS](https://fs.neo.org/).

This way you can both publicly and privately save logs and test results, host web pages, and publish releases.

To use this action you need a wallet, some NeoFS balance and a container. The
easiest way to handle deposit and container creation is via [Panel](https://panel.fs.neo.org/).

## Supported platforms

This action supports the following platforms:

- Linux x64

This action tested on the following runners:

- [Ubuntu 22.04 GitHub-hosted runners](https://github.com/actions/runner-images/blob/main/images/linux/Ubuntu2204-Readme.md)

# Configuration

## GitHub secrets

The following Sensitive information must be passed as
[GitHub Actions secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions).
It is very important to use SECRETS and NOT variables, otherwise your wallet, password and token will be available to
the whole internet.

| Key | Value | Required | Default |
|-------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|---------|
| `NEOFS_WALLET` | Base64-encoded NEP-6 Neo N3 wallet. To create N3 wallet: `neo-go wallet init -w wallet.json -a` The output of this command should be here: 'cat wallet.json | base64' | **Yes** | N/A |
| `NEOFS_WALLET_PASSWORD` | N3 wallet password | **Yes** | N/A |

Please keep sensitive data safe.

## GitHub environment variables

### NeoFS network environment variables

The following variables must be passed as
[GitHub Actions vars context](https://docs.github.com/en/actions/learn-github-actions/variables#using-the-vars-context-to-access-configuration-variable-values)
or [GitHub Actions environment variables](https://docs.github.com/en/actions/learn-github-actions/variables).

Up-to-date information about NeoFS network can be seen on https://status.fs.neo.org.

If you are using the NeoFS mainnet, we recommend that you do not change the `NEOFS_ENDPOINT`
environment variable.

| Key | Value | Required | Default |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------|----------|-----------------------------|
| `NEOFS_ENDPOINT` | RPC endpoint for the NeoFS node. Supports full address with port and scheme, e.g. `host:8080` or `grpcs://host:9090`. | **No** | grpcs://st1.storage.fs.neo.org:8082 |
| `STORE_OBJECTS_CID` | Container ID for your data. For example: 7gHG4HB3BrpFcH9BN3KMZg6hEETx4mFP71nEoNXHFqrv | **Yes** | N/A |

### Data handling environment variables

The following variables must be passed as
[GitHub Actions vars context](https://docs.github.com/en/actions/learn-github-actions/variables#using-the-vars-context-to-access-configuration-variable-values)
or [GitHub Actions environment variables](https://docs.github.com/en/actions/learn-github-actions/variables).

These inputs control uploaded data. Attributes can be used to identify all objects for a given uploaded set. `LIFETIME`
can be used to autodelete objects that don't need to be stored forever (like logs or test reports).

| Key | Value | Required | Default |
|---------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|----------|---------|
| `PATH_TO_FILES_DIR` | Path to the directory with the files to be pushed. The directory itself is treated as the root: its name is stripped and only the contents are uploaded. | **Yes** | N/A |
| `HTTP_URL_PREFIX` | Full URL prefix for `OUTPUT_CONTAINER_URL`. Examples: `https://rest.fs.neo.org/MYCID/` or `https://reports.example.com/`. | **No** | N/A |
| `LIFETIME` | Number of epochs (for mainnet 1 epoch is ~1 hour) for object to stay valid (it's deleted afterwards), "0" means "unlimited" | **No** | 0 |
| `NEOFS_ATTRIBUTES` | User attributes in form of Key1=Value1,Key2=Value2. By default, each object contains attributes of relative path to the file and MIME type of the file. | **No** | N/A |
| `REPLACE_OBJECTS` | Boolean controlling object replacement by path, with "false" objects are uploaded and old ones are kept even if they have the same "FilePath" | **No** | true |
| `REPLACE_CONTAINER_CONTENTS` | Boolean controlling complete container contents replacement, when "true" all old container objects are deleted | **No** | false |
| `URL_PREFIX` | Prefix added to the `FilePath` attribute of each uploaded object (e.g. a run ID like `96-1697035975`). When `HTTP_URL_PREFIX` is not set, also appended to `OUTPUT_CONTAINER_URL`. | **No** | N/A |

## Output

| Key | Value | Required | Default |
|------------------------|-------------------------------------------------------------------------------------------------------------|----------|---------|
| `OUTPUT_CONTAINER_URL` | Output example: https://http.storage.fs.neo.org/HXSaMJXk2g8C14ht8HSi7BBaiYZ1HeWh2xnWPGQCg4H6/872-1696332227 | **No** | N/A |

# Migrating from 0.3.1 to 0.4.0

Update your workflow files as described below.

## 1. Replace `NEOFS_NETWORK_DOMAIN` with `NEOFS_ENDPOINT`

`NEOFS_NETWORK_DOMAIN` accepted a bare domain name and the port was hardcoded to `8080` internally.
`NEOFS_ENDPOINT` accepts a full address including scheme and port, giving you full control over which
node and transport you use.

```yaml
# Before
NEOFS_NETWORK_DOMAIN: ${{ vars.NEOFS_NETWORK_DOMAIN }}  # e.g. st1.storage.fs.neo.org

# After
NEOFS_ENDPOINT: ${{ vars.NEOFS_ENDPOINT }}  # e.g. grpcs://st1.storage.fs.neo.org:8082
```

If you were using the NeoFS mainnet default and did not set `NEOFS_NETWORK_DOMAIN` at all, the new
default (`grpcs://st1.storage.fs.neo.org:8082`) will work without any changes.

## 2. Replace `NEOFS_HTTP_GATE` with `HTTP_URL_PREFIX`

`NEOFS_HTTP_GATE` accepted a gateway domain and the action constructed the container URL automatically.
`HTTP_URL_PREFIX` expects the full URL prefix (including the container ID), which makes it easier to
use custom gateways or CDN URLs in front of NeoFS.

```yaml
# Before
NEOFS_HTTP_GATE: ${{ vars.NEOFS_HTTP_GATE }}  # e.g. rest.fs.neo.org
# The action would build: https://rest.fs.neo.org/<CID>/

# After
HTTP_URL_PREFIX: https://rest.fs.neo.org/${{ vars.STORE_OBJECTS_CID }}/
# Or with a custom domain: https://reports.example.com/
```

The value of `OUTPUT_CONTAINER_URL` is now set directly to `HTTP_URL_PREFIX` (with `URL_PREFIX`
appended if provided). If `HTTP_URL_PREFIX` is not set, the action falls back to
`https://rest.fs.neo.org/<CID>/`.

## 3. Remove `STRIP_PREFIX` — it is now always on

Previously, `STRIP_PREFIX: true` was needed to make the action treat `PATH_TO_FILES_DIR` as the
upload root (i.e. strip the directory name itself from every `FilePath` attribute). This is now the
default and only behavior; the `STRIP_PREFIX` input no longer exists.

```yaml
# Before — you had to opt in
STRIP_PREFIX: 'true'
PATH_TO_FILES_DIR: ./my-reports

# After — just remove STRIP_PREFIX; the directory is always treated as the root
PATH_TO_FILES_DIR: ./my-reports
```

If you were relying on the old behavior where the directory name was included in `FilePath` (i.e.
`STRIP_PREFIX` was `false` or not set), you will need to adjust your `PATH_TO_FILES_DIR` or
`URL_PREFIX` values to reproduce the same object paths.

# Dependencies

## Python

The GitHub runner must have Python 3 installed on it.

You can install Python like this:

```yml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11.6'
```

# Examples

## How to store files from the directory to NeoFS

```yml
name: Publish to NeoFS
on:
  push:
    branches: [ master ]
jobs:
  push-to-neofs:
    runs-on: ubuntu-latest
    steps:
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11.6'
  
      - uses: actions/checkout@v4
      - name: Publish to NeoFS
        uses: nspcc-dev/gh-push-to-neofs@master
        with:
          NEOFS_WALLET: ${{ secrets.NEOFS_WALLET }}
          NEOFS_WALLET_PASSWORD: ${{ secrets.NEOFS_WALLET_PASSWORD }}
          NEOFS_ENDPOINT: ${{ vars.NEOFS_ENDPOINT }}
          STORE_OBJECTS_CID: ${{ vars.STORE_OBJECTS_CID }}
          HTTP_URL_PREFIX: https://rest.fs.neo.org/${{ vars.STORE_OBJECTS_CID }}/
          LIFETIME: ${{ vars.LIFETIME }}
          PATH_TO_FILES_DIR: ${{ env.PATH_TO_FILES_DIR }}
```

## How to store Allure report to NeoFS as static page

See https://github.com/nspcc-dev/gh-push-allure-report-to-neofs for more details.

In the [NeoFS](https://github.com/nspcc-dev/neofs-node) project, we use the following workflow to store the
[Allure report](https://github.com/allure-framework/allure2) as a static page in the NeoFS mainnet.
This is a good example of practical use of this action.

To avoid creating a huge (weighing hundreds of megabytes or more) web page, in this example we upload zip archives with
attachments as separate objects.
Access to them from the Allure report will be via hyperlinks from the report page. Yes, this is the Web 1.0 world
in the Web 3.0. And it's beautiful.

We use the [simple-elf/allure-report-action](https://github.com/simple-elf/allure-report-action) action to generate
the Allure report and the [allure-combine](https://github.com/MihanEntalpo/allure-single-html-file) tool to convert
the report to a static page.
Of course, you can use any other tool to generate the Allure report and convert it to a static page. For example, you
can use [allure-commandline](https://github.com/allure-framework/allure-npm) or Allure itself according to
[this](https://github.com/allure-framework/allure2/pull/2072) merged pull request.

The Allure report will be available in a web browser at a link like this:
https://http.fs.neo.org/86C4P6uJC7gb5n3KkwEGpXRfdczubXyRNW5N9KeJRW73/53-1696453127/comb_report/complete.html#

Attachments will also be available at the link:
https://http.fs.neo.org/86C4P6uJC7gb5n3KkwEGpXRfdczubXyRNW5N9KeJRW73/876-1696502182/comb_report/data/attachments/ce0fa9e280851f32.zip
