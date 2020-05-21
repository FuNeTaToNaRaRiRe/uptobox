# Uptobox

Some functions that allows you to interact with Uptobox API.

## Prerequisites

- Go on https://uptobox.com/my_account and get your token.
- Paste it on the "self.token" line.

## Functions:

### file_search(path, limit, search)

- Path is the Uptobox folder path (basepath of Uptobox is "//")
- Limit is the number of maximal search results
- Search is pretty obvious

### get_download_link(code)

- Takes as an argument the code of an Uptobox file. Code is the unique identifier for a file hosted on Uptobox. It's the string at the end of an Uptobox link.
- Regex can handle Uptobox link so you can use the link as an argument.

### upload_file(file)

- Takes as an argument the path of the file you want to upload.

## Need to do:

- Add something to monitor the upload.

## Licensing

- MIT
