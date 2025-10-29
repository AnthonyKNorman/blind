from ota import OTAUpdater

firmware_url = "https://github.com/AnthonyKNorman/blind/"

ota_updater = OTAUpdater(firmware_url, "test.py")

ota_updater.download_and_install_update_if_available()