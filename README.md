# PixLite Mk3 TouchDesigner Plugin

A community-built TouchDesigner component for real-time control and pixel-data
workflows with Advatek PixLite Mk3 controllers.

> [!IMPORTANT]
> This is an early-stage, unofficial community project. It is not supported by
> Advatek Lighting, and features or compatibility may change.

## What it does

The component connects TouchDesigner to a PixLite Mk3 controller over its
WebSocket API. It can:

- read and update system, pixel-output and auxiliary-port settings;
- control test mode and monitor controller statistics;
- send pixel data from a TouchDesigner POP; and
- support interactive visuals, prototyping and show-control workflows.

## Compatibility

- Advatek PixLite Mk3 controllers
- PixLite WebSocket API v1.7
- Windows or macOS
- A TouchDesigner build with Python extensions and WebSocket DAT support
- A network connection between TouchDesigner and the PixLite controller

Exact TouchDesigner build compatibility has not yet been formally qualified.
Use a current production build and report any compatibility problems through
[GitHub Issues](https://github.com/advatekcommunitylabs/PixLite-Mk3-TouchDesigner/issues).

## Installation

1. Download or clone this repository.
2. From the repository root, run the setup script for your operating system:
   - Windows PowerShell: `.\setup.ps1`
   - macOS Terminal: `bash setup.sh`
3. Restart TouchDesigner so it can read the `TD_PIXLITE` environment variable.
4. Add [`tox/Pixlite.tox`](tox/Pixlite.tox) to your TouchDesigner project.
5. On the component's **Connection** page, enter the PixLite controller's IP
   address and credentials.
6. Connect the component, configure the required outputs or input source, and
   begin your workflow.

## Project status

This project is suitable for experimentation, live visuals and rapid
prototyping. Review the [changelog](CHANGELOG.md) for recent changes before
updating an existing project.

## Contributing

Bug reports, improvements and pull requests are welcome.

- Open an issue before starting a substantial change.
- Create feature and fix branches from `main`.
- Open pull requests against `main`.
- Reference the related issue in the pull request when one exists.

## Support and disclaimer

This plugin is not affiliated with or supported by Advatek Lighting. For
official product documentation and support, visit
[Advatek Lighting](https://www.advateklighting.com).

## License

Licensed under the [MIT License](LICENSE).
