{...}: {
  perSystem = {
    pkgs,
    lib,
    pythonSet,
    ...
  }: {
    devShells.default = pkgs.mkShell {
      packages = with pkgs; [
        pythonSet.python
        uv
        treefmt
        alejandra
        ruff
        pre-commit
      ];

      env = let
        baseEnv = {
          # Prevent uv from managing Python downloads
          UV_PYTHON_DOWNLOADS = "never";
          # Force uv to use nixpkgs Python interpreter
          UV_PYTHON = pythonSet.python.interpreter;
        };

        linuxEnv = lib.optionalAttrs pkgs.stdenv.isLinux {
          # Python libraries often load native shared objects using dlopen(3).
          # Setting LD_LIBRARY_PATH makes the dynamic library loader aware of libraries without using RPATH for lookup.
          LD_LIBRARY_PATH = lib.makeLibraryPath pkgs.pythonManylinuxPackages.manylinux1;
        };
      in
        baseEnv // linuxEnv;

      shellHook = ''
        unset PYTHONPATH
      '';
    };
  };
}
