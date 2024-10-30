let
  # Import Nixpkgs with allowUnfree enabled
  pkgs = import <nixpkgs> {
    config.allowUnfree = true;  # Enable unfree packages within this shell
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
pkgs.mkShell {
  # Set up the Python shell from mach-nix
  buildInputs = [
    (mach-nix.mkPython {
      requirements = builtins.readFile ./requirements.txt;
    })
    pkgs.postman
  ];
}
