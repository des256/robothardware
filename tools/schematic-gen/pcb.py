"""Build backbone.kicad_pcb from the schematic netlist: footprints with nets and schematic paths,
one placement rule area per hierarchical sheet, the usb_section rule area the DRU keys on, the
board outline, mounting holes and the version text.  Components are packed block by block into the
floorplan below (the "placement diagram"); routing is left for the layout stage.

Runs inside the KiCad 10 Flatpak python (pcbnew 10):
  flatpak run --filesystem=<repo>:rw --command=/usr/bin/python3 org.kicad.KiCad tools/schematic-gen/pcb.py
"""
import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sx import parse, find, first  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
PROJ = os.path.join(REPO, 'backbone')
NETLIST = os.path.join(PROJ, 'outputs', 'scratch', 'backbone.net')
PCB = os.path.join(PROJ, 'backbone.kicad_pcb')
SKELETON_PCB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'skeleton', 'backbone.kicad_pcb')
LIB = os.path.join(PROJ, '0_backbone.pretty')

BOARD_W, BOARD_H = 190.0, 130.0

# floorplan: sheet path -> (x0, y0, x1, y1, connector edge)
REGIONS = {
    '/input/': (0, 0, 46, 78, 'left'),
    '/buck-12v-servo/': (46, 0, 98, 44, None),
    '/buck-5v-servo/': (98, 0, 146, 44, None),
    '/buck-5v-usb/': (146, 0, 190, 44, None),
    '/servo-uart/': (46, 44, 90, 78, None),
    '/usb-hub/': (90, 44, 134, 78, None),
    '/usbc-upstream/': (134, 44, 190, 66, 'right'),
    '/usb-port-1/': (134, 66, 190, 83, 'right'),
    '/usb-port-2/': (134, 83, 190, 100, 'right'),
    '/usb-port-3/': (134, 100, 190, 117, 'right'),
    '/servo-port-0/': (0, 78, 33.5, 130, 'bottom'),
    '/servo-port-1/': (33.5, 78, 67, 130, 'bottom'),
    '/servo-port-2/': (67, 78, 100.5, 130, 'bottom'),
    '/servo-port-3/': (100.5, 78, 134, 130, 'bottom'),
}
USB_SECTION = (90, 44, 190, 130)
HOLES = [(4.5, 4.5), (BOARD_W - 4.5, 4.5), (4.5, BOARD_H - 4.5), (BOARD_W - 4.5, BOARD_H - 4.5)]
# connector rotation so the mating face points off the board edge (degrees, per footprint name prefix)
CONN_ROT = {'left': 180, 'right': 0, 'bottom': 270, 'top': 90}
MARGIN = 2.5
GAP = 1.2
EDGE_INSET = 0.6


def mm(v):
    return pcbnew.FromMM(v)


