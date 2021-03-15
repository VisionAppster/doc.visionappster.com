docsearch({
  appId: 'MNFG6E4KCT',
  apiKey: 'ab1dd5e10c75cf48a5b36bde9bc3d44f',
  indexName: 'visionappster',
  // Replace inputSelector with a CSS selector
  // matching your search input
  inputSelector: '#rtd-search-form input[type=text]',
  // Set debug to true if you want to inspect the dropdown
  debug: false,
  algoliaOptions: {
    hitsPerPage: 8,
  }
});

// Close search popup on hamburger menu click (on mobile)
document.querySelector('.wy-nav-top [data-toggle=wy-nav-top]').addEventListener('click', () => {
  document.getElementById('algolia-autocomplete-listbox-0').style.display = 'none';
});
