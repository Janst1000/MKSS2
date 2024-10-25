let
  mach-nix = import (
    builtins.fetchGit {
      url = "https://github.com/DavHau/mach-nix";
      ref = "refs/heads/master";
    }
  ) {};
in
mach-nix.mkPythonShell {
  requirements = builtins.readFile ./requirements.txt;
}
