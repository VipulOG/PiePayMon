{workspace, ...}: {
  perSystem = {
    pythonSet,
    lib,
    ...
  }: {
    packages = {
      default = (pythonSet.mkVirtualEnv "piepaymon-env" workspace.deps.default).overrideAttrs (old: {
        # Set meta.mainProgram for commands like `nix run`.
        # https://nixos.org/manual/nixpkgs/stable/#var-meta-mainProgram
        meta = (old.meta or {}) // {mainProgram = "piepaymon";};
      });
    };
  };
}
