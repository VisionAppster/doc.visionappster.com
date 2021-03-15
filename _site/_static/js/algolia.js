docsearch({
  appId: 'AOWZ909P6D',
  apiKey: '57c6eeb255d542f3ae88b288ea12928e',
  indexName: 'doc-3-0-beta5',
  // Replace inputSelector with a CSS selector
  // matching your search input
  inputSelector: '#rtd-search-form input[type=text]',
  // Set debug to true if you want to inspect the dropdown
  debug: false,
  algoliaOptions: {
    hitsPerPage: 8,
  },
  transformData: hits => {
    const match = document.URL.match(/https?:\/\/[^/]*(\/[^/]*)/);
    const root = match ? match[1] : '';
    for (const hit of hits) {
      if (typeof hit.url === 'string') {
        // Make relative to the root of this site
        hit.url = hit.url.replace(/https?:\/\/[^/]*/, root);
      }
    }
    return hits;
  }
});

// Close search popup on hamburger menu click (on mobile)
document.querySelector('.wy-nav-top [data-toggle=wy-nav-top]').addEventListener('click', () => {
  document.getElementById('algolia-autocomplete-listbox-0').style.display = 'none';
});
