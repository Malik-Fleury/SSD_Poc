#!/data/data/com.termux/files/usr/bin/bash
# À lancer UNE fois dans Termux, après `termux-setup-storage`.
# Usage : bash ~/storage/downloads/poc/setup.sh <nom-du-noeud>
set -e
NODE_NAME="${1:-a5-01}"
SRC="$HOME/storage/downloads/poc"

pkg update -y
pkg install -y python openssh

mkdir -p "$HOME/poc"
cp "$SRC/server.py" "$SRC/index.html" "$HOME/poc/"
echo "$NODE_NAME" > "$HOME/poc/node_name"

# SSH (port 8022) : permet de piloter le téléphone depuis le PC au lieu de taper sur l'écran.
echo "Choisis un mot de passe SSH :"
passwd
sshd

termux-wake-lock

cat > "$HOME/poc/run.sh" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock
pgrep sshd >/dev/null || sshd
NODE_NAME="$(cat ~/poc/node_name)" exec python ~/poc/server.py
EOF
chmod +x "$HOME/poc/run.sh"
echo "OK. Lancer le serveur : bash ~/poc/run.sh"
