![The logo. I suck at that ;)](./assets/images/logo.svg)

# GOTO publication

*Citation-based URL/DOI searches and redirections*, by [Pierre Beaujean](https://pierrebeaujean.net).

Because the journal, the volume and the page should be enough to find an article (for which, of course, you don't have the DOI, otherwise this is stupid).

**Note:** Since I have a (quantum) chemistry background, I will limit this project to the journals that are in the chemistry and physics fields.
Feel free to fork the project if you want something else :)

## Installation and usage

First, [clone the repository](https://help.github.com/en/articles/cloning-a-repository).

Then, install the requirements: 

+ for the **backend**, you need [python 3.6](https://www.python.org/) and [pipenv](https://docs.pipenv.org/en/latest/),
+ for the **frontend**, you need [node](https://nodejs.org/en/) (consider an installation via [nvm](https://github.com/nvm-sh/nvm)).

Finally, the [Makefile](./Makefile) contains the install commands:

```bash
make init # install backend and dependancies
make front # install frontend and dependancies
```

To launch the website, use

```bash
make run
```

A web server (in **debug mode**) should be accessible at [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

## API

While the web server runs, an API is accessible.
All request are done in `GET`.

### `/api/providers` and `/api/journals`

Parameters | Value
-----------|-------
`start` | Result offset
`count` | Number of results (must be between 0 and 100)

List the providers of journals (`/api/providers`) or the journals (`/api/journals`) that are available.

Examples: 

+ the request [`/api/providers?count=2`](http://localhost:5000/api/providers?count=2) results in 

```json
{
    "start": 0,
    "count": 2,
    "total": 9,
    "providers": [
        {
            "providerName": "American Chemical Society",
            "providerIcon": "https://pubs.acs.org/favicon.ico",
            "providerWebsite": "https://pubs.acs.org/"
        },
        {
            "providerName": "American Physical Society",
            "providerIcon": "https://cdn.journals.aps.org/development/journals/images/favicon.ico",
            "providerWebsite": "https://journals.aps.org/"
        }
    ]
}
```

+ the request [`/api/journals?count=2`](http://localhost:5000/api/journals?count=2) results in 

```json
{
    "start": 0,
    "count": 2,
    "total": 1378,
    "journals": [
        {
            "journal": "Accounts of Chemical Research",
            "abbreviation": "Acc Chem Res",
            "providerName": "American Chemical Society",
            "providerIcon": "https://pubs.acs.org/favicon.ico",
            "providerWebsite": "https://pubs.acs.org/"
        },
        {
            "journal": "ACS Applied Bio Materials",
            "abbreviation": "ACS Appl Bio Mater",
            "providerName": "American Chemical Society",
            "providerIcon": "https://pubs.acs.org/favicon.ico",
            "providerWebsite": "https://pubs.acs.org/"
        }
    ]
}
```

### `/api/suggests`

Parameters | Value
-----------|-------
`q` (**mandatory**) | Any string
`source` | Search in journal names (`name`, default) or abbreviations (`abbr`)
`count` | Number of results (must be between 0 and 100)
`cutoff` | Severity cutoff on the results (must be between 0 and 1, the larger, the severer)

Suggest (at most) ten journals for which the `source` field (name or abbreviation) is the closest to `q`.

Example: the request [`/api/suggests?q=chemical`](http://localhost:5000/api/suggests?q=chemical) results in:

```json
{
    "request": "chemical",
    "source": "name",
    "count": 10,
    "cutoff": 0.6,
    "suggestions": [
        "Chemical Papers",
        "Chemical Science",
        "Chemical Reviews",
        "Chemical Physics",
        "Chem",
        "ChemCatChem",
        "ChemBioChem"
    ]
}
```

### `/api/url` and `/api/doi`

Parameters | Value
-----------|-------
`journal` (**mandatory**) | Valid journal, obtained via `/api/suggests`
`volume` (**mandatory**) | Volume number (may be the year for certain providers)
`page`  (**mandatory**) | Page number (may be the article number for certain providers)
`apiKey` | Valid key to use the provider API. Only required for DOI search in [Elsevier](https://dev.elsevier.com/).

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

You are welcomed [to contribute](https://github.com/pierre-24/goto-publication/pulls) and [report issues or make suggestions](https://github.com/pierre-24/goto-publication/issues).

For the backend, this web server relies on [Flask](https://flask.palletsprojects.com/), which is a small web development package.
The API is powered by [Flask-RESTful](https://flask-restful.readthedocs.io/), and rate limits are enforced by [Flask-Limiter](https://flask-limiter.readthedocs.io/).
To extract info in webpages, [beautifulsoup](https://www.crummy.com/software/BeautifulSoup/) is sometimes involved.

For the frontend the following NPM packages are used:

+ [`autocompleter`](https://www.npmjs.com/package/autocompleter) for a powerful (yet simple) autocompletion,
+ [`clipboard-copy`](https://www.npmjs.com/package/clipboard-copy) to copy stuffs in clipboard,
+ [`gulp`](https://gulpjs.com/) (and [many plugins](./package.json)) to build the front,
+ [`browserify`](https://www.npmjs.com/package/browserify) to pack everything in one JS file,
+ [`less`](http://lesscss.org/) for the CSS.

I am not fluent in Javascript, so pardon me ;)