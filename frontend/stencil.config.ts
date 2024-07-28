import { Config } from '@stencil/core';
import { sass } from '@stencil/sass';

export const config: Config = {
  namespace: 'esrihackathon',
  outputTargets: [
    {
      type: 'dist',
      esmLoaderPath: '../loader',
    },
    {
      type: 'dist-custom-elements',
      customElementsExportBehavior: 'auto-define-custom-elements',
      externalRuntime: false,
    },
    {
      type: 'docs-readme',
    },
    {
      type: 'www',
      serviceWorker: null, // disable service workers
      copy: [{ src: 'media', dest: 'build/media' }],
    },
  ],
  testing: {
    browserHeadless: 'new',
  },
  plugins: [
    sass({
      includePaths: ['./node_modules/'],
    }),
  ],
};
