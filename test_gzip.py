import gzip
try:
    gzip.decompress(b'not a gzip')
except Exception as e:
    print(f"Exception: {type(e).__name__}: {e}")
