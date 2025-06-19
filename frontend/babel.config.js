module.exports = {
  presets: [
    ['next/babel', { 'preset-react': { runtime: 'automatic' } }],
    '@babel/preset-typescript',
  ],
  plugins: [
    ['@babel/plugin-proposal-class-properties', { loose: true }],
    '@babel/plugin-syntax-jsx',
    'babel-plugin-transform-typescript-metadata',
  ],
};
