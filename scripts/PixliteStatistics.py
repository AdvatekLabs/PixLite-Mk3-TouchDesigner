"""
PixliteStatistics - Statistics functionality mixin for Pixlite extension

This module provides statistics monitoring including:
- Subscribing to live statistics updates
- One-time statistics read
- Syncing statistics to TD parameters
- Parameter change handlers
"""


class PixliteStatisticsMixin:
    """Statistics functionality for Pixlite extension."""

    # =========================================================================
    # Public API - Statistics
    # =========================================================================

    def GetStatistics(self, callback=None):
        """
        Request current statistics (one-time read).
        Result stored in self.Data['statistics']
        """
        return self._SendRequest('statisticRead', callback=callback)

    def SubscribeStatistics(self, interval_sec=1, callback=None):
        """
        Subscribe to statistics updates.

        Args:
            interval_sec: Update interval in seconds (1-255)
            callback: Optional callback for subscription confirmation
        """
        self._subscriptions.add('statistic')
        params = {
            'sub': True,
            'period': int(interval_sec),  # API requires integer
            'path': ['']  # Empty string = entire statistic object
        }
        return self._SendRequest('statisticSub', params=params, callback=callback)

    def UnsubscribeStatistics(self, callback=None):
        """Unsubscribe from statistics updates."""
        self._subscriptions.discard('statistic')
        params = {
            'sub': False,
            'path': ['']
        }
        return self._SendRequest('statisticSub', params=params, callback=callback)

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _SyncStatisticsToParams(self, stats):
        """Update TD statistics parameters from device data."""
        if not stats:
            return

        # Device stats
        dev = stats.get('dev', {})
        temp = dev.get('temp', {})
        self.ownerComp.par.Statstemp = temp.get('current', 0)
        self.ownerComp.par.Statstempmin = temp.get('min', 0)
        self.ownerComp.par.Statstempmax = temp.get('max', 0)
        self.ownerComp.par.Statscpu = dev.get('cpu', 0)
        # Bank voltages as comma-separated string
        bankVolt = dev.get('bankVolt', [])
        self.ownerComp.par.Statsbankvolt = ', '.join(str(v) for v in bankVolt) if bankVolt else ''

        # Frame rates
        pixData = stats.get('pixData', {})
        self.ownerComp.par.Statsoutfps = pixData.get('outFrmRate', 0)
        self.ownerComp.par.Statsinfps = pixData.get('inFrmRate', 0)
        self.ownerComp.par.Statsrecfps = pixData.get('recFrmRate', 0)
        self.ownerComp.par.Statsoverrun = pixData.get('overrun', 0)
        self.ownerComp.par.Statsextsync = str(pixData.get('extSync', ''))

        # Network
        net = stats.get('net', {})
        self.ownerComp.par.Statsipaddr = net.get('ipAddr', '')
        self.ownerComp.par.Statsnetmask = net.get('netmask', '')
        self.ownerComp.par.Statsgateway = net.get('gateway', '')

        # Power outputs
        pixPwrOuts = stats.get('pixPwrOuts', {})
        pwrCurrent = pixPwrOuts.get('current', [])
        self.ownerComp.par.Statspwrcurrent = ', '.join(str(v) for v in pwrCurrent) if pwrCurrent else ''
        fuseGood = pixPwrOuts.get('fuseGood', [])
        self.ownerComp.par.Statspwrfuse = ', '.join('Good' if v else 'Bad' for v in fuseGood) if fuseGood else ''

        # Diagnostics
        diag = stats.get('diag', {})
        self.ownerComp.par.Statserrcount = diag.get('errCnt', 0)
        self.ownerComp.par.Statserrmsg = diag.get('err', '')

    # =========================================================================
    # Parameter Change Handlers
    # =========================================================================

    def par_Statssubscribe(self, par):
        """Handle subscribe toggle change."""
        if not self._connected:
            return
        if par.eval():
            interval_sec = self.ownerComp.par.Statsinterval.eval()
            self.SubscribeStatistics(interval_sec)
        else:
            self.UnsubscribeStatistics()

    def par_Statsinterval(self, par):
        """Handle interval change - resubscribe if active."""
        if not self._connected:
            return
        if self.ownerComp.par.Statssubscribe.eval():
            interval_sec = par.eval()
            self.SubscribeStatistics(interval_sec)

    def pulse_Statsrefresh(self):
        """Manual refresh of statistics."""
        if self._connected:
            self.GetStatistics()
