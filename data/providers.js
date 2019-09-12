module.exports = {
  "aip": {
    "name": "American Institute of Physics",
    "method": "GET",
    "action": (journal, volume, page) => {
      let url = "https://aip.scitation.org/action/quickLink";
      url += '?quickLinkJournal=' + journal + '&quickLinkVolume=' + volume + '&quickLinkPage=' + page + '&quickLink=true';
      return url;
    }
  },
  "acs": {
    "name": "American Chemical Society",
    "method": "GET",
    "action": (journal, volume, page) => {
      let url = "https://pubs.acs.org/action/quickLink";
      url += '?quickLinkJournal=' + journal + '&quickLinkVolume=' + volume + '&quickLinkPage=' + page + '&quickLink=true';
      return url;
    }
  },
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
  },
  "wiley": {
    "name": "Wiley",
    "method": "GET",
    "action": (journal, volume, page) => {
      let url = "https://onlinelibrary.wiley.com/action/quickLink";
      url += '?quickLinkJournal=' + journal + '&quickLinkVolume=' + volume + '&quickLinkPage=' + page + '&quickLink=true';
      /*let article_url = '';
      $.ajax({
        url: url,
        dataType: "json",
        async: false, // blocking request
        success: result => {
          if('link' in result)
            article_url = 'https://onlinelibrary.wiley.com/' + result['link'];
          else
            flash_error('Cannot find article in Wiley');
        },
        error: (xhr, status, error) => console.log(status + ', ' + error)
      });*/

      return url;
    }
  }
};

