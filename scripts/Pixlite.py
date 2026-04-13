from json import loads, dumps
import traceback
import hashlib
import base64
import time

from CallbacksExt import CallbacksExt
from TDVersionExt import TDVersionExt
from TDStoreTools import StorageManager
from PixlitePars import ensurePars
from PixliteTestMode import PixliteTestModeMixin
from PixliteStatistics import PixliteStatisticsMixin
from PixlitePixelOutputs import PixlitePixelOutputsMixin
from PixlitePixelData import PixlitePixelDataMixin
from PixliteSystem import PixliteSystemMixin
from PixliteAuxPort import PixliteAuxPortMixin

TDF = op.TDModules.mod.TDFunctions


class Pixlite(CallbacksExt, TDVersionExt, PixliteSystemMixin, PixliteAuxPortMixin, PixliteTestModeMixin, PixliteStatisticsMixin, PixlitePixelOutputsMixin, PixlitePixelDataMixin):
    """
    Pixlite WebSocket API Extension

    Interfaces with PixLite Mk3 LED controllers via WebSocket.
    Handles connection, authentication, request/response correlation,
    and exposes a clean public API.
    """

    def __init__(self, ownerComp):
        self.ownerComp = ownerComp

        # Ensure all custom parameters exist
        ensurePars(ownerComp)

        # Initialize callbacks
        self.callbackDat = self.ownerComp.par.Callbackdat.eval()
        try:
            CallbacksExt.__init__(self, ownerComp)
        except:
            self.ownerComp.addScriptError(traceback.format_exc() +
                    "Error in CallbacksExt __init__. See textport.")
            print()
            print("Error initializing callbacks - " + self.ownerComp.path)
            print(traceback.format_exc())

        # Run onInit callback
        try:
            self.DoCallback('onInit', {'ownerComp': self.ownerComp})
        except:
            self.ownerComp.addScriptError(traceback.format_exc() +
                    "Error in custom onInit callback. See textport.")
            print(traceback.format_exc())

        # Initialize version tracking mixin
        TDVersionExt.__init__(self, ownerComp)

        # Data storage component
        self.dataComp = ownerComp.op('data')

        # Stored items (persistent across saves)
        storedItems = [
            {'name': 'Data', 'default': {
                'config': None,
                'status': None,
                'statistics': None,
                'constants': None,
                'version': None
            }, 'readOnly': False, 'property': True, 'dependable': True},
        ]
        self.stored = StorageManager(self, self.dataComp, storedItems)

        # WebSocket DAT reference
        self.websocketDat = ownerComp.op('websocket')

        # Message ID counter for request/response correlation
        self._messageId = 0

        # Pending requests awaiting responses: {id: {callback, timestamp, request_type}}
        self._pendingRequests = {}

        # Connection state
        self._connected = False
        self._connecting = False

        # Check if already connected (handles extension reinit while connected)
        # If websocket is active and we have stored config data, assume still connected
        if self.websocketDat.par.active.eval() and self.Data.get('config'):
            self._connected = True
            self._UpdateConnectionStatus('Connected')

        # Subscription tracking
        self._subscriptions = set()

        # Flag to prevent feedback loop when syncing from device
        self._syncingFromDevice = False

        # If we already have data (e.g., after reinit), sync parameters
        if self.Data.get('constants'):
            self.UpdatePortCount()
            self.PopulatePixelTypeMenu()
        if self.Data.get('config'):
            self._SyncSystemConfigFromDevice(self.Data['config'])
            self._SyncAuxPortConfigFromDevice(self.Data['config'])
            self._SyncPixelConfigFromDevice(self.Data['config'])
            self._SyncPixelDataFromDevice(self.Data['config'])

        # Auto-connect if enabled
        if self.ownerComp.par.Autoconnect.eval():
            run(self.Connect, delayMilliSeconds=500)

    # =========================================================================
    # Internal Helper Methods
    # =========================================================================

    def _NextMessageId(self):
        """Generate next unique message ID for request tracking."""
        self._messageId += 1
        if self._messageId > 4294967295:
            self._messageId = 1
        return self._messageId

    def _BuildWebSocketUrl(self):
        """
        Build the WebSocket URL with authentication.
        Format: ws://[ip]/v1.7?user=admin&auth=[Base64URL(SHA256(password))]
        """
        ip = self.ownerComp.par.Websocketnetaddress.eval()
        api_version = self.ownerComp.par.Apiversion.eval()
        username = self.ownerComp.par.Username.eval()
        password = self.ownerComp.par.Password.eval()

        # SHA256 hash of password, then Base64URL encode
        password_bytes = password.encode('utf-8')
        sha256_hash = hashlib.sha256(password_bytes).digest()
        # Base64URL encoding (URL-safe, no padding)
        auth_hash = base64.urlsafe_b64encode(sha256_hash).rstrip(b'=').decode('ascii')

        url = f"ws://{ip}/{api_version}?user={username}&auth={auth_hash}"

        return url

    def _SendRequest(self, request_name, params=None, callback=None):
        """
        Send a request to the device and track it for response correlation.

        Args:
            request_name: API method name (e.g., 'configRead')
            params: Optional dict of parameters
            callback: Optional callback function(result, error)

        Returns:
            message_id: The ID of the sent request
        """
        if not self._connected:
            if callback:
                callback(None, {'code': -1, 'msg': 'Not connected'})
            return None

        msg_id = self._NextMessageId()

        message = {
            'req': request_name,
            'id': msg_id
        }
        if params:
            message['params'] = params

        # Track pending request
        self._pendingRequests[msg_id] = {
            'callback': callback,
            'timestamp': time.time(),
            'request_type': request_name
        }

        # Send via websocket
        self.websocketDat.sendText(dumps(message))

        return msg_id

    def _HandleResponse(self, data):
        """Route incoming response to appropriate handler based on message ID."""
        msg_id = data.get('id')

        if msg_id and msg_id in self._pendingRequests:
            pending = self._pendingRequests.pop(msg_id)

            if 'err' in data:
                # Error response
                error = data['err']
                if pending['callback']:
                    pending['callback'](None, error)
                self._OnError(pending['request_type'], error)
            else:
                # Success response
                result = data.get('result', {})
                if pending['callback']:
                    pending['callback'](result, None)
                self._OnResponse(data.get('resp', pending['request_type']), result)

    def _HandleNotification(self, data):
        """Handle incoming notifications (unsolicited messages from device)."""
        notify_type = data.get('notify')
        params = data.get('params', {})

        if notify_type == 'statisticSub':
            # Statistics notification - data is in params.statistic
            stats = params.get('statistic', params)
            self.Data['statistics'] = stats
            self._SyncStatisticsToParams(stats)
            self.DoCallback('onStatistics', {
                'ownerComp': self.ownerComp,
                'statistics': stats
            })
        elif notify_type == 'configChange':
            # Config changed externally, refresh
            self.GetConfig()
            self.DoCallback('onConfigChanged', {
                'ownerComp': self.ownerComp,
                'params': params
            })
        elif notify_type == 'statusChange':
            status = params.get('status', params)
            self.Data['status'] = status
            self._SyncTestModeFromStatus(status)
            self.DoCallback('onStatusChanged', {
                'ownerComp': self.ownerComp,
                'status': status
            })
        elif notify_type == 'disconnect':
            # Server-initiated disconnect
            self.DoCallback('onServerDisconnect', {
                'ownerComp': self.ownerComp,
                'reason': params.get('reason', 'unknown')
            })
        else:
            # Unknown notification type
            self.DoCallback('onNotification', {
                'ownerComp': self.ownerComp,
                'type': notify_type,
                'params': params
            })

    def _OnResponse(self, response_type, result):
        """Handle successful responses and update stored data."""
        if response_type == 'configRead':
            config = result.get('config', result)
            self.Data['config'] = config
            self._UpdateDeviceInfo(config)
            self._SyncSystemConfigFromDevice(config)
            self._SyncAuxPortConfigFromDevice(config)
            self._SyncPixelConfigFromDevice(config)
            self._SyncPixelDataFromDevice(config)
            self.DoCallback('onConfigRead', {
                'ownerComp': self.ownerComp,
                'config': config
            })
        elif response_type == 'statusRead':
            status = result.get('status', result)
            self.Data['status'] = status
            self._SyncTestModeFromStatus(status)
            self.DoCallback('onStatusRead', {
                'ownerComp': self.ownerComp,
                'status': status
            })
        elif response_type == 'constantRead':
            constants = result.get('constant', result)
            self.Data['constants'] = constants
            self.PopulatePixelTypeMenu()
            self.UpdatePortCount()
            self.DoCallback('onConstantsRead', {
                'ownerComp': self.ownerComp,
                'constants': constants
            })
        elif response_type == 'ver':
            self.Data['version'] = result
            self.DoCallback('onVersionRead', {
                'ownerComp': self.ownerComp,
                'version': result
            })
        elif response_type == 'statisticRead':
            stats = result.get('statistic', result)
            self.Data['statistics'] = stats
            self._SyncStatisticsToParams(stats)
            self.DoCallback('onStatisticsRead', {
                'ownerComp': self.ownerComp,
                'statistics': stats
            })
        elif response_type == 'identify':
            self.DoCallback('onIdentify', {
                'ownerComp': self.ownerComp,
                'result': result
            })
        elif response_type == 'configChange':
            self.DoCallback('onConfigChangeResponse', {
                'ownerComp': self.ownerComp,
                'result': result
            })

    def _OnError(self, request_type, error):
        """Handle error responses."""
        print(f"Pixlite API Error [{request_type}]: {error.get('msg', error)}")
        self.DoCallback('onError', {
            'ownerComp': self.ownerComp,
            'requestType': request_type,
            'error': error
        })

    def _UpdateConnectionStatus(self, status):
        """Update the connection status parameter."""
        try:
            self.ownerComp.par.Connectionstatus.val = status
        except:
            pass

    def _UpdateDeviceInfo(self, config):
        """Extract device info from config."""
        # Could update a device name parameter if we add one
        pass

    # =========================================================================
    # WebSocket Callbacks (called from websocket_callbacks DAT)
    # =========================================================================

    def onConnectWebsocket(self, dat):
        """Called when WebSocket connection is established."""
        self._connected = True
        self._connecting = False
        self._UpdateConnectionStatus('Connected')

        print(f"Pixlite connected to {self.ownerComp.par.Websocketnetaddress.eval()}")

        # Initial data fetch sequence
        self.GetVersion()
        self.GetConstants()
        self.GetConfig()
        self.GetStatus()

        # Start statistics subscription if toggle is already enabled
        if self.ownerComp.par.Statssubscribe.eval():
            interval_sec = self.ownerComp.par.Statsinterval.eval()
            self.SubscribeStatistics(interval_sec)

        # Fire callback
        self.DoCallback('onConnect', {'ownerComp': self.ownerComp})

    def onDisconnectWebsocket(self, dat):
        """Called when WebSocket connection is closed."""
        was_connected = self._connected
        self._connected = False
        self._connecting = False
        self._UpdateConnectionStatus('Disconnected')

        # Clear pending requests with error
        for msg_id, pending in list(self._pendingRequests.items()):
            if pending['callback']:
                pending['callback'](None, {'code': -1, 'msg': 'Disconnected'})
        self._pendingRequests.clear()
        self._subscriptions.clear()

        print("Pixlite disconnected")

        # Fire callback
        self.DoCallback('onDisconnect', {'ownerComp': self.ownerComp})

        # Auto-reconnect if enabled and was previously connected
        if was_connected and self.ownerComp.par.Reconnect.eval():
            delay = self.ownerComp.par.Reconnectdelay.eval()
            self._UpdateConnectionStatus(f'Reconnecting in {delay}s...')
            run(self.Connect, delayMilliSeconds=int(delay * 1000))

    def onReceiveTextWebsocket(self, dat, rowIndex, message):
        """Called when a text message is received."""
        try:
            data = loads(message)

            if 'resp' in data or 'err' in data:
                # This is a response to a request
                self._HandleResponse(data)
            elif 'notify' in data:
                # This is a notification
                self._HandleNotification(data)
            else:
                # Unknown message type
                self.DoCallback('onMessage', {
                    'ownerComp': self.ownerComp,
                    'message': data
                })
        except Exception as e:
            print(f"Pixlite: Error parsing message: {e}")
            print(f"Raw message: {message[:200]}")

    def onReceiveBinaryWebsocket(self, dat, contents):
        """Called when binary data is received."""
        self.DoCallback('onBinaryMessage', {
            'ownerComp': self.ownerComp,
            'contents': contents
        })

    def onReceivePingWebsocket(self, dat, contents):
        """Called when a ping is received - respond with pong."""
        dat.sendPong(contents)

    def onReceivePongWebsocket(self, dat, contents):
        """Called when a pong is received."""
        pass

    def onMonitorMessageWebsocket(self, dat, message):
        """Called for WebSocket status/debug messages."""
        msg_lower = message.lower()
        if 'connecting' in msg_lower:
            self._UpdateConnectionStatus('Connecting...')
        elif 'error' in msg_lower or 'failed' in msg_lower:
            self._UpdateConnectionStatus(f'Error')
            print(f"Pixlite WebSocket: {message}")

    # =========================================================================
    # Public API Methods - Connection
    # =========================================================================

    def Connect(self):
        """
        Connect to the PixLite controller.
        Builds URL with authentication and activates WebSocket.
        """
        if self._connected:
            print("Pixlite: Already connected")
            return

        if self._connecting:
            print("Pixlite: Connection already in progress")
            return

        self._connecting = True
        self._UpdateConnectionStatus('Connecting...')

        # Build and set the WebSocket URL
        url = self._BuildWebSocketUrl()
        self.websocketDat.par.netaddress = url
        self.websocketDat.par.active = True

        print(f"Pixlite: Connecting to {self.ownerComp.par.Websocketnetaddress.eval()}...")

    def Disconnect(self):
        """Disconnect from the PixLite controller."""
        self.websocketDat.par.active = False
        self._connected = False
        self._connecting = False
        self._UpdateConnectionStatus('Disconnected')

    def IsConnected(self):
        """Return True if currently connected."""
        return self._connected

    # =========================================================================
    # Public API Methods - Data Retrieval
    # =========================================================================

    def GetConfig(self, callback=None):
        """
        Request full device configuration.
        Result stored in self.Data['config']
        """
        return self._SendRequest('configRead', callback=callback)

    def GetStatus(self, callback=None):
        """
        Request device status.
        Result stored in self.Data['status']
        """
        return self._SendRequest('statusRead', callback=callback)

    def GetConstants(self, callback=None):
        """
        Request device constants (model, capabilities, etc.).
        Result stored in self.Data['constants']
        """
        return self._SendRequest('constantRead', callback=callback)

    def GetVersion(self, callback=None):
        """
        Request API version info.
        Result stored in self.Data['version']
        """
        return self._SendRequest('ver', callback=callback)

    # =========================================================================
    # Public API Methods - Device Control
    # =========================================================================

    def SetConfig(self, config_changes, action='apply', callback=None):
        """
        Update device configuration.

        Args:
            config_changes: Dict of configuration values to change
            action: 'apply' (temp), 'save' (permanent), or 'revert'
            callback: Optional callback(result, error)
        """
        params = {
            'action': action,
            'config': config_changes
        }
        return self._SendRequest('configChange', params=params, callback=callback)

    def SaveConfig(self, callback=None):
        """Save current running configuration to non-volatile memory."""
        params = {'action': 'save'}
        return self._SendRequest('configChange', params=params, callback=callback)

    def RevertConfig(self, callback=None):
        """Revert to last saved configuration."""
        params = {'action': 'revert'}
        return self._SendRequest('configChange', params=params, callback=callback)

    def Identify(self, duration=5, callback=None):
        """
        Flash device LED for identification.

        Args:
            duration: How long to flash in seconds (1-120), or 121 for continuous
            callback: Optional callback(result, error)
        """
        params = {'duration': duration}
        return self._SendRequest('identify', params=params, callback=callback)

    def Refresh(self):
        """Re-fetch all device data (config, status, constants)."""
        if not self._connected:
            print("Pixlite: Not connected, cannot refresh")
            return
        self.GetConfig()
        self.GetStatus()
        self.GetConstants()

    def Restart(self, callback=None):
        """Restart the device."""
        return self._SendRequest('restart', callback=callback)

    # =========================================================================
    # Public API Methods - Raw Access
    # =========================================================================

    def SendRequest(self, request_name, params=None, callback=None):
        """
        Send a raw API request for advanced use cases.

        Args:
            request_name: API method name
            params: Optional parameters dict
            callback: Optional callback(result, error)

        Returns:
            message_id
        """
        return self._SendRequest(request_name, params, callback)

    # =========================================================================
    # Pulse Parameter Handlers
    # =========================================================================

    def pulse_Connect(self):
        """Handle Connect pulse parameter."""
        self.Connect()

    def pulse_Disconnect(self):
        """Handle Disconnect pulse parameter."""
        self.Disconnect()

    def pulse_Refresh(self):
        """Handle Refresh pulse parameter."""
        self.Refresh()

    def pulse_Identify(self):
        """Handle Identify pulse parameter."""
        if self._connected:
            self.Identify(duration=5)
        else:
            print("Pixlite: Not connected, cannot identify")

