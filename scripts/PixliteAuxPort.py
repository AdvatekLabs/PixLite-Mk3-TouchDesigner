"""
PixliteAuxPort - Aux port configuration mixin for Pixlite extension

This module provides aux port (DMX512) configuration including:
- Mode selection (Off, DMX512 Output, DMX512 Input)
- Data source and universe settings
- Output color settings
- External intensity channel
"""


class PixliteAuxPortMixin:
    """Aux port (DMX512) configuration for Pixlite extension."""

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _SyncAuxPortConfigFromDevice(self, config):
        """Update TD aux port parameters from device config."""
        if not config:
            return

        auxPort = config.get('auxPort', {})
        if not auxPort:
            return

        self._syncingFromDevice = True
        try:
            # Helper to get first element of array
            def get(field, default):
                arr = auxPort.get(field, [])
                return arr[0] if arr else default

            self.ownerComp.par.Auxmode = get('mode', 'Off')

            # Data source - API uses empty string for default
            dataSrc = get('dataSrc', 'sACN')
            self.ownerComp.par.Auxdatasrc = dataSrc if dataSrc else 'sACN'

            self.ownerComp.par.Auxuni = get('uni', 1)
            self.ownerComp.par.Auxholdlast = get('holdLastFrm', False)
            self.ownerComp.par.Auxdropframe = get('dropFrmOnOvrn', True)
            self.ownerComp.par.Auxpbmode = get('pbMode', 'Play')
            self.ownerComp.par.Auxcolortype = get('colorType', 'RGB')
            self.ownerComp.par.Auxinformat = get('inFormat', '8Bit')
            self.ownerComp.par.Auxcolororder = get('colorOrder', 'RGB')

            # External intensity - enabled if liveIntSrc is not empty
            liveIntSrc = get('liveIntSrc', '')
            self.ownerComp.par.Auxextint = bool(liveIntSrc)

        finally:
            self._syncingFromDevice = False

    # =========================================================================
    # Parameter Change Handlers (UI only, no auto-apply)
    # =========================================================================

    def par_Auxmode(self, par):
        """Handle mode change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Auxdatasrc(self, par):
        """Handle data source change (UI only, no auto-apply)."""
        pass

    def par_Auxuni(self, par):
        """Handle universe change (UI only, no auto-apply)."""
        pass

    def par_Auxholdlast(self, par):
        """Handle hold last frame change (UI only, no auto-apply)."""
        pass

    def par_Auxdropframe(self, par):
        """Handle drop frame change (UI only, no auto-apply)."""
        pass

    def par_Auxpbmode(self, par):
        """Handle playback mode change (UI only, no auto-apply)."""
        pass

    def par_Auxcolortype(self, par):
        """Handle color type change (UI only, no auto-apply)."""
        pass

    def par_Auxinformat(self, par):
        """Handle input format change (UI only, no auto-apply)."""
        pass

    def par_Auxcolororder(self, par):
        """Handle color order change (UI only, no auto-apply)."""
        pass

    def par_Auxextint(self, par):
        """Handle external intensity change (UI only, no auto-apply)."""
        pass

    # =========================================================================
    # Apply/Save/Revert Button Handlers
    # =========================================================================

    def pulse_Auxapply(self):
        """Apply aux port changes to device (temporary)."""
        self._SendAuxPortConfig(save=False)

    def pulse_Auxsave(self):
        """Save aux port changes to device (permanent)."""
        self._SendAuxPortConfig(save=True)

    def pulse_Auxrevert(self):
        """Revert local changes and reload from device."""
        if self._connected:
            self.GetConfig()

    def _SendAuxPortConfig(self, save=False):
        """Send all current Aux Port settings to device."""
        if not self._connected:
            return

        action = 'save' if save else 'apply'

        # Build config arrays (single element for first aux port)
        auxPortConfig = {
            'mode': [self.ownerComp.par.Auxmode.eval()],
            'dataSrc': [self.ownerComp.par.Auxdatasrc.eval()],
            'uni': [int(self.ownerComp.par.Auxuni.eval())],
            'holdLastFrm': [self.ownerComp.par.Auxholdlast.eval()],
            'dropFrmOnOvrn': [self.ownerComp.par.Auxdropframe.eval()],
            'pbMode': [self.ownerComp.par.Auxpbmode.eval()],
            'colorType': [self.ownerComp.par.Auxcolortype.eval()],
            'inFormat': [self.ownerComp.par.Auxinformat.eval()],
            'colorOrder': [self.ownerComp.par.Auxcolororder.eval()],
            # External intensity: use data source if enabled, empty string if disabled
            'liveIntSrc': [self.ownerComp.par.Auxdatasrc.eval() if self.ownerComp.par.Auxextint.eval() else ''],
        }

        params = {
            'action': action,
            'config': {'auxPort': auxPortConfig}
        }
        self._SendRequest('configChange', params=params)
