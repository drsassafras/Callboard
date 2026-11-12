function stIdenticon(id) {
    const value = String(id).replace(/[\W_]/g, ""); let cells = "";
    for (let row = 0; row < 5; row++) {
      for (let col = 2; col >= 0; col--) {
        if (value.charCodeAt(row + col * 5) % 2) continue;
        cells += '<rect x="' + col + '" y="' + row + '" width="1" height="1"/>';
        if (col !== 2) cells += '<rect x="' + (4 - col) + '" y="' + row + '" width="1" height="1"/>';
      }
    }
    return '<svg class="identicon" viewBox="0 0 5 5" shape-rendering="crispEdges" aria-hidden="true"><g fill="currentColor">' + cells + "</g></svg>";
  }
