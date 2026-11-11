"""Legge un raw LTspice binario non compresso (time double, resto float32) e riassume a finestre."""
import struct, sys

def leggi(path):
    f = open(path, "rb")
    data = f.read()
    i = data.find("Binary:\n".encode("utf-16-le"))
    head = data[:i].decode("utf-16-le")
    body = data[i + len("Binary:\n".encode("utf-16-le")):]
    names = []
    npts = 0
    lines = head.splitlines()
    for k, l in enumerate(lines):
        if l.startswith("No. Points:"):
            npts = int(l.split(":")[1])
        if l.startswith("Variables:"):
            for m in lines[k + 1:]:
                p = m.split()
                if len(p) >= 2:
                    names.append(p[1])
    nv = len(names)
    rec = 8 + 4 * (nv - 1)
    fmt = "<d" + "f" * (nv - 1)
    return names, npts, body, rec, fmt

def main(path, dt=0.05, cols=None):
    names, npts, body, rec, fmt = leggi(path)
    st = struct.Struct(fmt)
    idx = [names.index(c) for c in cols] if cols else list(range(1, len(names)))
    print("t", " ".join(names[i] for i in idx))
    win = 0.0
    mx = [-1e30] * len(names)
    mn = [1e30] * len(names)
    for k in range(npts):
        r = st.unpack_from(body, k * rec)
        t = abs(r[0])
        for i in idx:
            v = r[i]
            if v > mx[i]: mx[i] = v
            if v < mn[i]: mn[i] = v
        if t >= win + dt or k == npts - 1:
            print("%.2f " % t + " ".join("%.3g/%.3g" % (mn[i], mx[i]) for i in idx))
            win = t
            mx = [-1e30] * len(names)
            mn = [1e30] * len(names)

if __name__ == "__main__":
    p = sys.argv[1]
    dt = float(sys.argv[2]) if len(sys.argv) > 2 else 0.05
    cols = sys.argv[3].split(",") if len(sys.argv) > 3 else None
    main(p, dt, cols)
