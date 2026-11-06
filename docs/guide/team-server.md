# Team server and login

By default `serve` listens on `127.0.0.1` without login: only your machine reaches the app. To work as a team on
one Mission, run one server with accounts.

## Accounts

```bash
python3 -m segowl user add alice     # asks the password twice
```

- Accounts live in `~/.config/segowl/users`, one line per account (`login:scrypt$salt$hash`), file mode 600:
  no password is stored in clear.
- The same command on an existing login changes its password.
- To remove an account, delete its line. No restart needed: the file is read on every request.
- As soon as the file holds one account, login is required, on loopback too.
- Every account has the same rights: the Mission, the Auditor Kits, the report.
- `--config DIR`, on both `user add` and `serve`, keeps the accounts somewhere else (one folder per server, for
  example). The same folder holds the list of your kit folders.

## Listen on the network

```bash
python3 -m segowl serve mission/ --host 0.0.0.0 --port 8000 --cert cert.pem --key key.pem
```

- The server refuses to start on a network address without an account.
- Without `--cert` / `--key` it serves plain HTTP and warns you: passwords and the Mission travel in clear.
- No certificate at hand? A self-signed one is enough for a Mission server:

```bash
openssl req -x509 -newkey rsa:2048 -nodes -days 90 -subj "/CN=segowl" \
  -addext "subjectAltName=IP:10.0.0.5" -keyout key.pem -out cert.pem
openssl x509 -in cert.pem -noout -fingerprint -sha256   # give this to the team to check the browser warning
```

!!! tip "No network exposure at all"
    Keep the server on loopback and reach it through SSH: `ssh -L 8000:127.0.0.1:8000 server`, then open
    `http://127.0.0.1:8000/`. No certificate needed, SSH already encrypts.

## Sessions

- Sign in on `/login`; **log out** is at the top right, next to your login.
- Sessions live in the server's memory: restarting it signs everyone out.
- The session cookie is `HttpOnly`, `SameSite=Strict`, and `Secure` under HTTPS.
- Without accounts, the app only answers to the address it listens on: a web page cannot reach it through
  DNS rebinding.

## Two auditors, one Mission

Saves never overwrite each other: if a file changed since you loaded it, your save is refused with
**Modified elsewhere** and a **Reload** button. Reload, then redo your change.
