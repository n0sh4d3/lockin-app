from urllib.parse import urlparse
import ctypes
import subprocess
import os


# i'll use bare excepts and you shouldn't care


class WebsiteBlocker:
    def __init__(self, platform):
        self.platform = platform
        self.is_blocking = False
        self.proxy_server = None
        self.proxy_thread = None
        self.blocked_sites = set()
        self.original_hosts = ""

    def add_blocked_site(self, url):
        """Add a site to the blocked list"""
        if not url.startswith(("http://", "https://")):
            url = "http://" + url

        try:
            domain = urlparse(url).netloc
            if domain:
                self.blocked_sites.add(domain)
                if not domain.startswith("www."):
                    self.blocked_sites.add("www." + domain)
                else:
                    self.blocked_sites.add(domain[4:])  # remove www
        except:
            pass

    def remove_blocked_site(self, url):
        """Remove a site from the blocked list"""
        if not url.startswith(("http://", "https://")):
            url = "http://" + url

        try:
            domain = urlparse(url).netloc
            if domain:
                self.blocked_sites.discard(domain)
                if not domain.startswith("www."):
                    self.blocked_sites.discard("www." + domain)
                else:
                    self.blocked_sites.discard(domain[4:])
        except:
            pass

    def get_hosts_file_path(self):
        """Get the hosts file path for current platform"""
        if self.platform == "windows":
            return r"C:\Windows\System32\drivers\etc\hosts"
        else:
            return "/etc/hosts"

    def backup_hosts_file(self):
        """Backup original hosts file"""
        try:
            hosts_path = self.get_hosts_file_path()
            with open(hosts_path, "r") as f:
                self.original_hosts = f.read()
            return True
        except:
            return False

    def restore_hosts_file(self):
        """Restore original hosts file"""
        try:
            hosts_path = self.get_hosts_file_path()
            with open(hosts_path, "w") as f:
                f.write(self.original_hosts)
            return True
        except:
            return False

    def modify_hosts_file(self, block=True):
        """Modify hosts file to block/unblock sites"""
        try:
            hosts_path = self.get_hosts_file_path()

            if block:
                blocked_entries = []
                for site in self.blocked_sites:
                    blocked_entries.append(f"127.0.0.1 {site}")

                with open(hosts_path, "a") as f:
                    f.write("\n# Fokus App Blocked Sites\n")
                    f.write("\n".join(blocked_entries))
                    f.write("\n# End Fokus App Blocked Sites\n")
            else:
                with open(hosts_path, "r") as f:
                    lines = f.readlines()

                filtered_lines = []
                skip_section = False

                for line in lines:
                    if "# Fokus App Blocked Sites" in line:
                        skip_section = True
                        continue
                    elif "# End Fokus App Blocked Sites" in line:
                        skip_section = False
                        continue
                    elif not skip_section:
                        filtered_lines.append(line)

                with open(hosts_path, "w") as f:
                    f.writelines(filtered_lines)

            return True
        except:
            return False

    def flush_dns(self):
        """Flush DNS cache to apply hosts file changes"""
        try:
            if self.platform == "windows":
                subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
            elif self.platform == "darwin":
                subprocess.run(
                    ["sudo", "dscacheutil", "-flushcache"], capture_output=True
                )
            else:
                subprocess.run(
                    ["sudo", "systemctl", "restart", "systemd-resolved"],
                    capture_output=True,
                )
        except:
            pass

    def start_blocking(self):
        """Start blocking websites"""
        if not self.blocked_sites or self.is_blocking:
            return False

        if not self.backup_hosts_file():
            return False

        if self.modify_hosts_file(block=True):
            self.flush_dns()
            self.is_blocking = True
            return True

        return False

    def stop_blocking(self):
        """Stop blocking websites"""
        if not self.is_blocking:
            return True

        if self.restore_hosts_file():
            self.flush_dns()
            self.is_blocking = False
            return True

        return False

    def is_admin(self):
        """Check if running with admin privileges"""
        try:
            if self.platform == "windows":
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except:
            return False


class SettingsManager:
    def __init__(self):
        self.settings_file = "fokus_settings.json"
        self.settings = self.load_settings()

    def load_settings(self):
        """Load settings from file"""
        try:
            with open(self.settings_file, "r") as f:
                return json.load(f)
        except:
            return {
                "theme": "system",
                "website_blocking_enabled": False,
                "blocked_sites": [
                    "facebook.com",
                    "twitter.com",
                    "instagram.com",
                    "youtube.com",
                    "tiktok.com",
                    "reddit.com",
                ],
            }

    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=2)
        except:
            pass

    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
        self.save_settings()
