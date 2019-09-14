module.exports = {
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

