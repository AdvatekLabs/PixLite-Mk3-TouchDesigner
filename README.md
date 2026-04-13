# PixLite TouchDesigner Plugin

Unofficial TouchDesigner plugin for Advatek PixLite controllers, built by the community.

---

## Overview

This project enables real-time integration between TouchDesigner and Advatek PixLite devices. It provides a simple interface for sending pixel data, managing outputs, and incorporating PixLite controllers into interactive and generative visual workflows.

Designed for experimentation, live visuals, and rapid prototyping.

## Features

- Integration with PixLite Mk3 controllers  
- Lightweight and flexible workflow  
- Designed for creative coding and show control environments  

## Getting Started

1. Download or clone this repository
2. Run the setup script
   - a. WINDOWS: run ```setup.ps1```
   - b. OSX: run ```setup.sh```
2. Add the tox file to your TouchDesigner project (```tox/Pixlite.tox```)
3. Configure your PixLite device (IP, outputs, protocol)  
4. Connect your TouchDesigner network to the plugin
5. Start sending pixel data  

## Requirements

- TouchDesigner (latest recommended build)  
- Advatek PixLite Mk3 controller  
- Network connection between host machine and device  

## Status

This is an early-stage, community-driven project. Features may change and stability is not guaranteed.

## Contributing

Contributions are welcome. If you have improvements, bug fixes, or ideas, feel free to open an issue or submit a pull request.

Please open all pull requests against the `dev` branch.

Create feature and fix branches from `dev`.

If an issue exists, include the issue number in your pull request.

---

## Disclaimer

This is an unofficial plugin and is not affiliated with or supported by Advatek Lighting.  

For official documentation and support, visit:  
https://www.advateklighting.com

---

## License

Licensed under the MIT License. See `LICENSE` for details.
