# app/ssl_patch.py
import ssl
import httpcore._ssl as httpcore_ssl
import httpcore._sync.connection as sync_conn
import httpcore._async.connection as async_conn

CERT_PATH = "/etc/ssl/certs/ca-certificates.crt"


def apply_patch():
    def _patched_default_ssl_context() -> ssl.SSLContext:
        context = ssl.create_default_context()
        context.load_verify_locations(cafile=CERT_PATH)
        return context

    httpcore_ssl.default_ssl_context = _patched_default_ssl_context
    sync_conn.default_ssl_context = _patched_default_ssl_context
    async_conn.default_ssl_context = _patched_default_ssl_context
    print("SSL patch applied")