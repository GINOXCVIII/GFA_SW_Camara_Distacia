#! /bin/sh
usr=$USER
dsk=/home/$usr/Desktop/
app=/usr/share/applications/
bin=/usr/bin/

# PATH donde se ejecutó script
SCRIPT_PATH=$( cd $(dirname $0) ; pwd )
cd "${SCRIPT_PATH}"

echo "Creando archivos..."

# Creando archivos
# bin
cd $bin
echo "#!/bin/bash
cd $SCRIPT_PATH
./start.sh" > pendulo-frd

chmod +x pendulo-frd

echo "bin pendulo-frd creado"

# .desktop
cd $app
echo "[Desktop Entry]
Name=Pendulo
# Exec=$SCRIPT_PATH/start.sh
Exec=pendulo-frd
Icon=$SCRIPT_PATH/asst/icon.ico
Terminal=false
Type=Application
Categories=Development;
" > Pendulo.desktop

chmod +x Pendulo.desktop

echo ".desktop creado"

# Crear enlace simbolico al codigo en escritorio
cd ~/Desktop
ln -s $SCRIPT_PATH/src codigos

echo "Enlace simbolico creado"

echo "Listo."





