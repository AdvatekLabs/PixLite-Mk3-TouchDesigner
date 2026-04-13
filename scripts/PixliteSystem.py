"""
PixliteSystem - System configuration mixin for Pixlite extension

This module provides system configuration including:
- Device name
- IP address configuration (Static/DHCP)
- Indicator LEDs enable/disable
"""


class PixliteSystemMixin:
    """System configuration for Pixlite extension."""

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _SyncSystemConfigFromDevice(self, config):
        """Update TD system parameters from device config."""
        if not config:
            return

        self._syncingFromDevice = True
        try:
            # Device settings
            dev = config.get('dev', {})
            if 'nickname' in dev:
                self.ownerComp.par.Sysname = dev['nickname']
            if 'indsEn' in dev:
                self.ownerComp.par.Sysledsen = dev['indsEn']

            # Network settings
            net = config.get('net', {})
            if 'ipMode' in net:
                self.ownerComp.par.Sysipmode = net['ipMode']
            if 'staticIpAddr' in net:
                self.ownerComp.par.Sysipaddr = net['staticIpAddr']
            if 'staticNetmask' in net:
                self.ownerComp.par.Sysnetmask = net['staticNetmask']
            if 'staticGateway' in net:
                self.ownerComp.par.Sysgateway = net['staticGateway']

        finally:
            self._syncingFromDevice = False

    # =========================================================================
    # Parameter Change Handlers (UI only, no auto-apply)
    # =========================================================================

    def par_Sysname(self, par):
        """Handle device name change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Sysipmode(self, par):
        """Handle IP mode change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Sysipaddr(self, par):
        """Handle IP address change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Sysnetmask(self, par):
        """Handle subnet mask change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Sysgateway(self, par):
        """Handle gateway change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Sysledsen(self, par):
        """Handle indicator LEDs change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    # =========================================================================
    # Apply/Save/Revert Button Handlers
    # =========================================================================

    def pulse_Sysapply(self):
        """Apply system changes to device (temporary)."""
        self._SendSystemConfig(save=False)

    def pulse_Syssave(self):
        """Save system changes to device (permanent)."""
        self._SendSystemConfig(save=True)

    def pulse_Sysrevert(self):
        """Revert local changes and reload from device."""
        if self._connected:
            self.GetConfig()

    def _SendSystemConfig(self, save=False):
        """Send all current System settings to device."""
        if not self._connected:
            return

        action = 'save' if save else 'apply'

        # Build config from current parameter values
        devConfig = {
            'nickname': self.ownerComp.par.Sysname.eval(),
            'indsEn': self.ownerComp.par.Sysledsen.eval(),
        }

        netConfig = {
            'ipMode': self.ownerComp.par.Sysipmode.eval(),
        }

        # Only include static IP fields if in Static mode
        if self.ownerComp.par.Sysipmode.eval() == 'Static':
            netConfig['staticIpAddr'] = self.ownerComp.par.Sysipaddr.eval()
            netConfig['staticNetmask'] = self.ownerComp.par.Sysnetmask.eval()
            netConfig['staticGateway'] = self.ownerComp.par.Sysgateway.eval()

        params = {
            'action': action,
            'config': {
                'dev': devConfig,
                'net': netConfig
            }
        }
        self._SendRequest('configChange', params=params)
