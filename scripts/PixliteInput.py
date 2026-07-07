"""
PixliteInput - Input / transmit configuration mixin for Pixlite extension

Wires the "Input" custom parameter page to the internal POP chain that sends
pixel data from the user's scene out to the PixLite device:

    select1 (pop)  ->  dmxfixture1 (net/subnet/universe/channel/changap)  ->  dmxout1

Parameter -> operator bindings:

    Inpixeldata     -> select1.pop            (scene pixel data source)
    Innet           -> dmxfixture1.net        (Art-Net only)
    Insubnet        -> dmxfixture1.subnet     (Art-Net only)
    Inuniverse      -> dmxfixture1.universe
    Inchannel       -> dmxfixture1.channel
    Inlocaladdress  -> dmxout1.localaddress   (local NIC to transmit from)

Transmit settings that are governed by other pages are derived here too:

    dmxout1.interface   follows the Pixel Data page 'Data Source' (Pixdatasrc)
    dmxout1.netaddress  follows the connected device IP (Websocketnetaddress)

All bindings are live expressions, so changes take effect immediately. These
target local operators (not device config pushed over WebSocket), so no
Apply/Save step is required.
"""


class PixliteInputMixin:
    """Input / transmit configuration for the Pixlite extension."""

    # Internal op names in the send chain
    _SELECT_OP = 'select1'
    _FIXTURE_OP = 'dmxfixture1'
    _OUTPUT_OP = 'dmxout1'

    # "Infer from Pixel Data" derives the transmit base address from the first
    # pixel output (Port 0) on the Pixel Data page. Port 0's Start Universe is a
    # flat, 1-based universe; the DMX Fixture POP addresses via the Art-Net
    # 15-bit split (net*256 + subnet*16 + universe, 0-based), so we decompose
    # (StartUni - 1). The -1 assumes the device's "Universe 1" is the first
    # transmitted universe (Art-Net universe 0) - which matches this project's
    # existing defaults (Port 0 StartUni 1 <-> dmxfixture universe 0).
    _INFER_EXPRS = {
        'Innet':      "max(0, int(me.par.Port0portstartuni.eval()) - 1) // 256",
        'Insubnet':   "(max(0, int(me.par.Port0portstartuni.eval()) - 1) // 16) % 16",
        'Inuniverse': "max(0, int(me.par.Port0portstartuni.eval()) - 1) % 16",
        'Inchannel':  "int(me.par.Port0portstartch.eval())",
    }

    # =========================================================================
    # Setup (called from __init__)
    # =========================================================================

    def _SetupInput(self):
        """Populate menus, seed defaults, and bind Input params to internal ops.

        Order matters: seeding reads the operators' current constant values, so
        it must run before binding replaces those values with expressions.
        """
        self._PopulateLocalAddressMenu()
        self._SeedInputDefaults()
        self._BindInputToOps()
        self._ApplyInferMode()

    def _PopulateLocalAddressMenu(self):
        """Copy the machine's available NICs from dmxout1 into Inlocaladdress."""
        out = self.ownerComp.op(self._OUTPUT_OP)
        if not out or not hasattr(self.ownerComp.par, 'Inlocaladdress'):
            return
        names = list(out.par.localaddress.menuNames or [])
        if names:
            self.ownerComp.par.Inlocaladdress.menuNames = names
            self.ownerComp.par.Inlocaladdress.menuLabels = names

    def _SeedInputDefaults(self):
        """Seed custom params from current operator values (non-breaking on first run).

        Must run BEFORE _BindInputToOps, which replaces the operators' constant
        values with expressions that reference these params.
        """
        comp = self.ownerComp
        out = comp.op(self._OUTPUT_OP)

        # Local address: adopt whatever dmxout1 currently transmits from, but
        # only on first run (empty). After binding, localaddress evaluates to
        # this param, so re-init leaves the user's choice untouched.
        if out and hasattr(comp.par, 'Inlocaladdress') and comp.par.Inlocaladdress.eval() == '':
            try:
                comp.par.Inlocaladdress = out.par.localaddress.eval()
            except Exception:
                pass

    def _BindInputToOps(self):
        """Bind internal POP-chain parameters to the Input custom parameters.

        Expressions use parent() because each target op is a direct child of the
        Pixlite component, so parent() resolves to the component that owns the
        custom parameters.
        """
        comp = self.ownerComp
        sel = comp.op(self._SELECT_OP)
        fix = comp.op(self._FIXTURE_OP)
        out = comp.op(self._OUTPUT_OP)

        # Scene pixel data source -> select1
        if sel:
            sel.par.pop.expr = (
                "parent().par.Inpixeldata.eval().path "
                "if parent().par.Inpixeldata.eval() else ''"
            )

        # Base addressing -> dmxfixture1
        if fix:
            fix.par.net.expr = 'parent().par.Innet.eval()'
            fix.par.subnet.expr = 'parent().par.Insubnet.eval()'
            fix.par.universe.expr = 'parent().par.Inuniverse.eval()'
            fix.par.channel.expr = 'parent().par.Inchannel.eval()'

        # Transmit settings -> dmxout1
        if out:
            out.par.localaddress.expr = 'parent().par.Inlocaladdress.eval()'
            # Protocol follows the Pixel Data page 'Data Source'
            out.par.interface.expr = (
                "'artnet' if parent().par.Pixdatasrc.eval() == 'Art-Net' else 'sacn'"
            )
            # Destination auto-tracks the connected device IP
            out.par.netaddress.expr = 'parent().par.Websocketnetaddress.eval()'

    def _ApplyInferMode(self):
        """Apply the 'Infer from Pixel Data' toggle to the addressing params.

        On  -> Net/Subnet/Universe/Start Channel become live expressions derived
               from Port 0 and are locked read-only. They update automatically
               whenever Port 0's Start Universe/Channel changes.
        Off -> the currently-shown (inferred) values are frozen as editable
               constants, so turning it off adopts the inferred address as a
               manual starting point.
        """
        comp = self.ownerComp
        if not hasattr(comp.par, 'Ininfer'):
            return
        infer = comp.par.Ininfer.eval()

        for name, expr in self._INFER_EXPRS.items():
            p = getattr(comp.par, name, None)
            if p is None:
                continue
            if infer:
                # Setting .expr switches the parameter to expression mode.
                p.expr = expr
                p.readOnly = True
            else:
                frozen = p.eval()
                p.mode = type(p.mode).CONSTANT
                p.val = frozen
                p.readOnly = False

    # =========================================================================
    # Parameter Change Handlers
    # =========================================================================

    def par_Ininfer(self, par):
        """Toggle inferred addressing on/off."""
        self._ApplyInferMode()

    # =========================================================================
    # Public API
    # =========================================================================

    def RefreshLocalAddresses(self):
        """Re-read the machine's available NICs into the Inlocaladdress menu."""
        self._PopulateLocalAddressMenu()
