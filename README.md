![The logo. I suck at that ;)](./assets/images/logo.svg)

# GOTO publication

*Citation-based DOI searches and redirections*, by [Pierre Beaujean](https://pierrebeaujean.net).

Because the journal, the volume and the page should be enough to find an article (for which, of course, you don't have the DOI, otherwise this is stupid).

**Note:** currently, very few journals and providers are available.
And since I have a (quantum) chemistry background, I may not be aware of what is important and what is not in other fields.

## Installation

First, [clone the repository](https://help.github.com/en/articles/cloning-a-repository).

Then, install the requirements: 

+ for the **backend**, you need [python 3.6](https://www.python.org/) and [pipenv](https://docs.pipenv.org/en/latest/),
+ for the **frontend**, you need [node](https://nodejs.org/en/) (consider an installation via [nvm](https://github.com/nvm-sh/nvm)).

Finally, the [Makefile](./Makefile) contains the install commands:

```bash
make init # install backend and dependancies
make front # install frontend and dependancies
```

## Usage

To launch the website, use

```bash
make run
```

A web server (in **debug mode**) should be accessible at [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

In the search bar, there is three fields that compose a citation:

+ the **journal** name: suggestions appears as you are typing,
+ the **volume**,
+ the (starting) **page**.

Then, you can select two what you want:

+ An **URL**: this is the fastest way, since the result is generated from an URL that get closer to the article you are looking for (either the article directly, or a search page).
  But notice that no check for the availability of the article is done.
+ A **DOI**: what you will get is the **correct** DOI, but the request is slower, since the server needs to make some (usually one) requests to check if the article is available and get its DOI.

Click on the "Get!" button, and the result will appear below the form, in a table. 
Successive requests pile up in the table.
If there is an error, the message is given above.

In this table, you have the possibility to copy the URL/DOI and to visit the article itself (which requires to allow pop-up in your navigator to open a new tab).


## API

While the web server runs, an API is accessible.
All request are done in `GET`.

### `/api/suggests`

Parameters | Value
-----------|-------
`q` (**mandatory**) | Any string

Suggest five journals that are close to `q`.

Example: the request [`/api/suggests?q=natu`](http://localhost:5000/api/suggests?q=natu) results in:

```json
{
    "request": "natu",
    "suggestions": [
        "Nature",
        "Theoretical Chemistry Accounts",
        "Journal of Mathematical Physics",
        "Theoretica chimica acta",
        "Journal of Applied Physics"
    ]
}
```

### `/api/url` and `/api/doi`

Parameters | Value
-----------|-------
`journal` (**mandatory**) | Valid journal, obtained via `/api/suggests`
`volume` (**mandatory**) | Volume number (may be the year for certain providers)
`page`  (**mandatory**) | Page number (may be the article number for certain providers)
`apiKey` (optional) | Valid key to use the provider API. Only required for DOI search in [Elsevier](https://dev.elsevier.com/).

Get an URL or a DOI associated with a citation.

Example: the request [`/api/doi?journal=The%20Journal%20of%20Chemical%20Physics&volume=151&page=064303`](http://localhost:5000/api/doi?journal=The%20Journal%20of%20Chemical%20Physics&volume=151&page=064303) results in:

```json
{
    "request": {
        "journal": "The Journal of Chemical Physics",
        "volume": "151",
        "page": "064303"
    },
    "result": {
        "providerName": "American Institute of Physics (AIP)",
        "providerIcon": "https://aip.scitation.org/favicon.ico",
        "providerWebsite": "https://aip.scitation.org/",
        "doi": "10.1063/1.5110375",
        "url": "https://dx.doi.org/10.1063/1.5110375"
    }
}
```

Which is the correct DOI for [this article](https://aip.scitation.org/doi/10.1063/1.5110375) (and for which the page number is actually an article number).


## Details

You are welcomed [to contribute ](https://github.com/pierre-24/goto-publication/pulls) and [report issues or make suggestions](https://github.com/pierre-24/goto-publication/issues).

For the backend, this web server relies on [Flask](https://flask.palletsprojects.com/), which is a small web development package.
The API is powered by [Flask-RESTful](https://flask-restful.readthedocs.io/).
To extract info in webpages, [beautifulsoup](https://www.crummy.com/software/BeautifulSoup/) is sometimes involved.

For the frontend the following NPM packages are used:

+ [`autocompleter`](https://www.npmjs.com/package/autocompleter) for a powerful (yet simple) autocompletion,
+ [`clipboard-copy`](https://www.npmjs.com/package/clipboard-copy) to copy stuffs in clipboard,
+ [`gulp`](https://gulpjs.com/) (and [many plugins](./package.json)) to build the front,
+ [`browserify`](https://www.npmjs.com/package/browserify) to pack everything in one JS file,
+ [`less`](http://lesscss.org/) for the CSS.

I am not fluent in Javascript, so pardon me ;)