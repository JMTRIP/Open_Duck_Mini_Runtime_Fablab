# Installation de la carte microSD du Pi (Runtime) — BiscaLab

Procédure suivie et validée le 13/10/2026 sur un **Raspberry Pi 4B** (banc de développement).
Elle vaut aussi pour le **Pi Zero 2 W** du robot : même image 64 bits, même code.

> Aucun mot de passe dans ce fichier. Le mot de passe du compte `biscalab` est rangé
> dans le coffre d'accès du club.

## Matériel

- microSD de marque (SanDisk, Samsung, Kingston), classe A1 ou A2, **32 Go minimum** (validé avec 128 Go).
- Lecteur de carte sur le PC.
- Alimentation USB-C 5 V / 3 A pour le Pi 4B.
- Un réseau Wi-Fi (pour le Zero 2 W : réseau en **2,4 GHz** obligatoire).
- Pas besoin d'écran ni de clavier.

## Pourquoi Raspberry Pi OS Bookworm (Debian 12) et pas la dernière version

Le Runtime fige ses bibliothèques (`onnxruntime 1.18.1`, `numpy 1.26.4`, `scipy 1.15.1`…).
`onnxruntime 1.18.1` ne s'installe pas avec Python 3.13 (issue #38 du dépôt d'origine).
Bookworm fournit **Python 3.11**, la version utilisée par le projet d'origine.
La version récente (Debian 13 « Trixie ») fournit Python 3.13 : à éviter pour l'instant.

## 1. Télécharger l'image Bookworm

