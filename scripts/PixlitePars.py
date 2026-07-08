"""
PixlitePars - Parameter definitions for Pixlite extension

This module defines all custom parameters for the Pixlite component.
Parameters are organized by page and created if missing during extension init.
"""

# Page order for sorting (includes pages from other extensions)
PAGE_ORDER = [
    'Connection',
    'Input',
    'System',
    'Pixel Outputs',
    'Pixel Data',
    'Aux Port',
    'Test Mode',
    'Statistics',
    'Callbacks',
]


# Page definitions: { 'PageName': [par_defs...] }
PAGES = {
    'Connection': [
        # Connection section
        {'name': 'Websocket', 'type': 'header', 'label': 'Connection'},
        {'name': 'Apiversion', 'type': 'str', 'default': 'v1.7', 'label': 'API Version', 'readOnly': True},
        {'name': 'Websocketnetaddress', 'type': 'str', 'default': '', 'label': 'IP Address'},

        # Authentication section
        {'name': 'Headerauth', 'type': 'header', 'label': 'Authentication'},
        {'name': 'Username', 'type': 'menu', 'default': 'admin', 'label': 'User',
         'menuNames': ['admin', 'oper'], 'menuLabels': ['admin', 'oper']},
        {'name': 'Password', 'type': 'str', 'default': '', 'label': 'Password'},

        # Options section
        {'name': 'Headeroptions', 'type': 'header', 'label': 'Options'},
        {'name': 'Websocketactive', 'type': 'toggle', 'default': False, 'label': 'Active'},
        {'name': 'Autoconnect', 'type': 'toggle', 'default': False, 'label': 'Auto Connect'},
        {'name': 'Reconnect', 'type': 'toggle', 'default': True, 'label': 'Auto Reconnect'},
        {'name': 'Reconnectdelay', 'type': 'float', 'default': 5.0, 'label': 'Reconnect Delay'},

        # Status section
        {'name': 'Headerstatus', 'type': 'header', 'label': 'Status'},
        {'name': 'Connectionstatus', 'type': 'str', 'default': 'Disconnected', 'label': 'Status', 'readOnly': True},

        # Controls section
        {'name': 'Headercontrols', 'type': 'header', 'label': 'Controls'},
        {'name': 'Connect', 'type': 'pulse', 'label': 'Connect'},
        {'name': 'Disconnect', 'type': 'pulse', 'label': 'Disconnect'},
        {'name': 'Refresh', 'type': 'pulse', 'label': 'Refresh'},
        {'name': 'Identify', 'type': 'pulse', 'label': 'Identify'},
    ],

    'Input': [
        # Source section - scene pixel data feeding this component
        {'name': 'Inheadersource', 'type': 'header', 'label': 'Source'},
        {'name': 'Inpixeldata', 'type': 'pop', 'default': '/components/null1', 'label': 'Pixel Data POP'},

        # Addressing section - base network address of the transmitted stream.
        # Net/Subnet only apply to Art-Net; sACN uses a flat universe.
        # When 'Infer from Pixel Data' is on, Net/Subnet/Universe/Start Channel
        # are derived from the first pixel output (Port 0) and locked read-only.
        {'name': 'Inheaderaddr', 'type': 'header', 'label': 'Addressing'},
        {'name': 'Ininfer', 'type': 'toggle', 'default': True, 'label': 'Infer from Pixel Data'},
        {'name': 'Innet', 'type': 'int', 'default': 0, 'label': 'Net',
         'min': 0, 'max': 127, 'clampMin': True, 'clampMax': True,
         'enableExpr': "me.par.Pixdatasrc.eval() == 'Art-Net' and not me.par.Ininfer.eval()"},
        {'name': 'Insubnet', 'type': 'int', 'default': 0, 'label': 'Subnet',
         'min': 0, 'max': 15, 'clampMin': True, 'clampMax': True,
         'enableExpr': "me.par.Pixdatasrc.eval() == 'Art-Net' and not me.par.Ininfer.eval()"},
        {'name': 'Inuniverse', 'type': 'int', 'default': 0, 'label': 'Universe',
         'min': 0, 'clampMin': True,
         'enableExpr': "not me.par.Ininfer.eval()"},
        {'name': 'Inchannel', 'type': 'int', 'default': 1, 'label': 'Start Channel',
         'min': 1, 'max': 512, 'clampMin': True, 'clampMax': True,
         'enableExpr': "not me.par.Ininfer.eval()"},

        # Network section - which local NIC transmits the data
        {'name': 'Inheadernet', 'type': 'header', 'label': 'Network'},
        {'name': 'Inlocaladdress', 'type': 'strmenu', 'default': '', 'label': 'Local Address'},
    ],

    'System': [
        # Device Name
        {'name': 'Sysheadername', 'type': 'header', 'label': 'Device Name'},
        {'name': 'Sysname', 'type': 'str', 'default': '', 'label': 'Name'},

        # IP Address
        {'name': 'Sysheaderip', 'type': 'header', 'label': 'IP Address'},
        {'name': 'Sysipmode', 'type': 'menu', 'default': 'Static', 'label': 'IP Mode',
         'menuNames': ['Static', 'DHCP/AutoIP'], 'menuLabels': ['Static', 'DHCP/AutoIP']},
        {'name': 'Sysipaddr', 'type': 'str', 'default': '', 'label': 'IP Address',
         'enableExpr': "me.par.Sysipmode.eval() == 'Static'"},
        {'name': 'Sysnetmask', 'type': 'str', 'default': '', 'label': 'Subnet Mask',
         'enableExpr': "me.par.Sysipmode.eval() == 'Static'"},
        {'name': 'Sysgateway', 'type': 'str', 'default': '', 'label': 'Gateway Address',
         'enableExpr': "me.par.Sysipmode.eval() == 'Static'"},

        # Indicator LEDs
        {'name': 'Sysheaderleds', 'type': 'header', 'label': 'Indicator LEDs'},
        {'name': 'Sysledsen', 'type': 'toggle', 'default': True, 'label': 'Enable Indicator LEDs'},

        # Controls
        {'name': 'Sysheadercontrols', 'type': 'header', 'label': 'Controls'},
        {'name': 'Sysapply', 'type': 'pulse', 'label': 'Apply'},
        {'name': 'Syssave', 'type': 'pulse', 'label': 'Apply & Save'},
        {'name': 'Sysrevert', 'type': 'pulse', 'label': 'Revert'},
    ],

    'Test Mode': [
        {'name': 'Testmode', 'type': 'menu', 'default': 'disabled', 'label': 'Mode',
         'menuNames': ['disabled', 'rgbwCycle', 'colorFade', 'setColor'],
         'menuLabels': ['Disabled', 'RGBW Cycle', 'Color Fade', 'Set Color']},

        {'name': 'Headercolor', 'type': 'header', 'label': 'Color'},
        {'name': 'Testcolorr', 'type': 'int', 'default': 0, 'label': 'Red',
         'min': 0, 'max': 255, 'clampMin': True, 'clampMax': True,
         'enableExpr': "me.par.Testmode == 'setColor'"},
        {'name': 'Testcolorg', 'type': 'int', 'default': 0, 'label': 'Green',
         'min': 0, 'max': 255, 'clampMin': True, 'clampMax': True,
         'enableExpr': "me.par.Testmode == 'setColor'"},
        {'name': 'Testcolorb', 'type': 'int', 'default': 0, 'label': 'Blue',
         'min': 0, 'max': 255, 'clampMin': True, 'clampMax': True,
         'enableExpr': "me.par.Testmode == 'setColor'"},
        {'name': 'Testcolorw', 'type': 'int', 'default': 0, 'label': 'White',
         'min': 0, 'max': 255, 'clampMin': True, 'clampMax': True,
         'enableExpr': "me.par.Testmode == 'setColor'"},
        {'name': 'Testcolorres', 'type': 'menu', 'default': '8Bit', 'label': 'Resolution',
         'menuNames': ['8Bit', '16Bit'], 'menuLabels': ['8 Bit', '16 Bit'],
         'enableExpr': "me.par.Testmode == 'setColor'"},

        {'name': 'Headerfilter', 'type': 'header', 'label': 'Filter'},
        {'name': 'Testoutputmode', 'type': 'menu', 'default': 'all', 'label': 'Outputs',
         'menuNames': ['all', 'individual'], 'menuLabels': ['All Outputs', 'Individual Output'],
         'enableExpr': "me.par.Testmode != 'disabled'"},
        {'name': 'Testoutputnum', 'type': 'int', 'default': 1, 'label': 'Output Number',
         'min': 1, 'clampMin': True,
         'enableExpr': "me.par.Testmode != 'disabled' and me.par.Testoutputmode == 'individual'"},
        {'name': 'Testpixelmode', 'type': 'menu', 'default': 'all', 'label': 'Pixels',
         'menuNames': ['all', 'individual'], 'menuLabels': ['All Pixels', 'Individual Pixel'],
         'enableExpr': "me.par.Testmode != 'disabled'"},
        {'name': 'Testpixelnum', 'type': 'int', 'default': 1, 'label': 'Pixel Number',
         'min': 1, 'clampMin': True,
         'enableExpr': "me.par.Testmode != 'disabled' and me.par.Testpixelmode == 'individual'"},
    ],

    'Statistics': [
        {'name': 'Statsheadercontrols', 'type': 'header', 'label': 'Controls'},
        {'name': 'Statssubscribe', 'type': 'toggle', 'default': False, 'label': 'Live Updates'},
        {'name': 'Statsinterval', 'type': 'float', 'default': 1.0, 'label': 'Interval (sec)',
         'min': 1, 'max': 255, 'clampMin': True, 'clampMax': True},
        {'name': 'Statsrefresh', 'type': 'pulse', 'label': 'Refresh'},

        {'name': 'Statsheaderdevice', 'type': 'header', 'label': 'Device'},
        {'name': 'Statstemp', 'type': 'float', 'default': 0, 'label': 'Temperature °C', 'readOnly': True},
        {'name': 'Statstempmin', 'type': 'float', 'default': 0, 'label': 'Temp Min °C', 'readOnly': True},
        {'name': 'Statstempmax', 'type': 'float', 'default': 0, 'label': 'Temp Max °C', 'readOnly': True},
        {'name': 'Statscpu', 'type': 'int', 'default': 0, 'label': 'CPU %', 'readOnly': True},
        {'name': 'Statsbankvolt', 'type': 'str', 'default': '', 'label': 'Bank Voltages (mV)', 'readOnly': True},

        {'name': 'Statsheaderframerates', 'type': 'header', 'label': 'Frame Rates'},
        {'name': 'Statsoutfps', 'type': 'int', 'default': 0, 'label': 'Output FPS', 'readOnly': True},
        {'name': 'Statsinfps', 'type': 'int', 'default': 0, 'label': 'Input FPS', 'readOnly': True},
        {'name': 'Statsrecfps', 'type': 'int', 'default': 0, 'label': 'Received FPS', 'readOnly': True},
        {'name': 'Statsextsync', 'type': 'str', 'default': '', 'label': 'External Sync', 'readOnly': True},

        {'name': 'Statsheadernetwork', 'type': 'header', 'label': 'Network'},
        {'name': 'Statsipaddr', 'type': 'str', 'default': '', 'label': 'IP Address', 'readOnly': True},
        {'name': 'Statsnetmask', 'type': 'str', 'default': '', 'label': 'Netmask', 'readOnly': True},
        {'name': 'Statsgateway', 'type': 'str', 'default': '', 'label': 'Gateway', 'readOnly': True},
        {'name': 'Statsoverrun', 'type': 'int', 'default': 0, 'label': 'Overruns', 'readOnly': True},

        {'name': 'Statsheaderpower', 'type': 'header', 'label': 'Power Outputs'},
        {'name': 'Statspwrcurrent', 'type': 'str', 'default': '', 'label': 'Current (mA)', 'readOnly': True},
        {'name': 'Statspwrfuse', 'type': 'str', 'default': '', 'label': 'Fuse Status', 'readOnly': True},

        {'name': 'Statsheaderdiag', 'type': 'header', 'label': 'Diagnostics'},
        {'name': 'Statserrcount', 'type': 'int', 'default': 0, 'label': 'Error Count', 'readOnly': True},
        {'name': 'Statserrmsg', 'type': 'str', 'default': '', 'label': 'Last Error', 'readOnly': True},
    ],

    'Pixel Outputs': [
        # Pixel Type section
        {'name': 'Pixheadertype', 'type': 'header', 'label': 'Pixel Type'},
        {'name': 'Pixtype', 'type': 'menu', 'default': 'WS2812B', 'label': 'Pixel Type',
         'menuNames': ['WS2812B'], 'menuLabels': ['WS2812B']},  # Populated dynamically from device
        {'name': 'Pixcolortype', 'type': 'menu', 'default': 'RGB', 'label': 'Color Type',
         'menuNames': ['RGB', 'RGBW'], 'menuLabels': ['RGB', 'RGBW']},

        # Options section
        {'name': 'Pixheaderoptions', 'type': 'header', 'label': 'Options'},
        {'name': 'Pixholdlast', 'type': 'toggle', 'default': False, 'label': 'Hold Last Frame'},
        {'name': 'Pixdropframe', 'type': 'toggle', 'default': True, 'label': 'Drop Frame on Overrun'},
        {'name': 'Pixexpand', 'type': 'toggle', 'default': False, 'label': 'Expanded Mode'},

        # Gamma section
        {'name': 'Pixheadergamma', 'type': 'header', 'label': 'Gamma'},
        {'name': 'Pixgammaon', 'type': 'toggle', 'default': False, 'label': 'Gamma Correction'},
        {'name': 'Pixditheron', 'type': 'toggle', 'default': False, 'label': 'Dithering',
         'enableExpr': "me.par.Pixgammaon.eval()"},
        {'name': 'Pixgammar', 'type': 'float', 'default': 2.0, 'label': 'Red',
         'min': 1.0, 'max': 3.0, 'clampMin': True, 'clampMax': True,
         'enableExpr': "me.par.Pixgammaon.eval()"},
        {'name': 'Pixgammag', 'type': 'float', 'default': 2.0, 'label': 'Green',
         'min': 1.0, 'max': 3.0, 'clampMin': True, 'clampMax': True,
         'enableExpr': "me.par.Pixgammaon.eval()"},
        {'name': 'Pixgammab', 'type': 'float', 'default': 2.0, 'label': 'Blue',
         'min': 1.0, 'max': 3.0, 'clampMin': True, 'clampMax': True,
         'enableExpr': "me.par.Pixgammaon.eval()"},
        {'name': 'Pixgammaw', 'type': 'float', 'default': 2.0, 'label': 'White',
         'min': 1.0, 'max': 3.0, 'clampMin': True, 'clampMax': True,
         'enableExpr': "me.par.Pixgammaon.eval() and me.par.Pixcolortype.eval() == 'RGBW'"},

        # Playback section
        {'name': 'Pixheaderplayback', 'type': 'header', 'label': 'Playback'},
        {'name': 'Pixpbmode', 'type': 'menu', 'default': 'Play', 'label': 'Playback Behavior',
         'menuNames': ['Play', 'Live', 'Blank', 'Freeze'],
         'menuLabels': ['Play', 'Live', 'Blank', 'Freeze']},

        # External Intensity section
        {'name': 'Pixheaderintensity', 'type': 'header', 'label': 'External Intensity'},
        {'name': 'Pixliveintsrc', 'type': 'menu', 'default': 'disabled', 'label': 'Source',
         'menuNames': ['disabled', 'sACN', 'Art-Net'],
         'menuLabels': ['Disabled', 'sACN', 'Art-Net']},
        {'name': 'Pixliveintuni', 'type': 'int', 'default': 1, 'label': 'Universe',
         'min': 1, 'max': 63999, 'clampMin': True, 'clampMax': True,
         'enableExpr': "me.par.Pixliveintsrc.eval() != 'disabled'"},
        {'name': 'Pixliveintch', 'type': 'int', 'default': 1, 'label': 'Channel',
         'min': 1, 'max': 512, 'clampMin': True, 'clampMax': True,
         'enableExpr': "me.par.Pixliveintsrc.eval() != 'disabled'"},

        # Controls section
        {'name': 'Pixoutcontrols', 'type': 'header', 'label': 'Controls'},
        {'name': 'Pixoutapply', 'type': 'pulse', 'label': 'Apply'},
        {'name': 'Pixoutsave', 'type': 'pulse', 'label': 'Apply & Save'},
        {'name': 'Pixoutrevert', 'type': 'pulse', 'label': 'Revert'},
    ],

    'Pixel Data': [
        # Data Source section
        {'name': 'Headerdatasrc', 'type': 'header', 'label': 'Data Source'},
        {'name': 'Pixdatasrc', 'type': 'menu', 'default': 'Art-Net', 'label': 'Data Source',
         'menuNames': ['Art-Net', 'sACN'], 'menuLabels': ['Art-Net', 'sACN']},
        {'name': 'Pixinformat', 'type': 'menu', 'default': '8Bit', 'label': 'Input Resolution',
         'menuNames': ['8Bit', '16Bit'], 'menuLabels': ['8 Bit', '16 Bit']},
        {'name': 'Pixspanuni', 'type': 'toggle', 'default': True, 'label': 'Split Pixels Across Universes'},
        {'name': 'Pixautopatch', 'type': 'toggle', 'default': False, 'label': 'Auto Patch'},

        # Status section (read-only)
        {'name': 'Headerdatastatus', 'type': 'header', 'label': 'Status'},
        {'name': 'Pixusedpixels', 'type': 'int', 'default': 0, 'label': 'Pixels Used', 'readOnly': True},
        {'name': 'Pixremainpixels', 'type': 'int', 'default': 0, 'label': 'Pixels Remaining', 'readOnly': True},
        {'name': 'Pixuseduni', 'type': 'int', 'default': 0, 'label': 'Universes Used', 'readOnly': True},
        {'name': 'Pixremainuni', 'type': 'int', 'default': 0, 'label': 'Universes Remaining', 'readOnly': True},

        # Controls section
        {'name': 'Headerpixcontrols', 'type': 'header', 'label': 'Controls'},
        {'name': 'Pixapply', 'type': 'pulse', 'label': 'Apply'},
        {'name': 'Pixsave', 'type': 'pulse', 'label': 'Apply & Save'},
        {'name': 'Pixrevert', 'type': 'pulse', 'label': 'Revert'},

        # Per-port sequence
        {'name': 'Headerports', 'type': 'header', 'label': 'Pixel Outputs'},
        {'name': 'Port', 'type': 'sequence', 'members': [
            {'name': 'Portdesc', 'type': 'str', 'default': '', 'label': 'Name'},
            {'name': 'Portstartuni', 'type': 'int', 'default': 1, 'label': 'Start Universe',
             'min': 1, 'max': 63999, 'clampMin': True, 'clampMax': True},
            {'name': 'Portstartch', 'type': 'int', 'default': 1, 'label': 'Start Channel',
             'min': 1, 'max': 512, 'clampMin': True, 'clampMax': True},
            {'name': 'Portpixels', 'type': 'int', 'default': 0, 'label': 'Pixels',
             'min': 0, 'clampMin': True},
            {'name': 'Portnullpix', 'type': 'int', 'default': 0, 'label': 'Null Pixels',
             'min': 0, 'clampMin': True},
            {'name': 'Portzigzag', 'type': 'int', 'default': 1, 'label': 'Zig Zag',
             'min': 1, 'clampMin': True},
            {'name': 'Portgroup', 'type': 'int', 'default': 1, 'label': 'Group',
             'min': 1, 'clampMin': True},
            {'name': 'Portintensity', 'type': 'int', 'default': 100, 'label': 'Intensity %',
             'min': 0, 'max': 100, 'clampMin': True, 'clampMax': True},
            {'name': 'Portreverse', 'type': 'toggle', 'default': False, 'label': 'Reversed'},
            {'name': 'Portcolororder', 'type': 'menu', 'default': 'RGB', 'label': 'Color Order',
             'menuNames': ['RGB', 'RBG', 'GRB', 'GBR', 'BRG', 'BGR'],
             'menuLabels': ['RGB', 'RBG', 'GRB', 'GBR', 'BRG', 'BGR']},
        ]},
    ],

    'Aux Port': [
        {'name': 'Auxmode', 'type': 'menu', 'default': 'Off', 'label': 'Mode',
         'menuNames': ['Off', 'DMX512Out', 'DMX512In'],
         'menuLabels': ['Off', 'DMX512 Output', 'DMX512 Input']},

        {'name': 'Auxdatasrc', 'type': 'menu', 'default': 'sACN', 'label': 'Data Source',
         'menuNames': ['sACN', 'Art-Net'], 'menuLabels': ['sACN (E1.31)', 'Art-Net'],
         'enableExpr': "me.par.Auxmode.eval() == 'DMX512Out'"},

        {'name': 'Auxuni', 'type': 'int', 'default': 1, 'label': 'Universe Number',
         'min': 1, 'max': 63999, 'clampMin': True, 'clampMax': True,
         'enableExpr': "me.par.Auxmode.eval() == 'DMX512Out'"},

        {'name': 'Auxholdlast', 'type': 'toggle', 'default': False, 'label': 'Hold Last Frame',
         'enableExpr': "me.par.Auxmode.eval() == 'DMX512Out'"},

        {'name': 'Auxdropframe', 'type': 'toggle', 'default': True, 'label': 'Drop Frame on Overrun',
         'enableExpr': "me.par.Auxmode.eval() == 'DMX512Out'"},

        {'name': 'Auxpbmode', 'type': 'menu', 'default': 'Play', 'label': 'Alt Playback Behavior',
         'menuNames': ['Play', 'Live', 'Blank', 'Freeze'],
         'menuLabels': ['Play', 'Live', 'Blank', 'Freeze'],
         'enableExpr': "me.par.Auxmode.eval() == 'DMX512Out'"},

        {'name': 'Auxcolortype', 'type': 'menu', 'default': 'RGB', 'label': 'Output Color Type',
         'menuNames': ['RGB', 'RGBW'], 'menuLabels': ['RGB', 'RGBW'],
         'enableExpr': "me.par.Auxmode.eval() == 'DMX512Out'"},

        {'name': 'Auxinformat', 'type': 'menu', 'default': '8Bit', 'label': 'Output Color Resolution',
         'menuNames': ['8Bit', '16Bit'], 'menuLabels': ['8 Bit', '16 Bit'],
         'enableExpr': "me.par.Auxmode.eval() == 'DMX512Out'"},

        {'name': 'Auxcolororder', 'type': 'menu', 'default': 'RGB', 'label': 'Output Color Order',
         'menuNames': ['RGB', 'RBG', 'GRB', 'GBR', 'BRG', 'BGR'],
         'menuLabels': ['RGB', 'RBG', 'GRB', 'GBR', 'BRG', 'BGR'],
         'enableExpr': "me.par.Auxmode.eval() == 'DMX512Out'"},

        {'name': 'Auxextint', 'type': 'toggle', 'default': False, 'label': 'External Intensity Channel',
         'enableExpr': "me.par.Auxmode.eval() == 'DMX512Out'"},

        # Controls
        {'name': 'Auxheadercontrols', 'type': 'header', 'label': 'Controls'},
        {'name': 'Auxapply', 'type': 'pulse', 'label': 'Apply'},
        {'name': 'Auxsave', 'type': 'pulse', 'label': 'Apply & Save'},
        {'name': 'Auxrevert', 'type': 'pulse', 'label': 'Revert'},
    ],
}


