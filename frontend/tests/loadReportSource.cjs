const fs = require('node:fs');
const path = require('node:path');

// Resolver los módulos locales ES sin cambiar el formato del proyecto Vue.
function loadReportSource(filename) {
  return fs.readFileSync(filename, 'utf8').replace(/from\s+(['"])(\.{1,2}\/[^'"]+)\1/g, (_, quote, relative) => {
    const dependency = path.resolve(path.dirname(filename), relative.endsWith('.js') ? relative : `${relative}.js`);
    const url = `data:text/javascript;base64,${Buffer.from(loadReportSource(dependency)).toString('base64')}`;
    return `from ${JSON.stringify(url)}`;
  });
}

module.exports = { loadReportSource };