Raspberry Pi Imager 2.0.12 ne propose plus Bookworm dans sa liste (nous ne l'y avons pas trouvé).
Il faut télécharger l'image à la main :

- Adresse : `https://downloads.raspberrypi.com/raspios_oldstable_lite_arm64/images/`
- Ouvrir le dossier le plus récent et prendre le fichier **`…-raspios-bookworm-arm64-lite.img.xz`**
  (le nom doit contenir `bookworm`, `arm64` et `lite`). Nous avons utilisé celle du 2026-10-06.
- Ne pas décompresser le fichier : Imager lit directement le `.img.xz`.

## 2. Écrire la carte avec Raspberry Pi Imager

1. **Appareil** : le modèle de Pi (Pi 4 ou Zero 2 W ; un réglage « Pi 3 » donne la même image).
2. **OS** : tout en bas, « Utiliser une image personnalisée », puis choisir le fichier téléchargé.
3. **Stockage** : la microSD. Vérifier la capacité affichée (Imager efface tout le disque choisi).
4. **Écrire**, en gardant la vérification activée.

Avec une image personnalisée, Imager 2.0.12 **saute l'étape de personnalisation**
(utilisateur, Wi-Fi, SSH). On la remplace par un fichier `custom.toml` (étape 3).

## 3. Préparer le fichier `custom.toml`

Après l'écriture, débrancher puis rebrancher le lecteur : un lecteur **`bootfs`** apparaît
(si Windows propose de formater un autre lecteur : **Annuler**).

Créer avec le Bloc-notes un fichier contenant exactement ceci, en remplaçant les trois valeurs
en majuscules :

```toml
config_version = 1

[system]
hostname = "canard"

[user]
name = "biscalab"
password = 'MOT_DE_PASSE_TEMPORAIRE'
password_encrypted = false

[ssh]
enabled = true
password_authentication = true

[wlan]
ssid = 'NOM_DU_WIFI'
password = 'MOT_DE_PASSE_WIFI'
password_encrypted = false
hidden = false
country = "FR"

[locale]
keymap = "fr"
timezone = "Europe/Paris"
```

- Enregistrer **à la racine de `bootfs`** (à côté de `cmdline.txt`), type « **Tous les fichiers** »,
  nom **`custom.toml`** (et non `custom.toml.txt`).
- Garder les apostrophes autour des valeurs. Si un mot de passe contient lui-même une apostrophe,
  le mettre entre guillemets doubles à la place.
- Éviter les accents dans ce fichier.

**À savoir :** le Pi lit ce fichier **une seule fois**, au tout premier démarrage, puis il
**l'efface**, même si une partie a échoué (par exemple un Wi-Fi mal recopié). Remettre un
`custom.toml` plus tard ne sert à rien : pour recommencer, il faut réécrire la carte (étape 2).
Le mot de passe en clair disparaît donc de la carte au premier démarrage.

## 4. Premier démarrage et connexion

1. Éjecter proprement la carte, la mettre dans le Pi, brancher l'alimentation.
2. Attendre **3 à 5 minutes** (le Pi agrandit le système et redémarre une fois tout seul).
   La LED verte clignote de façon irrégulière : c'est normal.
3. Trouver l'adresse IP du Pi dans l'interface de la box (appareil nommé `canard`).
   Chez nous, le nom `canard.local` n'était pas reconnu par Windows : l'adresse IP a marché.
4. Dans PowerShell sur le PC :

   ```
   ssh biscalab@<adresse IP>
   ```

   Répondre `yes` à la question sur l'empreinte, puis entrer le mot de passe temporaire
   (rien ne s'affiche pendant la saisie, c'est normal).
   L'invite doit devenir `biscalab@canard:~ $`.
5. Changer tout de suite le mot de passe avec `passwd`, et ranger le nouveau dans le coffre du club.

## 5. Vérifier le système

```
python3 --version; grep PRETTY_NAME /etc/os-release; df -h / | tail -1
```

Résultat obtenu : `Python 3.11.2`, `Debian GNU/Linux 12 (bookworm)`, et la taille de la carte
(117 Go pour une carte de 128 Go).

## 6. Mettre à jour et installer les outils de base

```
sudo apt update && sudo apt full-upgrade -y && sudo apt install -y git python3-pip python3-venv
sudo reboot
```

Compter 3 à 10 minutes, puis se reconnecter en SSH après une minute.

## 7. Installer le Runtime du club

```
git clone https://github.com/JMTRIP/Open_Duck_Mini_Runtime_Fablab.git && python3 -m venv ~/.venvs/canard && source ~/.venvs/canard/bin/activate && cd Open_Duck_Mini_Runtime_Fablab && pip install -e .
```

- Le dépôt est public : aucun identifiant GitHub n'est demandé. Le Pi **récupère** le code,
  il n'envoie jamais rien (on modifie sur le PC, on envoie, puis on fait `git pull` sur le Pi).
- Compter 5 à 15 minutes. Les avertissements jaunes `DEPRECATION` sont sans conséquence.
- Versions installées constatées : `onnxruntime 1.18.1`, `numpy 1.26.4`, `scipy 1.15.1`,
  `pygame 2.6.0`, `rustypot 0.1.0`, `pypot 5.0.2`, `adafruit-circuitpython-bno055 5.4.13`.
- Nous utilisons `python3 -m venv` au lieu de `virtualenvwrapper` (cité dans le README d'origine) :
  même résultat, une configuration en moins.

Activer l'environnement automatiquement à chaque connexion :

```
echo 'source ~/.venvs/canard/bin/activate' >> ~/.bashrc
```

L'invite commence alors par `(canard)`. Sans cela, il faut taper
`source ~/.venvs/canard/bin/activate` à chaque connexion.

## 8. Activer l'I²C (bus de l'IMU)

```
sudo raspi-config nonint do_i2c 0 && sudo apt install -y i2c-tools && sudo reboot
```

Après reconnexion, `ls /dev/i2c*` doit afficher au moins `/dev/i2c-1`
(sur Pi 4, `/dev/i2c-20` et `/dev/i2c-21` apparaissent aussi : bus internes, normal).

## 9. Ajouter d'autres réseaux Wi-Fi (maison, FabLab)

Le Pi retient plusieurs Wi-Fi et se connecte tout seul à celui qui est à portée.
Ajouter un réseau **avant** de changer de lieu (sinon plus d'accès au Pi sans câble) :

```
sudo nmcli connection add type wifi con-name biscalab-wifi ifname wlan0 ssid 'NOM_DU_WIFI' wifi-sec.key-mgmt wpa-psk wifi-sec.psk 'MOT_DE_PASSE_WIFI' connection.autoconnect yes
```

- Fonctionne même hors de portée du réseau (le profil est seulement enregistré).
- Réseau masqué : ajouter `802-11-wireless.hidden yes` à la fin.
- Vérifier avec `nmcli connection show`. Alternative en menus : `sudo nmtui`.
- Pour le Zero 2 W : le réseau doit exister en **2,4 GHz**.
- Sur un nouveau réseau, trouver l'adresse IP du Pi avec une appli de scan réseau sur téléphone
  (Fing par exemple), connecté au même Wi-Fi : le Pi apparaît sous le nom `canard`.

Pour une carte destinée au FabLab, mettre directement le Wi-Fi du FabLab dans `custom.toml`
(étape 3), et ajouter les réseaux personnels ensuite avec cette commande.

## Reste à faire quand le matériel sera là

- **Contrôleur de servos (USB-série)** : règle de latence, d'après le README d'origine.
  Créer `/etc/udev/rules.d/99-usb-serial.rules` contenant :

  ```
  SUBSYSTEM=="usb-serial", DRIVER=="ftdi_sio", ATTR{latency_timer}="1"
  ```

- **IMU (BNO055)** : vérifier qu'il répond avec `i2cdetect -y 1`, puis
  `python3 mini_bdx_runtime/mini_bdx_runtime/raw_imu.py`.
- **Servos** : `python3 scripts/check_motors.py`.
- **Configuration du robot** : `cp example_config.json ~/duck_config.json`, puis trouver les décalages
  avec `scripts/find_soft_offsets.py` et les reporter dans `duck_config.json`.
  Ce fichier et la calibration de l'IMU sont **propres à chaque robot** : ne pas les envoyer dans le dépôt.

## Passage du Pi 4B au Pi Zero 2 W

- La même carte démarre dans les deux (même image 64 bits, même brochage 40 broches).
- À refaire sur le robot : calibration IMU, décalages des servos, appairage de la manette Bluetooth.
- Les mesures de vitesse faites sur le Pi 4B sont **trop optimistes** pour le Zero 2 W
  (processeur nettement plus lent) : la boucle à 50 Hz devra être vérifiée sur le Zero lui-même.
- Pour le robot final, prévoir une carte neuve et refaire cette procédure : la carte de
  développement s'use et le code est de toute façon sur GitHub.
