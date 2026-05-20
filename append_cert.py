# append_cert.py
import certifi

cert_path = certifi.where()

with open("/tmp/company-ca.pem", "r") as f:
    corp_cert = f.read().strip()

with open(cert_path, "r") as f:
    bundle = f.read()

if corp_cert not in bundle:
    with open(cert_path, "a") as f:
        f.write("\n" + corp_cert + "\n")
    print(f"Appended corp cert to {cert_path}")
else:
    print(f"Already present in {cert_path}")