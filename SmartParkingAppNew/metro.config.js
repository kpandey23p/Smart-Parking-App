const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Exclude the other SmartParkingApp directory to avoid naming conflicts
config.resolver.blacklistRE = /.*SmartParkingApp.*/;

module.exports = config;
