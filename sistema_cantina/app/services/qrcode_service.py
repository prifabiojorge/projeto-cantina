from __future__ import annotations

import io

import qrcode


def make_qrcode_png_bytes(data: str) -> bytes:
    img = qrcode.make(data)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
