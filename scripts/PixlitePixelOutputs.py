"""
PixlitePixelOutputs - Pixel output configuration mixin for Pixlite extension

This module provides pixel output configuration including:
- Global pixel settings (pixel type, color type, gamma, etc.)
- Syncing pixel config from device
- Parameter change handlers
- Dynamic pixel type menu population from device constants
"""


class PixlitePixelOutputsMixin:
    """Pixel output configuration for Pixlite extension."""

    # =========================================================================
    # Public API - Pixel Configuration
    # =========================================================================

    def SetPixelConfig(self, config, save=False, callback=None):
        """
        Apply pixel output configuration changes.

        Args:
            config: Dict of pix configuration values to change
            save: If True, save to non-volatile memory
            callback: Optional callback(result, error)
        """
        action = 'save' if save else 'apply'
        params = {
            'action': action,
            'config': {'pix': config}
        }
        return self._SendRequest('configChange', params=params, callback=callback)

    def PopulatePixelTypeMenu(self):
        """
        Populate Pixtype menu from device constants.
        Should be called after constants are received.
        """
        constants = self.Data.get('constants')
        if not constants:
            return

        pixTypes = constants.get('pixTypes', [])
        if not pixTypes:
            return

        # Build menu names and labels from pixTypes
        menuNames = []
        menuLabels = []
        for pt in pixTypes:
            name = pt.get('pixType', '')
            if name:
                menuNames.append(name)
                menuLabels.append(name)

        if menuNames:
            self.ownerComp.par.Pixtype.menuNames = menuNames
            self.ownerComp.par.Pixtype.menuLabels = menuLabels

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _SyncPixelConfigFromDevice(self, config):
        """Update TD pixel output parameters from device config."""
        if not config:
            return

        pix = config.get('pix', {})
        if not pix:
            return

        self._syncingFromDevice = True
        try:
            # Pixel type
            if 'pixType' in pix:
                self.ownerComp.par.Pixtype = pix['pixType']
            if 'colorType' in pix:
                self.ownerComp.par.Pixcolortype = pix['colorType']

            # Options
            if 'holdLastFrm' in pix:
                self.ownerComp.par.Pixholdlast = pix['holdLastFrm']
            if 'dropFrmOnOvrn' in pix:
                self.ownerComp.par.Pixdropframe = pix['dropFrmOnOvrn']
            if 'expand' in pix:
                self.ownerComp.par.Pixexpand = pix['expand']

            # Gamma
            if 'gammaOn' in pix:
                self.ownerComp.par.Pixgammaon = pix['gammaOn']
            if 'ditherOn' in pix:
                self.ownerComp.par.Pixditheron = pix['ditherOn']
            if 'gamma' in pix:
                gamma = pix['gamma']
                if len(gamma) > 0:
                    self.ownerComp.par.Pixgammar = gamma[0]
                if len(gamma) > 1:
                    self.ownerComp.par.Pixgammag = gamma[1]
                if len(gamma) > 2:
                    self.ownerComp.par.Pixgammab = gamma[2]
                if len(gamma) > 3:
                    self.ownerComp.par.Pixgammaw = gamma[3]

            # Playback
            if 'pbMode' in pix:
                self.ownerComp.par.Pixpbmode = pix['pbMode']

            # External Intensity
            if 'liveIntSrc' in pix:
                # API uses empty string for disabled, TD uses 'disabled'
                src = pix['liveIntSrc']
                self.ownerComp.par.Pixliveintsrc = 'disabled' if src == '' else src
            if 'liveIntUni' in pix:
                self.ownerComp.par.Pixliveintuni = pix['liveIntUni']
            if 'liveIntCh' in pix:
                self.ownerComp.par.Pixliveintch = pix['liveIntCh']

        finally:
            self._syncingFromDevice = False

    def _ApplyPixelConfigField(self, field, value):
        """Send a single config field change to device."""
        if self._syncingFromDevice:
            return
        if not self._connected:
            return
        self.SetPixelConfig({field: value})

    def _ApplyGamma(self):
        """Send gamma values to device."""
        if self._syncingFromDevice:
            return
        if not self._connected:
            return

        colorType = self.ownerComp.par.Pixcolortype.eval()
        if colorType == 'RGBW':
            gamma = [
                round(self.ownerComp.par.Pixgammar.eval(), 1),
                round(self.ownerComp.par.Pixgammag.eval(), 1),
                round(self.ownerComp.par.Pixgammab.eval(), 1),
                round(self.ownerComp.par.Pixgammaw.eval(), 1),
            ]
        else:
            gamma = [
                round(self.ownerComp.par.Pixgammar.eval(), 1),
                round(self.ownerComp.par.Pixgammag.eval(), 1),
                round(self.ownerComp.par.Pixgammab.eval(), 1),
            ]
        self.SetPixelConfig({'gamma': gamma})

    # =========================================================================
    # Parameter Change Handlers (UI only, no auto-apply)
    # =========================================================================

    def par_Pixtype(self, par):
        """Handle pixel type change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Pixcolortype(self, par):
        """Handle color type change (UI only, no auto-apply)."""
        if self._syncingFromDevice:
            return
        # Recalculate auto-patch when color type changes (affects channels per pixel)
        if hasattr(self, '_ApplyAutoPatch'):
            self._ApplyAutoPatch()
        # Update used/remaining status (color type affects channels per pixel)
        if hasattr(self, '_UpdateStatusParams'):
            self._UpdateStatusParams()

    def par_Pixholdlast(self, par):
        """Handle hold last frame change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Pixdropframe(self, par):
        """Handle drop frame change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Pixexpand(self, par):
        """Handle expand mode change (UI only, no auto-apply)."""
        if self._syncingFromDevice:
            return
        # Update port count when expand mode changes
        if hasattr(self, 'UpdatePortCount'):
            self.UpdatePortCount()

    def par_Pixgammaon(self, par):
        """Handle gamma on change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Pixditheron(self, par):
        """Handle dither on change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Pixgammar(self, par):
        """Handle gamma red change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Pixgammag(self, par):
        """Handle gamma green change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Pixgammab(self, par):
        """Handle gamma blue change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Pixgammaw(self, par):
        """Handle gamma white change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Pixpbmode(self, par):
        """Handle playback mode change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Pixliveintsrc(self, par):
        """Handle live intensity source change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Pixliveintuni(self, par):
        """Handle live intensity universe change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Pixliveintch(self, par):
        """Handle live intensity channel change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    # =========================================================================
    # Apply/Save/Revert Button Handlers
    # =========================================================================

    def pulse_Pixoutapply(self):
        """Apply all Pixel Outputs changes to device (temporary)."""
        self._SendPixelOutputsConfig(save=False)

    def pulse_Pixoutsave(self):
        """Save all Pixel Outputs changes to device (permanent)."""
        self._SendPixelOutputsConfig(save=True)

    def pulse_Pixoutrevert(self):
        """Revert local changes and reload from device."""
        if self._connected:
            self.GetConfig()  # This will trigger _SyncPixelConfigFromDevice

    def _SendPixelOutputsConfig(self, save=False):
        """Send all current Pixel Outputs settings to device."""
        if not self._connected:
            return

        action = 'save' if save else 'apply'

        # Build gamma array
        colorType = self.ownerComp.par.Pixcolortype.eval()
        if colorType == 'RGBW':
            gamma = [
                round(self.ownerComp.par.Pixgammar.eval(), 1),
                round(self.ownerComp.par.Pixgammag.eval(), 1),
                round(self.ownerComp.par.Pixgammab.eval(), 1),
                round(self.ownerComp.par.Pixgammaw.eval(), 1),
            ]
        else:
            gamma = [
                round(self.ownerComp.par.Pixgammar.eval(), 1),
                round(self.ownerComp.par.Pixgammag.eval(), 1),
                round(self.ownerComp.par.Pixgammab.eval(), 1),
            ]

        # Convert live intensity source
        liveIntSrc = self.ownerComp.par.Pixliveintsrc.eval()
        if liveIntSrc == 'disabled':
            liveIntSrc = ''

        # Get current config for fields we don't expose in UI
        currentConfig = self.Data.get('config', {}).get('pix', {})

        # Build complete pix config - API requires all fields
        pixConfig = {
            'dataSrc': self.ownerComp.par.Pixdatasrc.eval(),
            'pixType': self.ownerComp.par.Pixtype.eval(),
            'colorType': colorType,
            'freq': currentConfig.get('freq', 800),
            'expand': self.ownerComp.par.Pixexpand.eval(),
            'inFormat': self.ownerComp.par.Pixinformat.eval(),
            'pixsSpanUni': self.ownerComp.par.Pixspanuni.eval(),
            'gammaOn': self.ownerComp.par.Pixgammaon.eval(),
            'gamma': gamma,
            'ditherOn': self.ownerComp.par.Pixditheron.eval(),
            'dropFrmOnOvrn': self.ownerComp.par.Pixdropframe.eval(),
            'holdLastFrm': self.ownerComp.par.Pixholdlast.eval(),
            'liveIntSrc': liveIntSrc,
            'liveIntUni': int(self.ownerComp.par.Pixliveintuni.eval()),
            'liveIntCh': int(self.ownerComp.par.Pixliveintch.eval()),
            'pbMode': self.ownerComp.par.Pixpbmode.eval(),
            'curCtrlGbl': currentConfig.get('curCtrlGbl', 0),
            'curCtrlCol': list(currentConfig.get('curCtrlCol', [0, 0, 0, 0])),
        }

        # Send config
        params = {
            'action': action,
            'config': {'pix': pixConfig}
        }
        self._SendRequest('configChange', params=params)
