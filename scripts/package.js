const { spawnSync } = require('child_process');
const { Builder } = require('./build');
const { MSICreator } = require('electron-wix-msi');
const path = require('path');

const builder = new Builder();

// Define input and output directories
const resolvePath = (directory) => {
  return path.resolve(__dirname, directory);
};

/**
 * @namespace Packager
 * @description - Packages app for various operating systems.
 */
class Packager {

  /**
   * @description - Creates DEB installer for linux.
   * @memberof Packager
   *
   * @tutorial https://github.com/electron-userland/electron-installer-debian
   */
  packageLinux = () => {

    // Build Python & React distribution files
    builder.buildAll();

    const options = {
      build: [
        'app',
        '--extra-resource=./resources',
        '--icon ./public/favicon.ico',
        '--platform linux',
        '--arch x64',
        '--out',
        './dist/linux',
        '--overwrite',
        '--executable-name=flash-for-anki'
      ].join(' '),

      package: [
        `--src ${resolvePath('../dist/linux/app-linux-x64/')}`,
        'flash-for-anki',
        `--dest ${resolvePath('../dist/linux/setup')}`,
        '--arch amd64',
        `--icon ${resolvePath('../utilities/deb/images/icon.ico')}`,
        `--background ${resolvePath('../utilities/deb/images/background.png')}`,
        '--title "FLASH - Flashcard Leveraging Agentic Study Help"',
        '--overwrite'
      ].join(' '),

      spawn: { detached: false, shell: true, stdio: 'inherit' }
    };

    spawnSync(`electron-packager . ${options.build}`, options.spawn);
    spawnSync(`electron-installer-debian ${options.package}`, options.spawn);
  };


  /**
   * @description - Creates DMG installer for macOS.
   * @memberof Packager
   *
   * @tutorial https://github.com/electron-userland/electron-installer-dmg
   */
  packageMacOS = () => {

    // Build Python & React distribution files
    builder.buildAll();

    const options = {
      build: [
        'app',
        '--extra-resource=./resources',
        '--icon ./public/favicon.ico',
        '--platform darwin',
        '--arch x64',
        '--out',
        './dist/mac',
        '--overwrite'
      ].join(' '),

      package: [
        resolvePath('../dist/mac/app-darwin-x64/app.app'),
        'flash-for-anki',
        `--out=${resolvePath('../dist/mac/setup')}`,
        `--icon=${resolvePath('../utilities/dmg/images/icon.icns')}`,
        `--background=${resolvePath('../utilities/dmg/images/background.png')}`,
        '--title="FLASH - Flashcard Leveraging Agentic Study Help"',
        '--overwrite'
      ].join(' '),

      spawn: { detached: false, shell: true, stdio: 'inherit' }
    };

    spawnSync(`electron-packager . ${options.build}`, options.spawn);
    spawnSync(`electron-installer-dmg ${options.package}`, options.spawn);
  };


  /**
   * @description - Creates MSI installer for Windows.
   * @memberof Packager
   *
   * @tutorial https://github.com/felixrieseberg/electron-wix-msi
   */
  packageWindows = () => {

    // eslint-disable-next-line no-console
    console.log('Building windows package...');

    // Build Python & React distribution files
    builder.buildAll();

    const options = {
      app: [
        'app',
        '--asar',
        '--extra-resource=./resources/app',
        '--icon ./public/favicon.ico',
        '--platform win32',
        '--arch x64',
        '--out',
        './dist/windows',
        '--overwrite',
        '--executable-name=FLASH'
      ].join(' '),

      spawn: { detached: false, shell: true, stdio: 'inherit' }
    };

    const result = spawnSync(`electron-packager . ${options.app}`, options.spawn);
    if (result.error) {
      console.error('Error during Electron packaging:', result.error);
      return;
    }
    console.log('Electron packaging completed.');

    const appDirectory = resolvePath('../dist/windows/app-win32-x64');
    const outputDirectory = resolvePath('../dist/windows/setup');
    const iconPath = resolvePath('../utilities/msi/images/icon.ico');

    console.log(`App directory: ${appDirectory}`);
    console.log(`Output directory: ${outputDirectory}`);
    console.log(`Icon path: ${iconPath}`);

    const msiCreator = new MSICreator({
      appDirectory,
      appIconPath: iconPath,
      description: 'FLASH - Flashcard Leveraging Agentic Study Help',
      exe: 'FLASH',
      manufacturer: 'Linus A. Schneider',
      name: 'FLASH for Anki',
      outputDirectory,
      ui: {
        chooseDirectory: true,
        images: {
          background: resolvePath('../utilities/msi/images/background.png'),
          banner: resolvePath('../utilities/msi/images/banner.png')
        }
      },
      version: '1.0.0'
    });

    // Customized MSI template
    msiCreator.wixTemplate = msiCreator.wixTemplate
      .replace(/ \(Machine - MSI\)/gi, '')
      .replace(/ \(Machine\)/gi, '');

    console.log('Creating .wxs template...');
    msiCreator.create()
      .then(() => {
        console.log('Template created successfully. Compiling MSI...');
        return msiCreator.compile();
      })
      .then(() => {
        console.log('MSI compilation completed successfully.');
      })
      .catch(error => {
        console.error('Error creating or compiling MSI:', error);
      });
  };
}

module.exports.Packager = Packager;
