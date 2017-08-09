# DOSIDO
### A CLI to maintain your helpscout knowledge base with markdown

## Installation
`pip3 install dosido`

## Overview

Dosido acts as an interpreter between your filesystem and your HelpScout Knowledge Base.

**Note: Dosido requires that you use Markdown formatted files that end in .md.**

In HelpScout the KnowledgeBase is structured like so:

```
site
├── collection
    ├── article
```

So we will mirror this in your project structure:

```
.
├── my_collection_name
|   ├── this_is_an_article_title.md
|   └── names_of_article_files_matter.md
├── another_collection_name
|   ├── another_article_name.md
|   └── header.html
```

## Usage

Dosido has three main uses:

1. Creating new collections in HelpScout.
2. Publishing new articles to HelpScout.
3. Updating already existing articles with new content.

### Create a Dosido Project

Use `dosido init` to create a new HelpScout collection. This will also created a config file at `.dosido/config.ini`.

The config file includes:
* The Helpscout API key
* Collection names and keys
* Site ID value
* The Image Host URL

When you create a Dosido project, you'll get a series of prompts to walk you through that process.

_Before using Dosido, you'll need a HelpScout API key. You can get this from HelpScout [here](https://secure.helpscout.net/users/authentication/59508/api-keys)._

**Complete these steps to create a new Dosido project.**

1. `dosido init`
_What is your API key?_
2. Enter your HelpScout API key.
_What is the sub domain?_
3. Enter the HelpScout subdomain. This the first part of your HelpScout KnowledgeBase URL. For example, **helpscout**.helpscoutdocs.com.
_Provide a name for the collection._
4. Enter the name you'd like to give the collection. It is case sensitive. NOTE: You can change the name in HelpScout later.
_Should this collection be private? Default is public. (yes/no)_
5. If you make the collection public (no), the articles in the collection will be published and visible to everyone. If it's private, they'll only be visible to HelpScout accounts. You can change this setting later [here](https://secure.helpscout.net/settings/docs/collections/).
_Do you want the directory for this folder created now? (yes/no)_
6. If you don't already have a directory in your local file system, choose yes.
_Would you like to make another collection? (yes/no)_
7. Choosing yes will loop you back to step 4. Choose no to finish.
_What is the url that you are going to host your assets.
Usually this will be your git repository's Github pages url._
8. Enter the URL where you're hosting your Markdown files. NOTE: Use `http://docs.meridianapps.com`.

### Publish New Articles

Use
`dosido article new <file-pattern> [--publish --skip-article-refs --ignore-existing]`
to upload a new article to HelpScout.

**`article new` flags**

_--publish_ or _-pb_
The new article will be published and visible to anyone.

_--skip-article-refs_ or _-s_
Ignores internal links in articles, because those articles might not be in HelpScout.

_NOTE: Links to other articles will fail if they're not published on Help Scout. Help Scout article URLs can't be determined by name alone._

_--ignore-existing_ or _-i_
When you're publishing an entire directory of Markdown files, use this flag to ignore articles that have already been published to HelpScout.

**Complete these steps to publish one or more new articles.**

1. `dosido article new <file-pattern>` Note: You can publish a single Markdown file or a directory of files.
2. Use `--publish` if you want the files to be publicly visible.
3. Use `--skip-article-refs` if you're worried about internal links between articles failing.
4. Use `--ignore-existing` if you're publishing a directory of Markdown files, some of which you've already published.

### Update Articles

Once a collection is in place and its articles have been published, you'll most likely be updating articles instead of publishing new ones.

Use
`dosido article update <file-pattern> [--draft --skip-article-refs --unpublish]`
to send article changes to HelpScout.

**article update flags**
_--draft_ or _-d_
Sets an article as a draft. This change won't be visible until the article status is changed. The older, published version of this article will be publicly visible on HelpScout. NOTE: This can be done in HelpScout too.

_--skip-article-refs_ or _-s_
Ignores internal links in articles, because those articles might not be in HelpScout.

_--unpublish_ or _-u_
Changes the state of an article from published to unpublished.

**Complete these steps to update and publish one more previously published articles.**

1. `dosido article update <file-pattern>` Note: You can publish a single Markdown file or a directory of files.
2. Use `--draft` if you don't want the articles to be published.
3. Use `--skip-article-refs` if you're worried about internal links between articles failing.
4. Use `--unpublish` if you'd like to make an article visible only to people with HelpScout accounts.
