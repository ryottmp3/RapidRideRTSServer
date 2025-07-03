import segno

if __name__ == "__main__":
    b64 = "eyJ0aWNrZXQiOiB7InRpY2tldF9pZCI6ICIwZDFkZDIwNy1iOWJhLTQxNDYtOGU1ZC1hN2M4OTAxMTRiZjAiLCAidXNlcl9pZCI6ICIwMDExMzIiLCAidGlja2V0X3R5cGUiOiAib25lX3RpbWUiLCAidmFsaWRfZm9yIjogIk5vbmUiLCAiaXNzdWVkX2F0IjogIjIwMjUwNzAyXzE4MjYtMDYwMCIsICJpc3N1ZXIiOiAiUlRTIFJhcGlkUmlkZSJ9LCAic2lnbmF0dXJlIjogIk1jaGZTREFWUnFlcUFuY2lTNnJxNStJYVdTeVVlOUpncTBrQlBiclB0OXBkQnFBajBmYlQwcDZJaEViMzRqY3d3bDk5RGFJejRJV0UvZUVIRWg0UEJBPT0ifQ=="
    qrcode = segno.make_qr(b64)
    qrcode.save(
        "ticket.png",
        scale=5
    )
