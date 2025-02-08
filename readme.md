# Memium

[![Open in Dev Container](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)][dev container]
[![PyPI](https://img.shields.io/pypi/v/memium.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/memium)][pypi status]
[![Roadmap](https://img.shields.io/badge/Board-Roadmap-green)][roadmap]

[dev container]: https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/MartinBernstorff/memium/
[pypi status]: https://pypi.org/project/memium/
[documentation]: https://MartinBernstorff.github.io/memium/
[roadmap]: https://github.com/users/MartinBernstorff/projects/2

<!-- start short-description -->

When you have to stop and look things up, it breaks up your flow. Adding this knowledge to long-term memory builds fluency, and being fluent at something makes it much more fun! The faster you can get from crawling to running, the more enjoyable it is.

Unfortunately, we forget most of what we read, [even stuff we care about](https://andymatuschak.org/books/).

It turns out that if you ask questions of the texts you read, and ask those questions of yourself in the future, you learn much more! But writing questions and quizzing yourself can feel quite mechanical. What if you wrote questions as part of your notes, and then your computer could quiz you in the future? That's the purpose of Memium. It extracts questions from your notes like 

```
Q. Why can spaced repetition result in more enjoyable learning?
A. It enables faster bootstrapping to proficiency, which is more fun!
```

And adding them to a spaced repetition service like [Anki](https://apps.ankiweb.net). 

This is an implementation of Andy Matuschak's [Personal Mnemonic Medium](https://notes.andymatuschak.org/The_mnemonic_medium_can_be_extended_to_one%E2%80%99s_personal_notes).

<!-- end short-description -->

## Use as an application
If you want to sync markdown notes to Anki, here's how to get started!

1. In Anki, install the [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on

### Command line interface
2. Install Memium in its own virtual environment with pipx,

```bash
> pipx install memium
```

3. Import your notes!

```cli-block
> memium --input-dir [YOUR_INPUT_DIR]
```

### In Docker container
2. Install [Orbstack](https://orbstack.dev/) or Docker Desktop. 
3. Setup a container
```bash
$INPUT_DIR="PATH_TO_YOUR_INPUT_DIR"

docker run -i \
  --name=memium-container \
  --rm \
  -e HOST_INPUT_DIR=$INPUT_DIR \
  -v $INPUT_DIR:/input \
  ghcr.io/martinbernstorff/memium:latest \
  memium \
  --input-dir /input/
```

This will start a docker container which updates your deck from `$INPUT_DIR`. In case of updated files, it will sync the difference (create new prompts and delete deleted prompts) to Anki. 

If you want to continuously sync the directory, set the `--watch-seconds [UPDATE_SECONDS]` argument as well.

Keeping the package update can be a bit of a chore, which can be automated with [WatchTower](https://github.com/containrrr/watchtower).

## Use as library
If you would like to build build your own Python application on top of the abstractions added here, you can install the library from pypi:

```bash
pip install memium
```

### Pipeline abstractions
The library is built as a pipeline illustrated below. Left describes the abstract pipeline, defined by interfaces. The right path describes an implementation of those interfaces from markdown to Anki, which is available in the CLI. 

```mermaid

graph TD 
	FD["File on disk"]
        DP["Prompts at Destination"]
	FD -- DocumentSource --> Document
	Document -- PromptExtractor --> Prompt
	Prompt -- Destination --> DP
 
	MD["Markdown file"]
	Prompts["[QAPrompt | ClozePrompt]"]
        Anki["Cards in the Anki app"]
 
	MD -- MarkdownDocumentSource --> Document
	Document -- "[QAPromptExtractor, \nClozePromptExtractor]" --> Prompts
        Prompts -- AnkiConnectDestination --> Anki
 ```

## Contributing
### Setting up a dev environment
1. Install [Orbstack](https://orbstack.dev/) or Docker Desktop. Make sure to complete the full install process before continuing.
2. If not installed, install VSCode
3. Press this [link](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/MartinBernstorff/memium/)
4. Complete the setup process

### Submitting a PR
Feel free to submit pull requests! If you want to run the entire pipeline locally, run:

```bash
inv validate_ci
```

# 💬 Where to ask questions

| Type                           |                        |
| ------------------------------ | ---------------------- |
| 🚨 **Bug Reports**              | [GitHub Issue Tracker] |
| 🎁 **Feature Requests & Ideas** | [GitHub Issue Tracker] |
| 👩‍💻 **Usage Questions**          | [GitHub Discussions]   |
| 🗯 **General Discussion**       | [GitHub Discussions]   |

[github issue tracker]: https://github.com/MartinBernstorff/memium/issues
[github discussions]: https://github.com/MartinBernstorff/memium/discussions
