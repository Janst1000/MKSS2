let
  # Import Nixpkgs with allowUnfree enabled
  pkgs = import <nixpkgs> {
  };

  # Import mach-nix
  mach-nix = import (
    builtins.fetchGit {
      url = "https://github.com/DavHau/mach-nix";
      ref = "refs/heads/master";
    }
  ) {};

in
# Creating a shell with Python and Postman
mach-nix.mkPython {
  requirements = builtins.readFile ./requirements.txt;
}
