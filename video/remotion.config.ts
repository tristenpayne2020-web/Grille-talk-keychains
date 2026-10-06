/**
 * Note: When using the Node.JS APIs, the config file
 * doesn't apply. Instead, pass options directly to the APIs.
 *
 * All configuration options: https://remotion.dev/docs/config
 */

import { Config } from "@remotion/cli/config";

Config.setRspack(true);
Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(95);
Config.setOverwriteOutput(true);
// WebGL on the GPU (ANGLE / Direct3D on Windows); the 3D scenes need it
Config.setChromiumOpenGlRenderer("angle");
// H.264, CRF 18, yuv420p, AAC (the brief's delivery spec)
Config.setCodec("h264");
Config.setCrf(18);
Config.setPixelFormat("yuv420p");
Config.setAudioCodec("aac");
// each 3D scene owns a WebGL canvas: fewer parallel tabs keep Chrome under its WebGL context limit
Config.setConcurrency(4);
Config.setDelayRenderTimeoutInMilliseconds(120000);
