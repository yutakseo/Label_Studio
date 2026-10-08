"""Show tree export on project pages even without a Settings navigation link."""
from pathlib import Path
import argparse

OLD = '''  const mount = () => {
    if (button.isConnected) return;
    const settings = [...document.querySelectorAll('a,button')].find(e =>
      /^(Settings|설정)$/.test(e.textContent.trim()) && e.getBoundingClientRect().width > 0);
    if (settings) settings.insertAdjacentElement('beforebegin', button);
  };'''
NEW = '''  const mount = () => {
    if (button.isConnected) return;
    // Keep export available in both Data Manager and the labeling screen.
    button.style.cssText = 'position:fixed;right:24px;bottom:76px;z-index:9999;padding:10px 16px;border:1px solid #879bff;border-radius:6px;background:#384b92;color:white;cursor:pointer;font:inherit';
    document.body.append(button);
  };'''


def patch(source):
    if NEW in source:
        return source
    if source.count(OLD) != 1:
        raise ValueError('Unsupported tree export button anchor')
    return source.replace(OLD, NEW, 1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('panel', type=Path)
    args = parser.parse_args()
    source = args.panel.read_text()
    result = patch(source)
    if result != source:
        args.panel.write_text(result)
