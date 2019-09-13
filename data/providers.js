module.exports = {
  "sd": {
    "name": "ScienceDirect (Elsevier)",
    "method": "GET",
    "action": (journal, volume, page) => {
      let url = "https://www.sciencedirect.com/search/advanced";
      url += '?cid=' + journal + '&volume=' + volume + '&page=' + page;
      return url;
    }
  },
  "sl": {
    "name": "SpringerLink (Springer)",
    "method": "GET",
    "action": (journal, volume, page) => {
      let url = "https://link.springer.com/journal/volumesAndIssues/";
      url += journal + '#volume' + volume;
      return url;
    }
  },
  "nature": {
    "name": "Nature",
    "method": "GET",
    "action": (journal, volume, page) => {
      let url = "https://www.nature.com/search";
      url += '?journal=' + journal + '&volume=' + volume + '&spage=' + page + '&order=relevance';
      return url;
    }
  }
};

