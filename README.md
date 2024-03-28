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

[Here](https://neospcc.medium.com/neofs-t5-testnet-has-been-started-ae75c30e856b) is a good article on how to get
started using the NeoFS testnet, this may be useful if you have no experience with NeoFS and want to get started with
the test network.

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

| Key                     | Value                                                                                                                                                                      | Required | Default |
|-------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|---------|
| `NEOFS_WALLET`          | Base64-encoded NEP-6 Neo N3 wallet. To create N3 wallet: `neo-go wallet init -w wallet.json -a` The output of this command should be here: 'cat wallet.json &#124; base64' | **Yes**  | N/A     |
| `NEOFS_WALLET_PASSWORD` | N3 wallet password                                                                                                                                                         | **Yes**  | N/A     |

Please keep sensitive data safe.

## GitHub environment variables

### NeoFS network environment variables
The following variables must be passed as
[GitHub Actions vars context](https://docs.github.com/en/actions/learn-github-actions/variables#using-the-vars-context-to-access-configuration-variable-values) 
or [GitHub Actions environment variables](https://docs.github.com/en/actions/learn-github-actions/variables).

Up-to-date information about NeoFS network can be seen on https://status.fs.neo.org.

If you are using the NeoFS mainnet, we recommend that you do not change `NEOFS_NETWORK_DOMAIN`
and `NEOFS_HTTP_GATE` environment variables.

| Key                    | Value                                                                                 | Required | Default                |
|------------------------|---------------------------------------------------------------------------------------|----------|------------------------|
| `NEOFS_NETWORK_DOMAIN` | Rpc endpoint domain address                                                           | **No**   | st1.storage.fs.neo.org |
| `NEOFS_HTTP_GATE`      | REST gateway domain address                                                           | **No**   | rest.fs.neo.org        |
| `STORE_OBJECTS_CID`    | Container ID for your data. For example: 7gHG4HB3BrpFcH9BN3KMZg6hEETx4mFP71nEoNXHFqrv | **Yes**  | N/A                    |


### Workflow environment variables
The following variables must be passed as
[GitHub Actions vars context](https://docs.github.com/en/actions/learn-github-actions/variables#using-the-vars-context-to-access-configuration-variable-values)
or [GitHub Actions environment variables](https://docs.github.com/en/actions/learn-github-actions/variables).

| Key                 | Value                                                                                                                                                   | Required | Default |
|---------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|----------|---------|
| `PATH_TO_FILES_DIR` | Path to the directory with the files to be pushed                                                                                                       | **Yes**  | N/A     |
| `NEOFS_ATTRIBUTES`  | User attributes in form of Key1=Value1,Key2=Value2. By default, each object contains attributes of relative path to the file and MIME type of the file. | **No**   | N/A     |
| `URL_PREFIX`        | Prefix to the url address for each of the files(objects)                                                                                                | **No**   | N/A     |

### Expiration period environment variables
The following variables must be passed as 
[GitHub Actions vars context](https://docs.github.com/en/actions/learn-github-actions/variables#using-the-vars-context-to-access-configuration-variable-values)
or [GitHub Actions environment variables](https://docs.github.com/en/actions/learn-github-actions/variables).

These environment variables are responsible for the storage time of the results in the storage network in epochs 
(in the mainnet, an epoch is approximately equal to one hour, so we can assume that values are specified in HOURS).

After the period is over, the data will be deleted. They are convenient to use for log rotation or test reports.

They default to 0, in which case the data will be stored until they are manually deleted.
We recommend setting a reasonable and convenient for work expiration period, for example, a month (744 hours).


| Key        | Value                                     | Required | Default |
|------------|-------------------------------------------|----------|---------|
| `LIFETIME` | Number of epochs for object to stay valid | **No**   | 0       |

## Output

| Key                    | Value                                                                                                       | Required | Default |
|------------------------|-------------------------------------------------------------------------------------------------------------|----------|---------|
| `OUTPUT_CONTAINER_URL` | Output example: https://http.storage.fs.neo.org/HXSaMJXk2g8C14ht8HSi7BBaiYZ1HeWh2xnWPGQCg4H6/872-1696332227 | **No**   | N/A     |

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
          NEOFS_NETWORK_DOMAIN: ${{ vars.NEOFS_NETWORK_DOMAIN }}
          NEOFS_HTTP_GATE: ${{ vars.NEOFS_HTTP_GATE }}
          STORE_OBJECTS_CID: ${{ vars.STORE_OBJECTS_CID }}
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