def _ensurePage(comp, pageName):
    """Get or create a custom page."""
    for page in comp.customPages:
        if page.name == pageName:
            return page
    return comp.appendCustomPage(pageName)


def _ensurePar(page, parDef):
    """Create a parameter if it doesn't exist."""
    name = parDef['name']
    parType = parDef['type']

    # Sequence type - create sequence and its member parameters
    if parType == 'sequence':
        _ensureSequence(page, parDef)
        return

    if hasattr(page.owner.par, name):
        return  # Already exists, don't overwrite

    label = parDef.get('label', name)

    # Create by type
    if parType == 'header':
        newPar = page.appendHeader(name, label=label)
    elif parType == 'str':
        newPar = page.appendStr(name, label=label)
    elif parType == 'float':
        newPar = page.appendFloat(name, label=label)
    elif parType == 'int':
        newPar = page.appendInt(name, label=label)
    elif parType == 'toggle':
        newPar = page.appendToggle(name, label=label)
    elif parType == 'menu':
        newPar = page.appendMenu(name, label=label)
    elif parType == 'pulse':
        newPar = page.appendPulse(name, label=label)
    elif parType == 'pop':
        newPar = page.appendPOP(name, label=label)
    elif parType == 'strmenu':
        newPar = page.appendStrMenu(name, label=label)
    else:
        return

    # Set metadata
    par = newPar[0]
    if 'default' in parDef:
        par.default = parDef['default']
        par.val = parDef['default']
    if parDef.get('readOnly'):
        par.readOnly = True
    if 'menuNames' in parDef:
        par.menuNames = parDef['menuNames']
        par.menuLabels = parDef.get('menuLabels', parDef['menuNames'])
    if 'enableExpr' in parDef:
        par.enableExpr = parDef['enableExpr']
    if 'min' in parDef:
        par.min = parDef['min']
    if 'max' in parDef:
        par.max = parDef['max']
    if parDef.get('clampMin'):
        par.clampMin = True
    if parDef.get('clampMax'):
        par.clampMax = True


