A testing system for codeforces and similar tasks made for Innopolis students

# Setup (Ubuntu)
1. Clone the repository:
```bash
git clone https://github.com/Makcal/Gigatester.git
```

2. Enter the directory:
```bash
cd Gigatester
```

3. Run the setup script:
```bash
sudo sh chore/setup.sh
```

4. Copy systemd unit files to the systemd's directory:
```bash
sudo cp chore/gigatester.service chore/gigaweb.service /etc/systemd/system/
```

5. Enable and start these services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable gigatester
sudo systemctl enable gigaweb
sudo systemctl start gigatester
sudo systemctl enable gigatester
```

6. [Optional] You can always check logs via:
```bash
journalctl -eu servicename
```
