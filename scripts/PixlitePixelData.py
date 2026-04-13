"""
PixlitePixelData - Pixel data and per-port configuration mixin for Pixlite extension

This module provides pixel data configuration including:
- Global data source settings (data source, input format, span universes)
- Per-port pixel output configuration via TD sequences
- Dynamic port count based on device constants and expand mode
- Status calculations (pixels/universes used/remaining)
"""

import re


class PixlitePixelDataMixin:
    """Pixel data and per-port configuration for Pixlite extension."""

    # =========================================================================
    # Public API
    # =========================================================================

    def SetPixPortConfig(self, portIndex, field, value, save=False, callback=None):
        """
        Apply a single per-port configuration change.

        Args:
            portIndex: 0-based port index
            field: API field name (e.g., 'startUni', 'pixCount')
            value: Value to set
            save: If True, save to non-volatile memory
            callback: Optional callback(result, error)
        """
        # Build partial config with array update for single port
        # API expects full arrays, so we need to send just the changed element
        # Using configChange with path-based update
        action = 'save' if save else 'apply'

        # Build the pixPort config with the specific field as an array
        # We need to send the full array for this field
        currentConfig = self.Data.get('config', {}).get('pixPort', {})
        currentArray = list(currentConfig.get(field, []))

        # Ensure array is long enough
        while len(currentArray) <= portIndex:
            currentArray.append(self._GetDefaultForField(field))

        currentArray[portIndex] = value

        params = {
            'action': action,
            'config': {'pixPort': {field: currentArray}}
        }
        return self._SendRequest('configChange', params=params, callback=callback)

    def UpdatePortCount(self):
        """Update sequence numBlocks based on device constants + expand mode."""
        portCount = self._GetPortCount()
        if hasattr(self.ownerComp.seq, 'Port'):
            seq = self.ownerComp.seq.Port
            if seq.numBlocks != portCount:
                seq.numBlocks = portCount

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _GetPortCount(self):
        """Get current port count from constants, considering expand mode."""
        constants = self.Data.get('constants', {})
        dev = constants.get('dev', {})
        basePorts = dev.get('pixPorts', 4)

        # Check if expand mode is enabled
        if hasattr(self.ownerComp.par, 'Pixexpand') and self.ownerComp.par.Pixexpand.eval():
            return basePorts * 2
        return basePorts

    def _GetDefaultForField(self, field):
        """Get default value for a pixPort field."""
        defaults = {
            'pixCount': 0,
            'startUni': 1,
            'startCh': 1,
            'nullPix': 0,
            'zigZag': 1,
            'group': 1,
            'intensity': 100,
            'reverse': False,
            'colorOrder': 'RGB',
            'desc': '',
        }
        return defaults.get(field, 0)

    def _SyncPixelDataFromDevice(self, config):
        """Update TD parameters from device config.pix and config.pixPort."""
        if not config:
            return

        self._syncingFromDevice = True
        try:
            # Sync global pix data settings
            pix = config.get('pix', {})
            if 'dataSrc' in pix:
                src = pix['dataSrc']
                # Handle empty string as Art-Net (default)
                if src == '':
                    src = 'Art-Net'
                self.ownerComp.par.Pixdatasrc = src
            if 'inFormat' in pix:
                self.ownerComp.par.Pixinformat = pix['inFormat']
            if 'pixsSpanUni' in pix:
                self.ownerComp.par.Pixspanuni = pix['pixsSpanUni']

            # Sync per-port configuration
            pixPort = config.get('pixPort', {})
            if pixPort:
                self._SyncAllPortsFromDevice(pixPort)

            # Update status
            self._UpdateStatusParams()

            # Update auto-patch read-only state
            self._UpdateAutoPatchReadOnly()

        finally:
            self._syncingFromDevice = False

    def _SyncAllPortsFromDevice(self, pixPort):
        """Sync all port blocks from device pixPort arrays."""
        # Get port count from constants (not array length - API returns extra empty slots)
        portCount = self._GetPortCount()

        if portCount == 0:
            return

        # Adjust sequence blocks
        if hasattr(self.ownerComp.seq, 'Port'):
            seq = self.ownerComp.seq.Port
            seq.numBlocks = portCount

            # Sync each block
            for i in range(portCount):
                self._SyncPortBlockFromDevice(i, pixPort)

    def _SyncPortBlockFromDevice(self, portIndex, pixPort):
        """Update a single port block from device data."""
        # Get the sequence block
        if not hasattr(self.ownerComp.seq, 'Port'):
            return

        seq = self.ownerComp.seq.Port
        if portIndex >= seq.numBlocks:
            return

        block = seq[portIndex]

        # Helper to safely get array element
        def getVal(field, default):
            arr = pixPort.get(field, [])
            return arr[portIndex] if portIndex < len(arr) else default

        # Sync each field
        if hasattr(block.par, 'Portdesc'):
            block.par.Portdesc.val = getVal('desc', '')
        if hasattr(block.par, 'Portstartuni'):
            block.par.Portstartuni.val = getVal('startUni', 1)
        if hasattr(block.par, 'Portstartch'):
            block.par.Portstartch.val = getVal('startCh', 1)
        if hasattr(block.par, 'Portpixels'):
            block.par.Portpixels.val = getVal('pixCount', 0)
        if hasattr(block.par, 'Portnullpix'):
            block.par.Portnullpix.val = getVal('nullPix', 0)
        if hasattr(block.par, 'Portzigzag'):
            block.par.Portzigzag.val = getVal('zigZag', 1)
        if hasattr(block.par, 'Portgroup'):
            block.par.Portgroup.val = getVal('group', 1)
        if hasattr(block.par, 'Portintensity'):
            block.par.Portintensity.val = getVal('intensity', 100)
        if hasattr(block.par, 'Portreverse'):
            block.par.Portreverse.val = getVal('reverse', False)
        if hasattr(block.par, 'Portcolororder'):
            block.par.Portcolororder.val = getVal('colorOrder', 'RGB')

    def _GetPortIndexFromPar(self, par):
        """Extract port index from sequence parameter name (e.g., 'Port0portstartuni' -> 0)."""
        # Parameter names follow pattern: Port{N}fieldname where N is 0-indexed
        match = re.match(r'Port(\d+)', par.name)
        if match:
            return int(match.group(1))  # Already 0-indexed
        return 0

    def _ApplyPortField(self, portIndex, field, value):
        """Send a single port field change to device."""
        if self._syncingFromDevice:
            return
        if not self._connected:
            return
        self.SetPixPortConfig(portIndex, field, value)

    def _UpdateStatusParams(self):
        """Calculate and update status parameters (used/remaining) from UI values."""
        constants = self.Data.get('constants', {})

        # Calculate total pixels from UI sequence parameters
        totalPixels = 0
        if hasattr(self.ownerComp.seq, 'Port'):
            seq = self.ownerComp.seq.Port
            for i in range(seq.numBlocks):
                totalPixels += int(seq[i].par.Portpixels.eval())

        # Get max pixels from constants
        dev = constants.get('dev', {})
        maxPixels = dev.get('maxPixs', 4080)

        self.ownerComp.par.Pixusedpixels = totalPixels
        self.ownerComp.par.Pixremainpixels = max(0, maxPixels - totalPixels)

        # Calculate universes used
        # Each universe = 512 channels, RGB = 3 channels per pixel, RGBW = 4
        colorType = self.ownerComp.par.Pixcolortype.eval()
        channelsPerPixel = 4 if colorType == 'RGBW' else 3
        totalChannels = totalPixels * channelsPerPixel
        universesUsed = (totalChannels + 511) // 512 if totalChannels > 0 else 0

        # Max universes from constants
        maxUniverses = dev.get('maxPixUnis', 24)

        self.ownerComp.par.Pixuseduni = universesUsed
        self.ownerComp.par.Pixremainuni = max(0, maxUniverses - universesUsed)

    # =========================================================================
    # Auto Patch Methods
    # =========================================================================

    def _CalculatePortAddressing(self, portIndex):
        """Calculate startUni and startCh for a port based on previous ports."""
        if portIndex == 0:
            return None  # Port 0 uses manual values

        # Get settings
        colorType = self.ownerComp.par.Pixcolortype.eval()
        inFormat = self.ownerComp.par.Pixinformat.eval()
        spanUni = self.ownerComp.par.Pixspanuni.eval()

        # Channels per pixel
        channels_per_pixel = 4 if colorType == 'RGBW' else 3
        if inFormat == '16Bit':
            channels_per_pixel *= 2

        # Start from port 0's values
        seq = self.ownerComp.seq.Port
        currentUni = seq[0].par.Portstartuni.eval()
        currentCh = seq[0].par.Portstartch.eval()

        # Calculate through each previous port
        for i in range(portIndex):
            block = seq[i]
            pixCount = block.par.Portpixels.eval()
            nullPix = block.par.Portnullpix.eval()
            totalChannels = (pixCount + nullPix) * channels_per_pixel

            if totalChannels == 0:
                continue  # Skip ports with no pixels

            if spanUni:
                # Calculate end position, then next start
                endChannel = currentCh + totalChannels - 1
                universesSpanned = (endChannel - 1) // 512
                currentUni += universesSpanned
                currentCh = ((endChannel - 1) % 512) + 2
                if currentCh > 512:
                    currentUni += 1
                    currentCh = 1
            else:
                # Each port starts at channel 1 of next universe
                universesUsed = (totalChannels + 511) // 512
                currentUni += universesUsed
                currentCh = 1

        return {'startUni': currentUni, 'startCh': currentCh}

    def _ApplyAutoPatch(self):
        """Recalculate and apply auto-patch values to all ports (UI only, no API call)."""
        if not hasattr(self.ownerComp.par, 'Pixautopatch'):
            return
        if not self.ownerComp.par.Pixautopatch.eval():
            return
        if not hasattr(self.ownerComp.seq, 'Port'):
            return

        seq = self.ownerComp.seq.Port
        portCount = seq.numBlocks

        self._syncingFromDevice = True
        try:
            for i in range(1, portCount):
                addressing = self._CalculatePortAddressing(i)
                if addressing:
                    seq[i].par.Portstartuni.val = addressing['startUni']
                    seq[i].par.Portstartch.val = addressing['startCh']
        finally:
            self._syncingFromDevice = False

    def _UpdateAutoPatchReadOnly(self):
        """Update readOnly state of startUni/startCh based on auto-patch."""
        if not hasattr(self.ownerComp.par, 'Pixautopatch'):
            return
        if not hasattr(self.ownerComp.seq, 'Port'):
            return

        autoPatch = self.ownerComp.par.Pixautopatch.eval()
        seq = self.ownerComp.seq.Port

        for i in range(seq.numBlocks):
            isReadOnly = autoPatch and i > 0
            seq[i].par.Portstartuni.readOnly = isReadOnly
            seq[i].par.Portstartch.readOnly = isReadOnly

    # =========================================================================
    # Parameter Change Handlers (Global)
    # =========================================================================

    def par_Pixdatasrc(self, par):
        """Handle data source change (UI only, no auto-apply)."""
        if self._syncingFromDevice:
            return
        # No API call - changes applied via Apply/Save buttons

    def par_Pixinformat(self, par):
        """Handle input format change (UI only, no auto-apply)."""
        if self._syncingFromDevice:
            return
        # Recalculate auto-patch when input format changes (affects channels per pixel)
        self._ApplyAutoPatch()

    def par_Pixspanuni(self, par):
        """Handle span universes toggle change (UI only, no auto-apply)."""
        if self._syncingFromDevice:
            return
        # Recalculate auto-patch when span mode changes
        self._ApplyAutoPatch()

    def par_Pixautopatch(self, par):
        """Handle auto-patch toggle change."""
        self._UpdateAutoPatchReadOnly()
        if par.eval():
            self._ApplyAutoPatch()

    # =========================================================================
    # Sequence Parameter Handlers
    # =========================================================================

    def par_Portdesc(self, par):
        """Handle port description change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Portstartuni(self, par):
        """Handle port start universe change (UI only, no auto-apply)."""
        if self._syncingFromDevice:
            return
        # If port 0 changed, recalculate all subsequent ports
        portIndex = self._GetPortIndexFromPar(par)
        if portIndex == 0:
            self._ApplyAutoPatch()

    def par_Portstartch(self, par):
        """Handle port start channel change (UI only, no auto-apply)."""
        if self._syncingFromDevice:
            return
        # If port 0 changed, recalculate all subsequent ports
        portIndex = self._GetPortIndexFromPar(par)
        if portIndex == 0:
            self._ApplyAutoPatch()

    def par_Portpixels(self, par):
        """Handle port pixel count change (UI only, no auto-apply)."""
        if self._syncingFromDevice:
            return
        # Recalculate auto-patch when pixel count changes
        self._ApplyAutoPatch()
        # Update used/remaining status
        self._UpdateStatusParams()

    def par_Portnullpix(self, par):
        """Handle port null pixels change (UI only, no auto-apply)."""
        if self._syncingFromDevice:
            return
        # Recalculate auto-patch when null pixels change
        self._ApplyAutoPatch()

    def par_Portzigzag(self, par):
        """Handle port zigzag change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Portgroup(self, par):
        """Handle port group change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Portintensity(self, par):
        """Handle port intensity change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Portreverse(self, par):
        """Handle port reverse change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    def par_Portcolororder(self, par):
        """Handle port color order change (UI only, no auto-apply)."""
        pass  # No API call - changes applied via Apply/Save buttons

    # =========================================================================
    # Apply/Save/Revert Button Handlers
    # =========================================================================

    def pulse_Pixapply(self):
        """Apply all Pixel Data changes to device (temporary)."""
        self._SendPixelDataConfig(save=False)

    def pulse_Pixsave(self):
        """Save all Pixel Data changes to device (permanent)."""
        self._SendPixelDataConfig(save=True)

    def pulse_Pixrevert(self):
        """Revert local changes and reload from device."""
        if self._connected:
            self.GetConfig()  # This will trigger _SyncPixelDataFromDevice

    def _SendPixelDataConfig(self, save=False):
        """Send all current Pixel Data settings to device."""
        if not self._connected:
            return

        action = 'save' if save else 'apply'

        # Build pix config from current parameter values
        pixConfig = {
            'dataSrc': self.ownerComp.par.Pixdatasrc.eval(),
            'inFormat': self.ownerComp.par.Pixinformat.eval(),
            'pixsSpanUni': self.ownerComp.par.Pixspanuni.eval(),
        }

        # Build pixPort config from sequence parameters
        if not hasattr(self.ownerComp.seq, 'Port'):
            return

        seq = self.ownerComp.seq.Port
        portCount = seq.numBlocks

        # Build complete pixPort config - API requires all fields together
        pixPortConfig = {
            'pixCount': [],
            'startUni': [],
            'startCh': [],
            'nullPix': [],
            'zigZag': [],
            'group': [],
            'reverse': [],
            'colorOrder': [],
            'intensity': [],
            'desc': [],
        }

        for i in range(portCount):
            block = seq[i]
            pixPortConfig['pixCount'].append(int(block.par.Portpixels.eval()))
            pixPortConfig['startUni'].append(int(block.par.Portstartuni.eval()))
            pixPortConfig['startCh'].append(int(block.par.Portstartch.eval()))
            pixPortConfig['nullPix'].append(int(block.par.Portnullpix.eval()))
            pixPortConfig['zigZag'].append(int(block.par.Portzigzag.eval()))
            pixPortConfig['group'].append(int(block.par.Portgroup.eval()))
            pixPortConfig['reverse'].append(block.par.Portreverse.eval())
            pixPortConfig['colorOrder'].append(block.par.Portcolororder.eval())
            pixPortConfig['intensity'].append(int(block.par.Portintensity.eval()))
            pixPortConfig['desc'].append(block.par.Portdesc.eval())

        # Send combined config
        params = {
            'action': action,
            'config': {
                'pix': pixConfig,
                'pixPort': pixPortConfig
            }
        }
        self._SendRequest('configChange', params=params)