def _ensureSequence(page, seqDef):
    """Create a sequence and its member parameters."""
    name = seqDef['name']
    members = seqDef.get('members', [])
    comp = page.owner

    # Create the sequence if it doesn't exist
    if not hasattr(comp.seq, name):
        page.appendSequence(name)

        # Create member parameters (these become the block template)
        for memberDef in members:
            _createPar(page, memberDef)

        # Set blockSize to number of members
        seq = getattr(comp.seq, name)
        seq.blockSize = len(members)

        # Start with 1 block minimum
        if seq.numBlocks == 0:
            seq.numBlocks = 1


def _createPar(page, parDef):
    """Create a parameter (without checking if it exists)."""
    name = parDef['name']
    parType = parDef['type']
    label = parDef.get('label', name)

    # Create by type
    if parType == 'header':
        newPar = page.appendHeader(name, label=label)
    elif parType == 'str':
        newPar = page.appendStr(name, label=label)
    elif parType == 'float':
        newPar = page.appendFloat(name, label=label)
    elif parType == 'int':
        newPar = page.appendInt(name, label=label)
    elif parType == 'toggle':
        newPar = page.appendToggle(name, label=label)
    elif parType == 'menu':
        newPar = page.appendMenu(name, label=label)
    elif parType == 'pulse':
        newPar = page.appendPulse(name, label=label)
    elif parType == 'pop':
        newPar = page.appendPOP(name, label=label)
    elif parType == 'strmenu':
        newPar = page.appendStrMenu(name, label=label)
    else:
        return

    # Set metadata
    par = newPar[0]
    if 'default' in parDef:
        par.default = parDef['default']
        par.val = parDef['default']
    if parDef.get('readOnly'):
        par.readOnly = True
    if 'menuNames' in parDef:
        par.menuNames = parDef['menuNames']
        par.menuLabels = parDef.get('menuLabels', parDef['menuNames'])
    if 'enableExpr' in parDef:
        par.enableExpr = parDef['enableExpr']
    if 'min' in parDef:
        par.min = parDef['min']
    if 'max' in parDef:
        par.max = parDef['max']
    if parDef.get('clampMin'):
        par.clampMin = True
    if parDef.get('clampMax'):
        par.clampMax = True


def _ensureSequences(comp):
    """Legacy function - sequences now handled in _ensureSequence."""
    pass


def ensurePars(comp):
    """Ensure all defined parameters exist on the component."""
    for pageName, parDefs in PAGES.items():
        page = _ensurePage(comp, pageName)
        for parDef in parDefs:
            _ensurePar(page, parDef)

    # Configure sequences after all params exist
    _ensureSequences(comp)

    # Sort pages in specified order
    _sortPages(comp)


def _sortPages(comp):
    """Sort custom pages according to PAGE_ORDER."""
    # Get existing custom page names
    existingPages = [p.name for p in comp.customPages]

    # Build ordered list: pages in PAGE_ORDER first (if they exist), then any others
    orderedPages = [p for p in PAGE_ORDER if p in existingPages]
    for p in existingPages:
        if p not in orderedPages:
            orderedPages.append(p)

    # Apply sort
    if orderedPages:
        comp.sortCustomPages(*orderedPages)
