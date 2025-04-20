#!/bin/bash

echo "==============================================="
echo "🕒 INSTALLATIONSSKRIPT FÖR KLOCKA (Raspberry Pi)"
echo "==============================================="
echo ""
echo "Detta skript kommer att:"
echo " - Uppdatera systemet (kan ta en stund...)"
echo " - Installera Python och nödvändiga bibliotek"
echo " - Ladda ner senaste koden från GitHub"
echo " - Skapa en systemd-tjänst som kör koden automatiskt vid uppstart"
echo ""
echo "⚠️  VIKTIGT: Raspberry Pi:n måste ha STRÖM och INTERNET"
echo "    under hela installationen. Avbryt INTE!"
echo ""

read -p "Tryck [Enter] för att fortsätta eller [Ctrl+C] för att avbryta..."

echo ""
echo "🔧 Uppdaterar systemet (detta kan ta några minuter)..."
sudo apt update && sudo apt upgrade -y

echo "🐍 Installerar Python och nödvändiga paket..."
sudo apt install -y python3 python3-pip python3-gpiozero curl

echo "📦 Installerar rpi_ws281x (kan bryta systempaket)..."
pip3 install rpi_ws281x --break-system-packages

echo "📁 Skapar mapp /opt/klocka-skript..."
sudo mkdir -p /opt/klocka-skript
cd /opt/klocka-skript

echo "⬇️ Laddar ner klocka-scriptet..."
sudo curl -o klockakod.py https://raw.githubusercontent.com/WilliamAnderssonDev/klocka/refs/heads/main/klockakod.py
sudo chmod +x klockakod.py

echo "🛠️ Skapar systemd-tjänst klockaskript.service (körs som root)..."
cat <<EOF | sudo tee /etc/systemd/system/klockaskript.service
[Unit]
Description=Starta klocka-script vid uppstart (wait for network)
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/bin/python3 /opt/klocka-skript/klockakod.py
WorkingDirectory=/opt/klocka-skript
StandardOutput=journal
StandardError=journal
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Aktiverar och startar tjänsten klockaskript..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable klockaskript.service
sudo systemctl start klockaskript.service

echo ""
echo "🎉 KLART!"
echo "Scriptet körs nu automatiskt vid varje uppstart så fort internet är tillgängligt."
echo "För att se loggar, kör: sudo journalctl -u klockaskript -f"
