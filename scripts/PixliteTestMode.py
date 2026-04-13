"""
PixliteTestMode - Test mode functionality mixin for Pixlite extension

This module provides test mode control including:
- Setting test patterns (RGBW cycle, color fade, set color)
- Syncing test mode state from device
- Parameter change handlers
"""


class PixliteTestModeMixin:
    """Test mode functionality for Pixlite extension."""

    # =========================================================================
    # Public API - Test Mode
    # =========================================================================

    def SetTestMode(self, mode, color=None, colorRes='8Bit', pixPortNum=0, pixNum=0, callback=None):
        """
        Set test mode on the device.

        Args:
            mode: 'disabled', 'rgbwCycle', 'colorFade', or 'setColor'
            color: [R, G, B, W] array for setColor mode
            colorRes: '8Bit' or '16Bit'
            pixPortNum: Port to test (0 = all)
            pixNum: Pixel to test (0 = all)
            callback: Optional callback(result, error)
        """
        if mode == 'disabled':
            return self._SendRequest('modeLive', callback=callback)

        params = {'op': mode}
        if mode == 'setColor' and color:
            params['color'] = color
            params['colorRes'] = colorRes
        if pixPortNum > 0:
            params['pixPortNum'] = pixPortNum
        if pixNum > 0:
            params['pixNum'] = pixNum

        return self._SendRequest('modeTestData', params=params, callback=callback)

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _ApplyTestMode(self):
        """Apply test mode settings from parameters."""
        if self._syncingFromDevice:
            return  # Don't push back while syncing from device
        if not self._connected:
            return

        mode = self.ownerComp.par.Testmode.eval()
        color = [
            int(self.ownerComp.par.Testcolorr.eval()),
            int(self.ownerComp.par.Testcolorg.eval()),
            int(self.ownerComp.par.Testcolorb.eval()),
            int(self.ownerComp.par.Testcolorw.eval()),
        ]
        colorRes = self.ownerComp.par.Testcolorres.eval()

        # Convert menu selections to API values
        pixPortNum = 0  # 0 = all
        if self.ownerComp.par.Testoutputmode.eval() == 'individual':
            pixPortNum = int(self.ownerComp.par.Testoutputnum.eval())

        pixNum = 0  # 0 = all
        if self.ownerComp.par.Testpixelmode.eval() == 'individual':
            pixNum = int(self.ownerComp.par.Testpixelnum.eval())

        self.SetTestMode(mode, color=color, colorRes=colorRes,
                         pixPortNum=pixPortNum, pixNum=pixNum)

    def _SyncTestModeFromStatus(self, status):
        """Update TD test mode parameters from device status."""
        if not status:
            return

        self._syncingFromDevice = True
        try:
            mode = status.get('mode', 'live')
            params = status.get('params', {})

            # Map device mode to parameter value
            if mode == 'live':
                self.ownerComp.par.Testmode = 'disabled'
            elif mode == 'testData':
                op_mode = params.get('op', 'rgbwCycle')
                self.ownerComp.par.Testmode = op_mode

                # Sync color if setColor mode
                if op_mode == 'setColor':
                    color = params.get('color', [0, 0, 0, 0])
                    self.ownerComp.par.Testcolorr = color[0] if len(color) > 0 else 0
                    self.ownerComp.par.Testcolorg = color[1] if len(color) > 1 else 0
                    self.ownerComp.par.Testcolorb = color[2] if len(color) > 2 else 0
                    self.ownerComp.par.Testcolorw = color[3] if len(color) > 3 else 0
                    self.ownerComp.par.Testcolorres = params.get('colorRes', '8Bit')

                # Sync filter settings
                pixPortNum = params.get('pixPortNum', 0)
                if pixPortNum == 0:
                    self.ownerComp.par.Testoutputmode = 'all'
                else:
                    self.ownerComp.par.Testoutputmode = 'individual'
                    self.ownerComp.par.Testoutputnum = pixPortNum

                pixNum = params.get('pixNum', 0)
                if pixNum == 0:
                    self.ownerComp.par.Testpixelmode = 'all'
                else:
                    self.ownerComp.par.Testpixelmode = 'individual'
                    self.ownerComp.par.Testpixelnum = pixNum
        finally:
            self._syncingFromDevice = False

    # =========================================================================
    # Parameter Change Handlers
    # =========================================================================

    def par_Testmode(self, par):
        self._ApplyTestMode()

    def par_Testcolorr(self, par):
        self._ApplyTestMode()

    def par_Testcolorg(self, par):
        self._ApplyTestMode()

    def par_Testcolorb(self, par):
        self._ApplyTestMode()

    def par_Testcolorw(self, par):
        self._ApplyTestMode()

    def par_Testcolorres(self, par):
        self._ApplyTestMode()

    def par_Testoutputmode(self, par):
        self._ApplyTestMode()

    def par_Testoutputnum(self, par):
        self._ApplyTestMode()

    def par_Testpixelmode(self, par):
        self._ApplyTestMode()

    def par_Testpixelnum(self, par):
        self._ApplyTestMode()