def vec(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def main():
    net = parse(open(NETLIST, encoding='utf-8').read())
    comps = find(first(net, 'components'), 'comp')
    nets = find(first(net, 'nets'), 'net')

    # always start from the skeleton board (layers, plot settings, DRU hooks) so reruns are clean
    board = pcbnew.LoadBoard(SKELETON_PCB)

    # ---- nets
    netmap = {}
    node_net = {}
    for n in nets:
        name = first(n, 'name')[1]
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        netmap[name] = ni
        for node in find(n, 'node'):
            node_net[(first(node, 'ref')[1], first(node, 'pin')[1])] = name

    # ---- footprints
    by_region = {}
    fps = {}
    for c in comps:
        ref = first(c, 'ref')[1]
        value = first(c, 'value')[1]
        fpname = first(c, 'footprint')[1].split(':', 1)[1]
        sp = first(c, 'sheetpath')
        names = first(sp, 'names')[1]
        tst = first(sp, 'tstamps')[1]
        sym_uuid = first(c, 'tstamps')[1]
        props = {first(p, 'name')[1]: (first(p, 'value')[1] if first(p, 'value') else '') for p in find(c, 'property')}
        fp = pcbnew.FootprintLoad(LIB, fpname)
        if fp is None:
            raise SystemExit(f'footprint {fpname} not found for {ref}')
        fp.SetFPID(pcbnew.LIB_ID('0_backbone', fpname))
        fp.SetReference(ref)
        fp.SetValue(value)
        try:
            fp.SetField('Footprint', '0_backbone:' + fpname)
            fp.SetField('Description', first(c, 'description')[1] if first(c, 'description') else '')
            fp.SetField('Datasheet', first(c, 'datasheet')[1] if first(c, 'datasheet') else '')
        except Exception:
            pass
        path = tst.rstrip('/') + '/' + sym_uuid
        fp.SetPath(pcbnew.KIID_PATH(path))
        fp.SetSheetname(names.strip('/') or 'backbone')
        fp.SetSheetfile(props.get('Sheetfile', ''))
        for fname in ('LCSC', 'MPN', 'max_mA'):
            if fname in props:
                try:
                    fp.SetField(fname, props[fname])
                except Exception:
                    pass
        attrs = fp.GetAttributes()
        if 'exclude_from_bom' in props:
            attrs |= pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES
        if 'dnp' in props:
            attrs |= pcbnew.FP_DNP
        fp.SetAttributes(attrs)
        for pad in fp.Pads():
            key = (ref, pad.GetNumber())
            if key in node_net:
                pad.SetNet(netmap[node_net[key]])
        board.Add(fp)
        fps[ref] = fp
        by_region.setdefault(names, []).append((ref, fp))

    # ---- placement
    reserved = [(hx - 6, hy - 6, hx + 6, hy + 6) for hx, hy in HOLES]

    def bbox_mm(fp):
        bb = fp.GetBoundingBox(False, False)
        return (pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom()))

    def place_center(fp, cx, cy):
        fp.SetPosition(vec(0, 0))
        l, t, r, b = bbox_mm(fp)
        ox, oy = (l + r) / 2, (t + b) / 2
        fp.SetPosition(vec(cx - ox, cy - oy))

    def intersects(a, b):
        return not (a[2] <= b[0] or a[0] >= b[2] or a[3] <= b[1] or a[1] >= b[3])

    placed_rects = []
    for sheet, items in by_region.items():
        if sheet == '/':
            continue
        x0, y0, x1, y1, edge = REGIONS[sheet]
        x0 += MARGIN
        y0 += MARGIN
        x1 -= MARGIN
        y1 -= MARGIN
        conns = [(r, f) for r, f in items if r.startswith('J') and not r.startswith('JP')]
        rest = [(r, f) for r, f in items if not (r.startswith('J') and not r.startswith('JP'))]
        occupied = list(reserved)
        # connectors along the edge
        if edge:
            cx, cy = x0, y0
            for r, f in sorted(conns):
                f.SetOrientationDegrees(0)
                f.SetPosition(vec(0, 0))
                l, t, rr, b = bbox_mm(f)
                pads = list(f.Pads())
                px = sum(pcbnew.ToMM(p.GetPosition().x) for p in pads) / len(pads) - (l + rr) / 2
                py = sum(pcbnew.ToMM(p.GetPosition().y) for p in pads) / len(pads) - (t + b) / 2
                # pick the rotation that moves the pad centroid inboard (away from the edge)
                want = {'left': (1, 0), 'right': (-1, 0), 'bottom': (0, -1), 'top': (0, 1)}[edge]
                best, bestdot = 0, None
                for rot in (0, 90, 180, 270):
                    import math
                    a = math.radians(rot)
                    qx = px * math.cos(a) - py * math.sin(a)
                    qy = px * math.sin(a) + py * math.cos(a)
                    dot = qx * want[0] + qy * want[1]
                    if bestdot is None or dot > bestdot + 1e-6:
                        best, bestdot = rot, dot
                if abs(bestdot) < 0.3:   # symmetric footprint (vertical header): keep the pin row along the edge
                    best = 0 if edge in ('bottom', 'top') else 90
                f.SetOrientationDegrees(best)
                f.SetPosition(vec(0, 0))
                l, t, rr, b = bbox_mm(f)
                w, h = rr - l, b - t
                if edge in ('left', 'right'):
                    rx0 = x0 if edge == 'left' else x1 - w
                    while any(intersects((rx0, cy, rx0 + w, cy + h), o) for o in occupied):
                        cy += 1.0
                    place_center(f, rx0 + (EDGE_INSET if edge == 'left' else -EDGE_INSET) + w / 2, cy + h / 2)
                    occupied.append((rx0, cy, rx0 + w, cy + h))
                    cy += h + GAP
                elif edge == 'bottom':
                    while any(intersects((cx, y1 - h, cx + w, y1), o) for o in occupied):
                        cx += 1.0
                    place_center(f, cx + w / 2, y1 - EDGE_INSET - h / 2)
                    occupied.append((cx, y1 - h, cx + w, y1))
                    cx += w + GAP
        # the rest in rows, largest first
        rest.sort(key=lambda rf: -(bbox_mm(rf[1])[3] - bbox_mm(rf[1])[1]) * (bbox_mm(rf[1])[2] - bbox_mm(rf[1])[0]))
        cx, cy, rowh = x0, y0, 0
        if edge == 'left':
            cx = x0 + max([bbox_mm(f)[2] - bbox_mm(f)[0] for _, f in conns] + [0]) + GAP
        xmin = cx
        xmax = x1 - (max([bbox_mm(f)[2] - bbox_mm(f)[0] for _, f in conns] + [0]) + GAP if edge == 'right' else 0)
        ymax = y1 - (max([bbox_mm(f)[3] - bbox_mm(f)[1] for _, f in conns] + [0]) + GAP if edge == 'bottom' else 0)
        for r, f in rest:
            f.SetPosition(vec(0, 0))
            l, t, rr, b = bbox_mm(f)
            w, h = rr - l, b - t
            for attempt in range(200):
                if cx + w > xmax and cx > xmin:
                    cx, cy, rowh = xmin, cy + rowh + GAP, 0
                rect = (cx, cy, cx + w, cy + h)
                if any(intersects(rect, o) for o in occupied):
                    cx += 1.0
                    continue
                break
            place_center(f, cx + w / 2, cy + h / 2)
            occupied.append(rect)
            placed_rects.append((r, rect))
            if cy + h > ymax + 0.01:
                print(f'  OVERFLOW {sheet} {r} bottom {cy + h:.1f} > {ymax:.1f}')
            cx += w + GAP
            rowh = max(rowh, h)
        print(f'{sheet:18s} parts {len(items):3d} used rows to y={cy + rowh:6.1f} of {ymax:6.1f}', flush=True)

    # mounting holes
    holes = [r for r in fps if r.startswith('H')]
    for (hx, hy), r in zip(HOLES, sorted(holes)):
        place_center(fps[r], hx, hy)

    # ---- outline
    outline = pcbnew.PCB_SHAPE(board)
    outline.SetShape(pcbnew.SHAPE_T_RECT)
    outline.SetStart(vec(0, 0))
    outline.SetEnd(vec(BOARD_W, BOARD_H))
    outline.SetLayer(pcbnew.Edge_Cuts)
    outline.SetWidth(mm(0.1))
    board.Add(outline)

    # ---- rule areas: one placement area per sheet instance + the usb_section keep-out anchor
    def rule_area(name, rect, sheet=None):
        z = pcbnew.ZONE(board)
        z.SetIsRuleArea(True)
        z.SetZoneName(name)
        ls = pcbnew.LSET()
        for layer in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
            ls.addLayer(layer)
        z.SetLayerSet(ls)
        z.SetDoNotAllowTracks(False)
        z.SetDoNotAllowVias(False)
        z.SetDoNotAllowZoneFills(False)
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
        if sheet:
            z.SetPlacementAreaEnabled(True)
            z.SetPlacementAreaSourceType(pcbnew.PLACEMENT_SOURCE_T_SHEETNAME)
            z.SetPlacementAreaSource(sheet)
        x0, y0, x1, y1 = rect
        o = z.Outline()
        o.NewOutline()
        for (x, y) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            o.Append(mm(x), mm(y))
        board.Add(z)
        return z

    for sheet, (x0, y0, x1, y1, edge) in REGIONS.items():
        rule_area(sheet.strip('/'), (x0, y0, x1, y1), sheet)
    rule_area('usb_section', USB_SECTION)

    # ---- texts
    def text(s, x, y, layer, size=1.2, bold=False):
        t = pcbnew.PCB_TEXT(board)
        t.SetText(s)
        t.SetPosition(vec(x, y))
        t.SetLayer(layer)
        t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
        t.SetTextThickness(mm(size * 0.15))
        if bold:
            t.SetBold(True)
        board.Add(t)
        return t

    text('ROBOT BACKBONE rev A', 162, 121, pcbnew.F_SilkS, 1.5, True)
    text('${KKH_VERSION_DATE}', 162, 124.5, pcbnew.F_SilkS, 1.2)
    tj = text('JLCJLCJLCJLC', 60, BOARD_H - 2.5, pcbnew.B_SilkS, 1.0)
    tj.SetMirrored(True)
    for sheet, (x0, y0, x1, y1, edge) in REGIONS.items():
        text(sheet.strip('/'), (x0 + x1) / 2, y0 + 1.6, pcbnew.Cmts_User, 1.4, True)

    pcbnew.SaveBoard(PCB, board, True)  # aSkipSettings: never rewrite backbone.kicad_pro
    print('saved', PCB, 'footprints', len(fps), 'nets', len(netmap))


if __name__ == '__main__':
    main()
