{
  description = "CSV row comparator tool";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      perSystem =
        { pkgs, ... }:
        {

          # Development shell with pandas
          devShells.default = pkgs.mkShell {
            buildInputs = with pkgs; [
              (python3.withPackages (
                ps: with ps; [
                  pandas
                ]
              ))
            ];
          };

          # App to run compare.py directly
          apps.default = {
            type = "app";
            program = toString (
              pkgs.writeShellScript "compare" ''
                exec ${pkgs.python3.withPackages (ps: [ ps.pandas ])}/bin/python ${./compare.py} "$@"
              ''
            );
          };

        };
    };
}
