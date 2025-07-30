document.addEventListener('DOMContentLoaded', () => {
  // Table sorting
  document.querySelectorAll('th').forEach((header, index) => {
    header.addEventListener('click', () => {
      const table = header.closest('table');
      const rows = Array.from(table.querySelectorAll('tbody tr'));
      const asc = !header.classList.contains('asc');
      rows.sort((a, b) => {
        const aText = a.children[index].textContent.trim();
        const bText = b.children[index].textContent.trim();
        return asc ? aText.localeCompare(bText, undefined, {numeric:true})
                   : bText.localeCompare(aText, undefined, {numeric:true});
      });
      table.querySelectorAll('th').forEach(th => th.classList.remove('asc','desc'));
      header.classList.add(asc ? 'asc' : 'desc');
      rows.forEach(row => table.querySelector('tbody').appendChild(row));
    });
  });

  // Highlight row logic
  function highlightRow(row, price) {
    const majorSupport = parseFloat(row.children[4].innerText);
    const minorSupport = parseFloat(row.children[5].innerText);
    const supportLevels = [majorSupport, minorSupport].filter(n => !isNaN(n));
    const resistance1 = parseFloat(row.children[7].innerText);
    const resistance2 = parseFloat(row.children[8].innerText);
    const resistanceLevels = [resistance1, resistance2].filter(n => !isNaN(n));
    const stop = parseFloat(row.children[9].innerText);

    const breachedSupport = supportLevels.some(s => price < s);
    const isNearSupport = supportLevels.some(s => Math.abs(price - s) / s < 0.02 && price >= s);
    row.classList.remove('near-stop','near-support','near-breakout');
    if (breachedSupport) row.classList.add('near-stop');
    else if (isNearSupport) row.classList.add('near-support');
    if (resistanceLevels.some(r => Math.abs(price - r) / r < 0.02)) row.classList.add('near-breakout');
  }

  // Apply static highlighting
  document.querySelectorAll('#strategyTable tbody tr').forEach(row => {
    const staticPrice = parseFloat(row.children[6].innerText) || 0;
    highlightRow(row, staticPrice);
  });

  // Color-code action badges
  document.querySelectorAll('.action-badge').forEach(badge => {
    const text = badge.textContent.toLowerCase();
    badge.classList.add('bg-secondary','text-light');
    if (text.includes('sell') || text.includes('take profit') || text.includes('target hit')) {
      badge.classList.replace('bg-secondary','bg-success');
    } else if (text.includes('stop') || text.includes('exit') || text.includes('cut')) {
      badge.classList.replace('bg-secondary','bg-danger');
    } else if (text.includes('watch') || text.includes('alert')) {
      badge.classList.replace('bg-secondary','bg-warning');
    } else if (text.includes('info') || text.includes('pending')) {
      badge.classList.replace('bg-secondary','bg-info');
    }
  });

  // Enable Bootstrap tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(el => new bootstrap.Tooltip(el));
});